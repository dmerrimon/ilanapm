using System;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    /// <summary>
    /// PHASE 1.1: Enhanced validation results form with 5 tabs
    /// Consolidates validation results and ML advisory into single view
    /// </summary>
    public class EnhancedValidationResultsForm : Form
    {
        private TabControl tabControl;
        private TabPage tabValidation;
        private TabPage tabMLPredictions;
        private TabPage tabRiskAnalysis;
        private TabPage tabRecommendations;
        private TabPage tabAutoFix;

        private Label lblSummary;
        private TextBox txtValidationResults;
        private TextBox txtMLPredictions;
        private TextBox txtRiskAnalysis;
        private TextBox txtRecommendations;
        private TextBox txtAutoFix;
        private Button btnClose;

        public EnhancedValidationResultsForm()
        {
            InitializeComponents();
        }

        private void InitializeComponents()
        {
            // Form settings
            this.Text = "Enhanced Validation Results";
            this.Width = 800;
            this.Height = 600;
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.Sizable;
            this.MinimumSize = new Size(600, 400);

            // Summary label at top
            lblSummary = new Label
            {
                Text = "Loading...",
                Left = 10,
                Top = 10,
                Width = 760,
                Height = 40,
                Font = new Font(FontFamily.GenericSansSerif, 10, FontStyle.Bold),
                AutoSize = false
            };

            // Tab control
            tabControl = new TabControl
            {
                Left = 10,
                Top = 60,
                Width = 760,
                Height = 450,
                Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right
            };

            // Tab 1: Validation Issues
            tabValidation = new TabPage("Validation Issues");
            txtValidationResults = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Dock = DockStyle.Fill,
                Font = new Font(FontFamily.GenericMonospace, 9),
                ReadOnly = true
            };
            tabValidation.Controls.Add(txtValidationResults);
            tabControl.TabPages.Add(tabValidation);

            // Tab 2: ML Duration Predictions
            tabMLPredictions = new TabPage("ML Predictions");
            txtMLPredictions = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Dock = DockStyle.Fill,
                Font = new Font(FontFamily.GenericMonospace, 9),
                ReadOnly = true
            };
            tabMLPredictions.Controls.Add(txtMLPredictions);
            tabControl.TabPages.Add(tabMLPredictions);

            // Tab 3: Risk Analysis
            tabRiskAnalysis = new TabPage("Risk Analysis");
            txtRiskAnalysis = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Dock = DockStyle.Fill,
                Font = new Font(FontFamily.GenericMonospace, 9),
                ReadOnly = true
            };
            tabRiskAnalysis.Controls.Add(txtRiskAnalysis);
            tabControl.TabPages.Add(tabRiskAnalysis);

            // Tab 4: Country Recommendations
            tabRecommendations = new TabPage("Recommendations");
            txtRecommendations = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Dock = DockStyle.Fill,
                Font = new Font(FontFamily.GenericMonospace, 9),
                ReadOnly = true
            };
            tabRecommendations.Controls.Add(txtRecommendations);
            tabControl.TabPages.Add(tabRecommendations);

            // Tab 5: Auto-Fix Options
            tabAutoFix = new TabPage("Auto-Fix");
            txtAutoFix = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Dock = DockStyle.Fill,
                Font = new Font(FontFamily.GenericMonospace, 9),
                ReadOnly = true
            };
            tabAutoFix.Controls.Add(txtAutoFix);
            tabControl.TabPages.Add(tabAutoFix);

            // Close button
            btnClose = new Button
            {
                Text = "Close",
                Left = 690,
                Top = 520,
                Width = 80,
                Height = 30,
                Anchor = AnchorStyles.Bottom | AnchorStyles.Right
            };
            btnClose.Click += (s, e) => this.Close();

            // Add controls to form
            this.Controls.Add(lblSummary);
            this.Controls.Add(tabControl);
            this.Controls.Add(btnClose);
        }

        public void DisplayResults(Models.ValidationResult validation, Models.TimelineAdvisory advisory, Models.Timeline timeline)
        {
            // Update summary
            UpdateSummary(validation, advisory);

            // Populate each tab
            PopulateValidationTab(validation);
            PopulateMLPredictionsTab(advisory);
            PopulateRiskAnalysisTab(advisory);
            PopulateRecommendationsTab(advisory, timeline);
            PopulateAutoFixTab(validation);
        }

        private void UpdateSummary(Models.ValidationResult validation, Models.TimelineAdvisory advisory)
        {
            int mlTaskCount = advisory?.duration_predictions?.total_tasks ?? 0;
            int highRiskCount = advisory?.risk_analysis?.high_risk_count ?? 0;
            double avgConfidence = advisory?.duration_predictions?.average_confidence ?? 0;

            lblSummary.Text = string.Format(
                "Validation: {0} | Errors: {1} | Warnings: {2} | ML Predictions: {3} tasks | High Risk: {4} tasks | Avg Confidence: {5:F0}%",
                validation.status.ToUpper(),
                validation.error_count,
                validation.warning_count,
                mlTaskCount,
                highRiskCount,
                avgConfidence * 100
            );
        }

        private void PopulateValidationTab(Models.ValidationResult validation)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine("                        VALIDATION RESULTS                            ");
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine();

            if (validation.issues != null && validation.issues.Count > 0)
            {
                foreach (var issue in validation.issues)
                {
                    sb.AppendLine("──────────────────────────────────────────────────────────────────────");
                    sb.AppendLine($"[{issue.severity.ToUpper()}] {issue.message}");
                    sb.AppendLine();
                    sb.AppendLine($"Detail: {issue.detail}");
                    sb.AppendLine();
                    sb.AppendLine($"Suggested Fix: {issue.suggested_fix}");

                    if (!string.IsNullOrEmpty(issue.task_id))
                    {
                        sb.AppendLine();
                        sb.AppendLine($"Task ID: {issue.task_id}");
                    }
                    sb.AppendLine();
                }
            }
            else
            {
                sb.AppendLine("✓ No validation issues found! Timeline looks good.");
            }

            txtValidationResults.Text = sb.ToString();
        }

        private void PopulateMLPredictionsTab(Models.TimelineAdvisory advisory)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine("                    ML DURATION PREDICTIONS                           ");
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine();

            if (advisory?.duration_predictions?.predictions != null && advisory.duration_predictions.predictions.Count > 0)
            {
                sb.AppendLine($"Model Version: {advisory.model_version}");
                sb.AppendLine($"Average Confidence: {advisory.duration_predictions.average_confidence * 100:F1}%");
                sb.AppendLine($"Total Tasks Analyzed: {advisory.duration_predictions.total_tasks}");
                sb.AppendLine();

                foreach (var pred in advisory.duration_predictions.predictions)
                {
                    sb.AppendLine("──────────────────────────────────────────────────────────────────────");
                    sb.AppendLine($"Task: {pred.task_name} (ID: {pred.task_id})");
                    sb.AppendLine();
                    sb.AppendLine($"  Current Duration:    {pred.current_duration} days");
                    sb.AppendLine($"  Predicted Duration:  {pred.prediction.predicted_duration_days} days");
                    sb.AppendLine($"  Confidence Range:    {pred.prediction.confidence_interval.lower}-{pred.prediction.confidence_interval.upper} days");
                    sb.AppendLine($"  Confidence Score:    {pred.prediction.confidence_score * 100:F1}%");
                    sb.AppendLine();
                    sb.AppendLine($"  Explanation: {pred.prediction.explanation}");
                    sb.AppendLine();
                }
            }
            else
            {
                sb.AppendLine("No ML predictions available.");
            }

            txtMLPredictions.Text = sb.ToString();
        }

        private void PopulateRiskAnalysisTab(Models.TimelineAdvisory advisory)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine("                         RISK ANALYSIS                                ");
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine();

            if (advisory?.risk_analysis?.risk_scores != null && advisory.risk_analysis.risk_scores.Count > 0)
            {
                sb.AppendLine($"Average Risk Score: {advisory.risk_analysis.average_risk:F1}");
                sb.AppendLine($"High Risk Tasks: {advisory.risk_analysis.high_risk_count}");
                sb.AppendLine();

                // Group by risk level
                var highRisk = advisory.risk_analysis.risk_scores.Where(r => r.risk.risk_level.ToLower() == "high").ToList();
                var mediumRisk = advisory.risk_analysis.risk_scores.Where(r => r.risk.risk_level.ToLower() == "medium").ToList();
                var lowRisk = advisory.risk_analysis.risk_scores.Where(r => r.risk.risk_level.ToLower() == "low").ToList();

                if (highRisk.Count > 0)
                {
                    sb.AppendLine("═══ HIGH RISK TASKS ═══");
                    sb.AppendLine();
                    foreach (var risk in highRisk)
                    {
                        sb.AppendLine($"▲ {risk.task_name} (ID: {risk.task_id})");
                        sb.AppendLine($"  Risk Score: {risk.risk.risk_score}/100");
                        sb.AppendLine($"  Risk Factors:");
                        foreach (var factor in risk.risk.risk_factors)
                        {
                            sb.AppendLine($"    • {factor}");
                        }
                        if (risk.risk.mitigation_suggestions != null && risk.risk.mitigation_suggestions.Count > 0)
                        {
                            sb.AppendLine($"  Mitigation:");
                            foreach (var suggestion in risk.risk.mitigation_suggestions)
                            {
                                sb.AppendLine($"    → {suggestion}");
                            }
                        }
                        sb.AppendLine();
                    }
                }

                if (mediumRisk.Count > 0)
                {
                    sb.AppendLine("═══ MEDIUM RISK TASKS ═══");
                    sb.AppendLine();
                    foreach (var risk in mediumRisk)
                    {
                        sb.AppendLine($"⚠ {risk.task_name} (ID: {risk.task_id})");
                        sb.AppendLine($"  Risk Score: {risk.risk.risk_score}/100");
                        sb.AppendLine($"  Risk Factors: {string.Join(", ", risk.risk.risk_factors)}");
                        sb.AppendLine();
                    }
                }
            }
            else
            {
                sb.AppendLine("No risk analysis available.");
            }

            txtRiskAnalysis.Text = sb.ToString();
        }

        private void PopulateRecommendationsTab(Models.TimelineAdvisory advisory, Models.Timeline timeline)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine("                      RECOMMENDATIONS                                 ");
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine();

            if (advisory?.recommendations != null && advisory.recommendations.Count > 0)
            {
                sb.AppendLine($"Study: {timeline.study_name}");
                sb.AppendLine($"Phase: {timeline.phase}");
                sb.AppendLine($"Authority: {timeline.authority}");
                sb.AppendLine();

                int count = 1;
                foreach (var recommendation in advisory.recommendations)
                {
                    sb.AppendLine($"{count}. {recommendation}");
                    sb.AppendLine();
                    count++;
                }
            }
            else
            {
                sb.AppendLine("No specific recommendations available.");
                sb.AppendLine();
                sb.AppendLine("General best practices:");
                sb.AppendLine("• Review high-risk tasks and allocate additional resources");
                sb.AppendLine("• Monitor tasks with aggressive timelines closely");
                sb.AppendLine("• Consider country-specific regulatory requirements");
                sb.AppendLine("• Plan for dependencies and potential delays");
            }

            txtRecommendations.Text = sb.ToString();
        }

        private void PopulateAutoFixTab(Models.ValidationResult validation)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine("                       AUTO-FIX OPTIONS                               ");
            sb.AppendLine("══════════════════════════════════════════════════════════════════════");
            sb.AppendLine();

            if (validation.issues != null && validation.issues.Count > 0)
            {
                int fixableCount = validation.issues.Count(i => !string.IsNullOrEmpty(i.suggested_fix));

                sb.AppendLine($"Fixable Issues: {fixableCount} of {validation.issues.Count}");
                sb.AppendLine();

                foreach (var issue in validation.issues.Where(i => !string.IsNullOrEmpty(i.suggested_fix)))
                {
                    sb.AppendLine("──────────────────────────────────────────────────────────────────────");
                    sb.AppendLine($"Issue: {issue.message}");
                    sb.AppendLine($"Task ID: {issue.task_id ?? "N/A"}");
                    sb.AppendLine();
                    sb.AppendLine($"Suggested Fix: {issue.suggested_fix}");
                    sb.AppendLine();
                    sb.AppendLine("[ ] Apply this fix automatically");
                    sb.AppendLine();
                }

                sb.AppendLine();
                sb.AppendLine("NOTE: Auto-fix feature will be implemented in a future update.");
            }
            else
            {
                sb.AppendLine("✓ No issues to fix!");
            }

            txtAutoFix.Text = sb.ToString();
        }
    }
}
