using IlanaPM.AddIn.Models;
using IlanaPM.AddIn.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    public partial class ClinicalSetupForm : Form
    {
        private Models.ClinicalMetadata clinicalMetadata;
        private Services.ClinicalMetadataManager manager;

        public ClinicalSetupForm()
        {
            InitializeComponent();
            manager = new Services.ClinicalMetadataManager();
        }

        private void ClinicalSetupForm_Load(object sender, EventArgs e)
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
                if (clinicalMetadata == null)
                {
                    clinicalMetadata = new Models.ClinicalMetadata();
                }

                LoadSitesGrid();
                LoadAmendmentsGrid();
                LoadCohortsGrid();
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error loading clinical metadata: {ex.Message}",
                    "Load Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        #region Sites Tab

        private void LoadSitesGrid()
        {
            dgvSites.Rows.Clear();
            foreach (var site in clinicalMetadata.sites)
            {
                dgvSites.Rows.Add(
                    site.id,
                    site.name,
                    site.country,
                    site.status,
                    site.irb_approval_date?.ToString("yyyy-MM-dd") ?? "",
                    site.principal_investigator);
            }
        }

        private void btnAddSite_Click(object sender, EventArgs e)
        {
            var newSite = new Models.Site
            {
                id = $"SITE-{(clinicalMetadata.sites.Count + 1):D3}",
                name = "New Site",
                country = "USA",
                status = "Pending",
                principal_investigator = ""
            };

            clinicalMetadata.sites.Add(newSite);
            LoadSitesGrid();
        }

        private void btnDeleteSite_Click(object sender, EventArgs e)
        {
            if (dgvSites.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select a site to delete.", "No Selection",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            var result = MessageBox.Show("Delete selected site(s)?", "Confirm Delete",
                MessageBoxButtons.YesNo, MessageBoxIcon.Question);

            if (result == DialogResult.Yes)
            {
                foreach (DataGridViewRow row in dgvSites.SelectedRows)
                {
                    if (!row.IsNewRow)
                    {
                        string siteId = row.Cells[0].Value?.ToString();
                        var site = clinicalMetadata.sites.FirstOrDefault(s => s.id == siteId);
                        if (site != null)
                        {
                            clinicalMetadata.sites.Remove(site);
                        }
                    }
                }
                LoadSitesGrid();
            }
        }

        private void dgvSites_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            try
            {
                var row = dgvSites.Rows[e.RowIndex];
                string siteId = row.Cells[0].Value?.ToString();

                var site = clinicalMetadata.sites.FirstOrDefault(s => s.id == siteId);
                if (site != null)
                {
                    site.id = row.Cells[0].Value?.ToString() ?? site.id;
                    site.name = row.Cells[1].Value?.ToString() ?? site.name;
                    site.country = row.Cells[2].Value?.ToString() ?? site.country;
                    site.status = row.Cells[3].Value?.ToString() ?? site.status;

                    string dateStr = row.Cells[4].Value?.ToString();
                    if (!string.IsNullOrWhiteSpace(dateStr) && DateTime.TryParse(dateStr, out DateTime date))
                    {
                        site.irb_approval_date = date;
                    }

                    site.principal_investigator = row.Cells[5].Value?.ToString() ?? site.principal_investigator;
                }
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error updating site: {ex.Message}", "Update Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        #endregion

        #region Amendments Tab

        private void LoadAmendmentsGrid()
        {
            dgvAmendments.Rows.Clear();
            foreach (var amendment in clinicalMetadata.amendments)
            {
                dgvAmendments.Rows.Add(
                    amendment.id,
                    amendment.number,
                    amendment.date.ToString("yyyy-MM-dd"),
                    amendment.description,
                    string.Join(", ", amendment.affected_sites),
                    amendment.amendment_type);
            }
        }

        private void btnAddAmendment_Click(object sender, EventArgs e)
        {
            var newAmendment = new Models.Amendment
            {
                id = $"AMD-{(clinicalMetadata.amendments.Count + 1):D3}",
                number = $"Amendment {clinicalMetadata.amendments.Count + 1}",
                date = DateTime.Now,
                description = "New Amendment",
                amendment_type = "substantial",
                affected_sites = new List<string>()
            };

            clinicalMetadata.amendments.Add(newAmendment);
            LoadAmendmentsGrid();
        }

        private void btnDeleteAmendment_Click(object sender, EventArgs e)
        {
            if (dgvAmendments.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select an amendment to delete.", "No Selection",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            var result = MessageBox.Show("Delete selected amendment(s)?", "Confirm Delete",
                MessageBoxButtons.YesNo, MessageBoxIcon.Question);

            if (result == DialogResult.Yes)
            {
                foreach (DataGridViewRow row in dgvAmendments.SelectedRows)
                {
                    if (!row.IsNewRow)
                    {
                        string amendmentId = row.Cells[0].Value?.ToString();
                        var amendment = clinicalMetadata.amendments.FirstOrDefault(a => a.id == amendmentId);
                        if (amendment != null)
                        {
                            clinicalMetadata.amendments.Remove(amendment);
                        }
                    }
                }
                LoadAmendmentsGrid();
            }
        }

        private void dgvAmendments_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            try
            {
                var row = dgvAmendments.Rows[e.RowIndex];
                string amendmentId = row.Cells[0].Value?.ToString();

                var amendment = clinicalMetadata.amendments.FirstOrDefault(a => a.id == amendmentId);
                if (amendment != null)
                {
                    amendment.id = row.Cells[0].Value?.ToString() ?? amendment.id;
                    amendment.number = row.Cells[1].Value?.ToString() ?? amendment.number;

                    string dateStr = row.Cells[2].Value?.ToString();
                    if (!string.IsNullOrWhiteSpace(dateStr) && DateTime.TryParse(dateStr, out DateTime date))
                    {
                        amendment.date = date;
                    }

                    amendment.description = row.Cells[3].Value?.ToString() ?? amendment.description;

                    string affectedSitesStr = row.Cells[4].Value?.ToString();
                    if (!string.IsNullOrWhiteSpace(affectedSitesStr))
                    {
                        amendment.affected_sites = affectedSitesStr.Split(',')
                            .Select(s => s.Trim())
                            .Where(s => !string.IsNullOrEmpty(s))
                            .ToList();
                    }

                    amendment.amendment_type = row.Cells[5].Value?.ToString() ?? amendment.amendment_type;
                }
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error updating amendment: {ex.Message}", "Update Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnEditAffectedSites_Click(object sender, EventArgs e)
        {
            if (dgvAmendments.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select an amendment first.", "No Selection",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            var row = dgvAmendments.SelectedRows[0];
            string amendmentId = row.Cells[0].Value?.ToString();
            var amendment = clinicalMetadata.amendments.FirstOrDefault(a => a.id == amendmentId);

            if (amendment != null)
            {
                string current = string.Join(", ", amendment.affected_sites);
                string input = Microsoft.VisualBasic.Interaction.InputBox(
                    "Enter affected site IDs (comma-separated):\nExample: SITE-001, SITE-005, SITE-012",
                    "Edit Affected Sites",
                    current);

                if (!string.IsNullOrWhiteSpace(input))
                {
                    amendment.affected_sites = input.Split(',')
                        .Select(s => s.Trim())
                        .Where(s => !string.IsNullOrEmpty(s))
                        .ToList();
                    LoadAmendmentsGrid();
                }
            }
        }

        #endregion

        #region Cohorts Tab

        private void LoadCohortsGrid()
        {
            dgvCohorts.Rows.Clear();
            foreach (var cohort in clinicalMetadata.cohorts)
            {
                dgvCohorts.Rows.Add(
                    cohort.id,
                    cohort.name,
                    cohort.enrollment_target,
                    string.Join(", ", cohort.prerequisites),
                    string.Join(", ", cohort.participating_sites));
            }
        }

        private void btnAddCohort_Click(object sender, EventArgs e)
        {
            var newCohort = new Models.Cohort
            {
                id = $"COH-{(clinicalMetadata.cohorts.Count + 1):D3}",
                name = $"Cohort {clinicalMetadata.cohorts.Count + 1}",
                enrollment_target = 0,
                prerequisites = new List<string>(),
                participating_sites = new List<string>()
            };

            clinicalMetadata.cohorts.Add(newCohort);
            LoadCohortsGrid();
        }

        private void btnDeleteCohort_Click(object sender, EventArgs e)
        {
            if (dgvCohorts.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select a cohort to delete.", "No Selection",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            var result = MessageBox.Show("Delete selected cohort(s)?", "Confirm Delete",
                MessageBoxButtons.YesNo, MessageBoxIcon.Question);

            if (result == DialogResult.Yes)
            {
                foreach (DataGridViewRow row in dgvCohorts.SelectedRows)
                {
                    if (!row.IsNewRow)
                    {
                        string cohortId = row.Cells[0].Value?.ToString();
                        var cohort = clinicalMetadata.cohorts.FirstOrDefault(c => c.id == cohortId);
                        if (cohort != null)
                        {
                            clinicalMetadata.cohorts.Remove(cohort);
                        }
                    }
                }
                LoadCohortsGrid();
            }
        }

        private void dgvCohorts_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            try
            {
                var row = dgvCohorts.Rows[e.RowIndex];
                string cohortId = row.Cells[0].Value?.ToString();

                var cohort = clinicalMetadata.cohorts.FirstOrDefault(c => c.id == cohortId);
                if (cohort != null)
                {
                    cohort.id = row.Cells[0].Value?.ToString() ?? cohort.id;
                    cohort.name = row.Cells[1].Value?.ToString() ?? cohort.name;

                    string targetStr = row.Cells[2].Value?.ToString();
                    if (!string.IsNullOrWhiteSpace(targetStr) && int.TryParse(targetStr, out int target))
                    {
                        cohort.enrollment_target = target;
                    }

                    string prereqStr = row.Cells[3].Value?.ToString();
                    if (!string.IsNullOrWhiteSpace(prereqStr))
                    {
                        cohort.prerequisites = prereqStr.Split(',')
                            .Select(s => s.Trim())
                            .Where(s => !string.IsNullOrEmpty(s))
                            .ToList();
                    }

                    string sitesStr = row.Cells[4].Value?.ToString();
                    if (!string.IsNullOrWhiteSpace(sitesStr))
                    {
                        cohort.participating_sites = sitesStr.Split(',')
                            .Select(s => s.Trim())
                            .Where(s => !string.IsNullOrEmpty(s))
                            .ToList();
                    }
                }
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error updating cohort: {ex.Message}", "Update Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnEditParticipatingSites_Click(object sender, EventArgs e)
        {
            if (dgvCohorts.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select a cohort first.", "No Selection",
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            var row = dgvCohorts.SelectedRows[0];
            string cohortId = row.Cells[0].Value?.ToString();
            var cohort = clinicalMetadata.cohorts.FirstOrDefault(c => c.id == cohortId);

            if (cohort != null)
            {
                string current = string.Join(", ", cohort.participating_sites);
                string input = Microsoft.VisualBasic.Interaction.InputBox(
                    "Enter participating site IDs (comma-separated):\nExample: SITE-001, SITE-005, SITE-012",
                    "Edit Participating Sites",
                    current);

                if (!string.IsNullOrWhiteSpace(input))
                {
                    cohort.participating_sites = input.Split(',')
                        .Select(s => s.Trim())
                        .Where(s => !string.IsNullOrEmpty(s))
                        .ToList();
                    LoadCohortsGrid();
                }
            }
        }

        #endregion

        #region Save/Cancel

        private void btnSave_Click(object sender, EventArgs e)
        {
            try
            {
                var project = Globals.ThisAddIn.Application.ActiveProject;
                if (project == null)
                {
                    MessageBox.Show("No active project.", "Error",
                        MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                manager.SaveMetadata(project, clinicalMetadata);

                MessageBox.Show(
                    $"Clinical metadata saved successfully!\n\n" +
                    $"Sites: {clinicalMetadata.sites.Count}\n" +
                    $"Amendments: {clinicalMetadata.amendments.Count}\n" +
                    $"Cohorts: {clinicalMetadata.cohorts.Count}",
                    "Save Successful",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information);

                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error saving clinical metadata: {ex.Message}",
                    "Save Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            this.DialogResult = DialogResult.Cancel;
            this.Close();
        }

        #endregion
    }
}
