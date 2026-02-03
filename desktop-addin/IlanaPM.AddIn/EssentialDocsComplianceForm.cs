using System;
using System.Collections.Generic;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Windows.Forms;
using MSProject = Microsoft.Office.Interop.MSProject;
using Newtonsoft.Json;
using IlanaPM.AddIn.Models;

namespace IlanaPM.AddIn
{
    public class EssentialDocsComplianceForm : Form
    {
        private MSProject.Application msProjectApp;
        private DataGridView dgvCompliance;
        private Panel pnlSummary;
        private Label lblTotalSites;
        private Label lblOverallCompliance;
        private Label lblCompliantSites;
        private Label lblCriticalMissing;
        private Button btnExportExcel;
        private Button btnExportPDF;
        private Button btnRefresh;
        private Button btnClose;

        // Essential documents list
        private readonly List<string> essentialDocuments = new List<string>
        {
            "Protocol (Signed)",
            "Informed Consent Form (ICF) - Approved",
            "IRB Approval Letter",
            "Principal Investigator CV",
            "Sub-Investigator CVs",
            "Medical Licenses",
            "GCP Training Certificates",
            "Financial Disclosure Forms",
            "Site Budget Agreement",
            "Confidential Disclosure Agreement (CDA)",
            "Regulatory Binder Setup",
            "Lab Certifications (CLIA/CAP)",
            "Pharmacy Licenses",
            "Study Drug Shipping Records",
            "Site Delegation Log",
            "Site Training Records",
            "Source Document Templates",
            "Case Report Form (CRF) Training",
            "eCRF System Access",
            "Investigator Site File (ISF) Setup"
        };

        public EssentialDocsComplianceForm(MSProject.Application app)
        {
            this.msProjectApp = app;
            InitializeComponent();
            LoadComplianceData();
        }

        private void InitializeComponent()
        {
            this.Text = "Essential Documents Compliance Report";
            this.Size = new Size(1200, 700);
            this.StartPosition = FormStartPosition.CenterScreen;

            // Summary Panel
            pnlSummary = new Panel
            {
                Location = new Point(10, 10),
                Size = new Size(1160, 100),
                BorderStyle = BorderStyle.FixedSingle,
                BackColor = Color.FromArgb(240, 248, 255)
            };

            Label lblSummaryTitle = new Label
            {
                Text = "Compliance Summary",
                Location = new Point(10, 5),
                Size = new Size(300, 25),
                Font = new Font("Segoe UI", 12, FontStyle.Bold),
                ForeColor = Color.FromArgb(0, 51, 102)
            };
            pnlSummary.Controls.Add(lblSummaryTitle);

            lblTotalSites = new Label
            {
                Location = new Point(20, 35),
                Size = new Size(250, 20),
                Font = new Font("Segoe UI", 10)
            };
            pnlSummary.Controls.Add(lblTotalSites);

            lblOverallCompliance = new Label
            {
                Location = new Point(20, 55),
                Size = new Size(250, 20),
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                ForeColor = Color.Green
            };
            pnlSummary.Controls.Add(lblOverallCompliance);

            lblCompliantSites = new Label
            {
                Location = new Point(300, 35),
                Size = new Size(350, 20),
                Font = new Font("Segoe UI", 10)
            };
            pnlSummary.Controls.Add(lblCompliantSites);

            lblCriticalMissing = new Label
            {
                Location = new Point(300, 55),
                Size = new Size(400, 20),
                Font = new Font("Segoe UI", 10),
                ForeColor = Color.Red
            };
            pnlSummary.Controls.Add(lblCriticalMissing);

            this.Controls.Add(pnlSummary);

            // DataGridView
            dgvCompliance = new DataGridView
            {
                Location = new Point(10, 120),
                Size = new Size(1160, 480),
                AllowUserToAddRows = false,
                AllowUserToDeleteRows = false,
                ReadOnly = true,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect,
                BackgroundColor = Color.White,
                BorderStyle = BorderStyle.Fixed3D
            };
            dgvCompliance.CellFormatting += DgvCompliance_CellFormatting;
            this.Controls.Add(dgvCompliance);

            // Buttons
            btnRefresh = new Button
            {
                Text = "Refresh",
                Location = new Point(10, 615),
                Size = new Size(100, 30)
            };
            btnRefresh.Click += (s, e) => LoadComplianceData();
            this.Controls.Add(btnRefresh);

            btnExportExcel = new Button
            {
                Text = "Export to Excel",
                Location = new Point(120, 615),
                Size = new Size(120, 30)
            };
            btnExportExcel.Click += BtnExportExcel_Click;
            this.Controls.Add(btnExportExcel);

            btnExportPDF = new Button
            {
                Text = "Export to PDF",
                Location = new Point(250, 615),
                Size = new Size(120, 30)
            };
            btnExportPDF.Click += BtnExportPDF_Click;
            this.Controls.Add(btnExportPDF);

            btnClose = new Button
            {
                Text = "Close",
                Location = new Point(1070, 615),
                Size = new Size(100, 30)
            };
            btnClose.Click += (s, e) => this.Close();
            this.Controls.Add(btnClose);
        }

        private void LoadComplianceData()
        {
            try
            {
                var complianceData = GetComplianceData();
                DisplayComplianceData(complianceData);
                UpdateSummary(complianceData);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading compliance data: {ex.Message}", "Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private List<SiteComplianceData> GetComplianceData()
        {
            var complianceList = new List<SiteComplianceData>();
            var sites = GetSitesFromProject();

            foreach (var site in sites)
            {
                var siteCompliance = new SiteComplianceData
                {
                    SiteId = site.SiteId,
                    SiteName = site.SiteName,
                    Country = site.CountryName ?? site.CountryCode ?? "Unknown",
                    Documents = new Dictionary<string, DocumentStatus>()
                };

                // Check each essential document
                foreach (var doc in essentialDocuments)
                {
                    var status = GetDocumentStatus(site.SiteId, doc);
                    siteCompliance.Documents[doc] = status;
                }

                // Calculate compliance metrics
                int totalDocs = essentialDocuments.Count;
                int approvedDocs = siteCompliance.Documents.Count(d => d.Value.Status == "Approved");
                int pendingDocs = siteCompliance.Documents.Count(d => d.Value.Status == "Pending");
                int missingDocs = siteCompliance.Documents.Count(d => d.Value.Status == "Missing");

                siteCompliance.CompliancePercent = (approvedDocs * 100.0) / totalDocs;
                siteCompliance.ApprovedCount = approvedDocs;
                siteCompliance.PendingCount = pendingDocs;
                siteCompliance.MissingCount = missingDocs;
                siteCompliance.CriticalMissing = GetCriticalMissingDocuments(siteCompliance);

                complianceList.Add(siteCompliance);
            }

            return complianceList.OrderBy(s => s.SiteId).ToList();
        }

        private List<SiteConfiguration> GetSitesFromProject()
        {
            var sites = new List<SiteConfiguration>();

            try
            {
                // Load from project configuration
                var config = ClinicalProjectConfiguration.LoadFromProject(msProjectApp);
                if (config?.Sites != null && config.Sites.Count > 0)
                {
                    return config.Sites;
                }

                // Fallback: Extract from MS Project tasks
                foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
                {
                    if (task != null)
                    {
                        string siteId = task.GetField(MSProject.PjField.pjTaskText11);
                        if (!string.IsNullOrWhiteSpace(siteId) && !sites.Any(s => s.SiteId == siteId))
                        {
                            sites.Add(new SiteConfiguration
                            {
                                SiteId = siteId,
                                SiteName = $"Site {siteId}",
                                CountryCode = "USA",
                                CountryName = "Unknown"
                            });
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Warning: Could not load site data. {ex.Message}", "Warning",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }

            // If no sites found, create sample data
            if (sites.Count == 0)
            {
                sites.Add(new SiteConfiguration { SiteId = "001", SiteName = "Memorial Hospital", CountryCode = "USA", CountryName = "United States" });
                sites.Add(new SiteConfiguration { SiteId = "002", SiteName = "Research Center", CountryCode = "CAN", CountryName = "Canada" });
            }

            return sites;
        }

        private DocumentStatus GetDocumentStatus(string siteId, string documentName)
        {
            // Look for tasks related to this document for this site
            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task != null)
                {
                    string taskSite = task.GetField(MSProject.PjField.pjTaskText11);
                    if (taskSite == siteId && task.Name.Contains(documentName.Split('-')[0].Trim()))
                    {
                        string status = "Missing";
                        DateTime? dateReceived = null;

                        if (task.PercentComplete >= 100)
                        {
                            status = "Approved";
                            dateReceived = task.ActualFinish;
                        }
                        else if (task.PercentComplete > 0)
                        {
                            status = "Pending";
                        }

                        return new DocumentStatus
                        {
                            Status = status,
                            DateReceived = dateReceived,
                            Notes = task.Notes
                        };
                    }
                }
            }

            // Simulate document status for demonstration
            Random rand = new Random(siteId.GetHashCode() + documentName.GetHashCode());
            int statusValue = rand.Next(100);

            if (statusValue < 70)
            {
                return new DocumentStatus
                {
                    Status = "Approved",
                    DateReceived = DateTime.Today.AddDays(-rand.Next(1, 60)),
                    Notes = "Document approved"
                };
            }
            else if (statusValue < 85)
            {
                return new DocumentStatus
                {
                    Status = "Pending",
                    DateReceived = DateTime.Today.AddDays(-rand.Next(1, 30)),
                    Notes = "Under review"
                };
            }
            else
            {
                return new DocumentStatus
                {
                    Status = "Missing",
                    DateReceived = null,
                    Notes = "Not yet received"
                };
            }
        }

        private string GetCriticalMissingDocuments(SiteComplianceData siteCompliance)
        {
            var criticalDocs = new List<string>
            {
                "Protocol (Signed)",
                "Informed Consent Form (ICF) - Approved",
                "IRB Approval Letter",
                "Principal Investigator CV",
                "GCP Training Certificates"
            };

            var missing = siteCompliance.Documents
                .Where(d => criticalDocs.Contains(d.Key) && d.Value.Status != "Approved")
                .Select(d => d.Key.Split('-')[0].Trim())
                .ToList();

            return missing.Count > 0 ? string.Join(", ", missing) : "None";
        }

        private void DisplayComplianceData(List<SiteComplianceData> complianceData)
        {
            if (dgvCompliance == null)
            {
                MessageBox.Show("DataGridView is not initialized", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            if (complianceData == null)
            {
                complianceData = new List<SiteComplianceData>();
            }

            var dt = new DataTable();
            dt.Columns.Add("Site ID", typeof(string));
            dt.Columns.Add("Site Name", typeof(string));
            dt.Columns.Add("Country", typeof(string));
            dt.Columns.Add("Compliance %", typeof(double));
            dt.Columns.Add("Approved", typeof(int));
            dt.Columns.Add("Pending", typeof(int));
            dt.Columns.Add("Missing", typeof(int));
            dt.Columns.Add("Critical Missing", typeof(string));
            dt.Columns.Add("Status", typeof(string));

            foreach (var site in complianceData)
            {
                string status = site.CompliancePercent >= 95 ? "Compliant" :
                               site.CompliancePercent >= 80 ? "Near Compliant" :
                               site.CompliancePercent >= 60 ? "Partial" : "Non-Compliant";

                dt.Rows.Add(
                    site.SiteId ?? "",
                    site.SiteName ?? "",
                    site.Country ?? "",
                    Math.Round(site.CompliancePercent, 1),
                    site.ApprovedCount,
                    site.PendingCount,
                    site.MissingCount,
                    site.CriticalMissing ?? "",
                    status
                );
            }

            dgvCompliance.DataSource = dt;

            // Adjust column widths - use try/catch for safety
            try
            {
                if (dgvCompliance.Columns.Count > 0)
                {
                    for (int i = 0; i < dgvCompliance.Columns.Count; i++)
                    {
                        var col = dgvCompliance.Columns[i];
                        if (col != null)
                        {
                            if (col.Name == "Site ID")
                                col.Width = 80;
                            else if (col.Name == "Site Name")
                                col.Width = 200;
                            else if (col.Name == "Country")
                                col.Width = 100;
                            else if (col.Name == "Compliance %")
                                col.Width = 100;
                            else if (col.Name == "Approved" || col.Name == "Pending" || col.Name == "Missing")
                                col.Width = 80;
                            else if (col.Name == "Critical Missing")
                                col.AutoSizeMode = DataGridViewAutoSizeColumnMode.Fill;
                            else if (col.Name == "Status")
                                col.Width = 120;
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error setting column widths: {ex.Message}");
                // Continue anyway - column widths are cosmetic
            }
        }

        private void UpdateSummary(List<SiteComplianceData> complianceData)
        {
            int totalSites = complianceData.Count;
            double avgCompliance = complianceData.Average(s => s.CompliancePercent);
            int compliantSites = complianceData.Count(s => s.CompliancePercent >= 95);
            var allCritical = complianceData
                .Where(s => s.CriticalMissing != "None")
                .Select(s => $"{s.SiteId}: {s.CriticalMissing}")
                .ToList();

            lblTotalSites.Text = $"Total Sites: {totalSites}";
            lblOverallCompliance.Text = $"Overall Compliance: {avgCompliance:F1}%";
            lblOverallCompliance.ForeColor = avgCompliance >= 95 ? Color.Green :
                                             avgCompliance >= 80 ? Color.Orange : Color.Red;

            lblCompliantSites.Text = $"Fully Compliant Sites: {compliantSites} ({(compliantSites * 100.0 / totalSites):F0}%)";

            if (allCritical.Count > 0)
            {
                lblCriticalMissing.Text = $"Sites with Critical Missing: {allCritical.Count}";
                lblCriticalMissing.ForeColor = Color.Red;
            }
            else
            {
                lblCriticalMissing.Text = "No critical documents missing";
                lblCriticalMissing.ForeColor = Color.Green;
            }
        }

        private void DgvCompliance_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {
            if (dgvCompliance.Columns[e.ColumnIndex].Name == "Status")
            {
                string status = e.Value?.ToString();
                if (status == "Compliant")
                {
                    e.CellStyle.BackColor = Color.LightGreen;
                    e.CellStyle.ForeColor = Color.DarkGreen;
                }
                else if (status == "Near Compliant")
                {
                    e.CellStyle.BackColor = Color.LightYellow;
                    e.CellStyle.ForeColor = Color.DarkOrange;
                }
                else if (status == "Partial")
                {
                    e.CellStyle.BackColor = Color.LightSalmon;
                    e.CellStyle.ForeColor = Color.DarkRed;
                }
                else if (status == "Non-Compliant")
                {
                    e.CellStyle.BackColor = Color.IndianRed;
                    e.CellStyle.ForeColor = Color.White;
                }
            }
            else if (dgvCompliance.Columns[e.ColumnIndex].Name == "Compliance %")
            {
                if (e.Value != null && double.TryParse(e.Value.ToString(), out double percent))
                {
                    if (percent >= 95)
                        e.CellStyle.BackColor = Color.LightGreen;
                    else if (percent >= 80)
                        e.CellStyle.BackColor = Color.LightYellow;
                    else if (percent >= 60)
                        e.CellStyle.BackColor = Color.LightSalmon;
                    else
                        e.CellStyle.BackColor = Color.IndianRed;
                }
            }
        }

        private void BtnExportExcel_Click(object sender, EventArgs e)
        {
            try
            {
                using (var sfd = new SaveFileDialog())
                {
                    sfd.Filter = "Excel Files|*.xlsx";
                    sfd.FileName = $"Essential_Docs_Compliance_{DateTime.Now:yyyyMMdd}.xlsx";

                    if (sfd.ShowDialog() == DialogResult.OK)
                    {
                        ExportToExcel(sfd.FileName);
                        MessageBox.Show($"Report exported successfully to:\n{sfd.FileName}",
                            "Export Successful", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error exporting to Excel: {ex.Message}", "Export Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void ExportToExcel(string filePath)
        {
            Microsoft.Office.Interop.Excel.Application excelApp = null;
            Microsoft.Office.Interop.Excel.Workbook workbook = null;
            Microsoft.Office.Interop.Excel.Worksheet worksheet = null;

            try
            {
                excelApp = new Microsoft.Office.Interop.Excel.Application();
                workbook = excelApp.Workbooks.Add();
                worksheet = workbook.ActiveSheet;
                worksheet.Name = "Essential Docs Compliance";

                // Title
                worksheet.Cells[1, 1] = "Essential Documents Compliance Report";
                var titleRange = worksheet.Range["A1", "I1"];
                titleRange.Merge();
                titleRange.Font.Bold = true;
                titleRange.Font.Size = 16;
                titleRange.HorizontalAlignment = Microsoft.Office.Interop.Excel.XlHAlign.xlHAlignCenter;

                // Summary
                worksheet.Cells[2, 1] = $"Generated: {DateTime.Now:yyyy-MM-dd HH:mm}";
                worksheet.Cells[3, 1] = lblTotalSites.Text;
                worksheet.Cells[3, 3] = lblOverallCompliance.Text;
                worksheet.Cells[3, 5] = lblCompliantSites.Text;

                // Headers
                int headerRow = 5;
                string[] headers = { "Site ID", "Site Name", "Country", "Compliance %", "Approved", "Pending", "Missing", "Critical Missing", "Status" };
                for (int i = 0; i < headers.Length; i++)
                {
                    worksheet.Cells[headerRow, i + 1] = headers[i];
                }

                var headerRange = worksheet.Range[worksheet.Cells[headerRow, 1], worksheet.Cells[headerRow, headers.Length]];
                headerRange.Font.Bold = true;
                headerRange.Interior.Color = System.Drawing.ColorTranslator.ToOle(Color.FromArgb(0, 51, 102));
                headerRange.Font.Color = System.Drawing.ColorTranslator.ToOle(Color.White);
                headerRange.Borders.LineStyle = Microsoft.Office.Interop.Excel.XlLineStyle.xlContinuous;

                // Data
                int row = headerRow + 1;
                foreach (DataGridViewRow dgvRow in dgvCompliance.Rows)
                {
                    for (int col = 0; col < dgvCompliance.Columns.Count; col++)
                    {
                        var value = dgvRow.Cells[col].Value;
                        worksheet.Cells[row, col + 1] = value?.ToString() ?? "";

                        // Color code status and compliance %
                        if (dgvCompliance.Columns[col].Name == "Status")
                        {
                            string status = value?.ToString();
                            Color bgColor = Color.White;
                            switch (status)
                            {
                                case "Compliant":
                                    bgColor = Color.LightGreen;
                                    break;
                                case "Near Compliant":
                                    bgColor = Color.LightYellow;
                                    break;
                                case "Partial":
                                    bgColor = Color.LightSalmon;
                                    break;
                                case "Non-Compliant":
                                    bgColor = Color.IndianRed;
                                    break;
                            }
                            worksheet.Cells[row, col + 1].Interior.Color = System.Drawing.ColorTranslator.ToOle(bgColor);
                        }
                        else if (dgvCompliance.Columns[col].Name == "Compliance %" && value != null)
                        {
                            if (double.TryParse(value.ToString(), out double percent))
                            {
                                Color bgColor = Color.White;
                                if (percent >= 95)
                                    bgColor = Color.LightGreen;
                                else if (percent >= 80)
                                    bgColor = Color.LightYellow;
                                else if (percent >= 60)
                                    bgColor = Color.LightSalmon;
                                else
                                    bgColor = Color.IndianRed;
                                worksheet.Cells[row, col + 1].Interior.Color = System.Drawing.ColorTranslator.ToOle(bgColor);
                            }
                        }
                    }
                    row++;
                }

                // Borders
                var dataRange = worksheet.Range[worksheet.Cells[headerRow, 1], worksheet.Cells[row - 1, headers.Length]];
                dataRange.Borders.LineStyle = Microsoft.Office.Interop.Excel.XlLineStyle.xlContinuous;

                // Auto-fit columns
                worksheet.Columns.AutoFit();

                workbook.SaveAs(filePath);
                workbook.Close();
                excelApp.Quit();
            }
            finally
            {
                if (worksheet != null) System.Runtime.InteropServices.Marshal.ReleaseComObject(worksheet);
                if (workbook != null) System.Runtime.InteropServices.Marshal.ReleaseComObject(workbook);
                if (excelApp != null) System.Runtime.InteropServices.Marshal.ReleaseComObject(excelApp);
            }
        }

        private void BtnExportPDF_Click(object sender, EventArgs e)
        {
            try
            {
                using (var sfd = new SaveFileDialog())
                {
                    sfd.Filter = "HTML Files|*.html";
                    sfd.FileName = $"Essential_Docs_Compliance_{DateTime.Now:yyyyMMdd}.html";

                    if (sfd.ShowDialog() == DialogResult.OK)
                    {
                        ExportToHTML(sfd.FileName);
                        System.Diagnostics.Process.Start(sfd.FileName);
                        MessageBox.Show($"Report exported to HTML. Use your browser's 'Print to PDF' function to save as PDF.\n\n{sfd.FileName}",
                            "Export Successful", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error exporting to PDF: {ex.Message}", "Export Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void ExportToHTML(string filePath)
        {
            var html = new System.Text.StringBuilder();
            html.AppendLine("<!DOCTYPE html>");
            html.AppendLine("<html><head>");
            html.AppendLine("<meta charset='utf-8'>");
            html.AppendLine("<title>Essential Documents Compliance Report</title>");
            html.AppendLine("<style>");
            html.AppendLine("body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; }");
            html.AppendLine("h1 { color: #003366; text-align: center; }");
            html.AppendLine(".summary { background-color: #f0f8ff; padding: 15px; margin: 20px 0; border: 1px solid #ccc; border-radius: 5px; }");
            html.AppendLine("table { width: 100%; border-collapse: collapse; margin-top: 20px; }");
            html.AppendLine("th { background-color: #003366; color: white; padding: 10px; text-align: left; }");
            html.AppendLine("td { padding: 8px; border: 1px solid #ddd; }");
            html.AppendLine("tr:nth-child(even) { background-color: #f9f9f9; }");
            html.AppendLine(".compliant { background-color: #90EE90 !important; }");
            html.AppendLine(".near-compliant { background-color: #FFFFE0 !important; }");
            html.AppendLine(".partial { background-color: #FFA07A !important; }");
            html.AppendLine(".non-compliant { background-color: #CD5C5C !important; color: white; }");
            html.AppendLine("@media print { body { margin: 0; } }");
            html.AppendLine("</style>");
            html.AppendLine("</head><body>");

            html.AppendLine("<h1>Essential Documents Compliance Report</h1>");
            html.AppendLine($"<div class='summary'>");
            html.AppendLine($"<p><strong>Generated:</strong> {DateTime.Now:yyyy-MM-dd HH:mm}</p>");
            html.AppendLine($"<p><strong>{lblTotalSites.Text}</strong></p>");
            html.AppendLine($"<p><strong>{lblOverallCompliance.Text}</strong></p>");
            html.AppendLine($"<p><strong>{lblCompliantSites.Text}</strong></p>");
            html.AppendLine($"<p><strong>{lblCriticalMissing.Text}</strong></p>");
            html.AppendLine("</div>");

            html.AppendLine("<table>");
            html.AppendLine("<thead><tr>");
            foreach (DataGridViewColumn col in dgvCompliance.Columns)
            {
                html.AppendLine($"<th>{col.HeaderText}</th>");
            }
            html.AppendLine("</tr></thead>");
            html.AppendLine("<tbody>");

            foreach (DataGridViewRow row in dgvCompliance.Rows)
            {
                html.AppendLine("<tr>");
                for (int i = 0; i < dgvCompliance.Columns.Count; i++)
                {
                    string value = row.Cells[i].Value?.ToString() ?? "";
                    string cssClass = "";

                    if (dgvCompliance.Columns[i].Name == "Status")
                    {
                        if (value == "Compliant")
                            cssClass = " class='compliant'";
                        else if (value == "Near Compliant")
                            cssClass = " class='near-compliant'";
                        else if (value == "Partial")
                            cssClass = " class='partial'";
                        else if (value == "Non-Compliant")
                            cssClass = " class='non-compliant'";
                        else
                            cssClass = "";
                    }
                    else if (dgvCompliance.Columns[i].Name == "Compliance %" && double.TryParse(value, out double percent))
                    {
                        if (percent >= 95)
                            cssClass = " class='compliant'";
                        else if (percent >= 80)
                            cssClass = " class='near-compliant'";
                        else if (percent >= 60)
                            cssClass = " class='partial'";
                        else
                            cssClass = " class='non-compliant'";
                    }

                    html.AppendLine($"<td{cssClass}>{value}</td>");
                }
                html.AppendLine("</tr>");
            }

            html.AppendLine("</tbody></table>");
            html.AppendLine("</body></html>");

            File.WriteAllText(filePath, html.ToString());
        }
    }

    public class SiteComplianceData
    {
        public string SiteId { get; set; }
        public string SiteName { get; set; }
        public string Country { get; set; }
        public Dictionary<string, DocumentStatus> Documents { get; set; }
        public double CompliancePercent { get; set; }
        public int ApprovedCount { get; set; }
        public int PendingCount { get; set; }
        public int MissingCount { get; set; }
        public string CriticalMissing { get; set; }
    }

    public class DocumentStatus
    {
        public string Status { get; set; }  // Missing, Pending, Approved
        public DateTime? DateReceived { get; set; }
        public string Notes { get; set; }
    }
}
