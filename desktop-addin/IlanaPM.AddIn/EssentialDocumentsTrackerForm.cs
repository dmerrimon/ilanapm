using IlanaPM.AddIn.Models;
using IlanaPM.AddIn.Services;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    public partial class EssentialDocumentsTrackerForm : Form
    {
        private ClinicalMetadata clinicalMetadata;
        private ClinicalMetadataManager manager;
        private Dictionary<string, List<EssentialDocument>> siteDocuments;

        public EssentialDocumentsTrackerForm()
        {
            InitializeComponent();
            manager = new ClinicalMetadataManager();
            siteDocuments = new Dictionary<string, List<EssentialDocument>>();
        }

        private void EssentialDocumentsTrackerForm_Load(object sender, EventArgs e)
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
                if (clinicalMetadata == null || clinicalMetadata.sites.Count == 0)
                {
                    MessageBox.Show(
                        "No sites defined.\n\n" +
                        "Please use Clinical Setup to define sites first.",
                        "No Sites",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                    this.Close();
                    return;
                }

                LoadSites();
                UpdateDocumentStats();
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Error loading essential documents: {ex.Message}",
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

        private void cboSite_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (cboSite.SelectedItem == null)
                return;

            var site = (Models.Site)cboSite.SelectedItem;
            LoadDocumentsForSite(site);
        }

        private void LoadDocumentsForSite(Models.Site site)
        {
            dgvDocuments.Rows.Clear();

            // Get country-specific essential documents
            var countryCode = GetCountryCode(site.country);
            var taskSet = CountryTemplateLibrary.GetSiteStartupByCountry(countryCode);

            if (taskSet == null || taskSet.essential_documents == null)
            {
                MessageBox.Show($"No essential documents defined for country: {site.country}",
                    "No Documents", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            // Load or initialize site documents
            if (!siteDocuments.ContainsKey(site.id))
            {
                siteDocuments[site.id] = new List<EssentialDocument>(taskSet.essential_documents);
            }

            var docs = siteDocuments[site.id];

            foreach (var doc in docs)
            {
                var statusColor = GetStatusColor(doc.status);
                int rowIndex = dgvDocuments.Rows.Add(
                    doc.document_name,
                    doc.regulatory_reference,
                    doc.status ?? "Not Collected",
                    doc.date_collected?.ToString("yyyy-MM-dd") ?? "",
                    doc.collected_by ?? "",
                    doc.version ?? "",
                    doc.is_mandatory ? "Yes" : "No"
                );

                // Color code by status
                dgvDocuments.Rows[rowIndex].DefaultCellStyle.BackColor = statusColor;
            }

            lblSiteInfo.Text = $"Site: {site.id} - {site.name} ({site.country})";
            UpdateCompletionPercentage(docs);
        }

        private Color GetStatusColor(string status)
        {
            switch (status)
            {
                case "Collected":
                    return Color.LightYellow;
                case "Verified":
                    return Color.LightGreen;
                case "Filed":
                    return Color.PaleGreen;
                case "Not Collected":
                default:
                    return Color.White;
            }
        }

        private void UpdateCompletionPercentage(List<EssentialDocument> docs)
        {
            var mandatory = docs.Where(d => d.is_mandatory).ToList();
            var collected = mandatory.Where(d => d.status == "Collected" || d.status == "Verified" || d.status == "Filed").Count();

            if (mandatory.Count == 0)
            {
                lblCompletion.Text = "No mandatory documents";
                return;
            }

            int percentage = (collected * 100) / mandatory.Count;
            lblCompletion.Text = $"Completion: {collected}/{mandatory.Count} ({percentage}%)";

            if (percentage == 100)
                lblCompletion.ForeColor = Color.Green;
            else if (percentage >= 75)
                lblCompletion.ForeColor = Color.DarkOrange;
            else
                lblCompletion.ForeColor = Color.Red;
        }

        private void UpdateDocumentStats()
        {
            int totalMandatory = 0;
            int totalCollected = 0;

            foreach (var site in clinicalMetadata.sites)
            {
                var countryCode = GetCountryCode(site.country);
                var taskSet = CountryTemplateLibrary.GetSiteStartupByCountry(countryCode);

                if (taskSet != null && taskSet.essential_documents != null)
                {
                    var mandatory = taskSet.essential_documents.Where(d => d.is_mandatory).Count();
                    totalMandatory += mandatory;

                    if (siteDocuments.ContainsKey(site.id))
                    {
                        var collected = siteDocuments[site.id]
                            .Where(d => d.is_mandatory && (d.status == "Collected" || d.status == "Verified" || d.status == "Filed"))
                            .Count();
                        totalCollected += collected;
                    }
                }
            }

            lblOverallStats.Text = $"Overall: {totalCollected}/{totalMandatory} documents collected across {clinicalMetadata.sites.Count} sites";
        }

        private void btnMarkCollected_Click(object sender, EventArgs e)
        {
            if (dgvDocuments.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select a document to mark as collected.",
                    "No Selection", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            if (cboSite.SelectedItem == null)
                return;

            var site = (Models.Site)cboSite.SelectedItem;
            var docs = siteDocuments[site.id];

            foreach (DataGridViewRow row in dgvDocuments.SelectedRows)
            {
                int docIndex = row.Index;
                if (docIndex < docs.Count)
                {
                    docs[docIndex].status = "Collected";
                    docs[docIndex].date_collected = DateTime.Now;
                    docs[docIndex].collected_by = Environment.UserName;
                }
            }

            LoadDocumentsForSite(site);
            UpdateDocumentStats();
        }

        private void btnMarkVerified_Click(object sender, EventArgs e)
        {
            if (dgvDocuments.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select a document to mark as verified.",
                    "No Selection", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            if (cboSite.SelectedItem == null)
                return;

            var site = (Models.Site)cboSite.SelectedItem;
            var docs = siteDocuments[site.id];

            foreach (DataGridViewRow row in dgvDocuments.SelectedRows)
            {
                int docIndex = row.Index;
                if (docIndex < docs.Count)
                {
                    docs[docIndex].status = "Verified";
                }
            }

            LoadDocumentsForSite(site);
            UpdateDocumentStats();
        }

        private void btnMarkFiled_Click(object sender, EventArgs e)
        {
            if (dgvDocuments.SelectedRows.Count == 0)
            {
                MessageBox.Show("Please select a document to mark as filed.",
                    "No Selection", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            if (cboSite.SelectedItem == null)
                return;

            var site = (Models.Site)cboSite.SelectedItem;
            var docs = siteDocuments[site.id];

            foreach (DataGridViewRow row in dgvDocuments.SelectedRows)
            {
                int docIndex = row.Index;
                if (docIndex < docs.Count)
                {
                    docs[docIndex].status = "Filed";
                }
            }

            LoadDocumentsForSite(site);
            UpdateDocumentStats();
        }

        private void btnExportChecklist_Click(object sender, EventArgs e)
        {
            if (cboSite.SelectedItem == null)
            {
                MessageBox.Show("Please select a site first.",
                    "No Selection", MessageBoxButtons.OK, MessageBoxIcon.Information);
                return;
            }

            var site = (Models.Site)cboSite.SelectedItem;

            var saveDialog = new SaveFileDialog
            {
                FileName = $"Essential_Docs_{site.id}_{DateTime.Now:yyyyMMdd}.csv",
                Filter = "CSV files (*.csv)|*.csv|All files (*.*)|*.*"
            };

            if (saveDialog.ShowDialog() == DialogResult.OK)
            {
                try
                {
                    ExportToCSV(site, saveDialog.FileName);
                    MessageBox.Show($"Checklist exported successfully!\n\nFile: {saveDialog.FileName}",
                        "Export Successful", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                catch (System.Exception ex)
                {
                    MessageBox.Show($"Error exporting checklist: {ex.Message}",
                        "Export Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        private void ExportToCSV(Models.Site site, string filePath)
        {
            var docs = siteDocuments[site.id];
            var csv = new System.Text.StringBuilder();

            // Header
            csv.AppendLine($"Essential Documents Checklist for {site.id} - {site.name}");
            csv.AppendLine($"Country: {site.country}");
            csv.AppendLine($"Generated: {DateTime.Now:yyyy-MM-dd HH:mm}");
            csv.AppendLine();
            csv.AppendLine("Document Name,Regulatory Reference,Mandatory,Status,Date Collected,Collected By,Version");

            // Data rows
            foreach (var doc in docs)
            {
                csv.AppendLine($"\"{doc.document_name}\",\"{doc.regulatory_reference}\"," +
                    $"\"{(doc.is_mandatory ? "Yes" : "No")}\",\"{doc.status ?? "Not Collected"}\"," +
                    $"\"{doc.date_collected?.ToString("yyyy-MM-dd") ?? ""}\",\"{doc.collected_by ?? ""}\"," +
                    $"\"{doc.version ?? ""}\"");
            }

            System.IO.File.WriteAllText(filePath, csv.ToString());
        }

        private void btnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private string GetCountryCode(string country)
        {
            // Map country names to codes
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
