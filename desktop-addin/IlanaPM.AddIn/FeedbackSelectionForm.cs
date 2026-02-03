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

        public FeedbackSelectionForm(List<Microsoft.Office.Interop.MSProject.Task> completedTasks, ProjectDataExtractor extractor, Microsoft.Office.Interop.MSProject.Application projectApp)
        {
            this.completedTasks = completedTasks;
            this.extractor = extractor;
            this.projectApp = projectApp;
            InitializeComponent();
            PopulateTasks();
        }

        private void PopulateTasks()
        {
            lstTasks.Items.Clear();

            foreach (var task in completedTasks)
            {
                var feedback = extractor.ExtractTaskFeedback(task, projectApp);

                var item = new ListViewItem(task.Name);
                item.Checked = true;
                item.Tag = feedback;

                string predicted = feedback.predicted_duration_days.HasValue ? feedback.predicted_duration_days.ToString() + " days" : "No prediction";
                item.SubItems.Add(predicted);

                item.SubItems.Add(feedback.actual_duration_days.ToString() + " days");

                if (feedback.predicted_duration_days.HasValue && feedback.predicted_duration_days > 0)
                {
                    int variance = feedback.actual_duration_days - feedback.predicted_duration_days.Value;
                    double varPercent = (variance / (double)feedback.predicted_duration_days.Value) * 100;
                    string varianceText = (variance >= 0 ? "+" : "") + variance.ToString() + " days (" + varPercent.ToString("F1") + "%)";
                    item.SubItems.Add(varianceText);

                    if (Math.Abs(varPercent) <= 20)
                    {
                        item.ForeColor = System.Drawing.Color.Green;
                    }
                    else
                    {
                        item.ForeColor = System.Drawing.Color.Red;
                    }
                }
                else
                {
                    item.SubItems.Add("N/A");
                }

                item.SubItems.Add(feedback.category ?? "N/A");

                lstTasks.Items.Add(item);
            }

            UpdateSummary();
        }

        private void UpdateSummary()
        {
            int totalTasks = lstTasks.Items.Count;
            int selectedTasks = lstTasks.CheckedItems.Count;
            int withPredictions = 0;

            foreach (ListViewItem item in lstTasks.Items)
            {
                var feedback = (TaskFeedback)item.Tag;
                if (feedback.predicted_duration_days.HasValue)
                {
                    withPredictions++;
                }
            }

            lblSummary.Text = totalTasks.ToString() + " completed tasks | " + selectedTasks.ToString() + " selected | " + withPredictions.ToString() + " with ML predictions";
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
                var selectedFeedback = new List<TaskFeedback>();

                foreach (ListViewItem item in lstTasks.CheckedItems)
                {
                    selectedFeedback.Add((TaskFeedback)item.Tag);
                }

                if (selectedFeedback.Count == 0)
                {
                    MessageBox.Show("No tasks selected.\n\nPlease select at least one task to submit.", "No Selection", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    return;
                }

                btnSubmit.Enabled = false;
                btnSubmit.Text = "Submitting...";

                var apiClient = new ApiClient();
                var response = await apiClient.SubmitBulkFeedbackAsync(selectedFeedback);

                btnSubmit.Enabled = true;
                btnSubmit.Text = "Submit Selected";

                string message = response.success ? "Bulk feedback submitted successfully!\n\n" + response.message + "\n\nTasks submitted: " + response.recorded_count.ToString() : "Failed to submit bulk feedback.\n\n" + response.message;

                MessageBox.Show(message, "Bulk Feedback Submitted", MessageBoxButtons.OK, response.success ? MessageBoxIcon.Information : MessageBoxIcon.Warning);

                if (response.success)
                {
                    this.DialogResult = DialogResult.OK;
                    this.Close();
                }
            }
            catch (System.Exception ex)
            {
                btnSubmit.Enabled = true;
                btnSubmit.Text = "Submit Selected";

                MessageBox.Show("Error submitting bulk feedback:\n\n" + ex.Message, "Bulk Feedback Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
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

            this.Text = "Submit Bulk Feedback";
            this.Size = new System.Drawing.Size(800, 500);
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.Sizable;
            this.MinimumSize = new System.Drawing.Size(800, 500);

            this.lblSummary.Location = new System.Drawing.Point(12, 12);
            this.lblSummary.Size = new System.Drawing.Size(760, 20);
            this.lblSummary.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold);

            this.lstTasks.Location = new System.Drawing.Point(12, 40);
            this.lstTasks.Size = new System.Drawing.Size(760, 360);
            this.lstTasks.View = View.Details;
            this.lstTasks.FullRowSelect = true;
            this.lstTasks.CheckBoxes = true;
            this.lstTasks.GridLines = true;
            this.lstTasks.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            this.lstTasks.ItemChecked += lstTasks_ItemChecked;

            this.lstTasks.Columns.Add("Task Name", 250);
            this.lstTasks.Columns.Add("Predicted", 100);
            this.lstTasks.Columns.Add("Actual", 100);
            this.lstTasks.Columns.Add("Variance", 120);
            this.lstTasks.Columns.Add("Category", 120);

            this.btnSelectAll.Location = new System.Drawing.Point(12, 410);
            this.btnSelectAll.Size = new System.Drawing.Size(100, 30);
            this.btnSelectAll.Text = "Select All";
            this.btnSelectAll.Anchor = AnchorStyles.Bottom | AnchorStyles.Left;
            this.btnSelectAll.Click += btnSelectAll_Click;

            this.btnDeselectAll.Location = new System.Drawing.Point(120, 410);
            this.btnDeselectAll.Size = new System.Drawing.Size(100, 30);
            this.btnDeselectAll.Text = "Deselect All";
            this.btnDeselectAll.Anchor = AnchorStyles.Bottom | AnchorStyles.Left;
            this.btnDeselectAll.Click += btnDeselectAll_Click;

            this.btnSubmit.Location = new System.Drawing.Point(572, 410);
            this.btnSubmit.Size = new System.Drawing.Size(120, 30);
            this.btnSubmit.Text = "Submit Selected";
            this.btnSubmit.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            this.btnSubmit.Click += btnSubmit_Click;

            this.btnCancel.Location = new System.Drawing.Point(700, 410);
            this.btnCancel.Size = new System.Drawing.Size(70, 30);
            this.btnCancel.Text = "Cancel";
            this.btnCancel.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            this.btnCancel.DialogResult = DialogResult.Cancel;

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
