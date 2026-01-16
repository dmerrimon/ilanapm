using Microsoft.Office.Tools.Ribbon;
using System;
using System.Windows.Forms;
using System.Collections.Generic;

namespace IlanaPM.AddIn
{
    public partial class IlanaPMRibbon
    {
        private void IlanaPMRibbon_Load(object sender, RibbonUIEventArgs e)
        {
            // Ribbon loaded                                                                                                                                                                                      
        }

        private async void btnValidate_Click(object sender, RibbonControlEventArgs e)
        {
            System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

            try
            {
                // FIRST: Ensure custom fields exist                                                                                                                                                              
                EnsureCustomFields();

                var extractor = new Services.ProjectDataExtractor();
                var timeline = extractor.ExtractTimeline(Globals.ThisAddIn.Application);

                var apiClient = new Services.ApiClient();
                var result = await apiClient.ValidateTimelineAsync(timeline);

                // Write back to MS Project                                                                                                                                                                       
                var writer = new Services.ProjectDataWriter();
                writer.WriteValidationResults(Globals.ThisAddIn.Application, result);

                ValidationResultsForm resultsForm = new ValidationResultsForm();
                resultsForm.DisplayResults(result);
                resultsForm.ShowDialog();
            }
            catch (System.Exception ex)
            {
                string detailedError = "Error: " + ex.Message;
                if (ex.InnerException != null)
                {
                    detailedError = detailedError + "\n\nInner: " + ex.InnerException.Message;
                }
                MessageBox.Show(detailedError, "Ilana PM Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void EnsureCustomFields()
        {
            try
            {
                var app = Globals.ThisAddIn.Application;
                if (app.ActiveProject == null) return;

                System.Diagnostics.Debug.WriteLine("Creating custom fields on demand...");

                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText1, "Regulatory Authority");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText2, "Study Phase");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText3, "Therapeutic Area");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText4, "Task Category");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText5, "Gating Status");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText6, "ML Predicted Duration");

                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskNumber1, "Checklist Completion %");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskNumber2, "Risk Score");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskNumber3, "ML Confidence %");

                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskFlag1, "Is Mandatory");

                System.Diagnostics.Debug.WriteLine("Custom fields created successfully");
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("Custom field creation: " + ex.Message);
            }
        }

        // ML ADVISORY BUTTON                                                                                                                                                                                     
        private void btnMLAdvisory_Click(object sender, RibbonControlEventArgs e)
        {
            MessageBox.Show(
                "ML Advisory feature is being configured." + Environment.NewLine + Environment.NewLine +
                "This feature will provide:" + Environment.NewLine +
                "- Duration predictions for tasks" + Environment.NewLine +
                "- Risk scoring and analysis" + Environment.NewLine +
                "- Recommendations based on historical data",
                "ML Advisory",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information);
        }

        // EXPORT TO TEAMS BUTTON                                                                                                                                                                                 
        private async void btnExportTeams_Click(object sender, RibbonControlEventArgs e)
        {
            try
            {
                string webhookUrl = PromptForWebhookUrl();
                if (string.IsNullOrEmpty(webhookUrl))
                    return;

                var extractor = new Services.ProjectDataExtractor();
                var timeline = extractor.ExtractTimeline(Globals.ThisAddIn.Application);

                var apiClient = new Services.ApiClient();
                var result = await apiClient.ValidateTimelineAsync(timeline);

                var notification = new Models.TeamsNotificationRequest
                {
                    webhook_url = webhookUrl,
                    study_name = timeline.study_name,
                    validation_summary = new Models.ValidationSummary
                    {
                        status = result.status,
                        error_count = result.error_count,
                        warning_count = result.warning_count,
                        total_tasks = result.total_tasks_analyzed
                    },
                    high_risk_tasks = new System.Collections.Generic.List<Models.HighRiskTaskSummary>()
                };

                foreach (var issue in result.issues)
                {
                    if (issue.severity == "error" && !string.IsNullOrEmpty(issue.task_id))
                    {
                        var task = timeline.tasks.Find(t => t.id == issue.task_id);
                        if (task != null)
                        {
                            notification.high_risk_tasks.Add(new Models.HighRiskTaskSummary
                            {
                                name = task.name,
                                risk_score = 90
                            });
                        }
                    }
                }

                bool success = await apiClient.SendTeamsNotificationAsync(notification);

                if (success)
                {
                    MessageBox.Show("Validation summary sent to Teams!", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                else
                {
                    MessageBox.Show("Failed to send to Teams. Check webhook URL.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
            catch (System.Exception ex)
            {
                MessageBox.Show("Error: " + ex.Message, "Teams Export Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private string PromptForWebhookUrl()
        {
            using (var form = new Form())
            {
                form.Text = "Teams Webhook URL";
                form.Width = 500;
                form.Height = 150;
                form.StartPosition = FormStartPosition.CenterScreen;

                var label = new Label { Text = "Enter Teams Incoming Webhook URL:", Left = 20, Top = 20, Width = 400 };
                var textBox = new TextBox { Left = 20, Top = 50, Width = 440 };
                var btnOk = new Button { Text = "OK", Left = 300, Top = 80, Width = 75, DialogResult = DialogResult.OK };
                var btnCancel = new Button { Text = "Cancel", Left = 385, Top = 80, Width = 75, DialogResult = DialogResult.Cancel };

                form.Controls.Add(label);
                form.Controls.Add(textBox);
                form.Controls.Add(btnOk);
                form.Controls.Add(btnCancel);
                form.AcceptButton = btnOk;
                form.CancelButton = btnCancel;

                return form.ShowDialog() == DialogResult.OK ? textBox.Text : null;
            }
        }

        // VIEW REPORT BUTTON                                                                                                                                                                                     
        private void btnViewReport_Click(object sender, RibbonControlEventArgs e)
        {
            try
            {
                using (var form = new Form())
                {
                    form.Text = "Select View";
                    form.Width = 300;
                    form.Height = 250;
                    form.StartPosition = FormStartPosition.CenterScreen;

                    var label = new Label { Text = "Choose a report view:", Left = 20, Top = 20, Width = 240 };

                    var btnValidation = new Button { Text = "Validation Summary", Left = 20, Top = 50, Width = 240 };
                    btnValidation.Click += (s, args) => {
                        var viewManager = new Services.ViewManager();
                        viewManager.CreateValidationSummaryView(Globals.ThisAddIn.Application);
                        form.Close();
                    };

                    var btnRisk = new Button { Text = "Risk Dashboard", Left = 20, Top = 85, Width = 240 };
                    btnRisk.Click += (s, args) => {
                        var viewManager = new Services.ViewManager();
                        viewManager.CreateRiskDashboardView(Globals.ThisAddIn.Application);
                        form.Close();
                    };

                    var btnExecutive = new Button { Text = "Executive Summary", Left = 20, Top = 120, Width = 240 };
                    btnExecutive.Click += (s, args) => {
                        var viewManager = new Services.ViewManager();
                        viewManager.CreateExecutiveSummaryView(Globals.ThisAddIn.Application);
                        form.Close();
                    };

                    var btnChecklist = new Button { Text = "Checklist Completion", Left = 20, Top = 155, Width = 240 };
                    btnChecklist.Click += (s, args) => {
                        var viewManager = new Services.ViewManager();
                        viewManager.CreateChecklistCompletionView(Globals.ThisAddIn.Application);
                        form.Close();
                    };

                    form.Controls.Add(label);
                    form.Controls.Add(btnValidation);
                    form.Controls.Add(btnRisk);
                    form.Controls.Add(btnExecutive);
                    form.Controls.Add(btnChecklist);

                    form.ShowDialog();
                }
            }
            catch (System.Exception ex)
            {
                MessageBox.Show("Error: " + ex.Message, "View Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // SETTINGS BUTTON                                                                                                                                                                                        
        private void btnSettings_Click(object sender, RibbonControlEventArgs e)
        {
            var settingsForm = new SettingsForm();
            settingsForm.ShowDialog();
        }
    }
}