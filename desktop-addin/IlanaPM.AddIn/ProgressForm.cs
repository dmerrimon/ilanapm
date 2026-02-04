using System;
using System.Drawing;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    /// <summary>
    /// Progress dialog for long-running operations like API calls and task generation
    /// Prevents "Server Busy" dialog by keeping UI responsive
    /// </summary>
    public class ProgressForm : Form
    {
        private Label lblStatus;
        private ProgressBar progressBar;
        private Label lblDetail;

        public ProgressForm(string title)
        {
            InitializeComponents(title);
        }

        private void InitializeComponents(string title)
        {
            // Form settings
            this.Text = title;
            this.Width = 500;
            this.Height = 180;
            this.StartPosition = FormStartPosition.CenterParent;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.ControlBox = false;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.ShowInTaskbar = false;

            // Status label
            lblStatus = new Label
            {
                Text = "Initializing...",
                Left = 20,
                Top = 20,
                Width = 460,
                Height = 30,
                Font = new Font(FontFamily.GenericSansSerif, 10, FontStyle.Bold)
            };

            // Progress bar
            progressBar = new ProgressBar
            {
                Left = 20,
                Top = 60,
                Width = 460,
                Height = 25,
                Style = ProgressBarStyle.Marquee,
                MarqueeAnimationSpeed = 30
            };

            // Detail label
            lblDetail = new Label
            {
                Text = "",
                Left = 20,
                Top = 95,
                Width = 460,
                Height = 40,
                Font = new Font(FontFamily.GenericSansSerif, 9),
                ForeColor = Color.Gray
            };

            // Add controls
            this.Controls.Add(lblStatus);
            this.Controls.Add(progressBar);
            this.Controls.Add(lblDetail);
        }

        /// <summary>
        /// Update progress status text
        /// </summary>
        public void UpdateStatus(string status, string detail = "")
        {
            if (this.InvokeRequired)
            {
                this.Invoke(new Action(() => UpdateStatus(status, detail)));
                return;
            }

            lblStatus.Text = status;
            lblDetail.Text = detail;
            this.Refresh();
            Application.DoEvents();
        }

        /// <summary>
        /// Set progress bar to determinate mode with percentage
        /// </summary>
        public void SetProgress(int percentage)
        {
            if (this.InvokeRequired)
            {
                this.Invoke(new Action(() => SetProgress(percentage)));
                return;
            }

            if (progressBar.Style != ProgressBarStyle.Continuous)
            {
                progressBar.Style = ProgressBarStyle.Continuous;
            }

            progressBar.Value = Math.Min(100, Math.Max(0, percentage));
            this.Refresh();
            Application.DoEvents();
        }
    }
}
