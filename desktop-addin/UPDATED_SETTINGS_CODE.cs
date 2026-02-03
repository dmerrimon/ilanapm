using System;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    public partial class SettingsForm : Form
    {
        // Control field declarations
        private Label lblHistoryTitle;
        private Label lblTotalHistory;
        private Label lblLastSubmission;
        private Label lblPrivacyNote;
        private Button btnClose;

        public SettingsForm()
        {
            InitializeComponent();
            LoadHistoryData();
        }

        private void LoadHistoryData()
        {
            // Get feedback count from settings
            int totalHistory = 0;
            if (Properties.Settings.Default.SubmittedFeedbackTasks != null)
            {
                totalHistory = Properties.Settings.Default.SubmittedFeedbackTasks.Count;
            }
            lblTotalHistory.Text = "Total Feedback Submitted: " + totalHistory.ToString() + " tasks";

            // Get last submission date from settings
            string lastSubmission = Properties.Settings.Default.LastSubmissionDate;
            if (!string.IsNullOrEmpty(lastSubmission))
            {
                lblLastSubmission.Text = "Last Submission: " + lastSubmission;
            }
            else
            {
                lblLastSubmission.Text = "Last Submission: Never";
            }
        }

        private void btnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void InitializeComponent()
        {
            this.lblHistoryTitle = new System.Windows.Forms.Label();
            this.lblTotalHistory = new System.Windows.Forms.Label();
            this.lblLastSubmission = new System.Windows.Forms.Label();
            this.lblPrivacyNote = new System.Windows.Forms.Label();
            this.btnClose = new System.Windows.Forms.Button();

            this.SuspendLayout();

            //
            // lblHistoryTitle
            //
            this.lblHistoryTitle.AutoSize = true;
            this.lblHistoryTitle.Font = new System.Drawing.Font("Segoe UI", 10F, System.Drawing.FontStyle.Bold);
            this.lblHistoryTitle.Location = new System.Drawing.Point(20, 20);
            this.lblHistoryTitle.Name = "lblHistoryTitle";
            this.lblHistoryTitle.Size = new System.Drawing.Size(150, 19);
            this.lblHistoryTitle.TabIndex = 0;
            this.lblHistoryTitle.Text = "Feedback Collection";

            //
            // lblTotalHistory
            //
            this.lblTotalHistory.AutoSize = true;
            this.lblTotalHistory.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular);
            this.lblTotalHistory.Location = new System.Drawing.Point(20, 55);
            this.lblTotalHistory.Name = "lblTotalHistory";
            this.lblTotalHistory.Size = new System.Drawing.Size(180, 15);
            this.lblTotalHistory.TabIndex = 1;
            this.lblTotalHistory.Text = "Total Feedback Submitted: 0 tasks";

            //
            // lblLastSubmission
            //
            this.lblLastSubmission.AutoSize = true;
            this.lblLastSubmission.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Regular);
            this.lblLastSubmission.Location = new System.Drawing.Point(20, 80);
            this.lblLastSubmission.Name = "lblLastSubmission";
            this.lblLastSubmission.Size = new System.Drawing.Size(150, 15);
            this.lblLastSubmission.TabIndex = 2;
            this.lblLastSubmission.Text = "Last Submission: Never";

            //
            // lblPrivacyNote
            //
            this.lblPrivacyNote.Location = new System.Drawing.Point(20, 120);
            this.lblPrivacyNote.Name = "lblPrivacyNote";
            this.lblPrivacyNote.Size = new System.Drawing.Size(510, 80);
            this.lblPrivacyNote.TabIndex = 3;
            this.lblPrivacyNote.Text = "Privacy Note:\r\n\r\nFeedback is automatically collected when tasks are completed to help improve timeline predictions. Only task durations and categories are submitted.\r\n\r\nNo patient data or confidential study information is collected.";

            //
            // btnClose
            //
            this.btnClose.Location = new System.Drawing.Point(455, 220);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(75, 30);
            this.btnClose.TabIndex = 4;
            this.btnClose.Text = "Close";
            this.btnClose.UseVisualStyleBackColor = true;
            this.btnClose.Click += new System.EventHandler(this.btnClose_Click);

            //
            // SettingsForm
            //
            this.ClientSize = new System.Drawing.Size(550, 270);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.lblPrivacyNote);
            this.Controls.Add(this.lblLastSubmission);
            this.Controls.Add(this.lblTotalHistory);
            this.Controls.Add(this.lblHistoryTitle);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "SettingsForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Ilana PM - Feedback History";
            this.ResumeLayout(false);
            this.PerformLayout();
        }
    }
}
