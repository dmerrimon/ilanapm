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

                // PHASE 1.1: Call BOTH validation AND ML advisory APIs in parallel
                var validationTask = apiClient.ValidateTimelineAsync(timeline);
                var advisoryTask = apiClient.GetTimelineAdvisoryAsync(timeline);

                // Wait for both to complete
                await System.Threading.Tasks.Task.WhenAll(validationTask, advisoryTask);

                var validationResult = await validationTask;
                var advisoryResult = await advisoryTask;

                // Write back to MS Project
                var writer = new Services.ProjectDataWriter();
                writer.WriteValidationResults(Globals.ThisAddIn.Application, validationResult);
                writer.WriteMLAdvisoryResults(Globals.ThisAddIn.Application, advisoryResult);

                // Show enhanced results form with both validation and ML predictions
                EnhancedValidationResultsForm resultsForm = new EnhancedValidationResultsForm();
                resultsForm.DisplayResults(validationResult, advisoryResult, timeline);
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

        // PHASE 1.3: ML ADVISORY BUTTON - REMOVED
        // ML Advisory functionality has been consolidated into the Validate button.
        // The Validate button now calls both validation AND ML advisory APIs in parallel.
        // Results are displayed in the EnhancedValidationResultsForm with 5 tabs:
        //   1. Validation Issues
        //   2. ML Duration Predictions
        //   3. Risk Analysis
        //   4. Country Recommendations
        //   5. Auto-Fix Options
        //
        // This provides a unified view of both validation and ML insights.

        // PHASE 1.3: EXPORT TO TEAMS BUTTON - REMOVED
        // Export to Teams functionality has been removed from the ribbon UI.
        // Reason: Not core to PM workflow. Users can share validation results manually.
        // The backend API endpoint remains available if needed in the future.

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

        // LOAD TEMPLATE BUTTON
        private async void btnLoadTemplate_Click(object sender, RibbonControlEventArgs e)
        {
            System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

            try
            {
                // Show template loader form
                var templateForm = new TemplateLoaderForm();

                if (templateForm.ShowDialog() == DialogResult.OK)
                {
                    // Create template request
                    // Note: All 92 tasks from ontology are included by default
                    var request = new Models.TemplateRequest
                    {
                        country_code = templateForm.SelectedCountryCode,
                        study_phase = templateForm.SelectedPhase,
                        therapeutic_area = templateForm.SelectedTherapeuticArea,
                        include_optional = templateForm.IncludeOptional
                    };

                    // Call API to generate template
                    var apiClient = new Services.ApiClient();
                    var template = await apiClient.GenerateTemplateAsync(request);

                    // Load template into MS Project
                    var loader = new Services.TemplateLoader();
                    loader.LoadTemplateIntoProject(template, Globals.ThisAddIn.Application);

                    // Show success message
                    MessageBox.Show(
                        $"Template loaded successfully!\n\n" +
                        $"Study: {template.study_name}\n" +
                        $"Tasks: {template.tasks.Count}\n" +
                        $"Dependencies: {template.dependencies.Count}\n" +
                        $"Country: {templateForm.SelectedCountryCode}\n" +
                        $"Phase: {templateForm.SelectedPhase}",
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
                    detailedError = detailedError + "\n\nInner: " + ex.InnerException.Message;
                }
                MessageBox.Show(detailedError, "Template Load Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // PHASE 1.2: CRITICAL PATH BUTTON
        private async void btnCriticalPath_Click(object sender, RibbonControlEventArgs e)
        {
            System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

            try
            {
                // Extract timeline from MS Project
                var extractor = new Services.ProjectDataExtractor();
                var timeline = extractor.ExtractTimeline(Globals.ThisAddIn.Application);

                // Call Critical Path API
                var apiClient = new Services.ApiClient();
                var criticalPath = await apiClient.GetCriticalPathAsync(timeline);

                // Highlight critical path tasks in MS Project
                HighlightCriticalPathTasks(criticalPath);

                // Show critical path results form
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

                // Clear existing highlights
                foreach (Microsoft.Office.Interop.MSProject.Task task in app.ActiveProject.Tasks)
                {
                    if (task != null)
                    {
                        task.Marked = false;
                    }
                }

                // Highlight critical path tasks with yellow flag
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
                                    task.Marked = true;  // Yellow flag marker

                                    // Add critical path note
                                    string note = string.Format(
                                        "[CRITICAL PATH]{0}Earliest Start: Day {1}{0}Earliest Finish: Day {2}{0}Total Critical Path Duration: {3} days{0}{0}",
                                        Environment.NewLine,
                                        criticalTask.earliest_start,
                                        criticalTask.earliest_finish,
                                        criticalPath.total_duration
                                    );

                                    string existingNotes = task.Notes ?? "";
                                    task.Notes = existingNotes + note;
                                    break;
                                }
                            }
                        }
                    }
                }

                System.Diagnostics.Debug.WriteLine($"Highlighted {criticalPath.task_count} critical path tasks");
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("Error highlighting critical path: " + ex.Message);
            }
        }
    }
}