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
    /// Site Activation Timeline Report
    /// Tracks site startup progress, IRB timelines, and bottlenecks
    /// </summary>
    public partial class SiteActivationTimelineForm : Form
    {
        private MSProject.Application msProjectApp;
        private ClinicalProjectConfiguration config;
        private List<SiteActivationMetrics> siteActivationMetrics;

        // UI Controls
        private Panel pnlSummary;
        private Label lblSitesInStartup;
        private Label lblAverageStartupDuration;
        private Label lblCommonBottleneck;
        private Label lblProjectedActivations;

        private DataGridView dgvSiteActivation;
        private Panel pnlButtons;
        private Button btnExportExcel;
        private Button btnExportPDF;
        private Button btnRefresh;
        private Button btnClose;

        public SiteActivationTimelineForm(MSProject.Application app)
        {
            this.msProjectApp = app;
            InitializeComponent();
            LoadData();
        }

        private void InitializeComponent()
        {
            this.Text = "Site Activation Timeline Report";
            this.Size = new Size(1400, 700);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.MinimumSize = new Size(1200, 600);

            // Summary Panel
            pnlSummary = new Panel
            {
                Dock = DockStyle.Top,
                Height = 100,
                BackColor = Color.FromArgb(240, 240, 240),
                Padding = new Padding(10)
            };

            // Summary Labels
            lblSitesInStartup = CreateSummaryLabel("Sites in Startup: 0", new Point(20, 15), Color.DarkBlue);
            lblAverageStartupDuration = CreateSummaryLabel("Avg Startup Duration: 0 days", new Point(20, 45), Color.DarkGreen);
            lblCommonBottleneck = CreateSummaryLabel("Common Bottleneck: None", new Point(400, 15), Color.DarkOrange);
            lblProjectedActivations = CreateSummaryLabel("Projected Activations (30 days): 0", new Point(400, 45), Color.Purple);

            pnlSummary.Controls.Add(lblSitesInStartup);
            pnlSummary.Controls.Add(lblAverageStartupDuration);
            pnlSummary.Controls.Add(lblCommonBottleneck);
            pnlSummary.Controls.Add(lblProjectedActivations);

            // DataGridView
            dgvSiteActivation = new DataGridView
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
            this.Controls.Add(dgvSiteActivation);
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

                // Calculate activation metrics for each site
                siteActivationMetrics = new List<SiteActivationMetrics>();
                foreach (var site in config.Sites)
                {
                    var metrics = CalculateSiteActivationMetrics(site);
                    siteActivationMetrics.Add(metrics);
                }

                // Update summary
                UpdateSummary();

                // Populate grid
                PopulateGrid();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading site activation data: {ex.Message}",
                    "Load Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private SiteActivationMetrics CalculateSiteActivationMetrics(SiteConfiguration site)
        {
            var metrics = new SiteActivationMetrics
            {
                SiteId = site.SiteId,
                Country = site.CountryCode,
                StartupStatus = DetermineStartupStatus(site),
                DocsCollected = CalculateDocsCollected(site),
                TotalDocs = CalculateTotalDocs(site),
                IRBSubmissionDate = GetIRBSubmissionDate(site),
                IRBApprovalDate = GetIRBApprovalDate(site),
                TrainingCompletionPercent = CalculateTrainingCompletion(site),
                ProjectedActivationDate = CalculateProjectedActivationDate(site),
                CurrentBottleneck = IdentifyBottleneck(site),
                StartupDuration = CalculateStartupDuration(site)
            };

            return metrics;
        }

        private string DetermineStartupStatus(SiteConfiguration site)
        {
            if (msProjectApp.ActiveProject == null) return "Unknown";

            int startupTasks = 0;
            int completedStartupTasks = 0;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                string stage = task.GetField(MSProject.PjField.pjTaskText12)?.ToString() ?? "";
                if (stage != "Startup") continue;

                startupTasks++;
                if (task.PercentComplete >= 100)
                    completedStartupTasks++;
            }

            if (startupTasks == 0) return "Not Started";
            if (completedStartupTasks == startupTasks) return "Completed";

            double percent = (double)completedStartupTasks / startupTasks * 100;
            if (percent >= 75) return "Near Complete";
            if (percent >= 50) return "In Progress";
            if (percent >= 25) return "Early Stage";
            return "Just Started";
        }

        private int CalculateDocsCollected(SiteConfiguration site)
        {
            if (msProjectApp.ActiveProject == null) return 0;

            int collected = 0;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                string stage = task.GetField(MSProject.PjField.pjTaskText12)?.ToString() ?? "";
                if (stage != "Startup") continue;

                string category = task.GetField(MSProject.PjField.pjTaskText4)?.ToString() ?? "";
                if (category.Contains("Document") || category.Contains("IRB") || category.Contains("Regulatory"))
                {
                    if (task.PercentComplete >= 100)
                        collected++;
                }
            }

            return collected;
        }

        private int CalculateTotalDocs(SiteConfiguration site)
        {
            if (msProjectApp.ActiveProject == null) return 0;

            int total = 0;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                string stage = task.GetField(MSProject.PjField.pjTaskText12)?.ToString() ?? "";
                if (stage != "Startup") continue;

                string category = task.GetField(MSProject.PjField.pjTaskText4)?.ToString() ?? "";
                if (category.Contains("Document") || category.Contains("IRB") || category.Contains("Regulatory"))
                {
                    total++;
                }
            }

            return total;
        }

        private DateTime? GetIRBSubmissionDate(SiteConfiguration site)
        {
            if (msProjectApp.ActiveProject == null) return null;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                if (task.Name.Contains("IRB") && task.Name.Contains("Submission") && task.PercentComplete >= 100)
                {
                    return task.ActualFinish;
                }
            }

            return null;
        }

        private DateTime? GetIRBApprovalDate(SiteConfiguration site)
        {
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

        private int CalculateTrainingCompletion(SiteConfiguration site)
        {
            if (msProjectApp.ActiveProject == null) return 0;

            int totalTrainingTasks = 0;
            int completedTrainingTasks = 0;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                string stage = task.GetField(MSProject.PjField.pjTaskText12)?.ToString() ?? "";
                if (stage != "Startup") continue;

                if (task.Name.Contains("Training"))
                {
                    totalTrainingTasks++;
                    if (task.PercentComplete >= 100)
                        completedTrainingTasks++;
                }
            }

            if (totalTrainingTasks == 0) return 0;
            return (int)((double)completedTrainingTasks / totalTrainingTasks * 100);
        }

        private DateTime? CalculateProjectedActivationDate(SiteConfiguration site)
        {
            if (msProjectApp.ActiveProject == null) return null;

            // Find the last startup task
            DateTime? latestFinish = null;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                string stage = task.GetField(MSProject.PjField.pjTaskText12)?.ToString() ?? "";
                if (stage != "Startup") continue;

                if (latestFinish == null || task.Finish > latestFinish.Value)
                    latestFinish = task.Finish;
            }

            return latestFinish;
        }

        private string IdentifyBottleneck(SiteConfiguration site)
        {
            if (msProjectApp.ActiveProject == null) return "Unknown";

            // Find incomplete tasks that are delaying startup
            DateTime today = DateTime.Today;
            string bottleneck = "None";
            int maxDelay = 0;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                string stage = task.GetField(MSProject.PjField.pjTaskText12)?.ToString() ?? "";
                if (stage != "Startup") continue;

                if (task.PercentComplete < 100 && task.Finish < today)
                {
                    int delay = (int)(today - task.Finish).TotalDays;
                    if (delay > maxDelay)
                    {
                        maxDelay = delay;
                        bottleneck = task.Name;
                    }
                }
            }

            return maxDelay > 0 ? $"{bottleneck} ({maxDelay}d late)" : "None";
        }

        private int CalculateStartupDuration(SiteConfiguration site)
        {
            if (msProjectApp.ActiveProject == null) return 0;

            DateTime? earliest = null;
            DateTime? latest = null;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task == null) continue;

                string taskSite = task.GetField(MSProject.PjField.pjTaskText11)?.ToString() ?? "";
                if (taskSite != site.SiteId) continue;

                string stage = task.GetField(MSProject.PjField.pjTaskText12)?.ToString() ?? "";
                if (stage != "Startup") continue;

                if (earliest == null || task.Start < earliest.Value)
                    earliest = task.Start;

                if (latest == null || task.Finish > latest.Value)
                    latest = task.Finish;
            }

            if (earliest == null || latest == null) return 0;
            return (int)(latest.Value - earliest.Value).TotalDays;
        }

        private void UpdateSummary()
        {
            if (siteActivationMetrics == null || siteActivationMetrics.Count == 0) return;

            int sitesInStartup = siteActivationMetrics.Count(s =>
                s.StartupStatus != "Not Started" && s.StartupStatus != "Completed");

            double avgDuration = siteActivationMetrics
                .Where(s => s.StartupDuration > 0)
                .Select(s => (double)s.StartupDuration)
                .DefaultIfEmpty(0)
                .Average();

            // Find most common bottleneck
            var bottlenecks = siteActivationMetrics
                .Where(s => s.CurrentBottleneck != "None" && s.CurrentBottleneck != "Unknown")
                .GroupBy(s => s.CurrentBottleneck.Split('(')[0].Trim())
                .OrderByDescending(g => g.Count())
                .FirstOrDefault();

            string commonBottleneck = bottlenecks != null ? $"{bottlenecks.Key} ({bottlenecks.Count()} sites)" : "None";

            int projectionsNext30Days = siteActivationMetrics
                .Count(s => s.ProjectedActivationDate.HasValue &&
                           s.ProjectedActivationDate.Value <= DateTime.Today.AddDays(30));

            lblSitesInStartup.Text = $"Sites in Startup: {sitesInStartup}";
            lblAverageStartupDuration.Text = $"Avg Startup Duration: {avgDuration:F0} days";
            lblCommonBottleneck.Text = $"Common Bottleneck: {commonBottleneck}";
            lblProjectedActivations.Text = $"Projected Activations (30 days): {projectionsNext30Days}";
        }

        private void PopulateGrid()
        {
            var dt = new DataTable();
            dt.Columns.Add("Site ID", typeof(string));
            dt.Columns.Add("Country", typeof(string));
            dt.Columns.Add("Startup Status", typeof(string));
            dt.Columns.Add("Docs Progress", typeof(string));
            dt.Columns.Add("IRB Submission", typeof(string));
            dt.Columns.Add("IRB Approval", typeof(string));
            dt.Columns.Add("Training %", typeof(int));
            dt.Columns.Add("Projected Activation", typeof(string));
            dt.Columns.Add("Current Bottleneck", typeof(string));
            dt.Columns.Add("Duration (days)", typeof(int));

            foreach (var metrics in siteActivationMetrics)
            {
                dt.Rows.Add(
                    metrics.SiteId,
                    metrics.Country,
                    metrics.StartupStatus,
                    $"{metrics.DocsCollected}/{metrics.TotalDocs}",
                    metrics.IRBSubmissionDate?.ToString("yyyy-MM-dd") ?? "Pending",
                    metrics.IRBApprovalDate?.ToString("yyyy-MM-dd") ?? "Pending",
                    metrics.TrainingCompletionPercent,
                    metrics.ProjectedActivationDate?.ToString("yyyy-MM-dd") ?? "TBD",
                    metrics.CurrentBottleneck,
                    metrics.StartupDuration
                );
            }

            dgvSiteActivation.DataSource = dt;

            // Apply cell formatting
            dgvSiteActivation.CellFormatting += DgvSiteActivation_CellFormatting;
        }

        private void DgvSiteActivation_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {
            if (dgvSiteActivation.Columns[e.ColumnIndex].Name == "Startup Status")
            {
                string status = e.Value?.ToString() ?? "";
                switch (status)
                {
                    case "Completed":
                        e.CellStyle.BackColor = Color.LightGreen;
                        e.CellStyle.ForeColor = Color.DarkGreen;
                        break;
                    case "Near Complete":
                        e.CellStyle.BackColor = Color.PaleGreen;
                        e.CellStyle.ForeColor = Color.DarkGreen;
                        break;
                    case "In Progress":
                        e.CellStyle.BackColor = Color.LightBlue;
                        e.CellStyle.ForeColor = Color.DarkBlue;
                        break;
                    case "Early Stage":
                    case "Just Started":
                        e.CellStyle.BackColor = Color.LightYellow;
                        e.CellStyle.ForeColor = Color.DarkOrange;
                        break;
                    case "Not Started":
                        e.CellStyle.BackColor = Color.LightGray;
                        e.CellStyle.ForeColor = Color.DarkGray;
                        break;
                }
            }
            else if (dgvSiteActivation.Columns[e.ColumnIndex].Name == "Current Bottleneck")
            {
                string bottleneck = e.Value?.ToString() ?? "";
                if (bottleneck != "None" && bottleneck != "Unknown")
                {
                    e.CellStyle.BackColor = Color.LightCoral;
                    e.CellStyle.ForeColor = Color.DarkRed;
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
                    FileName = $"SiteActivationTimeline_{DateTime.Now:yyyyMMdd}.xlsx",
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
                worksheet.Name = "Site Activation Timeline";

                // Title
                worksheet.Cells[1, 1] = "Site Activation Timeline Report";
                worksheet.Range["A1:J1"].Merge();
                worksheet.Range["A1"].Font.Size = 16;
                worksheet.Range["A1"].Font.Bold = true;

                worksheet.Cells[2, 1] = $"Study: {config.StudyName}";
                worksheet.Cells[3, 1] = $"Generated: {DateTime.Now:yyyy-MM-dd HH:mm:ss}";

                // Summary section
                int row = 5;
                worksheet.Cells[row, 1] = "SUMMARY";
                worksheet.Range[$"A{row}:J{row}"].Font.Bold = true;
                worksheet.Range[$"A{row}:J{row}"].Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightGray);

                row++;
                worksheet.Cells[row, 1] = "Sites in Startup:";
                worksheet.Cells[row, 2] = siteActivationMetrics.Count(s =>
                    s.StartupStatus != "Not Started" && s.StartupStatus != "Completed");

                row++;
                worksheet.Cells[row, 1] = "Average Startup Duration:";
                worksheet.Cells[row, 2] = $"{siteActivationMetrics.Where(s => s.StartupDuration > 0).Select(s => (double)s.StartupDuration).DefaultIfEmpty(0).Average():F0} days";

                row++;
                var bottlenecks = siteActivationMetrics
                    .Where(s => s.CurrentBottleneck != "None" && s.CurrentBottleneck != "Unknown")
                    .GroupBy(s => s.CurrentBottleneck.Split('(')[0].Trim())
                    .OrderByDescending(g => g.Count())
                    .FirstOrDefault();
                string commonBottleneck = bottlenecks != null ? $"{bottlenecks.Key} ({bottlenecks.Count()} sites)" : "None";
                worksheet.Cells[row, 1] = "Common Bottleneck:";
                worksheet.Cells[row, 2] = commonBottleneck;

                row++;
                worksheet.Cells[row, 1] = "Projected Activations (30 days):";
                worksheet.Cells[row, 2] = siteActivationMetrics.Count(s => s.ProjectedActivationDate.HasValue &&
                           s.ProjectedActivationDate.Value <= DateTime.Today.AddDays(30));

                // Data table header
                row += 2;
                int headerRow = row;
                worksheet.Cells[row, 1] = "Site ID";
                worksheet.Cells[row, 2] = "Country";
                worksheet.Cells[row, 3] = "Startup Status";
                worksheet.Cells[row, 4] = "Docs Progress";
                worksheet.Cells[row, 5] = "IRB Submission";
                worksheet.Cells[row, 6] = "IRB Approval";
                worksheet.Cells[row, 7] = "Training %";
                worksheet.Cells[row, 8] = "Projected Activation";
                worksheet.Cells[row, 9] = "Current Bottleneck";
                worksheet.Cells[row, 10] = "Duration (days)";

                // Format header
                worksheet.Range[$"A{headerRow}:J{headerRow}"].Font.Bold = true;
                worksheet.Range[$"A{headerRow}:J{headerRow}"].Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.FromArgb(47, 117, 181));
                worksheet.Range[$"A{headerRow}:J{headerRow}"].Font.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.White);

                // Data rows
                row++;
                foreach (var metrics in siteActivationMetrics)
                {
                    worksheet.Cells[row, 1] = metrics.SiteId;
                    worksheet.Cells[row, 2] = metrics.Country;
                    worksheet.Cells[row, 3] = metrics.StartupStatus;
                    worksheet.Cells[row, 4] = $"{metrics.DocsCollected}/{metrics.TotalDocs}";
                    worksheet.Cells[row, 5] = metrics.IRBSubmissionDate?.ToString("yyyy-MM-dd") ?? "Pending";
                    worksheet.Cells[row, 6] = metrics.IRBApprovalDate?.ToString("yyyy-MM-dd") ?? "Pending";
                    worksheet.Cells[row, 7] = metrics.TrainingCompletionPercent;
                    worksheet.Cells[row, 8] = metrics.ProjectedActivationDate?.ToString("yyyy-MM-dd") ?? "TBD";
                    worksheet.Cells[row, 9] = metrics.CurrentBottleneck;
                    worksheet.Cells[row, 10] = metrics.StartupDuration;

                    // Color-code status cells
                    var statusCell = worksheet.Cells[row, 3];
                    switch (metrics.StartupStatus)
                    {
                        case "Completed":
                            statusCell.Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightGreen);
                            break;
                        case "Near Complete":
                            statusCell.Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.PaleGreen);
                            break;
                        case "In Progress":
                            statusCell.Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightBlue);
                            break;
                        case "Early Stage":
                        case "Just Started":
                            statusCell.Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightYellow);
                            break;
                    }

                    var bottleneckCell = worksheet.Cells[row, 9];
                    if (metrics.CurrentBottleneck != "None" && metrics.CurrentBottleneck != "Unknown")
                    {
                        bottleneckCell.Interior.Color = System.Drawing.ColorTranslator.ToOle(System.Drawing.Color.LightCoral);
                    }

                    row++;
                }

                // Auto-fit columns
                worksheet.Columns.AutoFit();

                // Add borders to data table
                var tableRange = worksheet.Range[$"A{headerRow}:J{row - 1}"];
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
                    FileName = $"SiteActivationTimeline_{DateTime.Now:yyyyMMdd}.html",
                    Title = "Export to HTML (Print to PDF)"
                };

                if (saveDialog.ShowDialog() == DialogResult.OK)
                {
                    ExportToHtml(saveDialog.FileName);

                    MessageBox.Show(
                        $"Report exported successfully to:\n{saveDialog.FileName}\n\n" +
                        "To create a PDF:\n" +
                        "1. The HTML file will open in your web browser\n" +
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
            html.AppendLine("    <title>Site Activation Timeline Report</title>");
            html.AppendLine("    <style>");
            html.AppendLine("        body { font-family: Arial, sans-serif; margin: 20px; }");
            html.AppendLine("        h1 { color: #2c3e50; }");
            html.AppendLine("        .summary { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }");
            html.AppendLine("        .summary-item { display: inline-block; margin-right: 30px; margin-bottom: 10px; }");
            html.AppendLine("        .summary-label { font-weight: bold; color: #555; }");
            html.AppendLine("        .summary-value { font-size: 18px; color: #2c3e50; }");
            html.AppendLine("        table { border-collapse: collapse; width: 100%; margin-top: 20px; font-size: 12px; }");
            html.AppendLine("        th { background-color: #2c3e50; color: white; padding: 10px; text-align: left; }");
            html.AppendLine("        td { padding: 8px; border-bottom: 1px solid #ddd; }");
            html.AppendLine("        tr:hover { background-color: #f5f5f5; }");
            html.AppendLine("        .status-completed { background-color: #d4edda; color: #155724; padding: 4px 8px; border-radius: 3px; }");
            html.AppendLine("        .status-nearcomplete { background-color: #d1f2d5; color: #155724; padding: 4px 8px; border-radius: 3px; }");
            html.AppendLine("        .status-inprogress { background-color: #d1ecf1; color: #0c5460; padding: 4px 8px; border-radius: 3px; }");
            html.AppendLine("        .status-earlystage { background-color: #fff3cd; color: #856404; padding: 4px 8px; border-radius: 3px; }");
            html.AppendLine("        .bottleneck { background-color: #f8d7da; color: #721c24; padding: 4px 8px; border-radius: 3px; }");
            html.AppendLine("        .footer { margin-top: 30px; font-size: 12px; color: #999; }");
            html.AppendLine("        @media print { body { margin: 0; } }");
            html.AppendLine("    </style>");
            html.AppendLine("</head>");
            html.AppendLine("<body>");

            // Title
            html.AppendLine("    <h1>Site Activation Timeline Report</h1>");
            html.AppendLine($"    <p><strong>Study:</strong> {config.StudyName}</p>");
            html.AppendLine($"    <p><strong>Generated:</strong> {DateTime.Now:yyyy-MM-dd HH:mm:ss}</p>");

            // Summary Section
            int sitesInStartup = siteActivationMetrics.Count(s => s.StartupStatus != "Not Started" && s.StartupStatus != "Completed");
            double avgDuration = siteActivationMetrics.Where(s => s.StartupDuration > 0).Select(s => (double)s.StartupDuration).DefaultIfEmpty(0).Average();
            var bottlenecks = siteActivationMetrics.Where(s => s.CurrentBottleneck != "None" && s.CurrentBottleneck != "Unknown").GroupBy(s => s.CurrentBottleneck.Split('(')[0].Trim()).OrderByDescending(g => g.Count()).FirstOrDefault();
            string commonBottleneck = bottlenecks != null ? $"{bottlenecks.Key} ({bottlenecks.Count()} sites)" : "None";
            int projectionsNext30Days = siteActivationMetrics.Count(s => s.ProjectedActivationDate.HasValue && s.ProjectedActivationDate.Value <= DateTime.Today.AddDays(30));

            html.AppendLine("    <div class='summary'>");
            html.AppendLine("        <h2>Summary</h2>");
            html.AppendLine($"        <div class='summary-item'><span class='summary-label'>Sites in Startup:</span> <span class='summary-value'>{sitesInStartup}</span></div>");
            html.AppendLine($"        <div class='summary-item'><span class='summary-label'>Avg Startup Duration:</span> <span class='summary-value'>{avgDuration:F0} days</span></div>");
            html.AppendLine($"        <div class='summary-item'><span class='summary-label'>Common Bottleneck:</span> <span class='summary-value'>{commonBottleneck}</span></div>");
            html.AppendLine($"        <div class='summary-item'><span class='summary-label'>Projected Activations (30 days):</span> <span class='summary-value'>{projectionsNext30Days}</span></div>");
            html.AppendLine("    </div>");

            // Table
            html.AppendLine("    <table>");
            html.AppendLine("        <thead>");
            html.AppendLine("            <tr>");
            html.AppendLine("                <th>Site ID</th>");
            html.AppendLine("                <th>Country</th>");
            html.AppendLine("                <th>Startup Status</th>");
            html.AppendLine("                <th>Docs Progress</th>");
            html.AppendLine("                <th>IRB Submission</th>");
            html.AppendLine("                <th>IRB Approval</th>");
            html.AppendLine("                <th>Training %</th>");
            html.AppendLine("                <th>Projected Activation</th>");
            html.AppendLine("                <th>Current Bottleneck</th>");
            html.AppendLine("                <th>Duration (days)</th>");
            html.AppendLine("            </tr>");
            html.AppendLine("        </thead>");
            html.AppendLine("        <tbody>");

            foreach (var metrics in siteActivationMetrics)
            {
                string statusClass = GetHtmlStatusClass(metrics.StartupStatus);
                string bottleneckClass = (metrics.CurrentBottleneck != "None" && metrics.CurrentBottleneck != "Unknown") ? "bottleneck" : "";

                html.AppendLine("            <tr>");
                html.AppendLine($"                <td><strong>{metrics.SiteId}</strong></td>");
                html.AppendLine($"                <td>{metrics.Country}</td>");
                html.AppendLine($"                <td><span class='{statusClass}'>{metrics.StartupStatus}</span></td>");
                html.AppendLine($"                <td>{metrics.DocsCollected}/{metrics.TotalDocs}</td>");
                html.AppendLine($"                <td>{metrics.IRBSubmissionDate?.ToString("yyyy-MM-dd") ?? "Pending"}</td>");
                html.AppendLine($"                <td>{metrics.IRBApprovalDate?.ToString("yyyy-MM-dd") ?? "Pending"}</td>");
                html.AppendLine($"                <td>{metrics.TrainingCompletionPercent}%</td>");
                html.AppendLine($"                <td>{metrics.ProjectedActivationDate?.ToString("yyyy-MM-dd") ?? "TBD"}</td>");
                html.AppendLine($"                <td><span class='{bottleneckClass}'>{metrics.CurrentBottleneck}</span></td>");
                html.AppendLine($"                <td>{metrics.StartupDuration}</td>");
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

        private string GetHtmlStatusClass(string status)
        {
            switch (status)
            {
                case "Completed":
                    return "status-completed";
                case "Near Complete":
                    return "status-nearcomplete";
                case "In Progress":
                    return "status-inprogress";
                case "Early Stage":
                case "Just Started":
                    return "status-earlystage";
                default:
                    return "";
            }
        }

        private void btnRefresh_Click(object sender, EventArgs e)
        {
            LoadData();
            MessageBox.Show("Timeline refreshed successfully.",
                "Refresh Complete", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
    }

    /// <summary>
    /// Site activation metrics for timeline report
    /// </summary>
    public class SiteActivationMetrics
    {
        public string SiteId { get; set; }
        public string Country { get; set; }
        public string StartupStatus { get; set; }
        public int DocsCollected { get; set; }
        public int TotalDocs { get; set; }
        public DateTime? IRBSubmissionDate { get; set; }
        public DateTime? IRBApprovalDate { get; set; }
        public int TrainingCompletionPercent { get; set; }
        public DateTime? ProjectedActivationDate { get; set; }
        public string CurrentBottleneck { get; set; }
        public int StartupDuration { get; set; }
    }
}
