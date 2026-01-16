using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    public partial class ValidationResultsForm : Form
    {
        public ValidationResultsForm()
        {
            InitializeComponent();
        }

        private void btnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        public void DisplayResults(Models.ValidationResult result)
        {
            lblSummary.Text = string.Format("Status: {0} | Errors: {1} | Warnings: {2} | Info: {3}",
                result.status.ToUpper(),
                result.error_count,
                result.warning_count,
                result.info_count);

            System.Text.StringBuilder sb = new System.Text.StringBuilder();

            if (result.issues != null && result.issues.Count > 0)
            {
                foreach (var issue in result.issues)
                {
                    sb.AppendLine("═══════════════════════════════════════════════════════════");
                    sb.AppendLine(string.Format("[{0}] {1}", issue.severity.ToUpper(), issue.message));
                    sb.AppendLine();
                    sb.AppendLine("Detail: " + issue.detail);
                    sb.AppendLine();
                    sb.AppendLine("Suggested Fix: " + issue.suggested_fix);
                    sb.AppendLine();
                    if (!string.IsNullOrEmpty(issue.task_id))
                    {
                        sb.AppendLine("Task ID: " + issue.task_id);
                        sb.AppendLine();
                    }
                }
            }
            else
            {
                sb.AppendLine("No issues found! Timeline looks good.");
            }

            txtResults.Text = sb.ToString();
        }

        private void btnClose_Click_1(object sender, EventArgs e)
        {

        }
    }
}