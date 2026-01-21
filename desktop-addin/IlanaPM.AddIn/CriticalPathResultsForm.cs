using System;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    /// <summary>
    /// PHASE 1.2: Critical Path Results Form
    /// Displays critical path analysis with task details and timeline bottlenecks
    /// </summary>
    public class CriticalPathResultsForm : Form
    {
        private Label lblSummary;
        private TextBox txtResults;
        private Button btnClose;

        public CriticalPathResultsForm()
        {
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            // Form settings
            this.Text = "Critical Path Analysis";
            this.Width = 700;
            this.Height = 500;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.Sizable;
            this.MinimumSize = new Size(500, 400);

            // Summary label
            lblSummary = new Label
            {
                Text = "Loading critical path...",
                Left = 10,
                Top = 10,
                Width = 660,
                Height = 30,
                Font = new Font(FontFamily.GenericSansSerif, 10, FontStyle.Bold),
                AutoSize = false,
                Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right
            };

            // Results textbox
            txtResults = new TextBox
            {
                Left = 10,
                Top = 50,
                Width = 660,
                Height = 370,
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Font = new Font(FontFamily.GenericMonospace, 9),
                ReadOnly = true,
                Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right
            };

            // Close button
            btnClose = new Button
            {
                Text = "Close",
                Left = 590,
                Top = 430,
                Width = 80,
                Height = 30,
                Anchor = AnchorStyles.Bottom | AnchorStyles.Right
            };
            btnClose.Click += (s, e) => this.Close();

            // Add controls to form
            this.Controls.Add(lblSummary);
            this.Controls.Add(txtResults);
            this.Controls.Add(btnClose);
        }

        public void DisplayResults(Models.CriticalPathResult criticalPath, Models.Timeline timeline)
        {
            if (criticalPath == null)
            {
                lblSummary.Text = "No critical path data available.";
                txtResults.Text = "Unable to calculate critical path. Please check task dependencies.";
                return;
            }

            // Update summary
            lblSummary.Text = string.Format(
                "Critical Path: {0} tasks | Total Duration: {1} days | Study: {2}",
                criticalPath.task_count,
                criticalPath.total_duration,
                timeline.study_name
            );

            // Build detailed results
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine("                       CRITICAL PATH ANALYSIS                         ");
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine();
            sb.AppendLine($"Study: {timeline.study_name}");
            sb.AppendLine($"Phase: {timeline.phase}");
            sb.AppendLine($"Authority: {timeline.authority}");
            sb.AppendLine();
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine($"Total Critical Path Duration: {criticalPath.total_duration} days");
            sb.AppendLine($"Number of Critical Tasks: {criticalPath.task_count}");
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine();

            if (criticalPath.tasks != null && criticalPath.tasks.Count > 0)
            {
                sb.AppendLine("CRITICAL PATH TASKS (highlighted in MS Project with yellow flags):");
                sb.AppendLine();

                int cumulativeDuration = 0;
                int taskNumber = 1;

                foreach (var task in criticalPath.tasks)
                {
                    cumulativeDuration += task.duration_days;

                    sb.AppendLine("──────────────────────────────────────────────────────────────────────");
                    sb.AppendLine($"#{taskNumber}: {task.name}");
                    sb.AppendLine();
                    sb.AppendLine($"  Task ID:           {task.id}");
                    sb.AppendLine($"  Duration:          {task.duration_days} days");
                    sb.AppendLine($"  Category:          {task.category}");
                    sb.AppendLine($"  Mandatory:         {(task.is_mandatory ? "Yes" : "No")}");
                    sb.AppendLine();
                    sb.AppendLine($"  Earliest Start:    Day {task.earliest_start}");
                    sb.AppendLine($"  Earliest Finish:   Day {task.earliest_finish}");
                    sb.AppendLine($"  Cumulative:        {cumulativeDuration} days");
                    sb.AppendLine();

                    taskNumber++;
                }

                sb.AppendLine("══════════════════════════════════════════════════════════════════════");
                sb.AppendLine();
                sb.AppendLine("CRITICAL PATH INSIGHTS:");
                sb.AppendLine();
                sb.AppendLine("  ⚠ Tasks on the critical path have zero slack/float");
                sb.AppendLine("  ⚠ Any delay in these tasks will delay the entire project");
                sb.AppendLine("  ⚠ Focus resources on completing critical path tasks on time");
                sb.AppendLine();
                sb.AppendLine("RECOMMENDATIONS:");
                sb.AppendLine();
                sb.AppendLine("  • Monitor critical path tasks closely with daily check-ins");
                sb.AppendLine("  • Allocate top-performing resources to critical tasks");
                sb.AppendLine("  • Consider fast-tracking or crashing options if delays occur");
                sb.AppendLine("  • Build in buffer time for high-risk critical path tasks");
                sb.AppendLine("  • Review dependencies to identify parallelization opportunities");
                sb.AppendLine();

                // Calculate percentage of project on critical path
                int totalTasks = timeline.tasks?.Count ?? 0;
                double criticalPercentage = totalTasks > 0 ? (double)criticalPath.task_count / totalTasks * 100 : 0;

                sb.AppendLine("══════════════════════════════════════════════════════════════════════");
                sb.AppendLine($"Critical Path Tasks: {criticalPath.task_count} of {totalTasks} ({criticalPercentage:F1}%)");
                sb.AppendLine("══════════════════════════════════════════════════════════════════════");

                if (criticalPercentage > 50)
                {
                    sb.AppendLine();
                    sb.AppendLine("⚠ WARNING: Over 50% of tasks are on the critical path!");
                    sb.AppendLine("  This indicates limited flexibility in the schedule.");
                    sb.AppendLine("  Consider adding parallel work streams or reducing dependencies.");
                }
                else if (criticalPercentage < 20)
                {
                    sb.AppendLine();
                    sb.AppendLine($"✓ Good schedule flexibility with {criticalPercentage:F1}% critical tasks.");
                    sb.AppendLine("  Non-critical tasks have float and can absorb some delays.");
                }
            }
            else
            {
                sb.AppendLine("No critical path tasks identified.");
                sb.AppendLine();
                sb.AppendLine("This may indicate:");
                sb.AppendLine("  • No task dependencies defined");
                sb.AppendLine("  • All tasks are independent");
                sb.AppendLine("  • Project structure needs review");
            }

            txtResults.Text = sb.ToString();
        }
    }
}
