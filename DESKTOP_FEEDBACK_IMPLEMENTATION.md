# Desktop Add-in Feedback Loop Implementation Guide

This guide provides complete implementation for adding feedback collection to the MS Project desktop add-in.

## Overview

**Goal**: Allow PMs to submit completed task data to the backend, enabling ML to learn from actual project outcomes.

**What It Does**:
- Detects tasks marked 100% complete in MS Project
- Extracts predicted vs actual durations from custom fields
- Sends feedback to backend API
- Shows accuracy report to PM

---

## Files to Create/Modify

### 1. `desktop-addin/IlanaPM.AddIn/Models/FeedbackModels.cs` [CREATE]

```csharp
using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Task completion feedback model
    /// </summary>
    public class TaskCompletionFeedback
    {
        // Task identification
        public string task_id { get; set; }
        public string task_name { get; set; }
        public string category { get; set; }

        // Prediction data
        public int? predicted_duration_days { get; set; }
        public double? predicted_confidence { get; set; }
        public string model_version { get; set; }

        // Actual outcome
        public int actual_duration_days { get; set; }
        public string actual_start_date { get; set; }  // YYYY-MM-DD
        public string actual_end_date { get; set; }    // YYYY-MM-DD

        // Context
        public string country_code { get; set; }
        public string authority { get; set; }
        public string study_phase { get; set; }
        public string therapeutic_area { get; set; }

        // Metadata
        public string project_id { get; set; }
        public string recorded_by { get; set; }
    }

    /// <summary>
    /// Response from feedback submission
    /// </summary>
    public class TaskCompletionResponse
    {
        public bool success { get; set; }
        public int recorded_count { get; set; }
        public string message { get; set; }
        public AccuracySummary accuracy_summary { get; set; }
    }

    public class AccuracySummary
    {
        public int predicted_days { get; set; }
        public int actual_days { get; set; }
        public int variance_days { get; set; }
        public double variance_percent { get; set; }
        public bool was_accurate { get; set; }
        public string threshold { get; set; }
    }

    /// <summary>
    /// Accuracy report model
    /// </summary>
    public class AccuracyReport
    {
        public int total_predictions { get; set; }
        public int accurate_predictions { get; set; }
        public double accuracy_rate { get; set; }
        public double avg_error_days { get; set; }
        public double avg_error_percent { get; set; }

        public Dictionary<string, CategoryStats> by_category { get; set; }
        public Dictionary<string, CountryStats> by_country { get; set; }
        public Dictionary<string, AuthorityStats> by_authority { get; set; }

        public List<string> recommendations { get; set; }
    }

    public class CategoryStats
    {
        public int total { get; set; }
        public double accuracy_rate { get; set; }
        public double avg_error_days { get; set; }
    }

    public class CountryStats
    {
        public int total { get; set; }
        public double accuracy_rate { get; set; }
        public double avg_error_days { get; set; }
    }

    public class AuthorityStats
    {
        public int total { get; set; }
        public double accuracy_rate { get; set; }
        public double avg_error_days { get; set; }
    }
}
```

---

### 2. `desktop-addin/IlanaPM.AddIn/Services/ApiClient.cs` [MODIFY]

Add these methods to the existing ApiClient class:

```csharp
/// <summary>
/// Submit task completion feedback
/// </summary>
public async Task<Models.TaskCompletionResponse> SubmitTaskCompletionAsync(
    Models.TaskCompletionFeedback feedback)
{
    string jsonContent = JsonConvert.SerializeObject(feedback);
    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

    HttpResponseMessage response = await httpClient.PostAsync(
        API_BASE_URL + "/api/v1/feedback/task-completion", content);

    response.EnsureSuccessStatusCode();
    string responseBody = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<Models.TaskCompletionResponse>(responseBody);
}

/// <summary>
/// Submit multiple task completions in bulk
/// </summary>
public async Task<Models.TaskCompletionResponse> SubmitMultipleCompletionsAsync(
    List<Models.TaskCompletionFeedback> completions)
{
    string jsonContent = JsonConvert.SerializeObject(completions);
    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

    HttpResponseMessage response = await httpClient.PostAsync(
        API_BASE_URL + "/api/v1/feedback/task-completions", content);

    response.EnsureSuccessStatusCode();
    string responseBody = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<Models.TaskCompletionResponse>(responseBody);
}

/// <summary>
/// Get accuracy report
/// </summary>
public async Task<Models.AccuracyReport> GetAccuracyReportAsync()
{
    HttpResponseMessage response = await httpClient.GetAsync(
        API_BASE_URL + "/api/v1/feedback/accuracy-report");

    response.EnsureSuccessStatusCode();
    string responseBody = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<Models.AccuracyReport>(responseBody);
}
```

---

### 3. `desktop-addin/IlanaPM.AddIn/Services/FeedbackCollector.cs` [CREATE]

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Collects feedback from completed tasks
    /// </summary>
    public class FeedbackCollector
    {
        /// <summary>
        /// Find all completed tasks that haven't submitted feedback yet
        /// </summary>
        public List<Models.TaskCompletionFeedback> CollectCompletedTasks(Application projectApp)
        {
            if (projectApp.ActiveProject == null)
                throw new Exception("No active project found.");

            var completedTasks = new List<Models.TaskCompletionFeedback>();
            Project activeProject = projectApp.ActiveProject;

            foreach (Microsoft.Office.Interop.MSProject.Task task in activeProject.Tasks)
            {
                if (task == null) continue;

                // Check if task is 100% complete
                if (task.PercentComplete >= 100)
                {
                    // Check if we already submitted feedback for this task
                    string feedbackSubmitted = GetTaskCustomFieldText(task, "Feedback Submitted");
                    if (feedbackSubmitted == "Yes")
                        continue;  // Skip - already submitted

                    var feedback = ExtractTaskFeedback(task, activeProject);
                    if (feedback != null)
                        completedTasks.Add(feedback);
                }
            }

            return completedTasks;
        }

        /// <summary>
        /// Extract feedback from a single task
        /// </summary>
        private Models.TaskCompletionFeedback ExtractTaskFeedback(
            Microsoft.Office.Interop.MSProject.Task task,
            Project project)
        {
            try
            {
                // Get task details
                string taskId = task.ID.ToString();
                string taskName = task.Name;
                string category = GetTaskCustomFieldText(task, "Task Category");

                // Get actual duration (convert from minutes to days)
                int actualDurationDays = ConvertMinutesToDays(task.ActualDuration);

                // Get predicted duration from custom field
                int? predictedDays = null;
                double predictedValue = GetTaskCustomFieldNumber(task, "ML Predicted Duration");
                if (predictedValue > 0)
                    predictedDays = (int)predictedValue;

                // Get predicted confidence
                double? confidence = null;
                double confidenceValue = GetTaskCustomFieldNumber(task, "ML Confidence");
                if (confidenceValue > 0)
                    confidence = confidenceValue;

                // Get model version
                string modelVersion = GetTaskCustomFieldText(task, "ML Model Version");

                // Get actual dates
                string actualStart = task.ActualStart != null
                    ? ((DateTime)task.ActualStart).ToString("yyyy-MM-dd")
                    : null;

                string actualEnd = task.ActualFinish != null
                    ? ((DateTime)task.ActualFinish).ToString("yyyy-MM-dd")
                    : null;

                // Get context
                string countryCode = GetTaskCustomFieldText(task, "Country");
                string authority = GetTaskCustomFieldText(task, "Authority");
                string phase = GetTaskCustomFieldText(task, "Study Phase");

                // Get project ID (use filename without extension)
                string projectId = System.IO.Path.GetFileNameWithoutExtension(project.Name);

                // Get current user
                string recordedBy = Environment.UserName + "@" + Environment.UserDomainName;

                return new Models.TaskCompletionFeedback
                {
                    task_id = taskId,
                    task_name = taskName,
                    category = category,
                    predicted_duration_days = predictedDays,
                    predicted_confidence = confidence,
                    model_version = modelVersion,
                    actual_duration_days = actualDurationDays,
                    actual_start_date = actualStart,
                    actual_end_date = actualEnd,
                    country_code = countryCode,
                    authority = authority,
                    study_phase = phase,
                    project_id = projectId,
                    recorded_by = recordedBy
                };
            }
            catch (Exception ex)
            {
                // Log error but continue processing other tasks
                System.Diagnostics.Debug.WriteLine($"Error extracting feedback from task {task.Name}: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Mark task as feedback submitted
        /// </summary>
        public void MarkFeedbackSubmitted(Application projectApp, string taskId)
        {
            var task = FindTaskById(projectApp.ActiveProject, taskId);
            if (task != null)
            {
                SetTaskCustomFieldText(task, "Feedback Submitted", "Yes");
            }
        }

        #region Helper Methods

        private int ConvertMinutesToDays(int minutes)
        {
            // MS Project stores duration in minutes
            // 8 hours per day = 480 minutes
            return minutes / 480;
        }

        private Microsoft.Office.Interop.MSProject.Task FindTaskById(Project project, string taskId)
        {
            foreach (Microsoft.Office.Interop.MSProject.Task task in project.Tasks)
            {
                if (task != null && task.ID.ToString() == taskId)
                    return task;
            }
            return null;
        }

        private string GetTaskCustomFieldText(Microsoft.Office.Interop.MSProject.Task task, string fieldName)
        {
            try
            {
                // Try Text1-Text30 fields
                for (int i = 1; i <= 30; i++)
                {
                    string customFieldName = task.Application.CustomFieldGetName((PjCustomField)Enum.Parse(typeof(PjCustomField), "pjCustomTaskText" + i));
                    if (customFieldName == fieldName)
                    {
                        object value = task.GetField((PjField)Enum.Parse(typeof(PjField), "pjTaskText" + i));
                        return value?.ToString();
                    }
                }
            }
            catch { }
            return null;
        }

        private double GetTaskCustomFieldNumber(Microsoft.Office.Interop.MSProject.Task task, string fieldName)
        {
            try
            {
                // Try Number1-Number20 fields
                for (int i = 1; i <= 20; i++)
                {
                    string customFieldName = task.Application.CustomFieldGetName((PjCustomField)Enum.Parse(typeof(PjCustomField), "pjCustomTaskNumber" + i));
                    if (customFieldName == fieldName)
                    {
                        object value = task.GetField((PjField)Enum.Parse(typeof(PjField), "pjTaskNumber" + i));
                        if (value != null && double.TryParse(value.ToString(), out double result))
                            return result;
                    }
                }
            }
            catch { }
            return 0;
        }

        private void SetTaskCustomFieldText(Microsoft.Office.Interop.MSProject.Task task, string fieldName, string value)
        {
            try
            {
                // Find or create custom field
                for (int i = 1; i <= 30; i++)
                {
                    string customFieldName = task.Application.CustomFieldGetName((PjCustomField)Enum.Parse(typeof(PjCustomField), "pjCustomTaskText" + i));
                    if (customFieldName == fieldName || string.IsNullOrEmpty(customFieldName))
                    {
                        if (string.IsNullOrEmpty(customFieldName))
                        {
                            task.Application.CustomFieldRename((PjCustomField)Enum.Parse(typeof(PjCustomField), "pjCustomTaskText" + i), fieldName);
                        }
                        task.SetField((PjField)Enum.Parse(typeof(PjField), "pjTaskText" + i), value);
                        break;
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error setting custom field {fieldName}: {ex.Message}");
            }
        }

        #endregion
    }
}
```

---

### 4. `desktop-addin/IlanaPM.AddIn/IlanaPMRibbon.cs` [MODIFY]

Add this button click handler:

```csharp
private async void btnRecordCompletions_Click(object sender, RibbonControlEventArgs e)
{
    try
    {
        // Collect completed tasks
        var feedbackCollector = new Services.FeedbackCollector();
        var completedTasks = feedbackCollector.CollectCompletedTasks(Globals.ThisAddIn.Application);

        if (completedTasks.Count == 0)
        {
            MessageBox.Show(
                "No completed tasks found that haven't already submitted feedback.",
                "Record Completions",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information);
            return;
        }

        // Ask PM to confirm
        var confirmResult = MessageBox.Show(
            $"Found {completedTasks.Count} completed task(s) ready to submit feedback.\n\n" +
            "This data helps improve ML predictions for future projects.\n\n" +
            "Submit feedback now?",
            "Record Task Completions",
            MessageBoxButtons.YesNo,
            MessageBoxIcon.Question);

        if (confirmResult != DialogResult.Yes)
            return;

        // Submit to backend
        var apiClient = new Services.ApiClient();
        var response = await apiClient.SubmitMultipleCompletionsAsync(completedTasks);

        // Mark tasks as submitted
        foreach (var feedback in completedTasks)
        {
            feedbackCollector.MarkFeedbackSubmitted(Globals.ThisAddIn.Application, feedback.task_id);
        }

        // Show success message
        string message = $"✓ Recorded {response.recorded_count} completed tasks!\n\n" +
                        $"{response.message}\n\n" +
                        "Thank you for helping improve ML predictions.";

        MessageBox.Show(message, "Feedback Submitted", MessageBoxButtons.OK, MessageBoxIcon.Information);

        // Optionally show accuracy report
        var showReport = MessageBox.Show(
            "Would you like to see the overall prediction accuracy report?",
            "View Accuracy Report",
            MessageBoxButtons.YesNo,
            MessageBoxIcon.Question);

        if (showReport == DialogResult.Yes)
        {
            btnViewAccuracy_Click(sender, e);
        }
    }
    catch (Exception ex)
    {
        MessageBox.Show(
            $"Error recording completions:\n\n{ex.Message}",
            "Error",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error);
    }
}

private async void btnViewAccuracy_Click(object sender, RibbonControlEventArgs e)
{
    try
    {
        var apiClient = new Services.ApiClient();
        var report = await apiClient.GetAccuracyReportAsync();

        // Show accuracy report form
        var reportForm = new AccuracyReportForm();
        reportForm.DisplayReport(report);
        reportForm.ShowDialog();
    }
    catch (Exception ex)
    {
        MessageBox.Show(
            $"Error loading accuracy report:\n\n{ex.Message}",
            "Error",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error);
    }
}
```

---

### 5. `desktop-addin/IlanaPM.AddIn/IlanaPMRibbon.xml` [MODIFY]

Add buttons to the ribbon:

```xml
<group id="grpFeedback" label="Learning">
  <button id="btnRecordCompletions"
          label="Record Completions"
          imageMso="DatabaseCheckInOut"
          size="large"
          onAction="btnRecordCompletions_Click" />
  <button id="btnViewAccuracy"
          label="Accuracy Report"
          imageMso="ChartInsert"
          size="large"
          onAction="btnViewAccuracy_Click" />
</group>
```

---

### 6. `desktop-addin/IlanaPM.AddIn/AccuracyReportForm.cs` [CREATE]

```csharp
using System;
using System.Text;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    public partial class AccuracyReportForm : Form
    {
        private TextBox txtReport;
        private Button btnClose;

        public AccuracyReportForm()
        {
            InitializeComponent();
        }

        public void DisplayReport(Models.AccuracyReport report)
        {
            var sb = new StringBuilder();

            sb.AppendLine("═══ PREDICTION ACCURACY REPORT ═══\n");
            sb.AppendLine($"Total Predictions: {report.total_predictions}");
            sb.AppendLine($"Accurate (±20%): {report.accurate_predictions}");
            sb.AppendLine($"Accuracy Rate: {report.accuracy_rate:F1}%");
            sb.AppendLine($"Avg Error: {report.avg_error_days:F1} days ({report.avg_error_percent:F1}%)\n");

            if (report.by_category != null && report.by_category.Count > 0)
            {
                sb.AppendLine("═══ BY CATEGORY ═══\n");
                foreach (var kvp in report.by_category)
                {
                    sb.AppendLine($"{kvp.Key}:");
                    sb.AppendLine($"  Total: {kvp.Value.total}");
                    sb.AppendLine($"  Accuracy: {kvp.Value.accuracy_rate:F1}%");
                    sb.AppendLine($"  Avg Error: {kvp.Value.avg_error_days:F1} days\n");
                }
            }

            if (report.by_country != null && report.by_country.Count > 0)
            {
                sb.AppendLine("═══ BY COUNTRY ═══\n");
                foreach (var kvp in report.by_country)
                {
                    sb.AppendLine($"{kvp.Key}:");
                    sb.AppendLine($"  Total: {kvp.Value.total}");
                    sb.AppendLine($"  Accuracy: {kvp.Value.accuracy_rate:F1}%");
                    sb.AppendLine($"  Avg Error: {kvp.Value.avg_error_days:F1} days\n");
                }
            }

            if (report.recommendations != null && report.recommendations.Count > 0)
            {
                sb.AppendLine("═══ RECOMMENDATIONS ═══\n");
                foreach (var rec in report.recommendations)
                {
                    sb.AppendLine($"• {rec}");
                }
            }

            txtReport.Text = sb.ToString();
        }

        private void InitializeComponent()
        {
            this.txtReport = new System.Windows.Forms.TextBox();
            this.btnClose = new System.Windows.Forms.Button();
            this.SuspendLayout();

            // txtReport
            this.txtReport.Dock = System.Windows.Forms.DockStyle.Fill;
            this.txtReport.Font = new System.Drawing.Font("Consolas", 9F);
            this.txtReport.Location = new System.Drawing.Point(0, 0);
            this.txtReport.Multiline = true;
            this.txtReport.Name = "txtReport";
            this.txtReport.ReadOnly = true;
            this.txtReport.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtReport.Size = new System.Drawing.Size(684, 511);
            this.txtReport.TabIndex = 0;

            // btnClose
            this.btnClose.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.btnClose.DialogResult = System.Windows.Forms.DialogResult.OK;
            this.btnClose.Location = new System.Drawing.Point(597, 476);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(75, 23);
            this.btnClose.TabIndex = 1;
            this.btnClose.Text = "Close";
            this.btnClose.UseVisualStyleBackColor = true;

            // AccuracyReportForm
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(684, 511);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.txtReport);
            this.Name = "AccuracyReportForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Prediction Accuracy Report";
            this.ResumeLayout(false);
            this.PerformLayout();
        }
    }
}
```

---

## Testing Instructions

### 1. Backend Test (Mac - Already Complete ✓)

Backend is running and tested. Database has sample data.

### 2. Desktop Add-in Test (Windows VM)

**Step 1**: Build and deploy the add-in with new feedback functionality

**Step 2**: Open MS Project with a timeline that has:
- Tasks with ML predictions (from ML Advisory)
- Some tasks marked 100% complete

**Step 3**: Click "Record Completions" button
- Should find completed tasks
- Should submit feedback to backend
- Should mark tasks as submitted

**Step 4**: Complete more tasks, click "Record Completions" again
- Should NOT resubmit already-submitted tasks
- Should only submit new completions

**Step 5**: Click "Accuracy Report" button
- Should show overall accuracy statistics
- Should show breakdown by category, country, authority
- Should show recommendations

---

## Custom Fields Required

Make sure these custom fields exist in MS Project:

**Text Fields**:
- Task Category
- Country
- Authority
- Study Phase
- ML Model Version
- Feedback Submitted (NEW - auto-created)

**Number Fields**:
- ML Predicted Duration
- ML Confidence

---

## What Happens Next

1. **Week 1**: PMs submit feedback on 10-20 completed tasks
2. **Month 1**: Database has 100+ task outcomes
3. **Month 3**: Enough data to identify patterns:
   - "Vietnam regulatory always takes 30 days longer than predicted"
   - "Kenya EC approvals are accurate within 5 days"
   - "Site contracts always double our estimates"

4. **Month 6**: Use collected data to:
   - **Option B**: Manually update task_ontology.yaml with better estimates
   - **Option C**: Train ML models (Phase 5)

---

## Success Criteria

✅ Desktop add-in detects completed tasks
✅ Submits feedback to backend API
✅ Backend stores predicted vs actual durations
✅ Accuracy report shows meaningful insights
✅ Doesn't resubmit already-recorded tasks
✅ Works with tasks that have/don't have predictions

---

## Next Steps

1. Implement desktop add-in code (Windows VM)
2. Test end-to-end feedback loop
3. Start collecting real project data
4. After 50+ tasks: Analyze accuracy patterns
5. Decide: Update ontology manually (Option B) or build ML pipeline (Option C)
