using System;
using System.Collections.Generic;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using IlanaPM.AddIn.Models;
using MSProject = Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn
{
    /// <summary>
    /// Site Status Dashboard Report
    /// Shows overview of all clinical sites with activation status, documents completion, and timeline status
    /// </summary>
    public partial class SiteStatusDashboardForm : Form
    {
        private MSProject.Application msProjectApp;
        private ClinicalProjectConfiguration config;
        private List<SiteStatusMetrics> siteMetrics;

        // UI Controls
        private Panel pnlSummary;
        private Label lblTotalSites;
        private Label lblActiveSites;
        private Label lblEnrollingSites;
        private Label lblClosedSites;
        private Label lblAverageCompletion;
        private Label lblSitesAtRisk;

        private DataGridView dgvSites;
        private Panel pnlButtons;
        private Button btnExportExcel;
        private Button btnExportPDF;
        private Button btnRefresh;
        private Button btnClose;

        public SiteStatusDashboardForm(MSProject.Application app)
        {
            this.msProjectApp = app;
            InitializeComponent();
            LoadData();
        }

        private void InitializeComponent()
        {
            this.Text = "Site Status Dashboard";
            this.Size = new Size(1200, 700);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.MinimumSize = new Size(1000, 600);

            // Summary Panel
            pnlSummary = new Panel
            {
                Dock = DockStyle.Top,
                Height = 120,
                BackColor = Color.FromArgb(240, 240, 240),
                Padding = new Padding(10)
            };

            // Summary Labels
            lblTotalSites = CreateSummaryLabel("Total Sites: 0", new Point(20, 15), Color.DarkBlue);
            lblActiveSites = CreateSummaryLabel("Active: 0", new Point(20, 45), Color.Green);
            lblEnrollingSites = CreateSummaryLabel("Enrolling: 0", new Point(20, 75), Color.DarkGreen);

            lblClosedSites = CreateSummaryLabel("Closed: 0", new Point(200, 45), Color.Gray);
            lblSitesAtRisk = CreateSummaryLabel("At Risk: 0", new Point(200, 75), Color.Red);

            lblAverageCompletion = CreateSummaryLabel("Avg Docs Completion: 0%", new Point(400, 45), Color.DarkOrange);

            pnlSummary.Controls.Add(lblTotalSites);
            pnlSummary.Controls.Add(lblActiveSites);
            pnlSummary.Controls.Add(lblEnrollingSites);
            pnlSummary.Controls.Add(lblClosedSites);
            pnlSummary.Controls.Add(lblSitesAtRisk);
            pnlSummary.Controls.Add(lblAverageCompletion);

            // DataGridView
            dgvSites = new DataGridView
            {
                Dock = DockStyle.Fill,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
                AllowUserToAddRows = false,
                AllowUserToDeleteRows = false,
                ReadOnly = true,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect,
                MultiSelect = false,
                RowHeadersVisible = false,
                BackgroundColor = Color.White
            };

            // Button Panel
            pnlButtons = new Panel
            {
                Dock = DockStyle.Bottom,
                Height = 60,
                Padding = new Padding(10)
            };

            btnExportExcel = new Button
            {
                Text = "Export to Excel",
                Location = new Point(10, 15),
                Size = new Size(120, 35)
            };
            btnExportExcel.Click += btnExportExcel_Click;

            btnExportPDF = new Button
            {
                Text = "Export to PDF",
                Location = new Point(140, 15),
                Size = new Size(120, 35)
            };
            btnExportPDF.Click += btnExportPDF_Click;

            btnRefresh = new Button
            {
                Text = "Refresh",
                Location = new Point(270, 15),
                Size = new Size(100, 35)
            };
            btnRefresh.Click += btnRefresh_Click;

            btnClose = new Button
            {
                Text = "Close",
                Location = new Point(380, 15),
                Size = new Size(100, 35)
            };
            btnClose.Click += (s, e) => this.Close();

            pnlButtons.Controls.Add(btnExportExcel);
            pnlButtons.Controls.Add(btnExportPDF);
            pnlButtons.Controls.Add(btnRefresh);
            pnlButtons.Controls.Add(btnClose);

            // Add controls to form
            this.Controls.Add(dgvSites);
            this.Controls.Add(pnlSummary);
            this.Controls.Add(pnlButtons);
        }

        private Label CreateSummaryLabel(string text, Point location, Color foreColor)
        {
            return new Label
            {
                Text = text,
                Location = location,
                AutoSize = true,
                Font = new Font("Segoe UI", 10F, FontStyle.Bold),
                ForeColor = foreColor
            };
        }

        private void LoadData()
        {
            try
            {
                // Load configuration from project
                config = ClinicalProjectConfiguration.LoadFromProject(msProjectApp);

                if (config.Sites == null || config.Sites.Count == 0)
                {
                    MessageBox.Show(
                        "No sites found in this project.\n\n" +
                        "Please run Clinical Project Manager to add sites first.",
                        "No Sites",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);
                    return;
                }

                // Calculate metrics for each site
                siteMetrics = new List<SiteStatusMetrics>();
                foreach (var site in config.Sites)
                {
                    var metrics = CalculateSiteMetrics(site);
                    siteMetrics.Add(metrics);
                }

                // Update summary
                UpdateSummary();

                // Populate grid
                PopulateGrid();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading site data: {ex.Message}",
                    "Load Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private SiteStatusMetrics CalculateSiteMetrics(SiteConfiguration site)
        {
            var metrics = new SiteStatusMetrics
            {
                SiteId = site.SiteId,
                Country = site.CountryCode,
                PrincipalInvestigator = site.PrincipalInvestigator ?? "Not Assigned",
                ActivationStatus = DetermineActivationStatus(site),
                TimelineStatus = DetermineTimelineStatus(site),
                DocsCompletionPercent = CalculateDocsCompletion(site),
                IRBApprovalDate = GetIRBApprovalDate(site)
            };

            return metrics;
        }

        private string DetermineActivationStatus(SiteConfiguration site)
        {
            // Check task status for this site
            if (msProjectApp.ActiveProject == null) return "Unknown";

            int startupTasks = 0;
            int completedStartupTasks = 0;
            int implementationTasks = 0;
            int completedImplementationTasks = 0;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                string stage = task.GetField(MSProject.PjField.pjTaskText12)?.ToString() ?? "";

                if (stage == "Startup")
                {
                    startupTasks++;
                    if (task.PercentComplete >= 100)
                        completedStartupTasks++;
                }
                else if (stage == "Implementation")
                {
                    implementationTasks++;
                    if (task.PercentComplete >= 100)
                        completedImplementationTasks++;
                }
            }

            // Determine status based on task completion
            if (startupTasks == 0 && implementationTasks == 0)
                return "Not Started";

            if (startupTasks > 0 && completedStartupTasks < startupTasks)
                return "In Startup";

            if (startupTasks > 0 && completedStartupTasks == startupTasks && implementationTasks > 0)
                return "Activated";

            if (implementationTasks > 0 && completedImplementationTasks > 0)
                return "Enrolling";

            return "Active";
        }

        private string DetermineTimelineStatus(SiteConfiguration site)
        {
            // Check if site has delayed tasks
            if (msProjectApp.ActiveProject == null) return "Unknown";

            int totalTasks = 0;
            int delayedTasks = 0;
            DateTime today = DateTime.Today;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                totalTasks++;

                // Check if task is delayed (finish date < today and not 100% complete)
                if (task.Finish < today && task.PercentComplete < 100)
                {
                    delayedTasks++;
                }
            }

            if (totalTasks == 0) return "No Tasks";

            double delayedPercent = (double)delayedTasks / totalTasks * 100;

            if (delayedPercent >= 20)
                return "Delayed";
            else if (delayedPercent >= 10)
                return "At Risk";
            else
                return "On Track";
        }

        private int CalculateDocsCompletion(SiteConfiguration site)
        {
            // TODO: Integrate with Essential Documents Tracker
            // For now, return a placeholder calculation based on task completion
            if (msProjectApp.ActiveProject == null) return 0;

            int totalDocs = 0;
            int completedDocs = 0;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                string category = task.GetField(MSProject.PjField.pjTaskText4)?.ToString() ?? "";
                if (category.Contains("Document") || category.Contains("IRB") || category.Contains("Regulatory"))
                {
                    totalDocs++;
                    if (task.PercentComplete >= 100)
                        completedDocs++;
                }
            }

            if (totalDocs == 0) return 0;
            return (int)((double)completedDocs / totalDocs * 100);
        }

        private DateTime? GetIRBApprovalDate(SiteConfiguration site)
        {
            // Look for IRB approval task
            if (msProjectApp.ActiveProject == null) return null;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                if (task.Name.Contains("IRB") && task.Name.Contains("Approval") && task.PercentComplete >= 100)
                {
                    return task.ActualFinish;
                }
            }

            return null;
        }

        private void UpdateSummary()
        {
            if (siteMetrics == null || siteMetrics.Count == 0) return;

            int total = siteMetrics.Count;
            int active = siteMetrics.Count(s => s.ActivationStatus == "Activated" || s.ActivationStatus == "Active");
            int enrolling = siteMetrics.Count(s => s.ActivationStatus == "Enrolling");
            int closed = siteMetrics.Count(s => s.ActivationStatus == "Closed");
            int atRisk = siteMetrics.Count(s => s.TimelineStatus == "At Risk" || s.TimelineStatus == "Delayed");
            double avgCompletion = siteMetrics.Average(s => s.DocsCompletionPercent);

            lblTotalSites.Text = $"Total Sites: {total}";
            lblActiveSites.Text = $"Active: {active}";
            lblEnrollingSites.Text = $"Enrolling: {enrolling}";
            lblClosedSites.Text = $"Closed: {closed}";
            lblSitesAtRisk.Text = $"At Risk: {atRisk}";
            lblAverageCompletion.Text = $"Avg Docs Completion: {avgCompletion:F1}%";
        }

        private void PopulateGrid()
        {
            var dt = new DataTable();
            dt.Columns.Add("Site ID", typeof(string));
            dt.Columns.Add("Country", typeof(string));
            dt.Columns.Add("Principal Investigator", typeof(string));
            dt.Columns.Add("Activation Status", typeof(string));
            dt.Columns.Add("Timeline Status", typeof(string));
            dt.Columns.Add("Docs %", typeof(int));
            dt.Columns.Add("IRB Approval Date", typeof(string));

            foreach (var metrics in siteMetrics)
            {
                dt.Rows.Add(
                    metrics.SiteId,
                    metrics.Country,
                    metrics.PrincipalInvestigator,
                    metrics.ActivationStatus,
                    metrics.TimelineStatus,
                    metrics.DocsCompletionPercent,
                    metrics.IRBApprovalDate?.ToString("yyyy-MM-dd") ?? "Pending"
                );
            }

            dgvSites.DataSource = dt;

            // Apply cell formatting for status columns
            dgvSites.CellFormatting += DgvSites_CellFormatting;
        }

        private void DgvSites_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {
            if (dgvSites.Columns[e.ColumnIndex].Name == "Activation Status")
            {
                string status = e.Value?.ToString() ?? "";
                switch (status)
                {
                    case "Enrolling":
                        e.CellStyle.BackColor = Color.LightGreen;
                        e.CellStyle.ForeColor = Color.DarkGreen;
                        break;
                    case "Activated":
                    case "Active":
                        e.CellStyle.BackColor = Color.LightBlue;
                        e.CellStyle.ForeColor = Color.DarkBlue;
                        break;
                    case "In Startup":
                        e.CellStyle.BackColor = Color.LightYellow;
                        e.CellStyle.ForeColor = Color.DarkOrange;
                        break;
                    case "Not Started":
                        e.CellStyle.BackColor = Color.LightGray;
                        e.CellStyle.ForeColor = Color.DarkGray;
                        break;
                }
            }
            else if (dgvSites.Columns[e.ColumnIndex].Name == "Timeline Status")
            {
                string status = e.Value?.ToString() ?? "";
                switch (status)
                {
                    case "On Track":
                        e.CellStyle.BackColor = Color.LightGreen;
                        e.CellStyle.ForeColor = Color.DarkGreen;
                        break;
                    case "At Risk":
                        e.CellStyle.BackColor = Color.LightYellow;
                        e.CellStyle.ForeColor = Color.DarkOrange;
                        break;
                    case "Delayed":
                        e.CellStyle.BackColor = Color.LightCoral;
                        e.CellStyle.ForeColor = Color.DarkRed;
                        break;
                }
            }
        }

        private void btnExportExcel_Click(object sender, EventArgs e)
        {
            try
            {
                var saveDialog = new SaveFileDialog
                {
                    Filter = "Excel Files (*.xlsx)|*.xlsx",
                    FileName = $"SiteStatusDashboard_{DateTime.Now:yyyyMMdd}.xlsx",
                    Title = "Export to Excel"
                };

                if (saveDialog.ShowDialog() == DialogResult.OK)
                {
                    ExportToExcel(saveDialog.FileName);
                    MessageBox.Show($"Report exported successfully to:\n{saveDialog.FileName}",
                        "Export Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);

                    // Open the Excel file
                    System.Diagnostics.Process.Start(saveDialog.FileName);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error exporting to Excel: {ex.Message}",
                    "Export Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
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
                worksheet.Name = "Site Status Dashboard";

                // Title
                worksheet.Cells[1, 1] = "Site Status Dashboard Report";
                worksheet.Range["A1:G1"].Merge();
                worksheet.Range["A1"].Font.Size = 16;
                worksheet.Range["A1"].Font.Bold = true;

                worksheet.Cells[2, 1] = $"Study: {config.StudyName}";
                worksheet.Cells[3, 1] = $"Generated: {DateTime.Now:yyyy-MM-dd HH:mm:ss}";

                // Summary section
                int row = 5;
                worksheet.Cells[row, 1] = "SUMMARY";
                worksheet.Range[$"A{row}:G{row}"].Font.Bold = true;
                worksheet.Range[$"A{row}:G{row}"].Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightGray);

                row++;
                worksheet.Cells[row, 1] = "Total Sites:";
                worksheet.Cells[row, 2] = siteMetrics.Count;
                row++;
                worksheet.Cells[row, 1] = "Active Sites:";
                worksheet.Cells[row, 2] = siteMetrics.Count(s => s.ActivationStatus == "Activated" || s.ActivationStatus == "Active");
                row++;
                worksheet.Cells[row, 1] = "Enrolling Sites:";
                worksheet.Cells[row, 2] = siteMetrics.Count(s => s.ActivationStatus == "Enrolling");
                row++;
                worksheet.Cells[row, 1] = "Sites At Risk:";
                worksheet.Cells[row, 2] = siteMetrics.Count(s => s.TimelineStatus == "At Risk" || s.TimelineStatus == "Delayed");
                row++;
                worksheet.Cells[row, 1] = "Average Documents Completion:";
                worksheet.Cells[row, 2] = $"{siteMetrics.Average(s => s.DocsCompletionPercent):F1}%";

                // Data table header
                row += 2;
                int headerRow = row;
                worksheet.Cells[row, 1] = "Site ID";
                worksheet.Cells[row, 2] = "Country";
                worksheet.Cells[row, 3] = "Principal Investigator";
                worksheet.Cells[row, 4] = "Activation Status";
                worksheet.Cells[row, 5] = "Timeline Status";
                worksheet.Cells[row, 6] = "Docs %";
                worksheet.Cells[row, 7] = "IRB Approval Date";

                // Format header
                worksheet.Range[$"A{headerRow}:G{headerRow}"].Font.Bold = true;
                worksheet.Range[$"A{headerRow}:G{headerRow}"].Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.FromArgb(47, 117, 181));
                worksheet.Range[$"A{headerRow}:G{headerRow}"].Font.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.White);

                // Data rows
                row++;
                foreach (var metrics in siteMetrics)
                {
                    worksheet.Cells[row, 1] = metrics.SiteId;
                    worksheet.Cells[row, 2] = metrics.Country;
                    worksheet.Cells[row, 3] = metrics.PrincipalInvestigator;
                    worksheet.Cells[row, 4] = metrics.ActivationStatus;
                    worksheet.Cells[row, 5] = metrics.TimelineStatus;
                    worksheet.Cells[row, 6] = metrics.DocsCompletionPercent;
                    worksheet.Cells[row, 7] = metrics.IRBApprovalDate?.ToString("yyyy-MM-dd") ?? "Pending";

                    // Color-code status cells
                    var activationCell = worksheet.Cells[row, 4];
                    switch (metrics.ActivationStatus)
                    {
                        case "Enrolling":
                            activationCell.Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightGreen);
                            break;
                        case "Activated":
                        case "Active":
                            activationCell.Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightBlue);
                            break;
                        case "In Startup":
                            activationCell.Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightYellow);
                            break;
                    }

                    var timelineCell = worksheet.Cells[row, 5];
                    switch (metrics.TimelineStatus)
                    {
                        case "On Track":
                            timelineCell.Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightGreen);
                            break;
                        case "At Risk":
                            timelineCell.Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightYellow);
                            break;
                        case "Delayed":
                            timelineCell.Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightCoral);
                            break;
                    }

                    row++;
                }

                // Auto-fit columns
                worksheet.Columns.AutoFit();

                // Add borders to data table
                var tableRange = worksheet.Range[$"A{headerRow}:G{row - 1}"];
                tableRange.Borders.LineStyle = Microsoft.Office.Interop.Excel.XlLineStyle.xlContinuous;

                // Save and close
                workbook.SaveAs(filePath);
                workbook.Close();
                excelApp.Quit();
            }
            finally
            {
                // Clean up COM objects
                if (worksheet != null) System.Runtime.InteropServices.Marshal.ReleaseComObject(worksheet);
                if (workbook != null) System.Runtime.InteropServices.Marshal.ReleaseComObject(workbook);
                if (excelApp != null) System.Runtime.InteropServices.Marshal.ReleaseComObject(excelApp);
            }
        }

        private void btnExportPDF_Click(object sender, EventArgs e)
        {
            try
            {
                var saveDialog = new SaveFileDialog
                {
                    Filter = "HTML Files (*.html)|*.html",
                    FileName = $"SiteStatusDashboard_{DateTime.Now:yyyyMMdd}.html",
                    Title = "Export to HTML (Print to PDF)"
                };

                if (saveDialog.ShowDialog() == DialogResult.OK)
                {
                    ExportToHtml(saveDialog.FileName);

                    MessageBox.Show(
                        $"Report exported successfully to:\n{saveDialog.FileName}\n\n" +
                        "To create a PDF:\n" +
                        "1. Open the HTML file in your web browser\n" +
                        "2. Use File → Print or Ctrl+P\n" +
                        "3. Select 'Save as PDF' as the printer\n" +
                        "4. Click 'Save'",
                        "Export Complete",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information);

                    // Open the HTML file in default browser
                    System.Diagnostics.Process.Start(saveDialog.FileName);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error exporting to HTML: {ex.Message}",
                    "Export Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void ExportToHtml(string filePath)
        {
            var html = new System.Text.StringBuilder();

            html.AppendLine("<!DOCTYPE html>");
            html.AppendLine("<html>");
            html.AppendLine("<head>");
            html.AppendLine("    <meta charset='UTF-8'>");
            html.AppendLine("    <title>Site Status Dashboard Report</title>");
            html.AppendLine("    <style>");
            html.AppendLine("        body { font-family: Arial, sans-serif; margin: 20px; }");
            html.AppendLine("        h1 { color: #2c3e50; }");
            html.AppendLine("        .summary { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }");
            html.AppendLine("        .summary-item { display: inline-block; margin-right: 30px; margin-bottom: 10px; }");
            html.AppendLine("        .summary-label { font-weight: bold; color: #555; }");
            html.AppendLine("        .summary-value { font-size: 18px; color: #2c3e50; }");
            html.AppendLine("        table { border-collapse: collapse; width: 100%; margin-top: 20px; }");
            html.AppendLine("        th { background-color: #2c3e50; color: white; padding: 12px; text-align: left; }");
            html.AppendLine("        td { padding: 10px; border-bottom: 1px solid #ddd; }");
            html.AppendLine("        tr:hover { background-color: #f5f5f5; }");
            html.AppendLine("        .status-enrolling { background-color: #d4edda; color: #155724; padding: 5px 10px; border-radius: 3px; }");
            html.AppendLine("        .status-activated { background-color: #d1ecf1; color: #0c5460; padding: 5px 10px; border-radius: 3px; }");
            html.AppendLine("        .status-startup { background-color: #fff3cd; color: #856404; padding: 5px 10px; border-radius: 3px; }");
            html.AppendLine("        .status-notstarted { background-color: #e2e3e5; color: #383d41; padding: 5px 10px; border-radius: 3px; }");
            html.AppendLine("        .timeline-ontrack { background-color: #d4edda; color: #155724; padding: 5px 10px; border-radius: 3px; }");
            html.AppendLine("        .timeline-atrisk { background-color: #fff3cd; color: #856404; padding: 5px 10px; border-radius: 3px; }");
            html.AppendLine("        .timeline-delayed { background-color: #f8d7da; color: #721c24; padding: 5px 10px; border-radius: 3px; }");
            html.AppendLine("        .footer { margin-top: 30px; font-size: 12px; color: #999; }");
            html.AppendLine("        @media print {");
            html.AppendLine("            body { margin: 0; }");
            html.AppendLine("            .no-print { display: none; }");
            html.AppendLine("        }");
            html.AppendLine("    </style>");
            html.AppendLine("</head>");
            html.AppendLine("<body>");

            // Title
            html.AppendLine("    <h1>Site Status Dashboard Report</h1>");
            html.AppendLine($"    <p><strong>Study:</strong> {config.StudyName}</p>");
            html.AppendLine($"    <p><strong>Generated:</strong> {DateTime.Now:yyyy-MM-dd HH:mm:ss}</p>");

            // Summary Section
            html.AppendLine("    <div class='summary'>");
            html.AppendLine("        <h2>Summary</h2>");
            html.AppendLine($"        <div class='summary-item'><span class='summary-label'>Total Sites:</span> <span class='summary-value'>{siteMetrics.Count}</span></div>");
            html.AppendLine($"        <div class='summary-item'><span class='summary-label'>Active:</span> <span class='summary-value' style='color: green;'>{siteMetrics.Count(s => s.ActivationStatus == "Activated" || s.ActivationStatus == "Active")}</span></div>");
            html.AppendLine($"        <div class='summary-item'><span class='summary-label'>Enrolling:</span> <span class='summary-value' style='color: darkgreen;'>{siteMetrics.Count(s => s.ActivationStatus == "Enrolling")}</span></div>");
            html.AppendLine($"        <div class='summary-item'><span class='summary-label'>At Risk:</span> <span class='summary-value' style='color: red;'>{siteMetrics.Count(s => s.TimelineStatus == "At Risk" || s.TimelineStatus == "Delayed")}</span></div>");
            html.AppendLine($"        <div class='summary-item'><span class='summary-label'>Avg Docs Completion:</span> <span class='summary-value' style='color: darkorange;'>{siteMetrics.Average(s => s.DocsCompletionPercent):F1}%</span></div>");
            html.AppendLine("    </div>");

            // Table
            html.AppendLine("    <table>");
            html.AppendLine("        <thead>");
            html.AppendLine("            <tr>");
            html.AppendLine("                <th>Site ID</th>");
            html.AppendLine("                <th>Country</th>");
            html.AppendLine("                <th>Principal Investigator</th>");
            html.AppendLine("                <th>Activation Status</th>");
            html.AppendLine("                <th>Timeline Status</th>");
            html.AppendLine("                <th>Docs %</th>");
            html.AppendLine("                <th>IRB Approval Date</th>");
            html.AppendLine("            </tr>");
            html.AppendLine("        </thead>");
            html.AppendLine("        <tbody>");

            foreach (var metrics in siteMetrics)
            {
                string activationClass = GetStatusClass(metrics.ActivationStatus);
                string timelineClass = GetTimelineClass(metrics.TimelineStatus);

                html.AppendLine("            <tr>");
                html.AppendLine($"                <td><strong>{metrics.SiteId}</strong></td>");
                html.AppendLine($"                <td>{metrics.Country}</td>");
                html.AppendLine($"                <td>{metrics.PrincipalInvestigator}</td>");
                html.AppendLine($"                <td><span class='{activationClass}'>{metrics.ActivationStatus}</span></td>");
                html.AppendLine($"                <td><span class='{timelineClass}'>{metrics.TimelineStatus}</span></td>");
                html.AppendLine($"                <td>{metrics.DocsCompletionPercent}%</td>");
                html.AppendLine($"                <td>{metrics.IRBApprovalDate?.ToString("yyyy-MM-dd") ?? "Pending"}</td>");
                html.AppendLine("            </tr>");
            }

            html.AppendLine("        </tbody>");
            html.AppendLine("    </table>");

            // Footer
            html.AppendLine("    <div class='footer'>");
            html.AppendLine($"        <p>Report generated by Ilana PM Add-In on {DateTime.Now:yyyy-MM-dd HH:mm:ss}</p>");
            html.AppendLine("    </div>");

            html.AppendLine("</body>");
            html.AppendLine("</html>");

            System.IO.File.WriteAllText(filePath, html.ToString());
        }

        private string GetStatusClass(string status)
        {
            switch (status)
            {
                case "Enrolling":
                    return "status-enrolling";
                case "Activated":
                case "Active":
                    return "status-activated";
                case "In Startup":
                    return "status-startup";
                case "Not Started":
                    return "status-notstarted";
                default:
                    return "";
            }
        }

        private string GetTimelineClass(string status)
        {
            switch (status)
            {
                case "On Track":
                    return "timeline-ontrack";
                case "At Risk":
                    return "timeline-atrisk";
                case "Delayed":
                    return "timeline-delayed";
                default:
                    return "";
            }
        }

        private void btnRefresh_Click(object sender, EventArgs e)
        {
            LoadData();
            MessageBox.Show("Dashboard refreshed successfully.",
                "Refresh Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
    }

    /// <summary>
    /// Site status metrics for dashboard display
    /// </summary>
    public class SiteStatusMetrics
    {
        public string SiteId { get; set; }
        public string Country { get; set; }
        public string PrincipalInvestigator { get; set; }
        public string ActivationStatus { get; set; }
        public string TimelineStatus { get; set; }
        public int DocsCompletionPercent { get; set; }
        public DateTime? IRBApprovalDate { get; set; }
    }
}
