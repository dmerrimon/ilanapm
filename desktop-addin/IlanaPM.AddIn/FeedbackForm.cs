using System;
using System.Windows.Forms;
using IlanaPM.AddIn.Models;

namespace IlanaPM.AddIn
{
    public partial class FeedbackForm : Form
    {
        private TaskFeedback feedback;
        private Label lblTaskName;
        private Label lblPredicted;
        private Label lblActual;
        private Label lblCategory;
        private TextBox txtNotes;
        private Button btnSubmit;
        private Button btnCancel;

        public FeedbackForm(TaskFeedback feedback)
        {
            this.feedback = feedback;
            InitializeComponent();
            DisplayFeedback();
        }

        private void DisplayFeedback()
        {
            lblTaskName.Text = "Task: " + feedback.task_name;
            lblCategory.Text = "Category: " + (feedback.category ?? "N/A");
            lblActual.Text = "Actual Duration: " + feedback.actual_duration_days + " days";

            if (feedback.predicted_duration_days.HasValue)
            {
                int variance = feedback.actual_duration_days - feedback.predicted_duration_days.Value;
                double varPercent = (variance / (double)feedback.predicted_duration_days.Value) * 100;
                string varianceText = variance >= 0 ? "+" + variance : variance.ToString();

                lblPredicted.Text = "Predicted Duration: " + feedback.predicted_duration_days + " days (variance: " + varianceText + " days, " + varPercent.ToString("F1") + "%)";

                if (Math.Abs(varPercent) <= 20)
                {
                    lblPredicted.ForeColor = System.Drawing.Color.Green;
                }
                else
                {
                    lblPredicted.ForeColor = System.Drawing.Color.Red;
                }
            }
            else
            {
                lblPredicted.Text = "Predicted Duration: No ML prediction available";
                lblPredicted.ForeColor = System.Drawing.Color.Gray;
            }
        }

        private void btnSubmit_Click(object sender, EventArgs e)
        {
            this.DialogResult = DialogResult.OK;
            this.Close();
        }

        private void InitializeComponent()
        {
            this.lblTaskName = new System.Windows.Forms.Label();
            this.lblPredicted = new System.Windows.Forms.Label();
            this.lblActual = new System.Windows.Forms.Label();
            this.lblCategory = new System.Windows.Forms.Label();
            this.txtNotes = new System.Windows.Forms.TextBox();
            this.btnSubmit = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();

            this.Text = "Submit Task Feedback";
            this.Size = new System.Drawing.Size(500, 350);
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;

            this.lblTaskName.Location = new System.Drawing.Point(20, 20);
            this.lblTaskName.Size = new System.Drawing.Size(450, 30);
            this.lblTaskName.Font = new System.Drawing.Font("Segoe UI", 10F, System.Drawing.FontStyle.Bold);

            this.lblCategory.Location = new System.Drawing.Point(20, 60);
            this.lblCategory.Size = new System.Drawing.Size(450, 20);

            this.lblPredicted.Location = new System.Drawing.Point(20, 90);
            this.lblPredicted.Size = new System.Drawing.Size(450, 20);

            this.lblActual.Location = new System.Drawing.Point(20, 120);
            this.lblActual.Size = new System.Drawing.Size(450, 20);

            var lblNotesHeader = new Label();
            lblNotesHeader.Location = new System.Drawing.Point(20, 150);
            lblNotesHeader.Size = new System.Drawing.Size(450, 20);
            lblNotesHeader.Text = "Notes (optional):";

            this.txtNotes.Location = new System.Drawing.Point(20, 175);
            this.txtNotes.Size = new System.Drawing.Size(450, 80);
            this.txtNotes.Multiline = true;

            this.btnSubmit.Location = new System.Drawing.Point(280, 270);
            this.btnSubmit.Size = new System.Drawing.Size(90, 30);
            this.btnSubmit.Text = "Submit";
            this.btnSubmit.Click += btnSubmit_Click;

            this.btnCancel.Location = new System.Drawing.Point(380, 270);
            this.btnCancel.Size = new System.Drawing.Size(90, 30);
            this.btnCancel.Text = "Cancel";
            this.btnCancel.DialogResult = DialogResult.Cancel;

            this.Controls.Add(this.lblTaskName);
            this.Controls.Add(this.lblCategory);
            this.Controls.Add(this.lblPredicted);
            this.Controls.Add(this.lblActual);
            this.Controls.Add(lblNotesHeader);
            this.Controls.Add(this.txtNotes);
            this.Controls.Add(this.btnSubmit);
            this.Controls.Add(this.btnCancel);

            this.CancelButton = this.btnCancel;
        }
    }
}
