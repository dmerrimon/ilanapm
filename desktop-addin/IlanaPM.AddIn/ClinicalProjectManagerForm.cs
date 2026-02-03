using IlanaPM.AddIn.Models;
using IlanaPM.AddIn.Services;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Windows.Forms;
using MSProject = Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn
{
    /// <summary>
    /// Clinical Project Manager - 5-Step Unified Wizard
    /// Replaces separate Clinical Setup and Template Manager forms
    /// </summary>
    public partial class ClinicalProjectManagerForm : Form
    {
        private MSProject.Application msProjectApp;
        private ClinicalProjectConfiguration config;
        private int currentStep;
        private const int TOTAL_STEPS = 5;

        // UI Controls for Step 2 tabs (added programmatically)
        private TabControl tabStep2;
        private TabPage tabSites, tabAmendments, tabCohorts;
        private DataGridView dgvAmendments;
        private Button btnAddAmendment, btnEditAmendment, btnRemoveAmendment;
        private DataGridView dgvCohorts;
        private Button btnAddCohort, btnEditCohort, btnRemoveCohort;

        public ClinicalProjectManagerForm(MSProject.Application app)
        {
            InitializeComponent();
            this.msProjectApp = app;
            this.currentStep = 1;
            this.config = new ClinicalProjectConfiguration();

            // Initialize Step 2 with tabs for Sites, Amendments, Cohorts
            InitializeStep2Tabs();
        }

        private void InitializeStep2Tabs()
        {
            // Create TabControl to hold Sites, Amendments, and Cohorts tabs
            tabStep2 = new TabControl
            {
                Location = new Point(0, 30),
                Size = new Size(560, 365),
                Dock = DockStyle.None
            };

            // Create three tab pages
            tabSites = new TabPage("Sites");
            tabAmendments = new TabPage("Amendments");
            tabCohorts = new TabPage("Cohorts");

            tabStep2.TabPages.Add(tabSites);
            tabStep2.TabPages.Add(tabAmendments);
            tabStep2.TabPages.Add(tabCohorts);

            // SITES TAB: Move existing controls from designer
            // The designer already created these controls and added them to pnlStep2
            // We need to move them to the Sites tab
            var sitesControlsToMove = new List<Control>();
            foreach (Control ctrl in pnlStep2.Controls)
            {
                if (ctrl != lblStep2Title && ctrl != tabStep2) // Keep title in panel, don't move TabControl
                {
                    sitesControlsToMove.Add(ctrl);
                }
            }

            foreach (var ctrl in sitesControlsToMove)
            {
                pnlStep2.Controls.Remove(ctrl);
                tabSites.Controls.Add(ctrl);
            }

            // Now adjust positions AFTER adding to tab
            // DataGridView: position at top
            dgvSites.Location = new Point(0, 0);
            dgvSites.Size = new Size(540, 280);

            // Buttons: position at Y=295 (280 + 15 spacing) to be visible
            int buttonY = 295;
            btnAddSite.Location = new Point(0, buttonY);
            btnEditSite.Location = new Point(110, buttonY);
            btnRemoveSite.Location = new Point(220, buttonY);
            btnImportSites.Location = new Point(380, buttonY);

            // AMENDMENTS TAB: Create new controls
            dgvAmendments = new DataGridView
            {
                Location = new Point(10, 10),
                Size = new Size(520, 280),
                Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right,
                AllowUserToAddRows = false,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect,
                MultiSelect = false,
                ReadOnly = true,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
            };

            btnAddAmendment = new Button
            {
                Text = "Add Amendment",
                Location = new Point(10, 300),
                Size = new Size(120, 30),
                Anchor = AnchorStyles.Bottom | AnchorStyles.Left
            };
            btnEditAmendment = new Button
            {
                Text = "Edit Amendment",
                Location = new Point(140, 300),
                Size = new Size(120, 30),
                Anchor = AnchorStyles.Bottom | AnchorStyles.Left
            };
            btnRemoveAmendment = new Button
            {
                Text = "Remove Amendment",
                Location = new Point(270, 300),
                Size = new Size(140, 30),
                Anchor = AnchorStyles.Bottom | AnchorStyles.Left
            };

            btnAddAmendment.Click += btnAddAmendment_Click;
            btnEditAmendment.Click += btnEditAmendment_Click;
            btnRemoveAmendment.Click += btnRemoveAmendment_Click;

            tabAmendments.Controls.Add(dgvAmendments);
            tabAmendments.Controls.Add(btnAddAmendment);
            tabAmendments.Controls.Add(btnEditAmendment);
            tabAmendments.Controls.Add(btnRemoveAmendment);

            // COHORTS TAB: Create new controls
            dgvCohorts = new DataGridView
            {
                Location = new Point(10, 10),
                Size = new Size(520, 280),
                Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right,
                AllowUserToAddRows = false,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect,
                MultiSelect = false,
                ReadOnly = true,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill
            };

            btnAddCohort = new Button
            {
                Text = "Add Cohort",
                Location = new Point(10, 300),
                Size = new Size(120, 30),
                Anchor = AnchorStyles.Bottom | AnchorStyles.Left
            };
            btnEditCohort = new Button
            {
                Text = "Edit Cohort",
                Location = new Point(140, 300),
                Size = new Size(120, 30),
                Anchor = AnchorStyles.Bottom | AnchorStyles.Left
            };
            btnRemoveCohort = new Button
            {
                Text = "Remove Cohort",
                Location = new Point(270, 300),
                Size = new Size(140, 30),
                Anchor = AnchorStyles.Bottom | AnchorStyles.Left
            };

            btnAddCohort.Click += btnAddCohort_Click;
            btnEditCohort.Click += btnEditCohort_Click;
            btnRemoveCohort.Click += btnRemoveCohort_Click;

            tabCohorts.Controls.Add(dgvCohorts);
            tabCohorts.Controls.Add(btnAddCohort);
            tabCohorts.Controls.Add(btnEditCohort);
            tabCohorts.Controls.Add(btnRemoveCohort);

            // Add TabControl to pnlStep2
            pnlStep2.Controls.Add(tabStep2);
        }

        private void ClinicalProjectManagerForm_Load(object sender, EventArgs e)
        {
            try
            {
                // Load existing configuration from project (if any)
                config = ClinicalProjectConfiguration.LoadFromProject(msProjectApp);

                if (config.IsEmpty)
                {
                    MessageBox.Show(
                        "Starting new Clinical Project configuration.\n\n" +
                        "This wizard will guide you through:\n" +
                        "1. Study setup\n" +
                        "2. Site management\n" +
                        "3. Template selection\n" +
                        "4. Configuration\n" +
                        "5. Preview & generate",
                        "Clinical Project Manager",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                }
                else
                {
                    // Load existing data into Step 1
                    txtStudyName.Text = config.StudyName;
                    if (!string.IsNullOrEmpty(config.StudyPhase))
                        cmbStudyPhase.SelectedItem = config.StudyPhase;
                    if (!string.IsNullOrEmpty(config.TherapeuticArea))
                        cmbTherapeuticArea.SelectedItem = config.TherapeuticArea;

                    // Load countries
                    if (config.Countries != null)
                    {
                        foreach (string country in config.Countries)
                        {
                            int index = lstCountries.Items.IndexOf(country);
                            if (index >= 0)
                                lstCountries.SetItemChecked(index, true);
                        }
                    }

                    // Load sites into Step 2
                    RefreshSitesGrid();
                }

                ShowStep(1);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading configuration: {ex.Message}",
                    "Load Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        #region Navigation

        private void ShowStep(int step)
        {
            currentStep = step;

            // Hide all panels
            pnlStep1.Visible = false;
            pnlStep2.Visible = false;
            pnlStep3.Visible = false;
            pnlStep4.Visible = false;
            pnlStep5.Visible = false;

            // Show current panel
            switch (step)
            {
                case 1:
                    pnlStep1.Visible = true;
                    lblStepIndicator.Text = "Step 1 of 5: Study Configuration";
                    break;
                case 2:
                    pnlStep2.Visible = true;
                    lblStepIndicator.Text = "Step 2 of 5: Sites, Amendments & Cohorts";
                    RefreshSitesGrid();
                    RefreshAmendmentsGrid();
                    RefreshCohortsGrid();
                    break;
                case 3:
                    pnlStep3.Visible = true;
                    lblStepIndicator.Text = "Step 3 of 5: Template Selection";
                    break;
                case 4:
                    pnlStep4.Visible = true;
                    lblStepIndicator.Text = "Step 4 of 5: Configuration & Filters";
                    LoadStep4Configuration();
                    break;
                case 5:
                    pnlStep5.Visible = true;
                    lblStepIndicator.Text = "Step 5 of 5: Preview & Generate";
                    LoadStep5Preview();
                    break;
            }

            // Update button states
            btnBack.Enabled = (step > 1);
            btnNext.Visible = (step < 5);
            btnGenerate.Visible = (step == 5);
        }

        private void btnNext_Click(object sender, EventArgs e)
        {
            // Validate current step before moving forward
            if (!ValidateCurrentStep())
                return;

            // Save data from current step
            SaveCurrentStepData();

            // Move to next step
            if (currentStep < TOTAL_STEPS)
            {
                ShowStep(currentStep + 1);
            }
        }

        private void btnBack_Click(object sender, EventArgs e)
        {
            // Save current step data
            SaveCurrentStepData();

            // Move to previous step
            if (currentStep > 1)
            {
                ShowStep(currentStep - 1);
            }
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            var result = MessageBox.Show(
                "Are you sure you want to cancel?\n\n" +
                "Your progress will be saved for next time.",
                "Confirm Cancel",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question);

            if (result == DialogResult.Yes)
            {
                try
                {
                    // Save progress before closing
                    SaveCurrentStepData();
                    config.SaveToProject(msProjectApp);
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Error saving on cancel: {ex.Message}");
                }

                this.DialogResult = DialogResult.Cancel;
                this.Close();
            }
        }

        #endregion

        #region Validation

        private bool ValidateCurrentStep()
        {
            switch (currentStep)
            {
                case 1:
                    if (string.IsNullOrWhiteSpace(txtStudyName.Text))
                    {
                        MessageBox.Show("Please enter a Study Name.", "Validation",
                            MessageBoxButtons.OK, MessageBoxIcon.Warning);
                        txtStudyName.Focus();
                        return false;
                    }
                    return true;

                case 2:
                    // Sites are optional, but warn if none
                    if (config.Sites == null || config.Sites.Count == 0)
                    {
                        var result = MessageBox.Show(
                            "No sites have been added.\n\n" +
                            "You can still generate Full Study Timeline or Study Closeout templates, " +
                            "but site-specific templates require at least one site.\n\n" +
                            "Continue without sites?",
                            "No Sites",
                            MessageBoxButtons.YesNo,
                            MessageBoxIcon.Question);
                        return result == DialogResult.Yes;
                    }
                    return true;

                case 3:
                    if (!config.Templates.HasAnySelections)
                    {
                        MessageBox.Show(
                            "Please select at least one template type to generate.",
                            "Validation",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Warning);
                        return false;
                    }
                    return true;

                case 4:
                    // Validate that site-specific templates have sites selected
                    // Check the actual CheckedListBox controls, not the config (which isn't saved yet)
                    if (config.Templates.GenerateSiteStartup && clbSitesForStartup.CheckedItems.Count == 0)
                    {
                        MessageBox.Show(
                            "You selected Site Startup but didn't select any sites.\n\n" +
                            "Please select at least one site or uncheck Site Startup.",
                            "Validation",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Warning);
                        return false;
                    }
                    if (config.Templates.GenerateSiteImplementation && clbSitesForImplementation.CheckedItems.Count == 0)
                    {
                        MessageBox.Show(
                            "You selected Site Implementation but didn't select any sites.",
                            "Validation",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Warning);
                        return false;
                    }
                    if (config.Templates.GenerateSiteCloseout && clbSitesForCloseout.CheckedItems.Count == 0)
                    {
                        MessageBox.Show(
                            "You selected Site Closeout but didn't select any sites.",
                            "Validation",
                            MessageBoxButtons.OK,
                            MessageBoxIcon.Warning);
                        return false;
                    }
                    return true;

                case 5:
                    return true;

                default:
                    return true;
            }
        }

        #endregion

        #region Save Step Data

        private void SaveCurrentStepData()
        {
            switch (currentStep)
            {
                case 1:
                    SaveStep1Data();
                    break;
                case 2:
                    // Sites are already in config.Sites from grid operations
                    break;
                case 3:
                    SaveStep3Data();
                    break;
                case 4:
                    SaveStep4Data();
                    break;
                case 5:
                    // Preview step - no data to save
                    break;
            }
        }

        private void SaveStep1Data()
        {
            config.StudyName = txtStudyName.Text.Trim();
            config.StudyPhase = cmbStudyPhase.SelectedItem?.ToString() ?? "";
            config.TherapeuticArea = cmbTherapeuticArea.SelectedItem?.ToString() ?? "";

            // Save selected countries
            config.Countries.Clear();
            foreach (var item in lstCountries.CheckedItems)
            {
                config.Countries.Add(item.ToString());
            }
        }

        private void SaveStep3Data()
        {
            config.Templates.GenerateFullStudyTimeline = chkFullStudyTimeline.Checked;
            config.Templates.GenerateSiteStartup = chkSiteStartup.Checked;
            config.Templates.GenerateSiteImplementation = chkSiteImplementation.Checked;
            config.Templates.GenerateSiteCloseout = chkSiteCloseout.Checked;
            config.Templates.GenerateStudyCloseout = chkStudyCloseout.Checked;
        }

        private void SaveStep4Data()
        {
            // Save site selections for each template type
            config.Templates.SitesForStartup.Clear();
            foreach (var item in clbSitesForStartup.CheckedItems)
            {
                var siteConfig = item as SiteConfiguration;
                if (siteConfig != null)
                    config.Templates.SitesForStartup.Add(siteConfig.SiteId);
            }

            config.Templates.SitesForImplementation.Clear();
            foreach (var item in clbSitesForImplementation.CheckedItems)
            {
                var siteConfig = item as SiteConfiguration;
                if (siteConfig != null)
                    config.Templates.SitesForImplementation.Add(siteConfig.SiteId);
            }

            config.Templates.SitesForCloseout.Clear();
            foreach (var item in clbSitesForCloseout.CheckedItems)
            {
                var siteConfig = item as SiteConfiguration;
                if (siteConfig != null)
                    config.Templates.SitesForCloseout.Add(siteConfig.SiteId);
            }

            // Save filter options
            config.Filters.IncludeOptional = chkIncludeOptional.Checked;
        }

        #endregion

        #region Step 2: Site Management

        private void RefreshSitesGrid()
        {
            dgvSites.DataSource = null;

            if (config.Sites == null || config.Sites.Count == 0)
            {
                dgvSites.Columns.Clear();
                return;
            }

            var dt = new DataTable();
            dt.Columns.Add("Site ID", typeof(string));
            dt.Columns.Add("Site Name", typeof(string));
            dt.Columns.Add("Country", typeof(string));
            dt.Columns.Add("PI", typeof(string));
            dt.Columns.Add("Status", typeof(string));

            foreach (var site in config.Sites)
            {
                dt.Rows.Add(
                    site.SiteId,
                    site.SiteName,
                    site.CountryCode,
                    site.PrincipalInvestigator,
                    site.Status
                );
            }

            dgvSites.DataSource = dt;
        }

        private void btnAddSite_Click(object sender, EventArgs e)
        {
            // Create inline site add dialog
            var dialog = CreateSiteDialog(null);
            if (dialog.ShowDialog() == DialogResult.OK)
            {
                // Get values from dialog
                var siteId = dialog.Controls["txtSiteId"].Text;
                var siteName = dialog.Controls["txtSiteName"].Text;
                var country = dialog.Controls["txtCountry"].Text;
                var status = ((ComboBox)dialog.Controls["cmbStatus"]).SelectedItem?.ToString() ?? "Pending";
                var pi = dialog.Controls["txtPI"].Text;
                var irbDateStr = dialog.Controls["dtpIRB"].Text;

                // Create new site
                var newSite = new SiteConfiguration
                {
                    SiteId = siteId,
                    SiteName = siteName,
                    CountryCode = country,
                    CountryName = country,
                    Status = status,
                    PrincipalInvestigator = pi,
                    IrbApprovalDate = DateTime.TryParse(irbDateStr, out DateTime irbDate) ? irbDate : (DateTime?)null
                };

                config.Sites.Add(newSite);
                RefreshSitesGrid();
            }
        }

        private void btnEditSite_Click(object sender, EventArgs e)
        {
            if (dgvSites.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select a site to edit.", "Edit Site",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            int rowIndex = dgvSites.SelectedRows[0].Index;
            if (rowIndex >= 0 && rowIndex < config.Sites.Count)
            {
                var site = config.Sites[rowIndex];

                // Create dialog with existing site data
                var dialog = CreateSiteDialog(site);
                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    // Update site with new values
                    site.SiteId = dialog.Controls["txtSiteId"].Text;
                    site.SiteName = dialog.Controls["txtSiteName"].Text;
                    site.CountryCode = dialog.Controls["txtCountry"].Text;
                    site.CountryName = dialog.Controls["txtCountry"].Text;
                    site.Status = ((ComboBox)dialog.Controls["cmbStatus"]).SelectedItem?.ToString() ?? "Pending";
                    site.PrincipalInvestigator = dialog.Controls["txtPI"].Text;

                    var dtpIRB = (DateTimePicker)dialog.Controls["dtpIRB"];
                    site.IrbApprovalDate = dtpIRB.Checked ? dtpIRB.Value : (DateTime?)null;

                    RefreshSitesGrid();
                }
            }
        }

        private void btnRemoveSite_Click(object sender, EventArgs e)
        {
            if (dgvSites.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select a site to remove.", "Remove Site",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            int rowIndex = dgvSites.SelectedRows[0].Index;
            if (rowIndex >= 0 && rowIndex < config.Sites.Count)
            {
                var site = config.Sites[rowIndex];
                var result = MessageBox.Show(
                    $"Remove site '{site.SiteId}'?",
                    "Confirm Remove",
                    MessageBoxButtons.YesNo,
                    MessageBoxIcon.Question);

                if (result == DialogResult.Yes)
                {
                    config.Sites.RemoveAt(rowIndex);
                    RefreshSitesGrid();
                }
            }
        }

        private Form CreateSiteDialog(SiteConfiguration existingSite)
        {
            var dialog = new Form
            {
                Text = existingSite == null ? "Add Site" : "Edit Site",
                Width = 450,
                Height = 400,
                FormBorderStyle = FormBorderStyle.FixedDialog,
                StartPosition = FormStartPosition.CenterParent,
                MaximizeBox = false,
                MinimizeBox = false
            };

            int yPos = 20;

            // Site ID
            var lblSiteId = new Label { Text = "Site ID:", Left = 20, Top = yPos, Width = 120 };
            var txtSiteId = new TextBox { Name = "txtSiteId", Left = 150, Top = yPos, Width = 250, Text = existingSite?.SiteId ?? $"SITE-{config.Sites.Count + 1:D3}" };
            dialog.Controls.Add(lblSiteId);
            dialog.Controls.Add(txtSiteId);
            yPos += 35;

            // Site Name
            var lblSiteName = new Label { Text = "Site Name:", Left = 20, Top = yPos, Width = 120 };
            var txtSiteName = new TextBox { Name = "txtSiteName", Left = 150, Top = yPos, Width = 250, Text = existingSite?.SiteName ?? "" };
            dialog.Controls.Add(lblSiteName);
            dialog.Controls.Add(txtSiteName);
            yPos += 35;

            // Country
            var lblCountry = new Label { Text = "Country:", Left = 20, Top = yPos, Width = 120 };
            var txtCountry = new TextBox { Name = "txtCountry", Left = 150, Top = yPos, Width = 250, Text = existingSite?.CountryCode ?? "USA" };
            dialog.Controls.Add(lblCountry);
            dialog.Controls.Add(txtCountry);
            yPos += 35;

            // Status
            var lblStatus = new Label { Text = "Status:", Left = 20, Top = yPos, Width = 120 };
            var cmbStatus = new ComboBox { Name = "cmbStatus", Left = 150, Top = yPos, Width = 250, DropDownStyle = ComboBoxStyle.DropDownList };
            cmbStatus.Items.AddRange(new object[] { "Pending", "Active", "Closed", "On Hold" });
            cmbStatus.SelectedItem = existingSite?.Status ?? "Pending";
            dialog.Controls.Add(lblStatus);
            dialog.Controls.Add(cmbStatus);
            yPos += 35;

            // Principal Investigator
            var lblPI = new Label { Text = "Principal Investigator:", Left = 20, Top = yPos, Width = 120 };
            var txtPI = new TextBox { Name = "txtPI", Left = 150, Top = yPos, Width = 250, Text = existingSite?.PrincipalInvestigator ?? "" };
            dialog.Controls.Add(lblPI);
            dialog.Controls.Add(txtPI);
            yPos += 35;

            // IRB Approval Date
            var lblIRB = new Label { Text = "IRB Approval Date:", Left = 20, Top = yPos, Width = 120 };
            var dtpIRB = new DateTimePicker { Name = "dtpIRB", Left = 150, Top = yPos, Width = 250, Format = DateTimePickerFormat.Short, ShowCheckBox = true, Checked = existingSite?.IrbApprovalDate.HasValue ?? false };
            if (existingSite?.IrbApprovalDate.HasValue == true)
                dtpIRB.Value = existingSite.IrbApprovalDate.Value;
            dialog.Controls.Add(lblIRB);
            dialog.Controls.Add(dtpIRB);
            yPos += 50;

            // OK Button
            var btnOK = new Button { Text = "OK", Left = 230, Top = yPos, Width = 80, DialogResult = DialogResult.OK };
            dialog.Controls.Add(btnOK);
            dialog.AcceptButton = btnOK;

            // Cancel Button
            var btnCancel = new Button { Text = "Cancel", Left = 320, Top = yPos, Width = 80, DialogResult = DialogResult.Cancel };
            dialog.Controls.Add(btnCancel);
            dialog.CancelButton = btnCancel;

            return dialog;
        }

        private void btnImportSites_Click(object sender, EventArgs e)
        {
            try
            {
                // Load legacy ClinicalMetadata from project
                var metadataManager = new ClinicalMetadataManager();
                var legacyMetadata = metadataManager.LoadMetadata(msProjectApp.ActiveProject);

                if (legacyMetadata == null || legacyMetadata.sites == null || legacyMetadata.sites.Count == 0)
                {
                    MessageBox.Show(
                        "No sites found in legacy Clinical Setup data.\n\n" +
                        "Please use the 'Add Site' button to add sites manually.\n\n" +
                        "Note: The legacy Clinical Setup form has been replaced by this unified wizard.",
                        "No Sites Found",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                    return;
                }

                // Import sites
                int imported = 0;
                foreach (var legacySite in legacyMetadata.sites)
                {
                    // Check if site already exists
                    if (!config.Sites.Any(s => s.SiteId == legacySite.id))
                    {
                        config.Sites.Add(SiteConfiguration.FromSite(legacySite));
                        imported++;
                    }
                }

                MessageBox.Show(
                    $"Imported {imported} site(s) from Clinical Setup.",
                    "Import Complete",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);

                RefreshSitesGrid();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error importing sites: {ex.Message}",
                    "Import Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // Amendment Management

        private void RefreshAmendmentsGrid()
        {
            dgvAmendments.DataSource = null;

            var dt = new DataTable();
            dt.Columns.Add("ID", typeof(string));
            dt.Columns.Add("Number", typeof(string));
            dt.Columns.Add("Date", typeof(string));
            dt.Columns.Add("Description", typeof(string));
            dt.Columns.Add("Type", typeof(string));

            if (config.Amendments != null && config.Amendments.Count > 0)
            {
                foreach (var amendment in config.Amendments)
                {
                    dt.Rows.Add(
                        amendment.id,
                        amendment.number,
                        amendment.date.ToString("yyyy-MM-dd"),
                        amendment.description,
                        amendment.amendment_type
                    );
                }
            }

            dgvAmendments.DataSource = dt;
        }

        private void btnAddAmendment_Click(object sender, EventArgs e)
        {
            var dialog = CreateAmendmentDialog(null);
            if (dialog.ShowDialog() == DialogResult.OK)
            {
                var newAmendment = new Amendment
                {
                    id = dialog.Controls["txtAmendmentId"].Text,
                    number = dialog.Controls["txtAmendmentNumber"].Text,
                    date = ((DateTimePicker)dialog.Controls["dtpAmendmentDate"]).Value,
                    description = dialog.Controls["txtDescription"].Text,
                    amendment_type = ((ComboBox)dialog.Controls["cmbAmendmentType"]).SelectedItem?.ToString() ?? "substantial"
                };
                config.Amendments.Add(newAmendment);
                RefreshAmendmentsGrid();
            }
        }

        private void btnEditAmendment_Click(object sender, EventArgs e)
        {
            if (dgvAmendments.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select an amendment to edit.", "Edit Amendment",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            int rowIndex = dgvAmendments.SelectedRows[0].Index;
            if (rowIndex >= 0 && rowIndex < config.Amendments.Count)
            {
                var amendment = config.Amendments[rowIndex];
                var dialog = CreateAmendmentDialog(amendment);
                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    amendment.id = dialog.Controls["txtAmendmentId"].Text;
                    amendment.number = dialog.Controls["txtAmendmentNumber"].Text;
                    amendment.date = ((DateTimePicker)dialog.Controls["dtpAmendmentDate"]).Value;
                    amendment.description = dialog.Controls["txtDescription"].Text;
                    amendment.amendment_type = ((ComboBox)dialog.Controls["cmbAmendmentType"]).SelectedItem?.ToString() ?? "substantial";
                    RefreshAmendmentsGrid();
                }
            }
        }

        private void btnRemoveAmendment_Click(object sender, EventArgs e)
        {
            if (dgvAmendments.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select an amendment to remove.", "Remove Amendment",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            int rowIndex = dgvAmendments.SelectedRows[0].Index;
            if (rowIndex >= 0 && rowIndex < config.Amendments.Count)
            {
                var amendment = config.Amendments[rowIndex];
                var result = MessageBox.Show(
                    $"Remove amendment '{amendment.number}'?",
                    "Confirm Remove",
                    MessageBoxButtons.YesNo,
                    MessageBoxIcon.Question);

                if (result == DialogResult.Yes)
                {
                    config.Amendments.RemoveAt(rowIndex);
                    RefreshAmendmentsGrid();
                }
            }
        }

        private Form CreateAmendmentDialog(Amendment existingAmendment)
        {
            var dialog = new Form
            {
                Text = existingAmendment == null ? "Add Amendment" : "Edit Amendment",
                Width = 450,
                Height = 350,
                FormBorderStyle = FormBorderStyle.FixedDialog,
                StartPosition = FormStartPosition.CenterParent,
                MaximizeBox = false,
                MinimizeBox = false
            };

            int yPos = 20;

            // Amendment ID
            var lblId = new Label { Text = "Amendment ID:", Left = 20, Top = yPos, Width = 120 };
            var txtId = new TextBox { Name = "txtAmendmentId", Left = 150, Top = yPos, Width = 250,
                Text = existingAmendment?.id ?? $"AMD-{config.Amendments.Count + 1:D3}" };
            dialog.Controls.Add(lblId);
            dialog.Controls.Add(txtId);
            yPos += 35;

            // Amendment Number
            var lblNumber = new Label { Text = "Number:", Left = 20, Top = yPos, Width = 120 };
            var txtNumber = new TextBox { Name = "txtAmendmentNumber", Left = 150, Top = yPos, Width = 250,
                Text = existingAmendment?.number ?? $"Amendment {config.Amendments.Count + 1}" };
            dialog.Controls.Add(lblNumber);
            dialog.Controls.Add(txtNumber);
            yPos += 35;

            // Date
            var lblDate = new Label { Text = "Date:", Left = 20, Top = yPos, Width = 120 };
            var dtpDate = new DateTimePicker { Name = "dtpAmendmentDate", Left = 150, Top = yPos, Width = 250,
                Value = existingAmendment?.date ?? DateTime.Now };
            dialog.Controls.Add(lblDate);
            dialog.Controls.Add(dtpDate);
            yPos += 35;

            // Description
            var lblDesc = new Label { Text = "Description:", Left = 20, Top = yPos, Width = 120 };
            var txtDesc = new TextBox { Name = "txtDescription", Left = 150, Top = yPos, Width = 250, Height = 60,
                Multiline = true, Text = existingAmendment?.description ?? "" };
            dialog.Controls.Add(lblDesc);
            dialog.Controls.Add(txtDesc);
            yPos += 70;

            // Type
            var lblType = new Label { Text = "Type:", Left = 20, Top = yPos, Width = 120 };
            var cmbType = new ComboBox { Name = "cmbAmendmentType", Left = 150, Top = yPos, Width = 250,
                DropDownStyle = ComboBoxStyle.DropDownList };
            cmbType.Items.AddRange(new object[] { "substantial", "administrative" });
            cmbType.SelectedItem = existingAmendment?.amendment_type ?? "substantial";
            dialog.Controls.Add(lblType);
            dialog.Controls.Add(cmbType);
            yPos += 40;

            // Buttons
            var btnOk = new Button { Text = "OK", Left = 240, Top = yPos, Width = 80, DialogResult = DialogResult.OK };
            var btnCancel = new Button { Text = "Cancel", Left = 330, Top = yPos, Width = 80, DialogResult = DialogResult.Cancel };
            dialog.Controls.Add(btnOk);
            dialog.Controls.Add(btnCancel);
            dialog.AcceptButton = btnOk;
            dialog.CancelButton = btnCancel;

            return dialog;
        }

        // Cohort Management

        private void RefreshCohortsGrid()
        {
            dgvCohorts.DataSource = null;

            var dt = new DataTable();
            dt.Columns.Add("ID", typeof(string));
            dt.Columns.Add("Name", typeof(string));
            dt.Columns.Add("Target Enrollment", typeof(int));
            dt.Columns.Add("Sites", typeof(string));

            if (config.Cohorts != null && config.Cohorts.Count > 0)
            {
                foreach (var cohort in config.Cohorts)
                {
                    dt.Rows.Add(
                        cohort.id,
                        cohort.name,
                        cohort.enrollment_target,
                        cohort.participating_sites != null ? string.Join(", ", cohort.participating_sites) : ""
                    );
                }
            }

            dgvCohorts.DataSource = dt;
        }

        private void btnAddCohort_Click(object sender, EventArgs e)
        {
            var dialog = CreateCohortDialog(null);
            if (dialog.ShowDialog() == DialogResult.OK)
            {
                var newCohort = new Cohort
                {
                    id = dialog.Controls["txtCohortId"].Text,
                    name = dialog.Controls["txtCohortName"].Text,
                    enrollment_target = int.TryParse(dialog.Controls["txtEnrollmentTarget"].Text, out int target) ? target : 0
                };
                config.Cohorts.Add(newCohort);
                RefreshCohortsGrid();
            }
        }

        private void btnEditCohort_Click(object sender, EventArgs e)
        {
            if (dgvCohorts.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select a cohort to edit.", "Edit Cohort",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            int rowIndex = dgvCohorts.SelectedRows[0].Index;
            if (rowIndex >= 0 && rowIndex < config.Cohorts.Count)
            {
                var cohort = config.Cohorts[rowIndex];
                var dialog = CreateCohortDialog(cohort);
                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    cohort.id = dialog.Controls["txtCohortId"].Text;
                    cohort.name = dialog.Controls["txtCohortName"].Text;
                    cohort.enrollment_target = int.TryParse(dialog.Controls["txtEnrollmentTarget"].Text, out int target) ? target : 0;
                    RefreshCohortsGrid();
                }
            }
        }

        private void btnRemoveCohort_Click(object sender, EventArgs e)
        {
            if (dgvCohorts.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select a cohort to remove.", "Remove Cohort",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            int rowIndex = dgvCohorts.SelectedRows[0].Index;
            if (rowIndex >= 0 && rowIndex < config.Cohorts.Count)
            {
                var cohort = config.Cohorts[rowIndex];
                var result = MessageBox.Show(
                    $"Remove cohort '{cohort.name}'?",
                    "Confirm Remove",
                    MessageBoxButtons.YesNo,
                    MessageBoxIcon.Question);

                if (result == DialogResult.Yes)
                {
                    config.Cohorts.RemoveAt(rowIndex);
                    RefreshCohortsGrid();
                }
            }
        }

        private Form CreateCohortDialog(Cohort existingCohort)
        {
            var dialog = new Form
            {
                Text = existingCohort == null ? "Add Cohort" : "Edit Cohort",
                Width = 450,
                Height = 250,
                FormBorderStyle = FormBorderStyle.FixedDialog,
                StartPosition = FormStartPosition.CenterParent,
                MaximizeBox = false,
                MinimizeBox = false
            };

            int yPos = 20;

            // Cohort ID
            var lblId = new Label { Text = "Cohort ID:", Left = 20, Top = yPos, Width = 120 };
            var txtId = new TextBox { Name = "txtCohortId", Left = 150, Top = yPos, Width = 250,
                Text = existingCohort?.id ?? $"COH-{config.Cohorts.Count + 1:D3}" };
            dialog.Controls.Add(lblId);
            dialog.Controls.Add(txtId);
            yPos += 35;

            // Cohort Name
            var lblName = new Label { Text = "Name:", Left = 20, Top = yPos, Width = 120 };
            var txtName = new TextBox { Name = "txtCohortName", Left = 150, Top = yPos, Width = 250,
                Text = existingCohort?.name ?? $"Cohort {config.Cohorts.Count + 1}" };
            dialog.Controls.Add(lblName);
            dialog.Controls.Add(txtName);
            yPos += 35;

            // Enrollment Target
            var lblTarget = new Label { Text = "Target Enrollment:", Left = 20, Top = yPos, Width = 120 };
            var txtTarget = new TextBox { Name = "txtEnrollmentTarget", Left = 150, Top = yPos, Width = 250,
                Text = existingCohort?.enrollment_target.ToString() ?? "15" };
            dialog.Controls.Add(lblTarget);
            dialog.Controls.Add(txtTarget);
            yPos += 40;

            // Buttons
            var btnOk = new Button { Text = "OK", Left = 240, Top = yPos, Width = 80, DialogResult = DialogResult.OK };
            var btnCancel = new Button { Text = "Cancel", Left = 330, Top = yPos, Width = 80, DialogResult = DialogResult.Cancel };
            dialog.Controls.Add(btnOk);
            dialog.Controls.Add(btnCancel);
            dialog.AcceptButton = btnOk;
            dialog.CancelButton = btnCancel;

            return dialog;
        }

        #endregion

        #region Step 3: Template Selection

        private void TemplateCheckbox_CheckedChanged(object sender, EventArgs e)
        {
            // Just update the template selections - validation happens on Next
            SaveStep3Data();
        }

        #endregion

        #region Step 4: Configuration

        private void LoadStep4Configuration()
        {
            // Show/hide site selection groups based on Step 3 selections
            grpSiteStartup.Visible = config.Templates.GenerateSiteStartup;
            grpSiteImplementation.Visible = config.Templates.GenerateSiteImplementation;
            grpSiteCloseout.Visible = config.Templates.GenerateSiteCloseout;

            // Populate site lists
            if (config.Templates.GenerateSiteStartup)
            {
                clbSitesForStartup.Items.Clear();
                clbSitesForStartup.DisplayMember = "DisplayText";
                foreach (var site in config.Sites)
                {
                    int index = clbSitesForStartup.Items.Add(site);
                    // Auto-check if previously selected
                    if (config.Templates.SitesForStartup.Contains(site.SiteId))
                        clbSitesForStartup.SetItemChecked(index, true);
                }
            }

            if (config.Templates.GenerateSiteImplementation)
            {
                clbSitesForImplementation.Items.Clear();
                clbSitesForImplementation.DisplayMember = "DisplayText";
                foreach (var site in config.Sites)
                {
                    int index = clbSitesForImplementation.Items.Add(site);
                    if (config.Templates.SitesForImplementation.Contains(site.SiteId))
                        clbSitesForImplementation.SetItemChecked(index, true);
                }
            }

            if (config.Templates.GenerateSiteCloseout)
            {
                clbSitesForCloseout.Items.Clear();
                clbSitesForCloseout.DisplayMember = "DisplayText";
                foreach (var site in config.Sites)
                {
                    int index = clbSitesForCloseout.Items.Add(site);
                    if (config.Templates.SitesForCloseout.Contains(site.SiteId))
                        clbSitesForCloseout.SetItemChecked(index, true);
                }
            }

            // Load filter options
            chkIncludeOptional.Checked = config.Filters.IncludeOptional;
        }

        #endregion

        #region Step 5: Preview

        private void LoadStep5Preview()
        {
            // Calculate task count estimate (including cohort milestone tasks)
            int cohortCount = config.Cohorts?.Count ?? 0;
            int taskCount = config.Templates.GetEstimatedTaskCount(cohortCount);
            lblTaskCount.Text = $"{taskCount} tasks will be generated (estimated)";

            // Show summary
            string summary = config.Templates.GetSummary();
            MessageBox.Show(
                $"Ready to generate templates:\n\n{summary}\n\n" +
                $"Estimated tasks: {taskCount}\n\n" +
                "Click 'Generate' to create tasks in your MS Project file.",
                "Generation Ready",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information);

            // Load actual task preview based on selected templates
            LoadTaskPreview();
        }

        private void LoadTaskPreview()
        {
            var dt = new DataTable();
            dt.Columns.Add("Template Type", typeof(string));
            dt.Columns.Add("Site", typeof(string));
            dt.Columns.Add("Description", typeof(string));
            dt.Columns.Add("Est. Tasks", typeof(string));

            // Show summary of what will be generated
            // Note: Actual task count may vary based on country-specific regulations

            if (config.Templates.GenerateSiteStartup)
            {
                foreach (var siteId in config.Templates.SitesForStartup)
                {
                    var site = config.Sites.FirstOrDefault(s => s.SiteId == siteId);
                    string country = site?.CountryCode ?? "Unknown";
                    dt.Rows.Add("Site Startup", site?.SiteId ?? siteId,
                        $"Regulatory approval, site activation, training ({country})",
                        "~55");
                }
            }

            if (config.Templates.GenerateSiteImplementation)
            {
                foreach (var siteId in config.Templates.SitesForImplementation)
                {
                    var site = config.Sites.FirstOrDefault(s => s.SiteId == siteId);
                    string country = site?.CountryCode ?? "Unknown";
                    dt.Rows.Add("Site Implementation", site?.SiteId ?? siteId,
                        $"Enrollment, monitoring, data collection ({country})",
                        "~55");
                }
            }

            if (config.Templates.GenerateSiteCloseout)
            {
                foreach (var siteId in config.Templates.SitesForCloseout)
                {
                    var site = config.Sites.FirstOrDefault(s => s.SiteId == siteId);
                    string country = site?.CountryCode ?? "Unknown";
                    dt.Rows.Add("Site Closeout", site?.SiteId ?? siteId,
                        $"Database lock, site closure, archiving ({country})",
                        "~30-40");
                }
            }

            if (config.Templates.GenerateStudyCloseout)
            {
                dt.Rows.Add("Study Closeout", "All Sites",
                    "Final study report, regulatory submissions, archiving",
                    "~20-30");
            }

            if (dt.Rows.Count == 0)
            {
                dt.Rows.Add("", "", "No templates selected - go back and select at least one template", "0");
            }
            else
            {
                dt.Rows.Add("", "", "", "");
                int cohortCount = config.Cohorts?.Count ?? 0;
                dt.Rows.Add("TOTAL", "",
                    "Estimated total (actual may vary by country regulations)",
                    $"~{config.Templates.GetEstimatedTaskCount(cohortCount)}");
            }

            dgvPreview.DataSource = dt;
        }

        private void PreviewFilter_Changed(object sender, EventArgs e)
        {
            // TODO: Filter preview based on selected site/stage
        }

        #endregion

        #region Generation

        private void btnGenerate_Click(object sender, EventArgs e)
        {
            try
            {
                // Save final configuration
                SaveCurrentStepData();
                config.SaveToProject(msProjectApp);

                // Show progress
                this.Cursor = Cursors.WaitCursor;
                btnGenerate.Enabled = false;
                btnGenerate.Text = "Generating...";

                // Call UnifiedTemplateManager to generate templates
                var templateManager = new UnifiedTemplateManager();
                int tasksCreated = templateManager.GenerateTemplates(msProjectApp, config);

                this.Cursor = Cursors.Default;

                MessageBox.Show(
                    $"Successfully generated {tasksCreated} tasks!\n\n" +
                    "NEXT STEP - Add custom columns to view the data:\n\n" +
                    "1. Right-click any column header (like 'Duration')\n" +
                    "2. Click 'Insert Column'\n" +
                    "3. Type 'Text11' and press Enter (this adds Site column)\n" +
                    "4. Repeat for 'Text12' (Stage) and 'Text4' (Category)\n\n" +
                    "The custom fields are already on all tasks - you just need to make the columns visible.",
                    "Generation Complete",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);

                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            catch (Exception ex)
            {
                this.Cursor = Cursors.Default;
                btnGenerate.Enabled = true;
                btnGenerate.Text = "Generate";

                MessageBox.Show(
                    $"Error generating templates: {ex.Message}\n\n" +
                    "Please check the error and try again.",
                    "Generation Error",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error);
            }
        }

        #endregion
    }
}
