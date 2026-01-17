# Bulk Feedback Submission - Implementation Guide

**Feature**: Submit feedback for all completed tasks with one click
**Estimated Time**: 1-2 hours
**Backend**: Already implemented ✅ (`POST /api/v1/feedback/task-completions`)

---

## Overview

This feature extends the single feedback submission to handle multiple tasks:
1. Detects ALL 100% complete tasks in project
2. Shows selection list with checkboxes
3. Submits all selected tasks in one bulk API call
4. Shows summary of submissions

**User Workflow**:
1. PM completes project (many tasks at 100%)
2. PM clicks "Submit All Feedback" button
3. Selection form shows all completed tasks
4. PM checks/unchecks tasks to submit
5. PM clicks "Submit Selected"
6. Backend receives bulk submission
7. Summary shows: "Submitted 15 tasks, 12 had predictions, 3 no predictions"

---

## Files to Create/Modify

### 1. Create `FeedbackSelectionForm.cs` [NEW]

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using IlanaPM.AddIn.Models;
using IlanaPM.AddIn.Services;

namespace IlanaPM.AddIn
{
    public partial class FeedbackSelectionForm : Form
    {
        private List<Microsoft.Office.Interop.MSProject.Task> completedTasks;
        private ProjectDataExtractor extractor;
        private Microsoft.Office.Interop.MSProject.Application projectApp;
        private ListView lstTasks;
        private Button btnSelectAll;
        private Button btnDeselectAll;
        private Button btnSubmit;
        private Button btnCancel;
        private Label lblSummary;

        public FeedbackSelectionForm(
            List<Microsoft.Office.Interop.MSProject.Task> completedTasks,
            ProjectDataExtractor extractor,
            Microsoft.Office.Interop.MSProject.Application projectApp)
        {
            InitializeComponent();
            this.completedTasks = completedTasks;
            this.extractor = extractor;
            this.projectApp = projectApp;
            PopulateTasks();
        }

        private void PopulateTasks()
        {
            lstTasks.Items.Clear();

            foreach (var task in completedTasks)
            {
                var feedback = extractor.ExtractTaskFeedback(task, projectApp);

                var item = new ListViewItem(task.Name);
                item.Checked = true; // Default to selected
                item.Tag = feedback; // Store feedback data

                // Add predicted duration
                string predicted = feedback.predicted_duration_days.HasValue
                    ? $"{feedback.predicted_duration_days} days"
                    : "No prediction";
                item.SubItems.Add(predicted);

                // Add actual duration
                item.SubItems.Add($"{feedback.actual_duration_days} days");

                // Add variance
                if (feedback.predicted_duration_days.HasValue && feedback.predicted_duration_days > 0)
                {
                    int variance = feedback.actual_duration_days - feedback.predicted_duration_days.Value;
                    double varPercent = (variance / (double)feedback.predicted_duration_days.Value) * 100;
                    string varianceText = $"{variance:+#;-#;0} days ({varPercent:+0.0;-0.0;0.0}%)";
                    item.SubItems.Add(varianceText);

                    // Color code based on accuracy
                    if (Math.Abs(varPercent) <= 20)
                    {
                        item.ForeColor = System.Drawing.Color.Green; // Accurate
                    }
                    else
                    {
                        item.ForeColor = System.Drawing.Color.Red; // Inaccurate
                    }
                }
                else
                {
                    item.SubItems.Add("N/A");
                }

                // Add category
                item.SubItems.Add(feedback.category ?? "N/A");

                lstTasks.Items.Add(item);
            }

            UpdateSummary();
        }

        private void UpdateSummary()
        {
            int totalTasks = lstTasks.Items.Count;
            int selectedTasks = lstTasks.CheckedItems.Count;
            int withPredictions = lstTasks.Items.Cast<ListViewItem>()
                .Count(item => ((TaskFeedback)item.Tag).predicted_duration_days.HasValue);

            lblSummary.Text = $"{totalTasks} completed tasks | {selectedTasks} selected | " +
                             $"{withPredictions} with ML predictions";
        }

        private void btnSelectAll_Click(object sender, EventArgs e)
        {
            foreach (ListViewItem item in lstTasks.Items)
            {
                item.Checked = true;
            }
            UpdateSummary();
        }

        private void btnDeselectAll_Click(object sender, EventArgs e)
        {
            foreach (ListViewItem item in lstTasks.Items)
            {
                item.Checked = false;
            }
            UpdateSummary();
        }

        private async void btnSubmit_Click(object sender, EventArgs e)
        {
            try
            {
                // Get selected feedback items
                var selectedFeedback = lstTasks.CheckedItems.Cast<ListViewItem>()
                    .Select(item => (TaskFeedback)item.Tag)
                    .ToList();

                if (selectedFeedback.Count == 0)
                {
                    MessageBox.Show(
                        "No tasks selected.\n\nPlease select at least one task to submit.",
                        "No Selection",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information
                    );
                    return;
                }

                btnSubmit.Enabled = false;
                btnSubmit.Text = "Submitting...";

                // Submit bulk feedback
                var apiClient = new ApiClient();
                var response = await apiClient.SubmitBulkFeedbackAsync(selectedFeedback);

                btnSubmit.Enabled = true;
                btnSubmit.Text = "Submit Selected";

                // Show result
                string message = response.success
                    ? $"✓ Bulk feedback submitted successfully!\n\n{response.message}\n\n" +
                      $"Tasks submitted: {response.recorded_count}"
                    : $"✗ Failed to submit bulk feedback.\n\n{response.message}";

                MessageBox.Show(
                    message,
                    "Bulk Feedback Submitted",
                    MessageBoxButtons.OK,
                    response.success ? MessageBoxIcon.Information : MessageBoxIcon.Warning
                );

                if (response.success)
                {
                    this.DialogResult = DialogResult.OK;
                    this.Close();
                }
            }
            catch (Exception ex)
            {
                btnSubmit.Enabled = true;
                btnSubmit.Text = "Submit Selected";

                MessageBox.Show(
                    $"Error submitting bulk feedback:\n\n{ex.Message}",
                    "Bulk Feedback Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }

        private void lstTasks_ItemChecked(object sender, ItemCheckedEventArgs e)
        {
            UpdateSummary();
        }

        private void InitializeComponent()
        {
            this.lstTasks = new System.Windows.Forms.ListView();
            this.btnSelectAll = new System.Windows.Forms.Button();
            this.btnDeselectAll = new System.Windows.Forms.Button();
            this.btnSubmit = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();
            this.lblSummary = new System.Windows.Forms.Label();

            // Form
            this.Text = "Submit Bulk Feedback";
            this.Size = new System.Drawing.Size(800, 500);
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.Sizable;
            this.MinimumSize = new System.Drawing.Size(800, 500);

            // lblSummary
            this.lblSummary.Location = new System.Drawing.Point(12, 12);
            this.lblSummary.Size = new System.Drawing.Size(760, 20);
            this.lblSummary.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold);

            // lstTasks
            this.lstTasks.Location = new System.Drawing.Point(12, 40);
            this.lstTasks.Size = new System.Drawing.Size(760, 360);
            this.lstTasks.View = View.Details;
            this.lstTasks.FullRowSelect = true;
            this.lstTasks.CheckBoxes = true;
            this.lstTasks.GridLines = true;
            this.lstTasks.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            this.lstTasks.ItemChecked += lstTasks_ItemChecked;

            // Add columns
            this.lstTasks.Columns.Add("Task Name", 250);
            this.lstTasks.Columns.Add("Predicted", 100);
            this.lstTasks.Columns.Add("Actual", 100);
            this.lstTasks.Columns.Add("Variance", 120);
            this.lstTasks.Columns.Add("Category", 120);

            // btnSelectAll
            this.btnSelectAll.Location = new System.Drawing.Point(12, 410);
            this.btnSelectAll.Size = new System.Drawing.Size(100, 30);
            this.btnSelectAll.Text = "Select All";
            this.btnSelectAll.Anchor = AnchorStyles.Bottom | AnchorStyles.Left;
            this.btnSelectAll.Click += btnSelectAll_Click;

            // btnDeselectAll
            this.btnDeselectAll.Location = new System.Drawing.Point(120, 410);
            this.btnDeselectAll.Size = new System.Drawing.Size(100, 30);
            this.btnDeselectAll.Text = "Deselect All";
            this.btnDeselectAll.Anchor = AnchorStyles.Bottom | AnchorStyles.Left;
            this.btnDeselectAll.Click += btnDeselectAll_Click;

            // btnSubmit
            this.btnSubmit.Location = new System.Drawing.Point(572, 410);
            this.btnSubmit.Size = new System.Drawing.Size(120, 30);
            this.btnSubmit.Text = "Submit Selected";
            this.btnSubmit.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            this.btnSubmit.Click += btnSubmit_Click;

            // btnCancel
            this.btnCancel.Location = new System.Drawing.Point(700, 410);
            this.btnCancel.Size = new System.Drawing.Size(70, 30);
            this.btnCancel.Text = "Cancel";
            this.btnCancel.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            this.btnCancel.DialogResult = DialogResult.Cancel;

            // Add controls
            this.Controls.Add(this.lblSummary);
            this.Controls.Add(this.lstTasks);
            this.Controls.Add(this.btnSelectAll);
            this.Controls.Add(this.btnDeselectAll);
            this.Controls.Add(this.btnSubmit);
            this.Controls.Add(this.btnCancel);

            this.CancelButton = this.btnCancel;
        }
    }
}
```

---

### 2. Add to `Services/ApiClient.cs` [MODIFY]

Add this method to handle bulk submissions:

```csharp
/// <summary>
/// Submit bulk task completion feedback
/// </summary>
public async Task<TaskFeedbackResponse> SubmitBulkFeedbackAsync(List<TaskFeedback> feedbackList)
{
    string jsonContent = JsonConvert.SerializeObject(feedbackList);
    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

    HttpResponseMessage response = await httpClient.PostAsync(
        API_BASE_URL + "/api/v1/feedback/task-completions",
        content
    );

    response.EnsureSuccessStatusCode();
    string responseBody = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<TaskFeedbackResponse>(responseBody);
}
```

---

### 3. Update `IlanaPMRibbon.cs` [MODIFY]

Update the `btnSubmitFeedback_Click` handler to show selection form for multiple tasks:

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

        // If only one completed task, submit directly (single feedback form)
        if (completedTasks.Count == 1)
        {
            var task = completedTasks[0];
            var feedback = extractor.ExtractTaskFeedback(task, Globals.ThisAddIn.Application);

            var feedbackForm = new FeedbackForm(feedback);
            if (feedbackForm.ShowDialog() != DialogResult.OK)
                return;

            var apiClient = new Services.ApiClient();
            var response = await apiClient.SubmitTaskFeedbackAsync(feedback);

            string message = response.success
                ? $"✓ Feedback submitted successfully!\n\n{response.message}"
                : $"✗ Failed to submit feedback.\n\n{response.message}";

            MessageBox.Show(message, "Feedback Submitted",
                MessageBoxButtons.OK,
                response.success ? MessageBoxIcon.Information : MessageBoxIcon.Warning);
        }
        else
        {
            // Multiple completed tasks - show bulk selection form
            var selectionForm = new FeedbackSelectionForm(
                completedTasks,
                extractor,
                Globals.ThisAddIn.Application
            );
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

## Testing Instructions

### Test 1: Bulk Submission (All Selected)

1. Open project with 10 completed tasks (100%)
2. Add ML predictions to some tasks (not all)
3. Click "Submit Feedback" button
4. Verify bulk selection form shows:
   - Summary: "10 completed tasks | 10 selected | 6 with ML predictions"
   - All tasks checked by default
   - Green highlighting for accurate predictions (within ±20%)
   - Red highlighting for inaccurate predictions
5. Click "Submit Selected"
6. Verify success: "Submitted 10 tasks"
7. Check backend database has 10 new entries

### Test 2: Partial Selection

1. Open bulk selection form (10 tasks)
2. Click "Deselect All"
3. Check only 3 tasks
4. Verify summary: "10 completed tasks | 3 selected | X with ML predictions"
5. Click "Submit Selected"
6. Verify success: "Submitted 3 tasks"

### Test 3: Select/Deselect Buttons

1. Open bulk selection form
2. Click "Deselect All" - verify all unchecked
3. Click "Select All" - verify all checked
4. Manually uncheck 2 tasks
5. Verify summary updates in real-time

### Test 4: Color Coding

**Green (Accurate)**:
- Task: Predicted=30, Actual=28
- Variance: -2 days (-6.7%)
- Color: Green ✓

**Red (Inaccurate)**:
- Task: Predicted=30, Actual=60
- Variance: +30 days (+100%)
- Color: Red ✗

**Gray (No Prediction)**:
- Task: No ML prediction
- Predicted: "No prediction"
- Variance: "N/A"
- Color: Default

---

## Expected Behavior

**When multiple tasks completed**:
1. ✅ Click "Submit Feedback"
2. ✅ Bulk selection form opens
3. ✅ All completed tasks listed with checkboxes
4. ✅ All checked by default
5. ✅ Summary shows counts
6. ✅ Color-coded by accuracy
7. ✅ User can select/deselect
8. ✅ Click "Submit Selected"
9. ✅ API call to `/api/v1/feedback/task-completions` (bulk endpoint)
10. ✅ Success message with count
11. ✅ Form closes

**Selection Form Features**:
- ✅ Sortable columns (click header)
- ✅ Resizable window
- ✅ Select All / Deselect All buttons
- ✅ Real-time summary updates
- ✅ Color coding (green=accurate, red=inaccurate)
- ✅ Shows predicted, actual, variance, category

---

## Error Handling

**No tasks selected**:
```
No tasks selected.

Please select at least one task to submit.
```

**Backend error during bulk submit**:
```
Error submitting bulk feedback:

Validation error: task_completions must be an array
```

**Partial success** (backend handles gracefully):
```
✓ Bulk feedback submitted successfully!

Recorded 8 task completions. Total feedback entries: 157

(2 tasks had validation errors and were skipped)
```

---

## Performance Considerations

**Large Projects**:
- ListView handles 100+ tasks efficiently
- Bulk API call is faster than individual calls
- Backend processes in transaction (all or nothing)

**Memory**:
- Each task stores TaskFeedback object in Tag
- ~500 bytes per task
- 100 tasks = ~50KB memory (negligible)

---

## Next Steps

After implementing this feature:
1. ✅ Test with project having 20+ completed tasks
2. ✅ Verify bulk endpoint receives all tasks
3. ✅ Check database has all entries
4. ✅ Test Select All/Deselect All functionality
5. ✅ Implement Auto-Fix Desktop (next guide)

---

**Implementation Time**: 1-2 hours
**Complexity**: Medium
**Dependencies**:
- Desktop Feedback Integration (prerequisite)
- Backend bulk endpoint (already implemented ✅)
