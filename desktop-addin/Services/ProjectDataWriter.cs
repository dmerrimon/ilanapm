using System;
using Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Services
{
    public class ProjectDataWriter
    {
        public void WriteValidationResults(Application projectApp, Models.ValidationResult validationResult)
        {
            if (projectApp.ActiveProject == null)
                throw new Exception("No active project found.");

            Project activeProject = projectApp.ActiveProject;

            // Update each task with its validation issues
            foreach (var issue in validationResult.issues)
            {
                if (!string.IsNullOrEmpty(issue.task_id))
                {
                    var task = FindTaskById(activeProject, issue.task_id);
                    if (task != null)
                    {
                        // Update Risk Score based on severity
                        int riskScore = GetRiskScoreFromSeverity(issue.severity);
                        SetTaskCustomFieldNumber(task, "Risk Score", riskScore);

                        // Update Gating Status if regulatory issue
                        if (issue.category == "regulatory")
                        {
                            SetTaskCustomFieldText(task, "Gating Status", "Blocked");
                        }

                        // Add note with issue details
                        AppendTaskNote(task, $"[{issue.severity.ToUpper()}] {issue.message}\n{issue.detail}\nSuggested Fix: {issue.suggested_fix}\n\n");

                        // Highlight high-risk tasks
                        if (riskScore >= 70)
                        {
                            task.Marked = true; // Flag for attention
                        }
                    }
                }
            }
        }

        public void WriteMLAdvisory(Application projectApp, string taskId, Models.DurationPrediction prediction, Models.RiskScore riskScore)
        {
            if (projectApp.ActiveProject == null)
                throw new Exception("No active project found.");

            Project activeProject = projectApp.ActiveProject;
            var task = FindTaskById(activeProject, taskId);

            if (task != null)
            {
                // Write ML predictions to custom fields
                if (prediction != null)
                {
                    string durationRange = $"{prediction.confidence_interval.lower}-{prediction.confidence_interval.upper} days";
                    SetTaskCustomFieldText(task, "ML Predicted Duration", durationRange);
                    SetTaskCustomFieldNumber(task, "ML Confidence %", (int)(prediction.confidence_score * 100));

                    // Add explanation to notes
                    AppendTaskNote(task, $"ML Duration Prediction: {prediction.explanation}\n\n");
                }

                if (riskScore != null)
                {
                    SetTaskCustomFieldNumber(task, "Risk Score", riskScore.risk_score);

                    // Add risk factors to notes
                    string riskFactors = string.Join("\n- ", riskScore.risk_factors);
                    AppendTaskNote(task, $"Risk Analysis [{riskScore.risk_level.ToUpper()}]:\n- {riskFactors}\n\n");
                }
            }
        }

        private Microsoft.Office.Interop.MSProject.Task FindTaskById(Project project, string taskId)
        {
            if (int.TryParse(taskId, out int id))
            {
                foreach (Microsoft.Office.Interop.MSProject.Task task in project.Tasks)
                {
                    if (task != null && task.ID == id)
                        return task;
                }
            }
            return null;
        }

        private void SetTaskCustomFieldText(Microsoft.Office.Interop.MSProject.Task task, string fieldName, string value)
        {
            try
            {
                var fieldConstant = task.Application.FieldNameToFieldConstant(fieldName, PjField.pjTaskField);
                task.SetField(fieldConstant, value);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error setting {fieldName}: {ex.Message}");
            }
        }

        private void SetTaskCustomFieldNumber(Microsoft.Office.Interop.MSProject.Task task, string fieldName, int value)
        {
            try
            {
                var fieldConstant = task.Application.FieldNameToFieldConstant(fieldName, PjField.pjTaskField);
                task.SetField(fieldConstant, value);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error setting {fieldName}: {ex.Message}");
            }
        }

        private void AppendTaskNote(Microsoft.Office.Interop.MSProject.Task task, string note)
        {
            try
            {
                string existingNotes = task.Notes ?? "";
                task.Notes = existingNotes + note;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error appending note: {ex.Message}");
            }
        }

        private int GetRiskScoreFromSeverity(string severity)
        {
            switch (severity.ToLower())
            {
                case "error":
                    return 90;
                case "warning":
                    return 60;
                case "info":
                    return 30;
                default:
                    return 50;
            }
        }
    }
}
