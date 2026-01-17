using System;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    public partial class MLAdvisoryForm : Form
    {
        public MLAdvisoryForm()
        {
            InitializeComponent();
        }

        public void DisplayAdvisory(Models.TimelineAdvisory advisory)
        {
            int predictionCount = advisory.duration_predictions?.predictions?.Count ?? 0;
            int highRiskCount = advisory.risk_analysis?.high_risk_tasks?.Count ?? 0;

            lblSummary.Text = string.Format("Analyzed {0} tasks | High Risk Tasks: {1}",
                predictionCount,
                highRiskCount);

            var sb = new System.Text.StringBuilder();

            // Summary Statistics
            if (advisory.summary_statistics != null)
            {
                sb.AppendLine("═══ SUMMARY ═══" + Environment.NewLine);
                sb.AppendLine(string.Format("Total Tasks: {0}", advisory.summary_statistics.total_tasks));
                sb.AppendLine(string.Format("Avg Predicted Duration: {0} days", advisory.summary_statistics.avg_predicted_duration));
                sb.AppendLine(string.Format("Avg Risk Score: {0}/100", advisory.summary_statistics.avg_risk_score));
                sb.AppendLine(string.Format("High Risk Tasks: {0}", advisory.summary_statistics.high_risk_count));
                sb.AppendLine(string.Format("Critical Risk Tasks: {0}", advisory.summary_statistics.critical_risk_count));
                sb.AppendLine(string.Format("Aggressive Durations: {0}", advisory.summary_statistics.aggressive_duration_count));
                sb.AppendLine();
            }

            // Recommendations
            if (advisory.recommendations != null && advisory.recommendations.Count > 0)
            {
                sb.AppendLine("═══ RECOMMENDATIONS ═══" + Environment.NewLine);
                foreach (var rec in advisory.recommendations)
                {
                    sb.AppendLine("• " + rec);
                }
                sb.AppendLine();
            }

            // Duration Predictions
            if (advisory.duration_predictions != null && advisory.duration_predictions.predictions != null)
            {
                sb.AppendLine("═══ DURATION PREDICTIONS ═══" + Environment.NewLine);
                foreach (var pred in advisory.duration_predictions.predictions)
                {
                    sb.AppendLine(string.Format("Task: {0}", pred.task_name));
                    sb.AppendLine(string.Format("  Current: {0} days", pred.current_duration));
                    sb.AppendLine(string.Format("  Predicted: {0} days", pred.prediction.predicted_duration_days));
                    sb.AppendLine(string.Format("  Range: {0}-{1} days",
                        pred.prediction.confidence_interval.lower,
                        pred.prediction.confidence_interval.upper));
                    sb.AppendLine(string.Format("  Confidence: {0:F0}%", pred.prediction.confidence_score * 100));
                    sb.AppendLine(string.Format("  {0}", pred.prediction.explanation));
                    sb.AppendLine();
                }
            }

            // High Risk Tasks
            if (advisory.risk_analysis != null && advisory.risk_analysis.high_risk_tasks != null && advisory.risk_analysis.high_risk_tasks.Count > 0)
            {
                sb.AppendLine("═══ HIGH RISK TASKS ═══" + Environment.NewLine);
                foreach (var task in advisory.risk_analysis.high_risk_tasks)
                {
                    sb.AppendLine(string.Format("⚠️  {0} (Risk Score: {1}/100)", task.task_name, task.risk_score));
                    sb.AppendLine("  Risk Factors:");
                    foreach (var factor in task.risk_factors)
                    {
                        sb.AppendLine(string.Format("    • {0}", factor));
                    }
                    sb.AppendLine();
                }
            }

            txtAdvisory.Text = sb.ToString();
        }

        private void InitializeComponent()
        {
            this.lblSummary = new System.Windows.Forms.Label();
            this.txtAdvisory = new System.Windows.Forms.TextBox();
            this.btnClose = new System.Windows.Forms.Button();
            this.SuspendLayout();

            // lblSummary
            this.lblSummary.AutoSize = true;
            this.lblSummary.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold);
            this.lblSummary.Location = new System.Drawing.Point(12, 12);
            this.lblSummary.Name = "lblSummary";
            this.lblSummary.Size = new System.Drawing.Size(200, 15);
            this.lblSummary.TabIndex = 0;
            this.lblSummary.Text = "ML Advisory Summary";

            // txtAdvisory
            this.txtAdvisory.Font = new System.Drawing.Font("Consolas", 9F);
            this.txtAdvisory.Location = new System.Drawing.Point(12, 40);
            this.txtAdvisory.Multiline = true;
            this.txtAdvisory.Name = "txtAdvisory";
            this.txtAdvisory.ReadOnly = true;
            this.txtAdvisory.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtAdvisory.Size = new System.Drawing.Size(760, 450);
            this.txtAdvisory.TabIndex = 1;

            // btnClose
            this.btnClose.Location = new System.Drawing.Point(697, 496);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(75, 23);
            this.btnClose.TabIndex = 2;
            this.btnClose.Text = "Close";
            this.btnClose.UseVisualStyleBackColor = true;
            this.btnClose.Click += new System.EventHandler(this.btnClose_Click);

            // MLAdvisoryForm
            this.ClientSize = new System.Drawing.Size(784, 531);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.txtAdvisory);
            this.Controls.Add(this.lblSummary);
            this.Name = "MLAdvisoryForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Ilana PM - ML Advisory";
            this.ResumeLayout(false);
            this.PerformLayout();
        }

        private Label lblSummary;
        private TextBox txtAdvisory;
        private Button btnClose;

        private void btnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }
    }
}
