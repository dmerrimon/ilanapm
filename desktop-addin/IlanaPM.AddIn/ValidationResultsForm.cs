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

        /// <summary>
        /// Display validation results only (backward compatibility)
        /// </summary>
        public void DisplayResults(Models.ValidationResult result)
        {
            DisplayResults(result, null);
        }

        /// <summary>
        /// Display both validation and intelligence results (NEW)
        /// </summary>
        public void DisplayResults(Models.ValidationResult validationResult, Models.VarianceReport intelligenceResult)
        {
            // Display validation summary
            lblSummary.Text = string.Format("Status: {0} | Errors: {1} | Warnings: {2} | Info: {3}",
                validationResult.status.ToUpper(),
                validationResult.error_count,
                validationResult.warning_count,
                validationResult.info_count);

            // Display validation issues
            System.Text.StringBuilder validationText = new System.Text.StringBuilder();

            if (validationResult.issues != null && validationResult.issues.Count > 0)
            {
                foreach (var issue in validationResult.issues)
                {
                    validationText.AppendLine("═══════════════════════════════════════════════════════════");
                    validationText.AppendLine(string.Format("[{0}] {1}", issue.severity.ToUpper(), issue.message));
                    validationText.AppendLine();
                    validationText.AppendLine("Detail: " + issue.detail);
                    validationText.AppendLine();
                    validationText.AppendLine("Suggested Fix: " + issue.suggested_fix);
                    validationText.AppendLine();
                    if (!string.IsNullOrEmpty(issue.task_id))
                    {
                        validationText.AppendLine("Task ID: " + issue.task_id);
                        validationText.AppendLine();
                    }
                }
            }
            else
            {
                validationText.AppendLine("No validation issues found! Timeline looks good.");
            }

            txtResults.Text = validationText.ToString();

            // Display intelligence results if available
            if (intelligenceResult != null)
            {
                DisplayIntelligenceResults(intelligenceResult);
            }
        }

        /// <summary>
        /// Display intelligence variance report
        /// </summary>
        private void DisplayIntelligenceResults(Models.VarianceReport report)
        {
            if (report == null || report.summary == null) return;

            System.Text.StringBuilder intelligenceText = new System.Text.StringBuilder();

            // Summary header
            intelligenceText.AppendLine("═══════════════════════════════════════════════════════════");
            intelligenceText.AppendLine("INTELLIGENCE ANALYSIS - BENCHMARK COMPARISON");
            intelligenceText.AppendLine("═══════════════════════════════════════════════════════════");
            intelligenceText.AppendLine();

            // Financial impact summary
            intelligenceText.AppendLine(string.Format("Financial Impact: ${0:N0}", report.summary.total_financial_impact_usd));
            intelligenceText.AppendLine(string.Format("Tasks Analyzed: {0}", report.summary.total_tasks_analyzed));
            intelligenceText.AppendLine(string.Format("Benchmark Coverage: {0:F1}%", report.summary.benchmark_coverage_percent));
            intelligenceText.AppendLine();

            // Variance breakdown
            intelligenceText.AppendLine(string.Format("Variances: {0} Critical | {1} Warning | {2} Acceptable",
                report.summary.critical_count,
                report.summary.warning_count,
                report.summary.acceptable_count));
            intelligenceText.AppendLine();

            // High-variance tasks
            if (report.variance_signals != null && report.variance_signals.Count > 0)
            {
                intelligenceText.AppendLine("───────────────────────────────────────────────────────────");
                intelligenceText.AppendLine("HIGH-VARIANCE TASKS");
                intelligenceText.AppendLine("───────────────────────────────────────────────────────────");
                intelligenceText.AppendLine();

                // Show critical and warning variances only
                var significantVariances = report.variance_signals
                    .Where(v => v.variance.severity == "critical" || v.variance.severity == "warning")
                    .OrderByDescending(v => Math.Abs(v.financial_impact_usd))
                    .ToList();

                foreach (var signal in significantVariances)
                {
                    intelligenceText.AppendLine(string.Format("[{0}] {1}",
                        signal.variance.severity.ToUpper(),
                        signal.task_name));
                    intelligenceText.AppendLine();

                    intelligenceText.AppendLine(string.Format("  Your Duration: {0} days", signal.customer_duration_days));
                    intelligenceText.AppendLine(string.Format("  Benchmark:     {0} days (p25: {1}, p75: {2})",
                        signal.benchmark.median_days,
                        signal.benchmark.p25_days,
                        signal.benchmark.p75_days));
                    intelligenceText.AppendLine(string.Format("  Variance:      {0:+0;-0}% ({1})",
                        signal.variance.percentage,
                        signal.variance.classification));
                    intelligenceText.AppendLine(string.Format("  Financial Impact: ${0:N0}", signal.financial_impact_usd));
                    intelligenceText.AppendLine();

                    if (!string.IsNullOrEmpty(signal.explanation))
                    {
                        intelligenceText.AppendLine(string.Format("  Explanation: {0}", signal.explanation));
                        intelligenceText.AppendLine();
                    }
                }
            }

            // Coverage information
            if (report.benchmark_coverage != null && report.benchmark_coverage.tasks_unmatched > 0)
            {
                intelligenceText.AppendLine("───────────────────────────────────────────────────────────");
                intelligenceText.AppendLine("BENCHMARK COVERAGE");
                intelligenceText.AppendLine("───────────────────────────────────────────────────────────");
                intelligenceText.AppendLine();
                intelligenceText.AppendLine(string.Format("Matched: {0} tasks", report.benchmark_coverage.tasks_matched));
                intelligenceText.AppendLine(string.Format("Unmatched: {0} tasks", report.benchmark_coverage.tasks_unmatched));
                intelligenceText.AppendLine();

                if (report.benchmark_coverage.unmatched_task_names != null && report.benchmark_coverage.unmatched_task_names.Count > 0)
                {
                    intelligenceText.AppendLine("Unmatched tasks:");
                    foreach (var taskName in report.benchmark_coverage.unmatched_task_names.Take(10))
                    {
                        intelligenceText.AppendLine(string.Format("  • {0}", taskName));
                    }
                    if (report.benchmark_coverage.unmatched_task_names.Count > 10)
                    {
                        intelligenceText.AppendLine(string.Format("  ... and {0} more",
                            report.benchmark_coverage.unmatched_task_names.Count - 10));
                    }
                }
            }

            // Append intelligence results after validation results
            txtResults.Text += "\n\n\n" + intelligenceText.ToString();
        }

        private void btnClose_Click_1(object sender, EventArgs e)
        {

        }
    }
}