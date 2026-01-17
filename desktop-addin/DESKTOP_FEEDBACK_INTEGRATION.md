# Desktop Feedback Integration - Implementation Guide

**Feature**: One-click feedback submission when tasks complete
**Estimated Time**: 2 hours
**Backend**: Already implemented ✅ (`POST /api/v1/feedback/task-completion`)

---

## Overview

This feature adds a "Submit Feedback" button to the ribbon that automatically:
1. Detects 100% complete tasks
2. Extracts predicted duration from custom fields
3. Auto-populates all metadata
4. Submits to backend with one click

**User Workflow**:
1. PM marks task as 100% complete in MS Project
2. PM clicks "Submit Feedback" button
3. Form appears with auto-populated data
4. PM reviews and clicks "Submit"
5. Backend records actual vs predicted duration

---

## Files to Create/Modify

### 1. Create `Models/TaskFeedback.cs` [NEW]

```csharp
using System;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Task feedback for ML learning
    /// </summary>
    public class TaskFeedback
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public string category { get; set; }

        // Prediction data (from custom fields)
        public int? predicted_duration_days { get; set; }
        public double? predicted_confidence { get; set; }
        public string model_version { get; set; }

        // Actual outcome (from MS Project)
        public int actual_duration_days { get; set; }
        public string actual_start_date { get; set; }
        public string actual_end_date { get; set; }

        // Context for learning
        public string country_code { get; set; }
        public string authority { get; set; }
        public string study_phase { get; set; }
        public string therapeutic_area { get; set; }

        // Metadata
        public string project_id { get; set; }
        public string recorded_by { get; set; }
    }

    /// <summary>
    /// Response after submitting feedback
    /// </summary>
    public class TaskFeedbackResponse
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
        public double? variance_percent { get; set; }
        public bool was_accurate { get; set; }
        public string threshold { get; set; }
    }
}
```

---

### 2. Add to `Services/ApiClient.cs` [MODIFY]

Add this method to the `ApiClient` class:

```csharp
/// <summary>
/// Submit task completion feedback
/// </summary>
public async Task<TaskFeedbackResponse> SubmitTaskFeedbackAsync(TaskFeedback feedback)
{
    string jsonContent = JsonConvert.SerializeObject(feedback);
    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

    HttpResponseMessage response = await httpClient.PostAsync(
        API_BASE_URL + "/api/v1/feedback/task-completion",
        content
    );

    response.EnsureSuccessStatusCode();
    string responseBody = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<TaskFeedbackResponse>(responseBody);
}
```

---

### 3. Add to `Services/ProjectDataExtractor.cs` [MODIFY]

Add this method to extract completed tasks:

```csharp
/// <summary>
/// Get all 100% complete tasks ready for feedback
/// </summary>
public List<Microsoft.Office.Interop.MSProject.Task> GetCompletedTasks(
    Microsoft.Office.Interop.MSProject.Application projectApp)
{
    if (projectApp.ActiveProject == null)
        throw new Exception("No active project found.");

    var completedTasks = new List<Microsoft.Office.Interop.MSProject.Task>();

    foreach (Microsoft.Office.Interop.MSProject.Task task in projectApp.ActiveProject.Tasks)
    {
        if (task != null && task.PercentComplete == 100)
        {
            completedTasks.Add(task);
        }
    }

    return completedTasks;
}

/// <summary>
/// Extract feedback data from a completed task
/// </summary>
public TaskFeedback ExtractTaskFeedback(
    Microsoft.Office.Interop.MSProject.Task task,
    Microsoft.Office.Interop.MSProject.Application projectApp)
{
    var feedback = new TaskFeedback
    {
        task_id = task.ID.ToString(),
        task_name = task.Name,

        // Get actual duration
        actual_duration_days = ConvertMinutesToDays(task.Duration),
        actual_start_date = task.Start.ToString("yyyy-MM-dd"),
        actual_end_date = task.Finish.ToString("yyyy-MM-dd"),

        // Extract from custom fields
        category = GetTaskCustomFieldText(task, "Task Category"),
        predicted_duration_days = GetTaskCustomFieldNumber(task, "ML Predicted Duration"),
        predicted_confidence = GetTaskCustomFieldNumber(task, "ML Confidence %"),
        model_version = "ontology-v3.0",

        // Context
        country_code = GetTaskCustomFieldText(task, "Country"),
        authority = GetTaskCustomFieldText(task, "Authority"),
        study_phase = GetTaskCustomFieldText(task, "Study Phase"),
        therapeutic_area = GetTaskCustomFieldText(task, "Therapeutic Area"),

        // Metadata
        project_id = projectApp.ActiveProject.Name,
        recorded_by = Environment.UserName
    };

    return feedback;
}

private int ConvertMinutesToDays(int minutes)
{
    return minutes / 480; // 480 minutes = 8 hour workday
}

private string GetTaskCustomFieldText(Microsoft.Office.Interop.MSProject.Task task, string fieldName)
{
    try
    {
        switch (fieldName)
        {
            case "Task Category":
                return task.Text1;
            case "Country":
                return task.Text2;
            case "Authority":
                return task.Text3;
            case "Study Phase":
                return task.Text4;
            case "Therapeutic Area":
                return task.Text5;
            default:
                return null;
        }
    }
    catch
    {
        return null;
    }
}

private int? GetTaskCustomFieldNumber(Microsoft.Office.Interop.MSProject.Task task, string fieldName)
{
    try
    {
        switch (fieldName)
        {
            case "ML Predicted Duration":
                return task.Number1 > 0 ? (int?)task.Number1 : null;
            case "ML Confidence %":
                return task.Number2 > 0 ? (int?)task.Number2 : null;
            default:
                return null;
        }
    }
    catch
    {
        return null;
    }
}
```

---

### 4. Create `FeedbackForm.cs` [NEW]

```csharp
using System;
using System.Windows.Forms;
using IlanaPM.AddIn.Models;

namespace IlanaPM.AddIn
{
    public partial class FeedbackForm : Form
    {
        private TaskFeedback feedback;

        public FeedbackForm(TaskFeedback feedback)
        {
            InitializeComponent();
            this.feedback = feedback;
            PopulateForm();
        }

        private void PopulateForm()
        {
            // Display task info
            lblTaskName.Text = $"Task: {feedback.task_name}";
            lblPredicted.Text = feedback.predicted_duration_days.HasValue
                ? $"Predicted: {feedback.predicted_duration_days} days"
                : "Predicted: N/A (no ML prediction)";
            lblActual.Text = $"Actual: {feedback.actual_duration_days} days";

            // Calculate variance if prediction exists
            if (feedback.predicted_duration_days.HasValue && feedback.predicted_duration_days > 0)
            {
                int variance = feedback.actual_duration_days - feedback.predicted_duration_days.Value;
                double varPercent = (variance / (double)feedback.predicted_duration_days.Value) * 100;

                lblVariance.Text = $"Variance: {variance} days ({varPercent:F1}%)";
                lblVariance.ForeColor = Math.Abs(varPercent) <= 20 ? System.Drawing.Color.Green : System.Drawing.Color.Red;
            }
            else
            {
                lblVariance.Text = "Variance: N/A";
            }

            // Show context
            txtContext.Text = $"Category: {feedback.category ?? "N/A"}\r\n" +
                             $"Country: {feedback.country_code ?? "N/A"}\r\n" +
                             $"Authority: {feedback.authority ?? "N/A"}\r\n" +
                             $"Phase: {feedback.study_phase ?? "N/A"}";
        }

        private void InitializeComponent()
        {
            this.lblTaskName = new System.Windows.Forms.Label();
            this.lblPredicted = new System.Windows.Forms.Label();
            this.lblActual = new System.Windows.Forms.Label();
            this.lblVariance = new System.Windows.Forms.Label();
            this.txtContext = new System.Windows.Forms.TextBox();
            this.btnSubmit = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();

            // Form
            this.Text = "Submit Task Feedback";
            this.Size = new System.Drawing.Size(450, 350);
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;

            // lblTaskName
            this.lblTaskName.Location = new System.Drawing.Point(12, 12);
            this.lblTaskName.Size = new System.Drawing.Size(410, 30);
            this.lblTaskName.Font = new System.Drawing.Font("Segoe UI", 10F, System.Drawing.FontStyle.Bold);

            // lblPredicted
            this.lblPredicted.Location = new System.Drawing.Point(12, 50);
            this.lblPredicted.Size = new System.Drawing.Size(200, 20);

            // lblActual
            this.lblActual.Location = new System.Drawing.Point(12, 75);
            this.lblActual.Size = new System.Drawing.Size(200, 20);

            // lblVariance
            this.lblVariance.Location = new System.Drawing.Point(12, 100);
            this.lblVariance.Size = new System.Drawing.Size(300, 20);
            this.lblVariance.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold);

            // txtContext
            this.txtContext.Location = new System.Drawing.Point(12, 130);
            this.txtContext.Size = new System.Drawing.Size(410, 120);
            this.txtContext.Multiline = true;
            this.txtContext.ReadOnly = true;
            this.txtContext.BorderStyle = BorderStyle.FixedSingle;

            // btnSubmit
            this.btnSubmit.Location = new System.Drawing.Point(250, 270);
            this.btnSubmit.Size = new System.Drawing.Size(80, 30);
            this.btnSubmit.Text = "Submit";
            this.btnSubmit.DialogResult = DialogResult.OK;

            // btnCancel
            this.btnCancel.Location = new System.Drawing.Point(340, 270);
            this.btnCancel.Size = new System.Drawing.Size(80, 30);
            this.btnCancel.Text = "Cancel";
            this.btnCancel.DialogResult = DialogResult.Cancel;

            // Add controls
            this.Controls.Add(this.lblTaskName);
            this.Controls.Add(this.lblPredicted);
            this.Controls.Add(this.lblActual);
            this.Controls.Add(this.lblVariance);
            this.Controls.Add(this.txtContext);
            this.Controls.Add(this.btnSubmit);
            this.Controls.Add(this.btnCancel);
        }

        private System.Windows.Forms.Label lblTaskName;
        private System.Windows.Forms.Label lblPredicted;
        private System.Windows.Forms.Label lblActual;
        private System.Windows.Forms.Label lblVariance;
        private System.Windows.Forms.TextBox txtContext;
        private System.Windows.Forms.Button btnSubmit;
        private System.Windows.Forms.Button btnCancel;
    }
}
```

---

### 5. Add to `IlanaPMRibbon.cs` [MODIFY]

Add this button click handler:

```csharp
private async void btnSubmitFeedback_Click(object sender, RibbonControlEventArgs e)
{
    try
    {
        var extractor = new Services.ProjectDataExtractor();
        var completedTasks = extractor.GetCompletedTasks(Globals.ThisAddIn.Application);

        if (completedTasks.Count == 0)
        {
            MessageBox.Show(
                "No completed tasks found (100% complete).\n\n" +
                "Mark tasks as 100% complete to submit feedback.",
                "No Completed Tasks",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
            return;
        }

        // If only one completed task, submit directly
        if (completedTasks.Count == 1)
        {
            var task = completedTasks[0];
            var feedback = extractor.ExtractTaskFeedback(task, Globals.ThisAddIn.Application);

            // Show feedback form
            var feedbackForm = new FeedbackForm(feedback);
            if (feedbackForm.ShowDialog() != DialogResult.OK)
                return;

            // Submit to backend
            var apiClient = new Services.ApiClient();
            var response = await apiClient.SubmitTaskFeedbackAsync(feedback);

            // Show result
            string message = response.success
                ? $"✓ Feedback submitted successfully!\n\n{response.message}"
                : $"✗ Failed to submit feedback.\n\n{response.message}";

            if (response.accuracy_summary != null)
            {
                var acc = response.accuracy_summary;
                message += $"\n\nAccuracy Summary:\n" +
                          $"  Predicted: {acc.predicted_days} days\n" +
                          $"  Actual: {acc.actual_days} days\n" +
                          $"  Variance: {acc.variance_days} days";

                if (acc.variance_percent.HasValue)
                {
                    message += $" ({acc.variance_percent:F1}%)\n";
                    message += acc.was_accurate
                        ? $"  ✓ Within {acc.threshold} threshold (accurate)"
                        : $"  ✗ Outside {acc.threshold} threshold";
                }
            }

            MessageBox.Show(message, "Feedback Submitted",
                MessageBoxButtons.OK,
                response.success ? MessageBoxIcon.Information : MessageBoxIcon.Warning);
        }
        else
        {
            // Multiple completed tasks - show selection list
            var selectionForm = new FeedbackSelectionForm(completedTasks, extractor, Globals.ThisAddIn.Application);
            selectionForm.ShowDialog();
        }
    }
    catch (Exception ex)
    {
        MessageBox.Show(
            $"Error submitting feedback:\n\n{ex.Message}",
            "Feedback Error",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error
        );
    }
}
```

---

### 6. Add to `IlanaPMRibbon.xml` [MODIFY]

Add this button to the ribbon XML:

```xml
<button id="btnSubmitFeedback"
        label="Submit Feedback"
        imageMso="ReviewAcceptChange"
        size="large"
        onAction="btnSubmitFeedback_Click" />
```

Add it in the Feedback group (create if doesn't exist):

```xml
<group id="grpFeedback" label="ML Learning">
  <button id="btnSubmitFeedback"
          label="Submit Feedback"
          imageMso="ReviewAcceptChange"
          size="large"
          onAction="btnSubmitFeedback_Click" />
</group>
```

---

## Testing Instructions

### Test 1: Single Completed Task

1. Open MS Project with a project
2. Mark one task as 100% complete
3. Add ML prediction to custom field (Number1 = 30)
4. Click "Submit Feedback" button
5. Verify form shows:
   - Task name
   - Predicted: 30 days
   - Actual: (calculated from task duration)
   - Variance and percentage
6. Click "Submit"
7. Verify success message with accuracy summary

### Test 2: No Predictions

1. Mark task as 100% complete (no ML prediction in custom fields)
2. Click "Submit Feedback"
3. Verify form shows "Predicted: N/A"
4. Submit anyway
5. Verify backend accepts (predicted_duration_days = null)

### Test 3: Accurate Prediction

1. Task with predicted=30, actual=28
2. Variance should be -2 days (-6.7%)
3. Should show green "✓ Within ±20% threshold"

### Test 4: Inaccurate Prediction

1. Task with predicted=30, actual=60
2. Variance should be +30 days (+100%)
3. Should show red "✗ Outside ±20% threshold"

---

## Expected Behavior

**When user clicks "Submit Feedback"**:
1. ✅ Scans for 100% complete tasks
2. ✅ If none found: Shows "No completed tasks" message
3. ✅ If 1 found: Shows feedback form with auto-populated data
4. ✅ If multiple found: Shows selection list (see Bulk Feedback guide)
5. ✅ User reviews data
6. ✅ User clicks "Submit"
7. ✅ API call to `/api/v1/feedback/task-completion`
8. ✅ Success message with accuracy summary
9. ✅ Backend stores for ML learning

**Data Auto-Populated**:
- ✅ Task ID, name, duration (from MS Project)
- ✅ Predicted duration, confidence (from custom fields)
- ✅ Category, country, authority (from custom fields)
- ✅ Start/end dates (from MS Project)
- ✅ Project ID, user name (from system)

---

## Error Handling

**Backend offline**:
```
Error submitting feedback:

No connection could be made because the target machine actively refused it.

Check that backend is running on http://localhost:8000
```

**Invalid data**:
```
Error submitting feedback:

Validation error: task_name is required
```

**Network timeout**:
```
Error submitting feedback:

The operation has timed out.
```

---

## Next Steps

After implementing this feature:
1. ✅ Test with real project data
2. ✅ Verify backend receives feedback
3. ✅ Check database has new entries
4. ✅ Implement Bulk Feedback (next guide)

---

**Implementation Time**: 2 hours
**Complexity**: Medium
**Dependencies**: Backend feedback API (already implemented ✅)
