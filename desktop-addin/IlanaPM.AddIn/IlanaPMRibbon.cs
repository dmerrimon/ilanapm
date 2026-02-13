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
            // Check for valid license on startup
            CheckLicenseActivation();
        }

        /// <summary>
        /// Check if user has activated license
        /// Show activation form if no token exists
        /// </summary>
        private void CheckLicenseActivation()
        {
            try
            {
                bool hasToken = Services.SecureStorage.HasToken();

                if (!hasToken)
                {
                    System.Diagnostics.Debug.WriteLine("No activation token found - showing activation form");

                    // Show activation form
                    var activationForm = new LicenseActivationForm();
                    var result = activationForm.ShowDialog();

                    if (result != System.Windows.Forms.DialogResult.OK)
                    {
                        // User canceled activation - show reminder
                        MessageBox.Show(
                            "Ilana PM requires an active license to function.\n\n" +
                            "You can activate your license anytime by clicking the Settings button in the ribbon.\n\n" +
                            "Some features may not work until you activate.",
                            "License Required",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Information
                        );
                    }
                    else
                    {
                        System.Diagnostics.Debug.WriteLine("License activated successfully on startup");
                    }
                }
                else
                {
                    System.Diagnostics.Debug.WriteLine("Valid activation token found");
                    string email = Services.SecureStorage.ReadUserEmail();
                    System.Diagnostics.Debug.WriteLine($"Licensed to: {email}");
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"License check error: {ex.Message}");
                // Don't block ribbon load if license check fails
            }
        }

        private async void btnValidate_Click(object sender, RibbonControlEventArgs e)
        {
            System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

            // Track telemetry
            var telemetryService = Globals.ThisAddIn.TelemetryService;
            if (telemetryService != null)
            {
                telemetryService.TrackEvent(TelemetryEventType.ValidationStarted, null);
            }

            try
            {
                // FIRST: Ensure custom fields exist
                EnsureCustomFields();

                // Load metadata from project (saved from Clinical Project Manager)
                var metadata = Services.MetadataHelper.LoadFromProject();

                // Debug: Show what we loaded
                if (metadata == null)
                {
                    System.Diagnostics.Debug.WriteLine("Validation: Metadata is NULL - no data in project summary task");
                }
                else
                {
                    System.Diagnostics.Debug.WriteLine($"Validation: Loaded metadata - Phase='{metadata.Phase}', Area='{metadata.TherapeuticArea}', Country='{metadata.PrimaryCountry}'");
                    System.Diagnostics.Debug.WriteLine($"Validation: IsValid()={metadata.IsValid()}");
                }

                if (metadata == null || !metadata.IsValid())
                {
                    string debugInfo = metadata == null
                        ? "Metadata is null (not saved to project)"
                        : $"Metadata incomplete: {metadata.GetValidationError()}";

                    System.Diagnostics.Debug.WriteLine($"Validation: {debugInfo}");

                    // Metadata is missing - user needs to set up study first
                    MessageBox.Show(
                        "Study information is required for validation.\n\n" +
                        "Please use the Clinical Project Manager to set up your study first:\n\n" +
                        "1. Click Clinical → Clinical Project Manager\n" +
                        "2. Enter study information (Phase, Therapeutic Area, Country)\n" +
                        "3. Generate your timeline\n" +
                        "4. Then return to validate\n\n" +
                        "This ensures all validation uses consistent study information.\n\n" +
                        $"Debug: {debugInfo}",
                        "Study Setup Required",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information
                    );
                    return; // Don't proceed without metadata
                }

                System.Diagnostics.Debug.WriteLine($"Validation: Using metadata from Clinical Project Manager - {metadata}");

                var extractor = new Services.ProjectDataExtractor();
                var timeline = extractor.ExtractTimeline(Globals.ThisAddIn.Application);

                var apiClient = new Services.ApiClient();

                // Create intelligence request with metadata
                var intelligenceRequest = new Models.IntelligenceValidationRequest
                {
                    timeline = timeline,
                    org_id = Services.SecureStorage.ReadOrgId() ?? "unknown",
                    tier = "core",
                    study_metadata = Models.StudyMetadataDTO.FromModel(metadata)
                };

                // Call BOTH validation and intelligence APIs in parallel for maximum performance
                var validationTask = apiClient.ValidateTimelineAsync(timeline);
                var intelligenceTask = apiClient.ValidateWithIntelligenceAsync(intelligenceRequest);

                System.Diagnostics.Debug.WriteLine("Running validation and intelligence in parallel...");
                await System.Threading.Tasks.Task.WhenAll(validationTask, intelligenceTask);

                var validationResult = await validationTask;
                var intelligenceResult = await intelligenceTask;

                System.Diagnostics.Debug.WriteLine($"Validation: {validationResult.status}, Intelligence: {intelligenceResult.summary.total_tasks_analyzed} tasks analyzed");

                // Write validation results back to MS Project
                var writer = new Services.ProjectDataWriter();
                writer.WriteValidationResults(Globals.ThisAddIn.Application, validationResult);

                // Track completion
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.ValidationCompleted, new Dictionary<string, object>
                    {
                        { "issue_count", validationResult.issues?.Count ?? 0 },
                        { "task_count", timeline.tasks?.Count ?? 0 },
                        { "metadata_source", metadata.MetadataSource },
                        { "variance_signals", intelligenceResult.variance_signals?.Count ?? 0 },
                        { "financial_impact", intelligenceResult.summary?.total_financial_impact_usd ?? 0 }
                    });
                }

                // Show validation results form with BOTH validation and intelligence data
                ValidationResultsForm resultsForm = new ValidationResultsForm();
                resultsForm.DisplayResults(validationResult, intelligenceResult);
                resultsForm.ShowDialog();
            }
            catch (Models.UnauthorizedException ex)
            {
                // License expired or invalid - show activation form
                MessageBox.Show(ex.Message, "License Required",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);

                var activationForm = new LicenseActivationForm();
                activationForm.ShowDialog();
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

                // Original custom fields (Text1-6)
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText1, "Regulatory Authority");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText2, "Study Phase");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText3, "Therapeutic Area");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText4, "Task Category");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText5, "Gating Status");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText6, "ML Predicted Duration");

                // Clinical entity fields (Text7-10)
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText7, "Site IDs");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText8, "Amendment IDs");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText9, "Cohort IDs");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText10, "Clinical Summary");

                // NEW: Filtering fields (Text11-14)
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText11, "Site");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText12, "Stage");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText13, "Subphase");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText14, "Template Source");

                // NEW: Authority-specific fields (Text16-17)
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText16, "Authority Type");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText17, "Submission Form");

                // Number fields
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskNumber1, "Checklist Completion %");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskNumber2, "Risk Score");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskNumber3, "ML Confidence %");

                // Flag fields
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskFlag1, "Is Mandatory");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskFlag2, "Is Site-Specific");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskFlag3, "Is Amendment-Generated");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskFlag4, "Requires IRB Approval");

                // Date fields
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskDate1, "Amendment Effective Date");
                app.CustomFieldRename(Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskDate2, "Cohort Enrollment Start");

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

        // VIEW REPORT BUTTON - REMOVED
        // View Report functionality has been removed from the ribbon UI.
        // The ViewManager methods (CreateValidationSummaryView, CreateRiskDashboardView, etc.)
        // remain available for future use if needed.

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
#pragma warning disable CS0618 // Type or member is obsolete
                var templateForm = new TemplateLoaderForm();
#pragma warning restore CS0618 // Type or member is obsolete

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
                    loader.LoadTemplateIntoProject(template, Globals.ThisAddIn.Application, templateForm.CustomColumnNames);

                    // Show success message with custom columns info
                    string customColumnsInfo = "";
                    if (templateForm.CustomColumnNames != null && templateForm.CustomColumnNames.Count > 0)
                    {
                        customColumnsInfo = $"\nCustom Columns: {string.Join(", ", templateForm.CustomColumnNames.Values)}";
                    }

                    MessageBox.Show(
                        $"Template loaded successfully!\n\n" +
                        $"Study: {template.study_name}\n" +
                        $"Tasks: {template.tasks.Count}\n" +
                        $"Dependencies: {template.dependencies.Count}\n" +
                        $"Country: {templateForm.SelectedCountryCode}\n" +
                        $"Phase: {templateForm.SelectedPhase}" +
                        customColumnsInfo,
                        "Template Loaded",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information
                    );
                }
            }
            catch (Models.UnauthorizedException ex)
            {
                MessageBox.Show(ex.Message, "License Required",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                var activationForm = new LicenseActivationForm();
                activationForm.ShowDialog();
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

        // PHASE 3: MULTI-COUNTRY CALCULATOR BUTTON
        private void btnMultiCountry_Click(object sender, RibbonControlEventArgs e)
        {
            try
            {
                // Track telemetry
                var telemetryService = Globals.ThisAddIn.TelemetryService;
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.FeatureOpened, new Dictionary<string, object>
                    {
                        { "feature", "MultiCountryCalculator" }
                    });
                }

                var multiCountryForm = new MultiCountryCalculatorForm();
                var result = multiCountryForm.ShowDialog();

                // Track close
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.FeatureClosed, new Dictionary<string, object>
                    {
                        { "feature", "MultiCountryCalculator" },
                        { "result", result.ToString() }
                    });
                }
            }
            catch (System.Exception ex)
            {
                string detailedError = "Error opening Multi-Country Calculator: " + ex.Message;
                if (ex.InnerException != null)
                {
                    detailedError = detailedError + "\n\nInner: " + ex.InnerException.Message;
                }
                MessageBox.Show(detailedError, "Multi-Country Calculator Error",
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

                // Track telemetry
                var telemetryService = Globals.ThisAddIn.TelemetryService;
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.CriticalPathAnalyzed, new Dictionary<string, object>
                    {
                        { "task_count", criticalPath.task_count },
                        { "total_duration", criticalPath.total_duration }
                    });
                }

                // Show critical path results form
                CriticalPathResultsForm resultsForm = new CriticalPathResultsForm();
                resultsForm.DisplayResults(criticalPath, timeline);
                resultsForm.ShowDialog();
            }
            catch (Models.UnauthorizedException ex)
            {
                MessageBox.Show(ex.Message, "License Required",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                var activationForm = new LicenseActivationForm();
                activationForm.ShowDialog();
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

        // CLINICAL ENTITY TRACKING: CLINICAL SETUP BUTTON
        private void btnClinicalSetup_Click(object sender, RibbonControlEventArgs e)
        {
            try
            {
                EnsureCustomFields();

                // Track telemetry
                var telemetryService = Globals.ThisAddIn.TelemetryService;
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.FeatureOpened, new Dictionary<string, object>
                    {
                        { "feature", "ClinicalSetup" }
                    });
                }

                var setupForm = new ClinicalSetupForm();
                var result = setupForm.ShowDialog();

                // Track close
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.FeatureClosed, new Dictionary<string, object>
                    {
                        { "feature", "ClinicalSetup" },
                        { "result", result.ToString() }
                    });
                }
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error opening Clinical Setup: {ex.Message}",
                    "Clinical Setup Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // DEPRECATED: UNIFIED TEMPLATE MANAGER BUTTON (replaced by Clinical Project Manager)
        private void btnUnifiedTemplateManager_Click(object sender, RibbonControlEventArgs e)
        {
            try
            {
                // Redirect to new Clinical Project Manager
                MessageBox.Show(
                    "The Template Manager has been replaced by the Clinical Project Manager.\n\n" +
                    "The new unified wizard combines Clinical Setup and Template Manager into one workflow.\n\n" +
                    "Opening Clinical Project Manager now...",
                    "Feature Replaced",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);

                // Launch new form
                btnClinicalProjectManager_Click(sender, e);
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error opening Clinical Project Manager: {ex.Message}",
                    "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // CLINICAL ENTITY TRACKING: ESSENTIAL DOCUMENTS TRACKER BUTTON (HIDDEN - NOT IMPLEMENTED)
        private void btnEssentialDocs_Click(object sender, RibbonControlEventArgs e)
        {
            MessageBox.Show("Essential Documents Tracker feature is not yet implemented.",
                "Not Available", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        // NEW: CLINICAL PROJECT MANAGER BUTTON (Phase 2 - Unified wizard)
        private void btnClinicalProjectManager_Click(object sender, RibbonControlEventArgs e)
        {
            try
            {
                EnsureCustomFields();

                // Launch the new unified Clinical Project Manager wizard
                var form = new ClinicalProjectManagerForm(Globals.ThisAddIn.Application);
                var result = form.ShowDialog();

                if (result == DialogResult.OK)
                {
                    MessageBox.Show(
                        "Clinical Project Manager completed successfully.\n\n" +
                        "Your project configuration has been saved and tasks have been generated.",
                        "Success",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                }
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error opening Clinical Project Manager: {ex.Message}",
                    "Clinical Project Manager Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // NEW: TAG TASKS WITH ENTITIES BUTTON
        private void btnTagTasks_Click(object sender, RibbonControlEventArgs e)
        {
            try
            {
                var app = Globals.ThisAddIn.Application;
                var project = app.ActiveProject;

                if (project == null)
                {
                    MessageBox.Show("No active project. Please open or create a project first.",
                        "No Active Project", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                // Get selected tasks
                var selectedTasks = new List<Microsoft.Office.Interop.MSProject.Task>();
                var selection = app.ActiveSelection;

                if (selection == null || selection.Tasks.Count == 0)
                {
                    MessageBox.Show("Please select one or more tasks to tag with clinical entities.",
                        "No Tasks Selected", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    return;
                }

                foreach (Microsoft.Office.Interop.MSProject.Task task in selection.Tasks)
                {
                    if (task != null)
                    {
                        selectedTasks.Add(task);
                    }
                }

                if (selectedTasks.Count == 0)
                {
                    MessageBox.Show("No valid tasks selected.",
                        "No Tasks Selected", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                // Open tagging form
                var form = new ClinicalEntityTaggingForm();
                form.LoadSelectedTasks(selectedTasks);
                form.ShowDialog();
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error tagging tasks: {ex.Message}",
                    "Tag Tasks Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        #region Reports Menu Event Handlers

        // REPORTS: SITE STATUS DASHBOARD
        private void btnSiteStatusDashboard_Click(object sender, RibbonControlEventArgs e)
        {
            try
            {
                var app = Globals.ThisAddIn.Application;
                var project = app.ActiveProject;

                if (project == null)
                {
                    MessageBox.Show("No active project. Please open or create a project first.",
                        "No Active Project", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                // Track telemetry
                var telemetryService = Globals.ThisAddIn.TelemetryService;
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.FeatureOpened, new Dictionary<string, object>
                    {
                        { "feature", "SiteStatusDashboard" }
                    });
                }

                // Launch Site Status Dashboard
                var dashboardForm = new SiteStatusDashboardForm(app);
                dashboardForm.ShowDialog();

                // Track close
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.FeatureClosed, new Dictionary<string, object>
                    {
                        { "feature", "SiteStatusDashboard" }
                    });
                }
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error opening Site Status Dashboard: {ex.Message}",
                    "Report Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // REPORTS: ESSENTIAL DOCUMENTS COMPLIANCE (HIDDEN - NOT IMPLEMENTED)
        private void btnEssentialDocsCompliance_Click(object sender, RibbonControlEventArgs e)
        {
            MessageBox.Show("Essential Documents Compliance Report is not yet implemented.",
                "Not Available", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        // REPORTS: STUDY TIMELINE STATUS (HIDDEN - NOT IMPLEMENTED)
        private void btnStudyTimelineStatus_Click(object sender, RibbonControlEventArgs e)
        {
            MessageBox.Show("Study Timeline Status Report is not yet implemented.",
                "Not Available", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        // REPORTS: SITE ACTIVATION TIMELINE
        private void btnSiteActivationTimeline_Click(object sender, RibbonControlEventArgs e)
        {
            try
            {
                var app = Globals.ThisAddIn.Application;
                var project = app.ActiveProject;

                if (project == null)
                {
                    MessageBox.Show("No active project. Please open or create a project first.",
                        "No Active Project", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                // Track telemetry
                var telemetryService = Globals.ThisAddIn.TelemetryService;
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.FeatureOpened, new Dictionary<string, object>
                    {
                        { "feature", "SiteActivationTimelineReport" }
                    });
                }

                // Launch Site Activation Timeline Report
                var timelineForm = new SiteActivationTimelineForm(app);
                timelineForm.ShowDialog();

                // Track close
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.FeatureClosed, new Dictionary<string, object>
                    {
                        { "feature", "SiteActivationTimelineReport" }
                    });
                }
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error opening Site Activation Timeline Report: {ex.Message}",
                    "Report Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        #endregion

        // ===================================================================
        // PHASE 5: TRACKER UPLOAD & INTELLIGENCE
        // ===================================================================

        /// <summary>
        /// Upload Tracker button - Upload Risk Log, TMF, Budget, or Vendor trackers
        /// Phase 5A: Core Tracker Upload workflow
        /// </summary>
        private async void btnUploadTracker_Click(object sender, RibbonControlEventArgs e)
        {
            System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

            try
            {
                // Get org_id from secure storage
                string orgId = Services.SecureStorage.ReadOrgId();
                if (string.IsNullOrEmpty(orgId))
                {
                    MessageBox.Show(
                        "Organization ID not found.\n\n" +
                        "Please re-activate your license in Settings to retrieve your organization information.",
                        "Configuration Required",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Warning
                    );
                    return;
                }

                // Get project_id from current MS Project file
                var app = Globals.ThisAddIn.Application;
                if (app.ActiveProject == null)
                {
                    MessageBox.Show(
                        "No active project.\n\n" +
                        "Please open or create a project first before uploading tracker data.",
                        "No Active Project",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Warning
                    );
                    return;
                }

                string projectId = app.ActiveProject.Name;
                System.Diagnostics.Debug.WriteLine($"Upload Tracker: org_id={orgId}, project_id={projectId}");

                // Show tracker upload form
                var uploadForm = new TrackerUploadForm(orgId, projectId);
                var result = uploadForm.ShowDialog();

                if (result == DialogResult.OK)
                {
                    // Upload succeeded - show results
                    var uploadResult = uploadForm.UploadResult;

                    if (uploadResult != null)
                    {
                        string healthIcon = uploadResult.health_status == "healthy" ? "✅" :
                                           uploadResult.health_status == "warning" ? "⚠️" : "🔴";

                        string message = $"✅ Tracker uploaded successfully!\n\n" +
                                       $"📊 {uploadResult.rows_processed} rows processed\n" +
                                       $"🔔 {uploadResult.signals_extracted} signals extracted\n" +
                                       $"⚠️ {uploadResult.escalations_detected} escalations detected\n\n" +
                                       $"{healthIcon} Study Health: {uploadResult.health_score:F1} ({uploadResult.health_status})\n\n" +
                                       $"View full details in Leadership Dashboard.";

                        MessageBox.Show(
                            message,
                            "Upload Complete",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Information
                        );

                        System.Diagnostics.Debug.WriteLine($"Tracker upload successful: {uploadResult.rows_processed} rows, " +
                                                           $"{uploadResult.signals_extracted} signals, " +
                                                           $"{uploadResult.escalations_detected} escalations, " +
                                                           $"health: {uploadResult.health_score} ({uploadResult.health_status})");

                        // Track telemetry
                        var telemetryService = Globals.ThisAddIn.TelemetryService;
                        if (telemetryService != null)
                        {
                            telemetryService.TrackEvent(TelemetryEventType.TrackerUploaded, new Dictionary<string, object>
                            {
                                { "tracker_type", uploadForm.SelectedTrackerType },
                                { "rows_processed", uploadResult.rows_processed },
                                { "signals_extracted", uploadResult.signals_extracted },
                                { "escalations_detected", uploadResult.escalations_detected },
                                { "health_score", uploadResult.health_score },
                                { "health_status", uploadResult.health_status }
                            });
                        }
                    }
                }
            }
            catch (Models.UnauthorizedException ex)
            {
                // License expired or invalid - show activation form
                MessageBox.Show(ex.Message, "License Required",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);

                var activationForm = new LicenseActivationForm();
                activationForm.ShowDialog();
            }
            catch (System.Exception ex)
            {
                string detailedError = "Error uploading tracker: " + ex.Message;
                if (ex.InnerException != null)
                {
                    detailedError = detailedError + "\n\nInner: " + ex.InnerException.Message;
                }

                System.Diagnostics.Debug.WriteLine($"Tracker upload error: {detailedError}");

                MessageBox.Show(detailedError, "Upload Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        /// <summary>
        /// Leadership Dashboard button - Open Leadership Dashboard in web browser
        /// Phase 5B: Leadership Dashboard Integration
        /// </summary>
        private void btnLeadershipDashboard_Click(object sender, RibbonControlEventArgs e)
        {
            try
            {
                // Get dashboard URL with auto-login token
                var apiClient = new Services.ApiClient();
                string dashboardUrl = apiClient.GetLeadershipDashboardUrl();

                System.Diagnostics.Debug.WriteLine($"Opening Leadership Dashboard: {dashboardUrl}");

                // Open in default browser
                System.Diagnostics.Process.Start(dashboardUrl);

                // Track telemetry
                var telemetryService = Globals.ThisAddIn.TelemetryService;
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.LeadershipDashboardOpened, new Dictionary<string, object>
                    {
                        { "source", "ribbon_button" }
                    });
                }

                System.Diagnostics.Debug.WriteLine("Leadership Dashboard opened successfully");
            }
            catch (Models.UnauthorizedException ex)
            {
                // License expired or no org_id - show activation form
                MessageBox.Show(
                    "Unable to open Leadership Dashboard.\n\n" + ex.Message +
                    "\n\nPlease activate your license in Settings.",
                    "License Required",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Warning
                );

                var activationForm = new LicenseActivationForm();
                activationForm.ShowDialog();
            }
            catch (System.Exception ex)
            {
                string detailedError = "Error opening Leadership Dashboard: " + ex.Message;
                if (ex.InnerException != null)
                {
                    detailedError = detailedError + "\n\nInner: " + ex.InnerException.Message;
                }

                System.Diagnostics.Debug.WriteLine($"Dashboard open error: {detailedError}");

                MessageBox.Show(
                    detailedError +
                    "\n\nPlease check your internet connection and try again.",
                    "Dashboard Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
            }
        }
    }
}