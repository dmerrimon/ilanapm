using Microsoft.Office.Tools.Ribbon;
using System;
using System.Windows.Forms;

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
                var extractor = new Services.ProjectDataExtractor();
                var timeline = extractor.ExtractTimeline(Globals.ThisAddIn.Application);

                var apiClient = new Services.ApiClient();
                var result = await apiClient.ValidateTimelineAsync(timeline);

                var writer = new Services.ProjectDataWriter();
                writer.WriteValidationResults(Globals.ThisAddIn.Application, result);

                var form = new ValidationResultsForm();
                form.DisplayResults(result);
                form.ShowDialog();
            }
            catch (System.Exception ex)
            {
                MessageBox.Show("Error during validation: " + ex.Message, "Validation Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private async void btnCriticalPath_Click(object sender, RibbonControlEventArgs e)
        {
            System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

            try
            {
                var extractor = new Services.ProjectDataExtractor();
                var timeline = extractor.ExtractTimeline(Globals.ThisAddIn.Application);

                var apiClient = new Services.ApiClient();
                var criticalPath = await apiClient.GetCriticalPathAsync(timeline);

                HighlightCriticalPathTasks(criticalPath);

                CriticalPathResultsForm resultsForm = new CriticalPathResultsForm();
                resultsForm.DisplayResults(criticalPath, timeline);
                resultsForm.ShowDialog();
            }
            catch (System.Exception ex)
            {
                string detailedError = "Error analyzing critical path: " + ex.Message;
                if (ex.InnerException != null)
                {
                    detailedError = detailedError + "\n\nInner: " + ex.InnerException.Message;
                }
                MessageBox.Show(detailedError, "Critical Path Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void HighlightCriticalPathTasks(Models.CriticalPathResult criticalPath)
        {
            try
            {
                var app = Globals.ThisAddIn.Application;
                if (app.ActiveProject == null) return;

                foreach (Microsoft.Office.Interop.MSProject.Task task in app.ActiveProject.Tasks)
                {
                    if (task != null)
                    {
                        task.Marked = false;
                    }
                }

                if (criticalPath.tasks != null)
                {
                    foreach (var criticalTask in criticalPath.tasks)
                    {
                        if (int.TryParse(criticalTask.id, out int taskId))
                        {
                            foreach (Microsoft.Office.Interop.MSProject.Task task in app.ActiveProject.Tasks)
                            {
                                if (task != null && task.ID == taskId)
                                {
                                    task.Marked = true;
                                    string note = "[CRITICAL PATH]\nEarliest Start: Day " + criticalTask.earliest_start.ToString() +
                                        "\nEarliest Finish: Day " + criticalTask.earliest_finish.ToString() + "\nTotal Duration: " +
                                        criticalPath.total_duration.ToString() + " days\n\n";
                                    task.Notes = (task.Notes ?? "") + note;
                                    break;
                                }
                            }
                        }
                    }
                }
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("Error highlighting critical path: " + ex.Message);
            }
        }

        private async void btnLoadTemplate_Click(object sender, RibbonControlEventArgs e)
        {
            System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

            try
            {
                var templateForm = new TemplateLoaderForm();

                if (templateForm.ShowDialog() == DialogResult.OK)
                {
                    var request = new Models.TemplateRequest
                    {
                        country_code = templateForm.SelectedCountryCode,
                        study_phase = templateForm.SelectedPhase,
                        therapeutic_area = templateForm.SelectedTherapeuticArea,
                        include_optional = templateForm.IncludeOptional
                    };

                    var apiClient = new Services.ApiClient();
                    var template = await apiClient.GenerateTemplateAsync(request);

                    var loader = new Services.TemplateLoader();
                    loader.LoadTemplateIntoProject(template, Globals.ThisAddIn.Application);

                    MessageBox.Show(
                        "Template loaded successfully!" + System.Environment.NewLine + System.Environment.NewLine +
                        "Study: " + template.study_name + System.Environment.NewLine +
                        "Tasks: " + template.tasks.Count + System.Environment.NewLine +
                        "Dependencies: " + template.dependencies.Count + System.Environment.NewLine +
                        "Country: " + templateForm.SelectedCountryCode + System.Environment.NewLine +
                        "Phase: " + templateForm.SelectedPhase,
                        "Template Loaded",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information
                    );
                }
            }
            catch (System.Exception ex)
            {
                string detailedError = "Error loading template: " + ex.Message;
                if (ex.InnerException != null)
                {
                    detailedError = detailedError + System.Environment.NewLine + System.Environment.NewLine + "Inner: " +
                        ex.InnerException.Message;
                }
                MessageBox.Show(detailedError, "Template Load Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnMultiCountry_Click(object sender, RibbonControlEventArgs e)
        {
            MessageBox.Show("Multi-Country Calculator will be implemented in Phase 2." + System.Environment.NewLine + System.Environment.NewLine +
                "This feature will help you optimize submission strategies for multi-country clinical trials.",
                "Multi-Country Calculator",
                MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

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

        private void btnSettings_Click(object sender, RibbonControlEventArgs e)
        {
            try
            {
                var settingsForm = new SettingsForm();
                settingsForm.ShowDialog();
            }
            catch (System.Exception ex)
            {
                MessageBox.Show("Error opening settings: " + ex.Message, "Settings Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
