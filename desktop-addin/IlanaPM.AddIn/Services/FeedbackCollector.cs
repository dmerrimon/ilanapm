using System;
using System.Collections.Generic;
using IlanaPM.AddIn.Models;
using MSProject = Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Collects task completion feedback from MS Project for ML learning
    /// </summary>
    public class FeedbackCollector
    {
        // Track which tasks we've already reported to avoid duplicates
        private static HashSet<int> reportedTaskIds = new HashSet<int>();

        /// <summary>
        /// Collect all completed tasks that haven't been reported yet
        /// </summary>
        public List<TaskCompletionFeedback> CollectCompletedTasks(MSProject.Project project)
        {
            var feedback = new List<TaskCompletionFeedback>();

            if (project == null || project.Tasks == null)
            {
                System.Diagnostics.Debug.WriteLine("FeedbackCollector: project or tasks null");
                return feedback;
            }

            System.Diagnostics.Debug.WriteLine($"FeedbackCollector: Scanning {project.Tasks.Count} tasks for completion");

            int completedCount = 0;
            foreach (MSProject.Task task in project.Tasks)
            {
                if (task == null) continue;

                // Skip if already reported
                if (reportedTaskIds.Contains(task.ID)) continue;

                // Check if task is 100% complete
                if (task.PercentComplete >= 100)
                {
                    completedCount++;
                    System.Diagnostics.Debug.WriteLine($"  Found completed task: {task.ID} - {task.Name} ({task.PercentComplete}%)");

                    var taskFeedback = ExtractTaskFeedback(task, project);
                    if (taskFeedback != null)
                    {
                        feedback.Add(taskFeedback);
                        reportedTaskIds.Add(task.ID);
                        System.Diagnostics.Debug.WriteLine($"    ✓ Feedback extracted successfully");
                    }
                    else
                    {
                        System.Diagnostics.Debug.WriteLine($"    ✗ Feedback extraction failed (null result)");
                    }
                }
            }

            System.Diagnostics.Debug.WriteLine($"FeedbackCollector: Found {completedCount} completed tasks, extracted {feedback.Count} valid feedback entries");
            return feedback;
        }

        /// <summary>
        /// Extract feedback data from a completed MS Project task
        /// </summary>
        private TaskCompletionFeedback ExtractTaskFeedback(MSProject.Task task, MSProject.Project project)
        {
            try
            {
                // Extract predicted duration from custom field (Number6) or calculate from original duration
                int? predictedDuration = ExtractPredictedDuration(task);
                System.Diagnostics.Debug.WriteLine($"      Predicted duration: {predictedDuration?.ToString() ?? "null"}");

                if (!predictedDuration.HasValue || predictedDuration.Value <= 0)
                {
                    // Skip tasks without predicted durations
                    System.Diagnostics.Debug.WriteLine($"      Skipping: No valid predicted duration");
                    return null;
                }

                // Calculate actual duration
                int actualDuration = CalculateActualDuration(task);
                System.Diagnostics.Debug.WriteLine($"      Actual duration: {actualDuration} days (Start: {task.Start}, Finish: {task.Finish})");

                if (actualDuration <= 0)
                {
                    // Skip tasks with invalid actual durations
                    System.Diagnostics.Debug.WriteLine($"      Skipping: No valid actual duration");
                    return null;
                }

                return new TaskCompletionFeedback
                {
                    task_id = task.UniqueID.ToString(),
                    task_name = task.Name,
                    category = GetFieldSafe(task, MSProject.PjField.pjTaskText4) ?? "Unknown",

                    predicted_duration_days = predictedDuration.Value,
                    predicted_confidence = ExtractConfidence(task),
                    model_version = "v1.0",

                    actual_duration_days = actualDuration,
                    actual_start_date = task.Start.ToString("yyyy-MM-dd"),
                    actual_end_date = task.Finish.ToString("yyyy-MM-dd"),

                    country_code = ExtractCountryCode(task),
                    authority = GetFieldSafe(task, MSProject.PjField.pjTaskText1),
                    study_phase = GetFieldSafe(task, MSProject.PjField.pjTaskText2),
                    therapeutic_area = GetFieldSafe(task, MSProject.PjField.pjTaskText3),

                    project_id = project.Name,
                    recorded_by = Environment.UserName
                };
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error extracting feedback for task {task.Name}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Extract predicted duration from task
        /// Checks Number6 custom field first, then falls back to Duration
        /// </summary>
        private int? ExtractPredictedDuration(MSProject.Task task)
        {
            try
            {
                // Check Number6 field for ML-predicted duration
                var number6 = GetFieldSafe(task, MSProject.PjField.pjTaskNumber6);
                if (!string.IsNullOrEmpty(number6))
                {
                    if (double.TryParse(number6, out double predicted))
                    {
                        return (int)Math.Round(predicted);
                    }
                }

                // Fall back to original Duration if no prediction stored
                // Convert from minutes to days (divide by 480 = 8 hours * 60 minutes)
                int durationMinutes = (int)task.Duration;
                if (durationMinutes > 0)
                {
                    return durationMinutes / 480; // 8-hour workdays
                }

                return null;
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Calculate actual duration from start and finish dates
        /// </summary>
        private int CalculateActualDuration(MSProject.Task task)
        {
            try
            {
                if (task.Start == null || task.Finish == null)
                    return 0;

                DateTime start = task.Start;
                DateTime finish = task.Finish;

                // Calculate business days
                int businessDays = 0;
                DateTime current = start.Date;
                while (current <= finish.Date)
                {
                    // Skip weekends
                    if (current.DayOfWeek != DayOfWeek.Saturday &&
                        current.DayOfWeek != DayOfWeek.Sunday)
                    {
                        businessDays++;
                    }
                    current = current.AddDays(1);
                }

                return businessDays;
            }
            catch
            {
                return 0;
            }
        }

        /// <summary>
        /// Extract confidence score from Number3 custom field
        /// </summary>
        private double ExtractConfidence(MSProject.Task task)
        {
            try
            {
                var number3 = GetFieldSafe(task, MSProject.PjField.pjTaskNumber3);
                if (!string.IsNullOrEmpty(number3))
                {
                    if (double.TryParse(number3, out double confidence))
                    {
                        // Confidence is stored as 0-100, convert to 0-1
                        return confidence / 100.0;
                    }
                }
                return 0.5; // Default medium confidence
            }
            catch
            {
                return 0.5;
            }
        }

        /// <summary>
        /// Extract country code from task
        /// Tries Text7 (Site IDs), Text14 (Template Source), then project name
        /// </summary>
        private string ExtractCountryCode(MSProject.Task task)
        {
            try
            {
                // Try Text14 (Template Source) - format: "API-UG" or "Library-GB"
                var templateSource = GetFieldSafe(task, MSProject.PjField.pjTaskText14);
                if (!string.IsNullOrEmpty(templateSource))
                {
                    var parts = templateSource.Split('-');
                    if (parts.Length >= 2)
                    {
                        return parts[1]; // Extract country code
                    }
                }

                // Try Text7 (Site IDs) - format: "SITE-UG-001"
                var siteId = GetFieldSafe(task, MSProject.PjField.pjTaskText7);
                if (!string.IsNullOrEmpty(siteId))
                {
                    var parts = siteId.Split('-');
                    if (parts.Length >= 2)
                    {
                        return parts[1]; // Extract country code
                    }
                }

                // Default to US if can't extract
                return "US";
            }
            catch
            {
                return "US";
            }
        }

        /// <summary>
        /// Safely get string value from MS Project task field
        /// </summary>
        private string GetFieldSafe(MSProject.Task task, MSProject.PjField field)
        {
            try
            {
                var value = task.GetField(field);
                return value?.ToString();
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Reset the reported tasks tracker (for testing)
        /// </summary>
        public static void ResetReportedTasks()
        {
            reportedTaskIds.Clear();
        }
    }
}
