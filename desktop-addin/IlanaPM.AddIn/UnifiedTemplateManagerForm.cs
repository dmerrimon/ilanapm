using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;
using IlanaPM.AddIn.Models;
using IlanaPM.AddIn.Services;

namespace IlanaPM.AddIn
{
    /// <summary>
    /// Unified Template Manager - 3-step wizard for all template types
    /// Step 1: Select template type
    /// Step 2: Configure (dynamic based on template type)
    /// Step 3: Preview & filter tasks
    /// </summary>
    public partial class UnifiedTemplateManagerForm : Form
    {
        private UnifiedTemplateManager templateManager;
        private TemplateConfiguration currentConfig;
        private FilterOptions currentFilters;
        private TemplateResult previewResult;
        private int currentStep = 1;

        // Template type selection (Step 1)
        private const int STEP_SELECT_TYPE = 1;
        private const int STEP_CONFIGURE = 2;
        private const int STEP_PREVIEW = 3;

        public UnifiedTemplateManagerForm()
        {
            InitializeComponent();
            templateManager = new UnifiedTemplateManager();
            currentConfig = new TemplateConfiguration();
            currentFilters = new FilterOptions();

            InitializeWizard();
        }

        /// <summary>
        /// Initialize wizard - show Step 1, hide others
        /// </summary>
        private void InitializeWizard()
        {
            currentStep = STEP_SELECT_TYPE;
            UpdateWizardUI();

            // Set default selections
            rbFullStudyTimeline.Checked = true;
        }

        /// <summary>
        /// Update wizard UI based on current step
        /// </summary>
        private void UpdateWizardUI()
        {
            // Show/hide panels
            panelStep1.Visible = (currentStep == STEP_SELECT_TYPE);
            panelStep2.Visible = (currentStep == STEP_CONFIGURE);
            panelStep3.Visible = (currentStep == STEP_PREVIEW);

            // Update step indicator
            lblStepIndicator.Text = $"Step {currentStep} of 3";

            // Update button states
            btnBack.Enabled = (currentStep > STEP_SELECT_TYPE);
            btnNext.Visible = (currentStep < STEP_PREVIEW);
            btnGenerate.Visible = (currentStep == STEP_PREVIEW);

            // Update step labels
            lblStep1Title.Font = new Font(lblStep1Title.Font, currentStep == STEP_SELECT_TYPE ? FontStyle.Bold : FontStyle.Regular);
            lblStep2Title.Font = new Font(lblStep2Title.Font, currentStep == STEP_CONFIGURE ? FontStyle.Bold : FontStyle.Regular);
            lblStep3Title.Font = new Font(lblStep3Title.Font, currentStep == STEP_PREVIEW ? FontStyle.Bold : FontStyle.Regular);
        }

        /// <summary>
        /// Next button - advance to next step
        /// </summary>
        private async void btnNext_Click(object sender, EventArgs e)
        {
            if (currentStep == STEP_SELECT_TYPE)
            {
                // Validate template type selection
                if (!ValidateStep1())
                {
                    MessageBox.Show("Please select a template type.", "Validation Error",
                        MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                // Update configuration based on selection
                UpdateConfigurationFromStep1();

                // Load dynamic configuration for Step 2
                LoadStep2Configuration();

                currentStep = STEP_CONFIGURE;
                UpdateWizardUI();
            }
            else if (currentStep == STEP_CONFIGURE)
            {
                // Validate configuration
                if (!ValidateStep2())
                {
                    return; // Validation error already shown
                }

                // Update configuration from Step 2 inputs
                UpdateConfigurationFromStep2();

                // Load preview in Step 3
                await LoadStep3PreviewAsync();

                currentStep = STEP_PREVIEW;
                UpdateWizardUI();
            }
        }

        /// <summary>
        /// Back button - go to previous step
        /// </summary>
        private void btnBack_Click(object sender, EventArgs e)
        {
            if (currentStep > STEP_SELECT_TYPE)
            {
                currentStep--;
                UpdateWizardUI();
            }
        }

        /// <summary>
        /// Generate button - apply template to project
        /// </summary>
        private async void btnGenerate_Click(object sender, EventArgs e)
        {
            try
            {
                btnGenerate.Enabled = false;
                Cursor = Cursors.WaitCursor;

                // Apply current filters from Step 3
                UpdateFiltersFromStep3();

                // Load template with filters
                TemplateResult result = await templateManager.LoadTemplateAsync(currentConfig, currentFilters);

                // Apply to MS Project
                var app = Globals.ThisAddIn.Application;
                templateManager.ApplyToProject(app, result);

                // Track telemetry
                var telemetryService = Globals.ThisAddIn.TelemetryService;
                if (telemetryService != null)
                {
                    telemetryService.TrackEvent(TelemetryEventType.TemplateLoaded, new Dictionary<string, object>
                    {
                        { "template_type", currentConfig.TemplateType.ToString() },
                        { "country_code", currentConfig.CountryCode },
                        { "task_count", result.TaskCount },
                        { "filters_applied", currentFilters != null }
                    });
                }

                MessageBox.Show(
                    $"Successfully generated {result.TaskCount} tasks\n" +
                    $"Template: {currentConfig.TemplateType}\n" +
                    $"Source: {result.TemplateSource}\n" +
                    $"Estimated Duration: {result.EstimatedDuration} days",
                    "Template Generated",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);

                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"Error generating template: {ex.Message}",
                    "Generation Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
            finally
            {
                btnGenerate.Enabled = true;
                Cursor = Cursors.Default;
            }
        }

        #region Step 1: Template Type Selection

        private bool ValidateStep1()
        {
            // Check if Amendment Workflow is selected (not yet implemented)
            if (rbAmendmentWorkflow.Checked)
            {
                MessageBox.Show(
                    "Amendment workflow templates will be available in Phase 2.\n\nPlease select a different template type.",
                    "Not Yet Implemented",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);
                return false;
            }

            // At least one radio button must be selected
            return rbFullStudyTimeline.Checked || rbSiteStartup.Checked ||
                   rbSiteImplementation.Checked || rbSiteCloseout.Checked ||
                   rbStudyCloseout.Checked;
        }

        private void UpdateConfigurationFromStep1()
        {
            if (rbFullStudyTimeline.Checked)
                currentConfig.TemplateType = TemplateType.FullStudyTimeline;
            else if (rbSiteStartup.Checked)
                currentConfig.TemplateType = TemplateType.SiteStartup;
            else if (rbSiteImplementation.Checked)
                currentConfig.TemplateType = TemplateType.SiteImplementation;
            else if (rbSiteCloseout.Checked)
                currentConfig.TemplateType = TemplateType.SiteCloseout;
            else if (rbStudyCloseout.Checked)
                currentConfig.TemplateType = TemplateType.StudyCloseout;
            else if (rbAmendmentWorkflow.Checked)
                currentConfig.TemplateType = TemplateType.AmendmentWorkflow;
        }

        #endregion

        #region Step 2: Dynamic Configuration

        private void LoadStep2Configuration()
        {
            // Hide all configuration panels first
            panelFullStudyConfig.Visible = false;
            panelSiteStartupConfig.Visible = false;
            panelSiteCloseoutConfig.Visible = false;
            panelStudyCloseoutConfig.Visible = false;

            // Show appropriate panel based on template type
            switch (currentConfig.TemplateType)
            {
                case TemplateType.FullStudyTimeline:
                    panelFullStudyConfig.Visible = true;
                    LoadCountryDropdown(cmbFullStudyCountry);
                    LoadStudyPhaseDropdown();
                    LoadTherapeuticAreaDropdown();
                    break;

                case TemplateType.SiteStartup:
                    panelSiteStartupConfig.Visible = true;
                    LoadCountryDropdown(cmbSiteStartupCountry);
                    LoadSitesFromClinicalSetup(cmbSiteStartupSiteId);
                    break;

                case TemplateType.SiteImplementation:
                    // Use same UI as Site Startup (same fields: Site ID + Country)
                    panelSiteStartupConfig.Visible = true;
                    LoadCountryDropdown(cmbSiteStartupCountry);
                    LoadSitesFromClinicalSetup(cmbSiteStartupSiteId);
                    break;

                case TemplateType.SiteCloseout:
                    panelSiteCloseoutConfig.Visible = true;
                    LoadCountryDropdown(cmbSiteCloseoutCountry);
                    LoadSitesFromClinicalSetup(cmbSiteCloseoutSiteId);
                    break;

                case TemplateType.StudyCloseout:
                    panelStudyCloseoutConfig.Visible = true;
                    // Study closeout has no configuration - just informational text
                    break;

                case TemplateType.AmendmentWorkflow:
                    MessageBox.Show(
                        "Amendment workflow templates will be available in Phase 2.",
                        "Not Yet Implemented",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                    break;
            }
        }

        private void LoadCountryDropdown(ComboBox cmb)
        {
            var countries = new List<string>
            {
                "USA", "CAN", "GBR", "DEU", "FRA", "ITA", "ESP", "NLD", "BEL", "CHE",
                "AUS", "JPN", "KOR", "CHN", "IND", "BRA", "MEX", "ARG", "RUS", "POL",
                "SWE", "DNK", "NOR"
            };

            cmb.Items.Clear();
            cmb.Items.AddRange(countries.ToArray());
            cmb.SelectedIndex = 0; // Default to USA
        }

        private void LoadStudyPhaseDropdown()
        {
            var phases = new List<string>
            {
                "Phase I", "Phase II", "Phase III", "Phase IV"
            };

            cmbStudyPhase.Items.Clear();
            cmbStudyPhase.Items.AddRange(phases.ToArray());
            cmbStudyPhase.SelectedIndex = 0;
        }

        private void LoadTherapeuticAreaDropdown()
        {
            var areas = new List<string>
            {
                "Oncology", "Cardiology", "Neurology", "Infectious Disease",
                "Immunology", "Metabolic Disorders", "Respiratory", "Dermatology"
            };

            cmbTherapeuticArea.Items.Clear();
            cmbTherapeuticArea.Items.AddRange(areas.ToArray());
            cmbTherapeuticArea.SelectedIndex = 0;
        }

        /// <summary>
        /// Load sites from Clinical Setup into combo box
        /// Allows manual typing if user doesn't manage sites
        /// Shows helpful prompt if no sites are configured
        /// </summary>
        private void LoadSitesFromClinicalSetup(ComboBox cmbSiteId)
        {
            try
            {
                cmbSiteId.Items.Clear();
                bool hasSites = false;

                // Try to load sites from Clinical Setup
                var project = Globals.ThisAddIn.Application.ActiveProject;
                if (project != null)
                {
                    var metadataManager = new Services.ClinicalMetadataManager();
                    var clinicalMetadata = metadataManager.LoadMetadata(project);

                    if (clinicalMetadata != null && clinicalMetadata.sites != null && clinicalMetadata.sites.Count > 0)
                    {
                        hasSites = true;

                        // Add separator hint
                        cmbSiteId.Items.Add("──── Sites from Clinical Setup ────");

                        // Add sites with helpful display format
                        foreach (var site in clinicalMetadata.sites)
                        {
                            string displayText = $"{site.id} ({site.country}, {site.principal_investigator})";
                            cmbSiteId.Items.Add(new SiteComboItem
                            {
                                SiteId = site.id,
                                Country = site.country,
                                PI = site.principal_investigator,
                                DisplayText = displayText
                            });
                        }

                        // Add separator
                        cmbSiteId.Items.Add("──────────────────────────────────");
                    }
                }

                // Show helpful message if no sites configured
                if (!hasSites)
                {
                    // First time setup hint
                    var result = MessageBox.Show(
                        "No sites found in Clinical Setup.\n\n" +
                        "Would you like to configure your sites first?\n\n" +
                        "• Recommended: Click 'Yes' to open Clinical Setup and add your sites\n" +
                        "• Or click 'No' to manually enter a Site ID",
                        "Clinical Setup",
                        MessageBoxButtons.YesNo,
                        MessageBoxIcon.Question);

                    if (result == DialogResult.Yes)
                    {
                        // Open Clinical Setup
                        var clinicalSetupForm = new ClinicalSetupForm();
                        if (clinicalSetupForm.ShowDialog() == DialogResult.OK)
                        {
                            // Reload sites after Clinical Setup is closed
                            LoadSitesFromClinicalSetup(cmbSiteId);
                            return;
                        }
                    }
                }

                // Add hint for manual entry
                cmbSiteId.Items.Add("(or type custom Site ID)");

                // Set placeholder text
                if (cmbSiteId.Items.Count > 0)
                {
                    cmbSiteId.SelectedIndex = -1; // No selection
                    cmbSiteId.Text = hasSites ? "" : "SITE-001"; // Empty if sites exist, default if not
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading sites from Clinical Setup: {ex.Message}");
                // Continue with manual entry if Clinical Setup fails
                cmbSiteId.Text = "SITE-001";
            }
        }

        /// <summary>
        /// Helper class for site combo box items
        /// </summary>
        private class SiteComboItem
        {
            public string SiteId { get; set; }
            public string Country { get; set; }
            public string PI { get; set; }
            public string DisplayText { get; set; }

            public override string ToString()
            {
                return DisplayText;
            }
        }

        /// <summary>
        /// Auto-fill country when site is selected from Clinical Setup
        /// </summary>
        private void cmbSiteStartupSiteId_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (cmbSiteStartupSiteId.SelectedItem is SiteComboItem siteItem)
            {
                // Auto-fill country
                int countryIndex = cmbSiteStartupCountry.Items.IndexOf(siteItem.Country);
                if (countryIndex >= 0)
                {
                    cmbSiteStartupCountry.SelectedIndex = countryIndex;
                }
            }
        }

        /// <summary>
        /// Auto-fill country when site is selected from Clinical Setup
        /// </summary>
        private void cmbSiteCloseoutSiteId_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (cmbSiteCloseoutSiteId.SelectedItem is SiteComboItem siteItem)
            {
                // Auto-fill country
                int countryIndex = cmbSiteCloseoutCountry.Items.IndexOf(siteItem.Country);
                if (countryIndex >= 0)
                {
                    cmbSiteCloseoutCountry.SelectedIndex = countryIndex;
                }
            }
        }

        private bool ValidateStep2()
        {
            switch (currentConfig.TemplateType)
            {
                case TemplateType.FullStudyTimeline:
                    if (cmbFullStudyCountry.SelectedIndex < 0)
                    {
                        MessageBox.Show("Please select a country.", "Validation Error",
                            MessageBoxButtons.OK, MessageBoxIcon.Warning);
                        return false;
                    }
                    if (cmbStudyPhase.SelectedIndex < 0)
                    {
                        MessageBox.Show("Please select a study phase.", "Validation Error",
                            MessageBoxButtons.OK, MessageBoxIcon.Warning);
                        return false;
                    }
                    if (cmbTherapeuticArea.SelectedIndex < 0)
                    {
                        MessageBox.Show("Please select a therapeutic area.", "Validation Error",
                            MessageBoxButtons.OK, MessageBoxIcon.Warning);
                        return false;
                    }
                    return true;

                case TemplateType.SiteStartup:
                case TemplateType.SiteImplementation:
                    if (string.IsNullOrWhiteSpace(cmbSiteStartupSiteId.Text))
                    {
                        MessageBox.Show("Please enter a Site ID.", "Validation Error",
                            MessageBoxButtons.OK, MessageBoxIcon.Warning);
                        return false;
                    }
                    if (cmbSiteStartupCountry.SelectedIndex < 0)
                    {
                        MessageBox.Show("Please select a country.", "Validation Error",
                            MessageBoxButtons.OK, MessageBoxIcon.Warning);
                        return false;
                    }
                    return true;

                case TemplateType.SiteCloseout:
                    if (string.IsNullOrWhiteSpace(cmbSiteCloseoutSiteId.Text))
                    {
                        MessageBox.Show("Please enter a Site ID.", "Validation Error",
                            MessageBoxButtons.OK, MessageBoxIcon.Warning);
                        return false;
                    }
                    if (cmbSiteCloseoutCountry.SelectedIndex < 0)
                    {
                        MessageBox.Show("Please select a country.", "Validation Error",
                            MessageBoxButtons.OK, MessageBoxIcon.Warning);
                        return false;
                    }
                    return true;

                case TemplateType.StudyCloseout:
                    // No validation needed
                    return true;

                case TemplateType.AmendmentWorkflow:
                    // Should never reach here due to Step 1 validation
                    MessageBox.Show(
                        "Amendment workflow templates are not yet implemented.",
                        "Not Yet Implemented",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Warning);
                    return false;

                default:
                    MessageBox.Show(
                        "Unknown template type selected.",
                        "Validation Error",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Error);
                    return false;
            }
        }

        /// <summary>
        /// Extract Site ID from combo box (handles both selected items and manual entry)
        /// </summary>
        private string GetSiteIdFromComboBox(ComboBox cmbSiteId)
        {
            // If user selected a SiteComboItem, extract just the ID
            if (cmbSiteId.SelectedItem is SiteComboItem siteItem)
            {
                return siteItem.SiteId;
            }

            // Otherwise, use the text they typed (manual entry)
            return cmbSiteId.Text.Trim();
        }

        private void UpdateConfigurationFromStep2()
        {
            switch (currentConfig.TemplateType)
            {
                case TemplateType.FullStudyTimeline:
                    currentConfig.CountryCode = cmbFullStudyCountry.SelectedItem?.ToString() ?? "USA";
                    currentConfig.StudyPhase = cmbStudyPhase.SelectedItem?.ToString() ?? "Phase I";
                    currentConfig.TherapeuticArea = cmbTherapeuticArea.SelectedItem?.ToString() ?? "Oncology";
                    break;

                case TemplateType.SiteStartup:
                case TemplateType.SiteImplementation:
                    currentConfig.SiteId = GetSiteIdFromComboBox(cmbSiteStartupSiteId);
                    currentConfig.CountryCode = cmbSiteStartupCountry.SelectedItem?.ToString() ?? "USA";
                    break;

                case TemplateType.SiteCloseout:
                    currentConfig.SiteId = GetSiteIdFromComboBox(cmbSiteCloseoutSiteId);
                    currentConfig.CountryCode = cmbSiteCloseoutCountry.SelectedItem?.ToString() ?? "USA";
                    break;

                case TemplateType.StudyCloseout:
                    // No configuration needed
                    break;
            }
        }

        #endregion

        #region Step 3: Preview & Filter

        private async System.Threading.Tasks.Task LoadStep3PreviewAsync()
        {
            try
            {
                Cursor = Cursors.WaitCursor;
                lblPreviewStatus.Text = "Loading preview...";

                // Use PreviewTasks for synchronous preview (library templates only)
                // API templates will need different handling
                if (currentConfig.TemplateType == TemplateType.FullStudyTimeline)
                {
                    // Load full result for API templates
                    previewResult = await templateManager.LoadTemplateAsync(currentConfig, null);
                    lblPreviewTaskCount.Text = $"{previewResult.TaskCount} tasks";
                    lblPreviewDuration.Text = $"{previewResult.EstimatedDuration} days";
                    lblPreviewSource.Text = previewResult.TemplateSource;

                    // For API templates, convert to simplified preview
                    var simplifiedTasks = new System.Collections.Generic.List<TemplateTask>();
                    foreach (var apiTask in previewResult.Timeline.tasks)
                    {
                        simplifiedTasks.Add(new TemplateTask
                        {
                            task_id = apiTask.id,
                            name = apiTask.name,
                            duration_days = apiTask.duration_days,
                            category = apiTask.category,
                            is_mandatory = apiTask.is_mandatory,
                            phase_type = apiTask.phase
                        });
                    }
                    LoadTaskListPreview(simplifiedTasks);
                    LoadFilterCheckboxes(simplifiedTasks);
                }
                else
                {
                    // For library templates, use PreviewTasks
                    var tasks = templateManager.PreviewTasks(currentConfig, null);
                    lblPreviewTaskCount.Text = $"{tasks.Count} tasks";
                    lblPreviewSource.Text = "Library";
                    LoadTaskListPreview(tasks);
                    LoadFilterCheckboxes(tasks);
                }

                lblPreviewStatus.Text = "Preview loaded";
            }
            catch (Exception ex)
            {
                lblPreviewStatus.Text = "Error loading preview";
                MessageBox.Show(
                    $"Error loading preview: {ex.Message}",
                    "Preview Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
            finally
            {
                Cursor = Cursors.Default;
            }
        }

        private void LoadTaskListPreview(List<TemplateTask> tasks)
        {
            dgvTaskPreview.Rows.Clear();

            int displayLimit = Math.Min(tasks.Count, 100); // Limit to 100 for performance
            for (int i = 0; i < displayLimit; i++)
            {
                var task = tasks[i];
                dgvTaskPreview.Rows.Add(
                    task.name,
                    task.duration_days,
                    task.category,
                    task.is_mandatory ? "Yes" : "No"
                );
            }

            if (tasks.Count > displayLimit)
            {
                lblPreviewStatus.Text = $"Showing {displayLimit} of {tasks.Count} tasks";
            }
        }

        private void LoadFilterCheckboxes(List<TemplateTask> tasks)
        {
            // Load categories
            var categories = tasks.Select(t => t.category).Distinct().Where(c => !string.IsNullOrEmpty(c)).ToList();
            clbCategories.Items.Clear();
            foreach (var category in categories)
            {
                clbCategories.Items.Add(category, true); // All checked by default
            }

            // Set include optional checkbox
            chkIncludeOptional.Checked = true;
        }

        private void UpdateFiltersFromStep3()
        {
            // Update filter options based on Step 3 selections
            currentFilters.IncludeOptional = chkIncludeOptional.Checked;

            // Get selected categories
            currentFilters.IncludedCategories.Clear();
            foreach (object item in clbCategories.CheckedItems)
            {
                currentFilters.IncludedCategories.Add(item.ToString());
            }

            // If all categories are selected, clear the list (no filtering)
            if (clbCategories.CheckedItems.Count == clbCategories.Items.Count)
            {
                currentFilters.IncludedCategories.Clear();
            }
        }

        private async void chkIncludeOptional_CheckedChanged(object sender, EventArgs e)
        {
            await RefreshPreviewWithFiltersAsync();
        }

        private async void clbCategories_ItemCheck(object sender, ItemCheckEventArgs e)
        {
            // ItemCheck fires before the checked state changes, so we need to delay
            BeginInvoke(new Action(async () => await RefreshPreviewWithFiltersAsync()));
        }

        private async System.Threading.Tasks.Task RefreshPreviewWithFiltersAsync()
        {
            if (previewResult == null) return;

            UpdateFiltersFromStep3();

            // Note: Filtering on already-loaded preview not fully implemented
            // This is a placeholder - full implementation would reload with filters
            await LoadStep3PreviewAsync();
        }

        #endregion

        private void btnCancel_Click(object sender, EventArgs e)
        {
            this.DialogResult = DialogResult.Cancel;
            this.Close();
        }
    }
}
