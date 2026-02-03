using IlanaPM.AddIn.Models;
using IlanaPM.AddIn.Services;
using Microsoft.Office.Interop.MSProject;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using MSProject = Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn
{
    /// <summary>
    /// Form for managing site phases and applying country-specific task templates
    /// DEPRECATED: Use UnifiedTemplateManagerForm instead.
    /// This form is kept for backward compatibility until the next major release.
    /// The Template Manager provides a unified interface for all template types including site phases.
    /// </summary>
    [Obsolete("Use UnifiedTemplateManagerForm instead. This form will be removed in the next major release.", false)]
    public partial class SitePhaseManagerForm : Form
    {
        private ClinicalMetadata clinicalMetadata;
        private ClinicalMetadataManager manager;
        private DependencyManager dependencyManager;

        public SitePhaseManagerForm()
        {
            InitializeComponent();
            manager = new ClinicalMetadataManager();
            dependencyManager = new DependencyManager();
        }

        private void SitePhaseManagerForm_Load(object sender, EventArgs e)
        {
            try
            {
                var project = Globals.ThisAddIn.Application.ActiveProject;
                if (project == null)
                {
                    MessageBox.Show("No active project.", "Error",
                        MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    this.Close();
                    return;
                }

                clinicalMetadata = manager.LoadMetadata(project);

                // Initialize phase selector
                cboPhase.SelectedIndex = 0;  // Default to "Site Startup"

                // Load sites (if available)
                if (clinicalMetadata != null && clinicalMetadata.sites.Count > 0)
                {
                    LoadSites();
                }
                else
                {
                    // No sites defined - disable site selector but allow Study Closeout
                    cboSite.Enabled = false;
                    lblSelectSite.Enabled = false;
                }
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error loading: {ex.Message}",
                    "Load Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void LoadSites()
        {
            cboSite.Items.Clear();
            foreach (var site in clinicalMetadata.sites)
            {
                cboSite.Items.Add(site);
            }

            if (cboSite.Items.Count > 0)
                cboSite.SelectedIndex = 0;
        }

        private void cboPhase_SelectedIndexChanged(object sender, EventArgs e)
        {
            string selectedPhase = cboPhase.SelectedItem?.ToString();

            if (selectedPhase == "Study Closeout")
            {
                // Hide site selector for Study Closeout
                lblSelectSite.Visible = false;
                cboSite.Visible = false;
                groupSiteInfo.Visible = false;

                // Load study closeout template
                LoadStudyCloseoutTemplate();
            }
            else
            {
                // Show site selector for Site Startup/Closeout
                lblSelectSite.Visible = true;
                cboSite.Visible = true;
                groupSiteInfo.Visible = true;

                // Reload site info if site is selected
                if (cboSite.SelectedItem != null)
                {
                    var site = (Models.Site)cboSite.SelectedItem;
                    LoadSiteInfo(site);
                    LoadAvailableTemplates(site);
                }
            }
        }

        private void cboSite_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (cboSite.SelectedItem == null)
                return;

            var site = (Models.Site)cboSite.SelectedItem;
            LoadSiteInfo(site);
            LoadAvailableTemplates(site);
        }

        private void LoadSiteInfo(Models.Site site)
        {
            lblSiteName.Text = $"Site: {site.id} - {site.name}";
            lblCountry.Text = $"Country: {site.country}";
            lblStatus.Text = $"Status: {site.status}";
            lblPI.Text = $"PI: {site.principal_investigator ?? "Not specified"}";

            // Determine current phase based on existing tasks (simplified logic)
            string currentPhase = DetermineCurrentPhase(site);
            lblCurrentPhase.Text = $"Current Phase: {currentPhase}";
        }

        private string DetermineCurrentPhase(Models.Site site)
        {
            // TODO: Implement logic to detect current phase from MS Project tasks
            // For now, default to "Not Started"
            return "Not Started";
        }

        private void LoadAvailableTemplates(Models.Site site)
        {
            lstTemplates.Items.Clear();

            string selectedPhase = cboPhase.SelectedItem?.ToString();
            string countryCode = GetCountryCode(site.country);
            SitePhaseTaskSet templateSet = null;

            if (selectedPhase == "Site Startup")
            {
                templateSet = CountryTemplateLibrary.GetSiteStartupByCountry(countryCode);
            }
            else if (selectedPhase == "Site Closeout")
            {
                templateSet = CountryTemplateLibrary.GetSiteCloseoutByCountry(countryCode);
            }

            if (templateSet != null)
            {
                string templateInfo = $"{selectedPhase} Template - {site.country} ({templateSet.tasks.Count} tasks)";
                lstTemplates.Items.Add(templateInfo);
            }

            DisplayTemplateDetails(templateSet);
        }

        private void LoadStudyCloseoutTemplate()
        {
            lstTemplates.Items.Clear();

            var templateSet = CountryTemplateLibrary.GetStudyCloseout();

            if (templateSet != null)
            {
                string templateInfo = $"Study Closeout Template - All Countries ({templateSet.tasks.Count} tasks)";
                lstTemplates.Items.Add(templateInfo);
            }

            DisplayTemplateDetails(templateSet);
        }

        private void DisplayTemplateDetails(SitePhaseTaskSet templateSet)
        {
            if (templateSet != null)
            {
                txtTemplateDetails.Clear();
                txtTemplateDetails.AppendText($"Template: {templateSet.phase_name}\n");
                txtTemplateDetails.AppendText($"Country: {templateSet.country_name}\n");
                txtTemplateDetails.AppendText($"Regulatory Authority: {templateSet.regulatory_authority}\n");
                txtTemplateDetails.AppendText($"Total Tasks: {templateSet.tasks.Count}\n");
                txtTemplateDetails.AppendText($"Essential Documents: {templateSet.essential_documents.Count}\n\n");

                // Group tasks by execution group
                var groups = dependencyManager.GroupTasksByExecutionGroup(templateSet.tasks);
                txtTemplateDetails.AppendText("Task Breakdown:\n");
                foreach (var group in groups)
                {
                    bool isParallel = group.Value.All(t => t.can_run_parallel);
                    txtTemplateDetails.AppendText($"  {group.Key}: {group.Value.Count} tasks ({(isParallel ? "Parallel" : "Sequential")})\n");
                }

                // Calculate estimated duration
                int estimatedDays = dependencyManager.CalculateEstimatedDuration(templateSet.tasks);
                txtTemplateDetails.AppendText($"\nEstimated Duration: {estimatedDays} days (~{estimatedDays / 7} weeks)\n");

                // Show critical path
                var criticalTasks = dependencyManager.GetCriticalPathTasks(templateSet.tasks);
                txtTemplateDetails.AppendText($"Critical Path Tasks: {criticalTasks.Count}\n");

                // SHOW ALL INDIVIDUAL TASKS (scrollable)
                txtTemplateDetails.AppendText("\n" + new string('=', 80) + "\n");
                txtTemplateDetails.AppendText("ALL TASKS:\n");
                txtTemplateDetails.AppendText(new string('=', 80) + "\n\n");

                foreach (var task in templateSet.tasks)
                {
                    txtTemplateDetails.AppendText($"{task.task_id}: {task.name}\n");
                    txtTemplateDetails.AppendText($"  Duration: {task.duration_days} days | Category: {task.category}\n");

                    if (task.predecessors != null && task.predecessors.Count > 0)
                    {
                        txtTemplateDetails.AppendText($"  Predecessors: {string.Join(", ", task.predecessors)}\n");
                    }

                    if (task.is_blocking)
                    {
                        txtTemplateDetails.AppendText("  [CRITICAL PATH]\n");
                    }

                    if (task.can_run_parallel)
                    {
                        txtTemplateDetails.AppendText($"  Execution: Parallel (Group {task.parallel_group_id})\n");
                    }
                    else
                    {
                        txtTemplateDetails.AppendText("  Execution: Sequential\n");
                    }

                    txtTemplateDetails.AppendText("\n");
                }
            }
        }

        private void btnGenerateStartupTasks_Click(object sender, EventArgs e)
        {
            string selectedPhase = cboPhase.SelectedItem?.ToString();

            if (selectedPhase == "Study Closeout")
            {
                // Study closeout doesn't need a site
                GenerateStudyCloseoutTasks();
                return;
            }

            // Site-specific phases (Startup or Closeout)
            if (cboSite.SelectedItem == null)
            {
                MessageBox.Show("Please select a site first.",
                    "No Selection", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            var site = (Models.Site)cboSite.SelectedItem;
            string countryCode = GetCountryCode(site.country);
            SitePhaseTaskSet templateSet = null;

            if (selectedPhase == "Site Startup")
            {
                templateSet = CountryTemplateLibrary.GetSiteStartupByCountry(countryCode);
            }
            else if (selectedPhase == "Site Closeout")
            {
                templateSet = CountryTemplateLibrary.GetSiteCloseoutByCountry(countryCode);
            }

            if (templateSet == null || templateSet.tasks.Count == 0)
            {
                MessageBox.Show($"No {selectedPhase.ToLower()} template available for country: {site.country}",
                    "No Template", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Confirm with user
            string phaseShort = selectedPhase.Replace("Site ", "");
            var result = MessageBox.Show(
                $"Generate {templateSet.tasks.Count} {selectedPhase.ToLower()} tasks for {site.name}?\n\n" +
                $"This will create tasks in MS Project under:\n" +
                $"  \"Site {site.id} - {phaseShort}\"\n\n" +
                $"Continue?",
                "Confirm Task Generation",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question);

            if (result != DialogResult.Yes)
                return;

            try
            {
                this.Cursor = Cursors.WaitCursor;
                btnGenerateStartupTasks.Enabled = false;

                // Generate tasks in MS Project
                GenerateTasksInProject(site, templateSet, phaseShort);

                MessageBox.Show(
                    $"Successfully generated {templateSet.tasks.Count} {selectedPhase.ToLower()} tasks!\n\n" +
                    $"Tasks created under: Site {site.id} - {phaseShort}\n" +
                    $"Dependencies applied: {templateSet.tasks.Count(t => t.predecessors != null && t.predecessors.Count > 0)} tasks\n" +
                    $"Critical path tasks: {templateSet.tasks.Count(t => t.is_blocking)}",
                    "Success",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error generating tasks: {ex.Message}",
                    "Generation Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                this.Cursor = Cursors.Default;
                btnGenerateStartupTasks.Enabled = true;
            }
        }

        private void GenerateStudyCloseoutTasks()
        {
            var templateSet = CountryTemplateLibrary.GetStudyCloseout();

            if (templateSet == null || templateSet.tasks.Count == 0)
            {
                MessageBox.Show("No study closeout template available.",
                    "No Template", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Confirm with user
            var result = MessageBox.Show(
                $"Generate {templateSet.tasks.Count} study closeout tasks?\n\n" +
                $"This will create study-level tasks in MS Project under:\n" +
                $"  \"Study Closeout\"\n\n" +
                $"Continue?",
                "Confirm Task Generation",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question);

            if (result != DialogResult.Yes)
                return;

            try
            {
                this.Cursor = Cursors.WaitCursor;
                btnGenerateStartupTasks.Enabled = false;

                // Generate study-level tasks
                GenerateStudyLevelTasks(templateSet);

                MessageBox.Show(
                    $"Successfully generated {templateSet.tasks.Count} study closeout tasks!\n\n" +
                    $"Tasks created under: Study Closeout\n" +
                    $"Dependencies applied: {templateSet.tasks.Count(t => t.predecessors != null && t.predecessors.Count > 0)} tasks\n" +
                    $"Critical path tasks: {templateSet.tasks.Count(t => t.is_blocking)}",
                    "Success",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error generating tasks: {ex.Message}",
                    "Generation Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                this.Cursor = Cursors.Default;
                btnGenerateStartupTasks.Enabled = true;
            }
        }

        private void GenerateTasksInProject(
            Models.Site site,
            SitePhaseTaskSet templateSet,
            string phase)
        {
            var app = Globals.ThisAddIn.Application;
            if (app.ActiveProject == null)
                throw new InvalidOperationException("No active project");

            var project = app.ActiveProject;

            // Create summary task for this site phase
            MSProject.Task summaryTask = project.Tasks.Add($"Site {site.id} - {phase}", Type.Missing);
            summaryTask.OutlineLevel = 1;
            // Note: Summary property is read-only. Tasks become summaries when child tasks are indented.

            // Create all tasks
            var createdTasks = new List<MSProject.Task>();
            var taskMap = new Dictionary<string, int>();  // template task_id -> MS Project UID

            foreach (var templateTask in templateSet.tasks)
            {
                MSProject.Task task = project.Tasks.Add(templateTask.name, Type.Missing);
                task.OutlineLevel = 2;
                task.Duration = templateTask.duration_days + "d";

                // Set custom fields
                task.SetField(MSProject.PjField.pjTaskText4, templateTask.category);
                task.SetField(MSProject.PjField.pjTaskText7, site.id);  // Site ID
                task.SetField(MSProject.PjField.pjTaskFlag2, templateTask.is_site_specific.ToString());
                task.SetField(MSProject.PjField.pjTaskFlag1, templateTask.is_mandatory.ToString());

                // Store mapping for dependency application
                taskMap[templateTask.task_id] = task.UniqueID;
                createdTasks.Add(task);
            }

            // Apply dependencies
            dependencyManager.ApplyDependencies(app, templateSet.tasks.ToList(), taskMap);

            // Optionally apply color coding (currently disabled)
            // dependencyManager.ApplyColorCodingByGroup(app, templateSet.tasks.ToList(), taskMap);
        }

        private void GenerateStudyLevelTasks(SitePhaseTaskSet templateSet)
        {
            var app = Globals.ThisAddIn.Application;
            if (app.ActiveProject == null)
                throw new InvalidOperationException("No active project");

            var project = app.ActiveProject;

            // Create summary task for study closeout
            MSProject.Task summaryTask = project.Tasks.Add("Study Closeout", Type.Missing);
            summaryTask.OutlineLevel = 1;
            // Note: Summary property is read-only. Tasks become summaries when child tasks are indented.

            // Create all tasks
            var taskMap = new Dictionary<string, int>();  // template task_id -> MS Project UID

            foreach (var templateTask in templateSet.tasks)
            {
                MSProject.Task task = project.Tasks.Add(templateTask.name, Type.Missing);
                task.OutlineLevel = 2;
                task.Duration = templateTask.duration_days + "d";

                // Set custom fields (no site ID for study-level tasks)
                task.SetField(MSProject.PjField.pjTaskText4, templateTask.category);
                task.SetField(MSProject.PjField.pjTaskFlag1, templateTask.is_mandatory.ToString());

                // Store mapping for dependency application
                taskMap[templateTask.task_id] = task.UniqueID;
            }

            // Apply dependencies
            dependencyManager.ApplyDependencies(app, templateSet.tasks.ToList(), taskMap);
        }

        private void btnPreview_Click(object sender, EventArgs e)
        {
            string selectedPhase = cboPhase.SelectedItem?.ToString();
            SitePhaseTaskSet templateSet = null;
            string previewTitle = "";

            if (selectedPhase == "Study Closeout")
            {
                templateSet = CountryTemplateLibrary.GetStudyCloseout();
                previewTitle = "Study Closeout";
            }
            else
            {
                // Site-specific phases
                if (cboSite.SelectedItem == null)
                {
                    MessageBox.Show("Please select a site first.",
                        "No Selection", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    return;
                }

                var site = (Models.Site)cboSite.SelectedItem;
                string countryCode = GetCountryCode(site.country);

                if (selectedPhase == "Site Startup")
                {
                    templateSet = CountryTemplateLibrary.GetSiteStartupByCountry(countryCode);
                }
                else if (selectedPhase == "Site Closeout")
                {
                    templateSet = CountryTemplateLibrary.GetSiteCloseoutByCountry(countryCode);
                }

                previewTitle = $"Site {site.id} - {site.name}";
            }

            if (templateSet == null)
                return;

            // Generate preview text
            var preview = new System.Text.StringBuilder();
            preview.AppendLine($"TASK PREVIEW: {previewTitle}");
            preview.AppendLine($"Phase: {selectedPhase}");
            preview.AppendLine($"Total Tasks: {templateSet.tasks.Count}");
            preview.AppendLine();
            preview.AppendLine("TASKS:");
            preview.AppendLine(new string('-', 80));

            foreach (var task in templateSet.tasks)
            {
                preview.AppendLine($"{task.task_id}: {task.name}");
                preview.AppendLine($"  Duration: {task.duration_days} days");
                preview.AppendLine($"  Category: {task.category}");
                if (task.predecessors != null && task.predecessors.Count > 0)
                {
                    preview.AppendLine($"  Predecessors: {string.Join(", ", task.predecessors)}");
                }
                if (task.is_blocking)
                {
                    preview.AppendLine("  ⚠ CRITICAL PATH");
                }
                preview.AppendLine();
            }

            // Show in message box (for simple preview) or create separate form
            MessageBox.Show(preview.ToString(), "Task Preview",
                MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        private void btnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private string GetCountryCode(string country)
        {
            var mapping = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                { "USA", "USA" },
                { "United States", "USA" },
                { "Germany", "DEU" },
                { "UK", "GBR" },
                { "United Kingdom", "GBR" },
                { "Canada", "CAN" },
                { "Japan", "JPN" }
            };

            return mapping.ContainsKey(country) ? mapping[country] : "USA";
        }
    }
}
