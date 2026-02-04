using IlanaPM.AddIn.Models;
using IlanaPM.AddIn.Services;
using Microsoft.Office.Interop.MSProject;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using MSProject = Microsoft.Office.Interop.MSProject;
using Site = IlanaPM.AddIn.Models.Site;

namespace IlanaPM.AddIn
{
    public partial class ClinicalEntityTaggingForm : Form
    {
        private List<MSProject.Task> selectedTasks;
        private Models.ClinicalMetadata clinicalMetadata;
        private Services.ClinicalMetadataManager manager;

        public ClinicalEntityTaggingForm()
        {
            InitializeComponent();
            manager = new Services.ClinicalMetadataManager();
        }

        public void LoadSelectedTasks(List<MSProject.Task> tasks)
        {
            selectedTasks = tasks;

            if (tasks == null || tasks.Count == 0)
            {
                MessageBox.Show("No tasks selected.", "Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                this.Close();
                return;
            }

            lblTaskCount.Text = $"Tagging {tasks.Count} selected task{(tasks.Count > 1 ? "s" : "")}";

            try
            {
                var project = Globals.ThisAddIn.Application.ActiveProject;
                clinicalMetadata = manager.LoadMetadata(project);

                if (clinicalMetadata == null ||
                    (clinicalMetadata.sites.Count == 0 &&
                     clinicalMetadata.amendments.Count == 0 &&
                     clinicalMetadata.cohorts.Count == 0))
                {
                    MessageBox.Show(
                        "No clinical entities defined.\n\n" +
                        "Please use Clinical Setup to define sites, amendments, and cohorts first.",
                        "No Entities",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                    this.Close();
                    return;
                }

                PopulateEntityCheckboxes();
                LoadExistingTags();
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error loading clinical entities: {ex.Message}",
                    "Load Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                this.Close();
            }
        }

        private void PopulateEntityCheckboxes()
        {
            clbSites.Items.Clear();
            foreach (var site in clinicalMetadata.sites)
            {
                clbSites.Items.Add(site.DisplayName, false);
            }

            clbAmendments.Items.Clear();
            foreach (var amendment in clinicalMetadata.amendments)
            {
                clbAmendments.Items.Add(amendment.DisplayName, false);
            }

            clbCohorts.Items.Clear();
            foreach (var cohort in clinicalMetadata.cohorts)
            {
                clbCohorts.Items.Add(cohort.DisplayName, false);
            }
        }

        private void LoadExistingTags()
        {
            if (selectedTasks.Count != 1)
                return;

            var task = selectedTasks[0];

            try
            {
                string siteIds = task.GetField(MSProject.PjField.pjTaskText7)?.ToString() ?? "";
                string amendmentIds = task.GetField(MSProject.PjField.pjTaskText8)?.ToString() ?? "";
                string cohortIds = task.GetField(MSProject.PjField.pjTaskText9)?.ToString() ?? "";

                if (!string.IsNullOrWhiteSpace(siteIds))
                {
                    var ids = siteIds.Split(',').Select(id => id.Trim()).ToList();
                    for (int i = 0; i < clbSites.Items.Count; i++)
                    {
                        var site = clinicalMetadata.sites[i];
                        if (ids.Contains(site.id))
                        {
                            clbSites.SetItemChecked(i, true);
                        }
                    }
                }

                if (!string.IsNullOrWhiteSpace(amendmentIds))
                {
                    var ids = amendmentIds.Split(',').Select(id => id.Trim()).ToList();
                    for (int i = 0; i < clbAmendments.Items.Count; i++)
                    {
                        var amendment = clinicalMetadata.amendments[i];
                        if (ids.Contains(amendment.id))
                        {
                            clbAmendments.SetItemChecked(i, true);
                        }
                    }
                }

                if (!string.IsNullOrWhiteSpace(cohortIds))
                {
                    var ids = cohortIds.Split(',').Select(id => id.Trim()).ToList();
                    for (int i = 0; i < clbCohorts.Items.Count; i++)
                    {
                        var cohort = clinicalMetadata.cohorts[i];
                        if (ids.Contains(cohort.id))
                        {
                            clbCohorts.SetItemChecked(i, true);
                        }
                    }
                }
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading existing tags: {ex.Message}");
            }
        }

        private void btnApplyTags_Click(object sender, EventArgs e)
        {
            try
            {
                var siteIds = new List<string>();
                foreach (int index in clbSites.CheckedIndices)
                {
                    siteIds.Add(clinicalMetadata.sites[index].id);
                }

                var amendmentIds = new List<string>();
                foreach (int index in clbAmendments.CheckedIndices)
                {
                    amendmentIds.Add(clinicalMetadata.amendments[index].id);
                }

                var cohortIds = new List<string>();
                foreach (int index in clbCohorts.CheckedIndices)
                {
                    cohortIds.Add(clinicalMetadata.cohorts[index].id);
                }

                int taggedCount = 0;
                foreach (var task in selectedTasks)
                {
                    manager.TagTaskWithEntities(task, siteIds, amendmentIds, cohortIds);
                    taggedCount++;
                }

                MessageBox.Show(
                    $"Successfully tagged {taggedCount} task{(taggedCount > 1 ? "s" : "")}!\n\n" +
                    $"Sites: {siteIds.Count}\n" +
                    $"Amendments: {amendmentIds.Count}\n" +
                    $"Cohorts: {cohortIds.Count}",
                    "Tagging Complete",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);

                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error tagging tasks: {ex.Message}",
                    "Tagging Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            this.DialogResult = DialogResult.Cancel;
            this.Close();
        }
    }
}
