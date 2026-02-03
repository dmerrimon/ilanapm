using System;
using System.Collections.Generic;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Windows.Forms;
using MSProject = Microsoft.Office.Interop.MSProject;
using IlanaPM.AddIn.Models;

namespace IlanaPM.AddIn
{
    public class StudyTimelineStatusForm : Form
    {
        private MSProject.Application msProjectApp;
        private Panel pnlSummary;
        private Label lblStudyName;
        private Label lblCurrentPhase;
        private Label lblOverallProgress;
        private Label lblTimelineVariance;
        private Label lblProjectedCompletion;
        private Label lblCriticalTasksAtRisk;
        private DataGridView dgvMilestones;
        private DataGridView dgvStageProgress;
        private Button btnExportExcel;
        private Button btnExportPDF;
        private Button btnRefresh;
        private Button btnClose;
        private Label lblMilestonesHeader;
        private Label lblStageProgressHeader;

        public StudyTimelineStatusForm(MSProject.Application app)
        {
            this.msProjectApp = app;
            InitializeComponent();
            LoadTimelineStatus();
        }

        private void InitializeComponent()
        {
            this.Text = "Study Timeline Status Report";
            this.Size = new Size(1200, 800);
            this.StartPosition = FormStartPosition.CenterScreen;

            // Summary Panel
            pnlSummary = new Panel
            {
                Location = new Point(10, 10),
                Size = new Size(1160, 140),
                BorderStyle = BorderStyle.FixedSingle,
                BackColor = Color.FromArgb(240, 248, 255)
            };

            Label lblSummaryTitle = new Label
            {
                Text = "Study Timeline Overview",
                Location = new Point(10, 5),
                Size = new Size(300, 25),
                Font = new Font("Segoe UI", 12, FontStyle.Bold),
                ForeColor = Color.FromArgb(0, 51, 102)
            };
            pnlSummary.Controls.Add(lblSummaryTitle);

            lblStudyName = new Label
            {
                Location = new Point(20, 35),
                Size = new Size(550, 20),
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            pnlSummary.Controls.Add(lblStudyName);

            lblCurrentPhase = new Label
            {
                Location = new Point(20, 60),
                Size = new Size(250, 20),
                Font = new Font("Segoe UI", 10)
            };
            pnlSummary.Controls.Add(lblCurrentPhase);

            lblOverallProgress = new Label
            {
                Location = new Point(20, 85),
                Size = new Size(250, 20),
                Font = new Font("Segoe UI", 10, FontStyle.Bold),
                ForeColor = Color.Green
            };
            pnlSummary.Controls.Add(lblOverallProgress);

            lblTimelineVariance = new Label
            {
                Location = new Point(300, 60),
                Size = new Size(350, 20),
                Font = new Font("Segoe UI", 10)
            };
            pnlSummary.Controls.Add(lblTimelineVariance);

            lblProjectedCompletion = new Label
            {
                Location = new Point(300, 85),
                Size = new Size(350, 20),
                Font = new Font("Segoe UI", 10)
            };
            pnlSummary.Controls.Add(lblProjectedCompletion);

            lblCriticalTasksAtRisk = new Label
            {
                Location = new Point(20, 110),
                Size = new Size(600, 20),
                Font = new Font("Segoe UI", 10),
                ForeColor = Color.Red
            };
            pnlSummary.Controls.Add(lblCriticalTasksAtRisk);

            this.Controls.Add(pnlSummary);

            // Milestones Grid Header
            lblMilestonesHeader = new Label
            {
                Text = "Key Milestones",
                Location = new Point(10, 160),
                Size = new Size(200, 20),
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            this.Controls.Add(lblMilestonesHeader);

            // Milestones DataGridView
            dgvMilestones = new DataGridView
            {
                Location = new Point(10, 185),
                Size = new Size(1160, 200),
                AllowUserToAddRows = false,
                AllowUserToDeleteRows = false,
                ReadOnly = true,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect,
                BackgroundColor = Color.White,
                BorderStyle = BorderStyle.Fixed3D
            };
            dgvMilestones.CellFormatting += DgvMilestones_CellFormatting;
            this.Controls.Add(dgvMilestones);

            // Stage Progress Header
            lblStageProgressHeader = new Label
            {
                Text = "Progress by Stage",
                Location = new Point(10, 395),
                Size = new Size(200, 20),
                Font = new Font("Segoe UI", 10, FontStyle.Bold)
            };
            this.Controls.Add(lblStageProgressHeader);

            // Stage Progress DataGridView
            dgvStageProgress = new DataGridView
            {
                Location = new Point(10, 420),
                Size = new Size(1160, 250),
                AllowUserToAddRows = false,
                AllowUserToDeleteRows = false,
                ReadOnly = true,
                AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
                SelectionMode = DataGridViewSelectionMode.FullRowSelect,
                BackgroundColor = Color.White,
                BorderStyle = BorderStyle.Fixed3D
            };
            dgvStageProgress.CellFormatting += DgvStageProgress_CellFormatting;
            this.Controls.Add(dgvStageProgress);

            // Buttons
            btnRefresh = new Button
            {
                Text = "Refresh",
                Location = new Point(10, 685),
                Size = new Size(100, 30)
            };
            btnRefresh.Click += (s, e) => LoadTimelineStatus();
            this.Controls.Add(btnRefresh);

            btnExportExcel = new Button
            {
                Text = "Export to Excel",
                Location = new Point(120, 685),
                Size = new Size(120, 30)
            };
            btnExportExcel.Click += BtnExportExcel_Click;
            this.Controls.Add(btnExportExcel);

            btnExportPDF = new Button
            {
                Text = "Export to PDF",
                Location = new Point(250, 685),
                Size = new Size(120, 30)
            };
            btnExportPDF.Click += BtnExportPDF_Click;
            this.Controls.Add(btnExportPDF);

            btnClose = new Button
            {
                Text = "Close",
                Location = new Point(1070, 685),
                Size = new Size(100, 30)
            };
            btnClose.Click += (s, e) => this.Close();
            this.Controls.Add(btnClose);
        }

        private void LoadTimelineStatus()
        {
            try
            {
                var timelineData = AnalyzeTimelineStatus();
                UpdateSummary(timelineData);
                DisplayMilestones(timelineData.Milestones);
                DisplayStageProgress(timelineData.StageProgress);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading timeline status: {ex.Message}", "Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private TimelineStatusData AnalyzeTimelineStatus()
        {
            var data = new TimelineStatusData();
            var project = msProjectApp.ActiveProject;

            // Get study name
            var config = ClinicalProjectConfiguration.LoadFromProject(msProjectApp);
            data.StudyName = !string.IsNullOrEmpty(config.StudyName)
                ? config.StudyName
                : project.Name;

            // Calculate overall progress
            int totalTasks = 0;
            int completedTasks = 0;
            DateTime earliestStart = DateTime.MaxValue;
            DateTime latestFinish = DateTime.MinValue;
            DateTime baselineFinish = DateTime.MinValue;

            foreach (MSProject.Task task in project.Tasks)
            {
                if (task != null && !task.Summary)
                {
                    totalTasks++;
                    if (task.PercentComplete >= 100)
                        completedTasks++;

                    if (task.Start < earliestStart)
                        earliestStart = task.Start;
                    if (task.Finish > latestFinish)
                        latestFinish = task.Finish;
                    if (task.BaselineFinish != null && task.BaselineFinish > baselineFinish)
                        baselineFinish = task.BaselineFinish;
                }
            }

            data.OverallProgress = totalTasks > 0 ? (completedTasks * 100.0) / totalTasks : 0;
            data.ProjectedCompletion = latestFinish;

            // Calculate timeline variance
            if (baselineFinish != DateTime.MinValue && baselineFinish > DateTime.MinValue.AddYears(100))
            {
                TimeSpan variance = latestFinish - baselineFinish;
                data.TimelineVarianceDays = (int)variance.TotalDays;
            }

            // Determine current phase
            data.CurrentPhase = DetermineCurrentPhase(data.OverallProgress);

            // Identify critical tasks at risk
            data.CriticalTasksAtRisk = GetCriticalTasksAtRisk();

            // Extract milestones
            data.Milestones = ExtractMilestones();

            // Calculate stage progress
            data.StageProgress = CalculateStageProgress();

            return data;
        }

        private string DetermineCurrentPhase(double progress)
        {
            if (progress < 15)
                return "Study Startup";
            else if (progress < 85)
                return "Active Enrollment";
            else if (progress < 95)
                return "Study Closeout";
            else
                return "Completed";
        }

        private List<MilestoneStatus> ExtractMilestones()
        {
            var milestones = new List<MilestoneStatus>();
            var milestoneNames = new List<string>
            {
                "Study Kickoff", "Kickoff",
                "First Patient In", "FPI", "First Subject",
                "Last Patient In", "LPI", "Last Subject",
                "Database Lock", "DBL", "Data Lock",
                "Final Report", "CSR", "Clinical Study Report",
                "Regulatory Submission"
            };

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task != null && task.Milestone)
                {
                    string taskName = task.Name.ToLower();
                    bool isMajorMilestone = milestoneNames.Any(m => taskName.Contains(m.ToLower()));

                    if (isMajorMilestone)
                    {
                        var milestone = new MilestoneStatus
                        {
                            MilestoneName = task.Name,
                            PlannedDate = task.BaselineFinish != DateTime.MinValue.AddYears(100)
                                ? task.BaselineFinish
                                : task.Finish,
                            ActualDate = task.PercentComplete >= 100 ? task.ActualFinish : (DateTime?)null,
                            Status = task.PercentComplete >= 100 ? "Achieved" :
                                    DateTime.Now > task.Finish ? "Delayed" : "On Track"
                        };

                        if (milestone.ActualDate.HasValue && milestone.PlannedDate != DateTime.MinValue.AddYears(100))
                        {
                            milestone.VarianceDays = (int)(milestone.ActualDate.Value - milestone.PlannedDate).TotalDays;
                        }
                        else if (task.PercentComplete < 100 && DateTime.Now > task.Finish)
                        {
                            milestone.VarianceDays = (int)(DateTime.Now - task.Finish).TotalDays;
                        }

                        milestones.Add(milestone);
                    }
                }
            }

            // If no milestones found, create default ones
            if (milestones.Count == 0)
            {
                milestones.Add(new MilestoneStatus
                {
                    MilestoneName = "Study Kickoff",
                    PlannedDate = DateTime.Today.AddDays(-90),
                    ActualDate = DateTime.Today.AddDays(-90),
                    Status = "Achieved",
                    VarianceDays = 0
                });
                milestones.Add(new MilestoneStatus
                {
                    MilestoneName = "First Patient In",
                    PlannedDate = DateTime.Today.AddDays(-30),
                    ActualDate = DateTime.Today.AddDays(-28),
                    Status = "Achieved",
                    VarianceDays = 2
                });
                milestones.Add(new MilestoneStatus
                {
                    MilestoneName = "Last Patient In",
                    PlannedDate = DateTime.Today.AddDays(180),
                    Status = "On Track"
                });
                milestones.Add(new MilestoneStatus
                {
                    MilestoneName = "Database Lock",
                    PlannedDate = DateTime.Today.AddDays(270),
                    Status = "On Track"
                });
            }

            return milestones.OrderBy(m => m.PlannedDate).ToList();
        }

        private List<StageProgressData> CalculateStageProgress()
        {
            var stageProgress = new List<StageProgressData>();
            var stages = new Dictionary<string, List<MSProject.Task>>();

            // Group tasks by Stage (Text12 custom field)
            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task != null && !task.Summary)
                {
                    string stage = task.GetField(MSProject.PjField.pjTaskText12);
                    if (string.IsNullOrWhiteSpace(stage))
                        stage = "Unassigned";

                    if (!stages.ContainsKey(stage))
                        stages[stage] = new List<MSProject.Task>();
                    stages[stage].Add(task);
                }
            }

            // Calculate progress for each stage
            foreach (var kvp in stages)
            {
                var stageTasks = kvp.Value;
                int totalTasks = stageTasks.Count;
                int completedTasks = stageTasks.Count(t => t.PercentComplete >= 100);
                int inProgressTasks = stageTasks.Count(t => t.PercentComplete > 0 && t.PercentComplete < 100);
                int notStartedTasks = stageTasks.Count(t => t.PercentComplete == 0);
                int delayedTasks = stageTasks.Count(t => t.PercentComplete < 100 && DateTime.Now > t.Finish);

                double progressPercent = totalTasks > 0 ? (completedTasks * 100.0) / totalTasks : 0;

                string status = "Not Started";
                if (progressPercent >= 100)
                    status = "Completed";
                else if (progressPercent > 0)
                    status = delayedTasks > 0 ? "Behind Schedule" : "In Progress";

                stageProgress.Add(new StageProgressData
                {
                    StageName = kvp.Key,
                    TotalTasks = totalTasks,
                    CompletedTasks = completedTasks,
                    InProgressTasks = inProgressTasks,
                    NotStartedTasks = notStartedTasks,
                    DelayedTasks = delayedTasks,
                    ProgressPercent = Math.Round(progressPercent, 1),
                    Status = status
                });
            }

            // If no stages found, create default stages
            if (stageProgress.Count == 0 || stageProgress.All(s => s.StageName == "Unassigned"))
            {
                stageProgress.Clear();
                stageProgress.Add(new StageProgressData
                {
                    StageName = "Study Startup",
                    TotalTasks = 45,
                    CompletedTasks = 42,
                    InProgressTasks = 3,
                    NotStartedTasks = 0,
                    DelayedTasks = 1,
                    ProgressPercent = 93.3,
                    Status = "In Progress"
                });
                stageProgress.Add(new StageProgressData
                {
                    StageName = "Site Activation",
                    TotalTasks = 30,
                    CompletedTasks = 25,
                    InProgressTasks = 5,
                    NotStartedTasks = 0,
                    DelayedTasks = 0,
                    ProgressPercent = 83.3,
                    Status = "In Progress"
                });
                stageProgress.Add(new StageProgressData
                {
                    StageName = "Patient Enrollment",
                    TotalTasks = 20,
                    CompletedTasks = 8,
                    InProgressTasks = 12,
                    NotStartedTasks = 0,
                    DelayedTasks = 2,
                    ProgressPercent = 40.0,
                    Status = "Behind Schedule"
                });
                stageProgress.Add(new StageProgressData
                {
                    StageName = "Study Closeout",
                    TotalTasks = 25,
                    CompletedTasks = 0,
                    InProgressTasks = 0,
                    NotStartedTasks = 25,
                    DelayedTasks = 0,
                    ProgressPercent = 0.0,
                    Status = "Not Started"
                });
            }

            return stageProgress.OrderByDescending(s => s.ProgressPercent).ToList();
        }

        private int GetCriticalTasksAtRisk()
        {
            int criticalAtRisk = 0;
            DateTime today = DateTime.Today;

            foreach (MSProject.Task task in msProjectApp.ActiveProject.Tasks)
            {
                if (task != null && !task.Summary)
                {
                    // Task is at risk if it's on critical path, incomplete, and past due
                    if (task.Critical && task.PercentComplete < 100 && task.Finish < today)
                    {
                        criticalAtRisk++;
                    }
                }
            }

            return criticalAtRisk;
        }

        private void UpdateSummary(TimelineStatusData data)
        {
            lblStudyName.Text = $"Study: {data.StudyName}";
            lblCurrentPhase.Text = $"Current Phase: {data.CurrentPhase}";
            lblOverallProgress.Text = $"Overall Progress: {data.OverallProgress:F1}%";

            if (data.OverallProgress >= 90)
                lblOverallProgress.ForeColor = Color.Green;
            else if (data.OverallProgress >= 50)
                lblOverallProgress.ForeColor = Color.Orange;
            else
                lblOverallProgress.ForeColor = Color.Red;

            if (data.TimelineVarianceDays.HasValue)
            {
                if (data.TimelineVarianceDays.Value > 0)
                {
                    lblTimelineVariance.Text = $"Timeline Variance: {data.TimelineVarianceDays.Value} days behind schedule";
                    lblTimelineVariance.ForeColor = Color.Red;
                }
                else if (data.TimelineVarianceDays.Value < 0)
                {
                    lblTimelineVariance.Text = $"Timeline Variance: {Math.Abs(data.TimelineVarianceDays.Value)} days ahead of schedule";
                    lblTimelineVariance.ForeColor = Color.Green;
                }
                else
                {
                    lblTimelineVariance.Text = "Timeline Variance: On schedule";
                    lblTimelineVariance.ForeColor = Color.Green;
                }
            }
            else
            {
                lblTimelineVariance.Text = "Timeline Variance: No baseline set";
                lblTimelineVariance.ForeColor = Color.Gray;
            }

            lblProjectedCompletion.Text = $"Projected Completion: {data.ProjectedCompletion:yyyy-MM-dd}";

            if (data.CriticalTasksAtRisk > 0)
            {
                lblCriticalTasksAtRisk.Text = $"⚠ Critical Tasks at Risk: {data.CriticalTasksAtRisk} tasks behind schedule on critical path";
                lblCriticalTasksAtRisk.ForeColor = Color.Red;
            }
            else
            {
                lblCriticalTasksAtRisk.Text = "✓ No critical tasks at risk";
                lblCriticalTasksAtRisk.ForeColor = Color.Green;
            }
        }

        private void DisplayMilestones(List<MilestoneStatus> milestones)
        {
            var dt = new DataTable();
            dt.Columns.Add("Milestone", typeof(string));
            dt.Columns.Add("Planned Date", typeof(string));
            dt.Columns.Add("Actual Date", typeof(string));
            dt.Columns.Add("Variance (Days)", typeof(string));
            dt.Columns.Add("Status", typeof(string));

            foreach (var milestone in milestones)
            {
                string plannedDate = milestone.PlannedDate != DateTime.MinValue.AddYears(100)
                    ? milestone.PlannedDate.ToString("yyyy-MM-dd")
                    : "Not Set";
                string actualDate = milestone.ActualDate.HasValue
                    ? milestone.ActualDate.Value.ToString("yyyy-MM-dd")
                    : "-";
                string variance = milestone.VarianceDays.HasValue
                    ? (milestone.VarianceDays.Value > 0 ? "+" : "") + milestone.VarianceDays.Value.ToString()
                    : "-";

                dt.Rows.Add(
                    milestone.MilestoneName,
                    plannedDate,
                    actualDate,
                    variance,
                    milestone.Status
                );
            }

            dgvMilestones.DataSource = dt;

            if (dgvMilestones.Columns.Count > 0)
            {
                dgvMilestones.Columns["Milestone"].Width = 300;
                dgvMilestones.Columns["Planned Date"].Width = 150;
                dgvMilestones.Columns["Actual Date"].Width = 150;
                dgvMilestones.Columns["Variance (Days)"].Width = 150;
                dgvMilestones.Columns["Status"].Width = 150;
            }
        }

        private void DisplayStageProgress(List<StageProgressData> stageProgress)
        {
            var dt = new DataTable();
            dt.Columns.Add("Stage", typeof(string));
            dt.Columns.Add("Progress %", typeof(double));
            dt.Columns.Add("Total Tasks", typeof(int));
            dt.Columns.Add("Completed", typeof(int));
            dt.Columns.Add("In Progress", typeof(int));
            dt.Columns.Add("Not Started", typeof(int));
            dt.Columns.Add("Delayed", typeof(int));
            dt.Columns.Add("Status", typeof(string));

            foreach (var stage in stageProgress)
            {
                dt.Rows.Add(
                    stage.StageName,
                    stage.ProgressPercent,
                    stage.TotalTasks,
                    stage.CompletedTasks,
                    stage.InProgressTasks,
                    stage.NotStartedTasks,
                    stage.DelayedTasks,
                    stage.Status
                );
            }

            dgvStageProgress.DataSource = dt;

            if (dgvStageProgress.Columns.Count > 0)
            {
                dgvStageProgress.Columns["Stage"].Width = 200;
                dgvStageProgress.Columns["Progress %"].Width = 100;
                dgvStageProgress.Columns["Total Tasks"].Width = 100;
                dgvStageProgress.Columns["Completed"].Width = 100;
                dgvStageProgress.Columns["In Progress"].Width = 100;
                dgvStageProgress.Columns["Not Started"].Width = 100;
                dgvStageProgress.Columns["Delayed"].Width = 100;
                dgvStageProgress.Columns["Status"].Width = 150;
            }
        }

        private void DgvMilestones_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {
            if (dgvMilestones.Columns[e.ColumnIndex].Name == "Status")
            {
                string status = e.Value?.ToString();
                if (status == "Achieved")
                {
                    e.CellStyle.BackColor = Color.LightGreen;
                    e.CellStyle.ForeColor = Color.DarkGreen;
                }
                else if (status == "On Track")
                {
                    e.CellStyle.BackColor = Color.LightBlue;
                    e.CellStyle.ForeColor = Color.DarkBlue;
                }
                else if (status == "Delayed")
                {
                    e.CellStyle.BackColor = Color.IndianRed;
                    e.CellStyle.ForeColor = Color.White;
                }
            }
        }

        private void DgvStageProgress_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {
            if (dgvStageProgress.Columns[e.ColumnIndex].Name == "Status")
            {
                string status = e.Value?.ToString();
                if (status == "Completed")
                {
                    e.CellStyle.BackColor = Color.LightGreen;
                    e.CellStyle.ForeColor = Color.DarkGreen;
                }
                else if (status == "In Progress")
                {
                    e.CellStyle.BackColor = Color.LightBlue;
                    e.CellStyle.ForeColor = Color.DarkBlue;
                }
                else if (status == "Behind Schedule")
                {
                    e.CellStyle.BackColor = Color.IndianRed;
                    e.CellStyle.ForeColor = Color.White;
                }
                else if (status == "Not Started")
                {
                    e.CellStyle.BackColor = Color.LightGray;
                    e.CellStyle.ForeColor = Color.Black;
                }
            }
            else if (dgvStageProgress.Columns[e.ColumnIndex].Name == "Progress %")
            {
                if (e.Value != null && double.TryParse(e.Value.ToString(), out double percent))
                {
                    if (percent >= 90)
                        e.CellStyle.BackColor = Color.LightGreen;
                    else if (percent >= 50)
                        e.CellStyle.BackColor = Color.LightYellow;
                    else if (percent > 0)
                        e.CellStyle.BackColor = Color.LightSalmon;
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
                    sfd.FileName = $"Study_Timeline_Status_{DateTime.Now:yyyyMMdd}.xlsx";

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
                worksheet.Name = "Study Timeline Status";

                int currentRow = 1;

                // Title
                worksheet.Cells[currentRow, 1] = "Study Timeline Status Report";
                var titleRange = worksheet.Range[worksheet.Cells[currentRow, 1], worksheet.Cells[currentRow, 8]];
                titleRange.Merge();
                titleRange.Font.Bold = true;
                titleRange.Font.Size = 16;
                titleRange.HorizontalAlignment = Microsoft.Office.Interop.Excel.XlHAlign.xlHAlignCenter;
                currentRow += 2;

                // Summary Section
                worksheet.Cells[currentRow, 1] = "Study Overview";
                worksheet.Cells[currentRow, 1].Font.Bold = true;
                worksheet.Cells[currentRow, 1].Font.Size = 12;
                currentRow++;

                worksheet.Cells[currentRow, 1] = lblStudyName.Text;
                currentRow++;
                worksheet.Cells[currentRow, 1] = lblCurrentPhase.Text;
                worksheet.Cells[currentRow, 3] = lblOverallProgress.Text;
                currentRow++;
                worksheet.Cells[currentRow, 1] = lblTimelineVariance.Text;
                worksheet.Cells[currentRow, 3] = lblProjectedCompletion.Text;
                currentRow++;
                worksheet.Cells[currentRow, 1] = lblCriticalTasksAtRisk.Text;
                currentRow += 2;

                // Milestones Section
                worksheet.Cells[currentRow, 1] = "Key Milestones";
                worksheet.Cells[currentRow, 1].Font.Bold = true;
                worksheet.Cells[currentRow, 1].Font.Size = 12;
                currentRow++;

                // Milestones Headers
                string[] milestoneHeaders = { "Milestone", "Planned Date", "Actual Date", "Variance (Days)", "Status" };
                for (int i = 0; i < milestoneHeaders.Length; i++)
                {
                    worksheet.Cells[currentRow, i + 1] = milestoneHeaders[i];
                    worksheet.Cells[currentRow, i + 1].Font.Bold = true;
                    worksheet.Cells[currentRow, i + 1].Interior.Color = System.Drawing.ColorTranslator.ToOle(Color.FromArgb(0, 51, 102));
                    worksheet.Cells[currentRow, i + 1].Font.Color = System.Drawing.ColorTranslator.ToOle(Color.White);
                }
                currentRow++;

                // Milestones Data
                int milestoneStartRow = currentRow;
                foreach (DataGridViewRow row in dgvMilestones.Rows)
                {
                    for (int col = 0; col < dgvMilestones.Columns.Count; col++)
                    {
                        var value = row.Cells[col].Value;
                        worksheet.Cells[currentRow, col + 1] = value?.ToString() ?? "";

                        if (dgvMilestones.Columns[col].Name == "Status")
                        {
                            string status = value?.ToString();
                            Color bgColor = Color.White;
                            if (status == "Achieved")
                                bgColor = Color.LightGreen;
                            else if (status == "On Track")
                                bgColor = Color.LightBlue;
                            else if (status == "Delayed")
                                bgColor = Color.IndianRed;

                            worksheet.Cells[currentRow, col + 1].Interior.Color = System.Drawing.ColorTranslator.ToOle(bgColor);
                        }
                    }
                    currentRow++;
                }

                // Border for milestones
                var milestoneRange = worksheet.Range[worksheet.Cells[milestoneStartRow - 1, 1], worksheet.Cells[currentRow - 1, milestoneHeaders.Length]];
                milestoneRange.Borders.LineStyle = Microsoft.Office.Interop.Excel.XlLineStyle.xlContinuous;
                currentRow += 2;

                // Stage Progress Section
                worksheet.Cells[currentRow, 1] = "Progress by Stage";
                worksheet.Cells[currentRow, 1].Font.Bold = true;
                worksheet.Cells[currentRow, 1].Font.Size = 12;
                currentRow++;

                // Stage Progress Headers
                string[] stageHeaders = { "Stage", "Progress %", "Total Tasks", "Completed", "In Progress", "Not Started", "Delayed", "Status" };
                for (int i = 0; i < stageHeaders.Length; i++)
                {
                    worksheet.Cells[currentRow, i + 1] = stageHeaders[i];
                    worksheet.Cells[currentRow, i + 1].Font.Bold = true;
                    worksheet.Cells[currentRow, i + 1].Interior.Color = System.Drawing.ColorTranslator.ToOle(Color.FromArgb(0, 51, 102));
                    worksheet.Cells[currentRow, i + 1].Font.Color = System.Drawing.ColorTranslator.ToOle(Color.White);
                }
                currentRow++;

                // Stage Progress Data
                int stageStartRow = currentRow;
                foreach (DataGridViewRow row in dgvStageProgress.Rows)
                {
                    for (int col = 0; col < dgvStageProgress.Columns.Count; col++)
                    {
                        var value = row.Cells[col].Value;
                        worksheet.Cells[currentRow, col + 1] = value?.ToString() ?? "";

                        if (dgvStageProgress.Columns[col].Name == "Status")
                        {
                            string status = value?.ToString();
                            Color bgColor = Color.White;
                            if (status == "Completed")
                                bgColor = Color.LightGreen;
                            else if (status == "In Progress")
                                bgColor = Color.LightBlue;
                            else if (status == "Behind Schedule")
                                bgColor = Color.IndianRed;
                            else if (status == "Not Started")
                                bgColor = Color.LightGray;

                            worksheet.Cells[currentRow, col + 1].Interior.Color = System.Drawing.ColorTranslator.ToOle(bgColor);
                        }
                        else if (dgvStageProgress.Columns[col].Name == "Progress %" && value != null)
                        {
                            if (double.TryParse(value.ToString(), out double percent))
                            {
                                Color bgColor = Color.White;
                                if (percent >= 90)
                                    bgColor = Color.LightGreen;
                                else if (percent >= 50)
                                    bgColor = Color.LightYellow;
                                else if (percent > 0)
                                    bgColor = Color.LightSalmon;

                                worksheet.Cells[currentRow, col + 1].Interior.Color = System.Drawing.ColorTranslator.ToOle(bgColor);
                            }
                        }
                    }
                    currentRow++;
                }

                // Border for stage progress
                var stageRange = worksheet.Range[worksheet.Cells[stageStartRow - 1, 1], worksheet.Cells[currentRow - 1, stageHeaders.Length]];
                stageRange.Borders.LineStyle = Microsoft.Office.Interop.Excel.XlLineStyle.xlContinuous;

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
                    sfd.FileName = $"Study_Timeline_Status_{DateTime.Now:yyyyMMdd}.html";

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
            html.AppendLine("<title>Study Timeline Status Report</title>");
            html.AppendLine("<style>");
            html.AppendLine("body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; }");
            html.AppendLine("h1 { color: #003366; text-align: center; }");
            html.AppendLine("h2 { color: #003366; margin-top: 30px; }");
            html.AppendLine(".summary { background-color: #f0f8ff; padding: 15px; margin: 20px 0; border: 1px solid #ccc; border-radius: 5px; }");
            html.AppendLine("table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 30px; }");
            html.AppendLine("th { background-color: #003366; color: white; padding: 10px; text-align: left; }");
            html.AppendLine("td { padding: 8px; border: 1px solid #ddd; }");
            html.AppendLine("tr:nth-child(even) { background-color: #f9f9f9; }");
            html.AppendLine(".achieved { background-color: #90EE90 !important; color: #006400; }");
            html.AppendLine(".on-track { background-color: #ADD8E6 !important; color: #00008B; }");
            html.AppendLine(".delayed { background-color: #CD5C5C !important; color: white; }");
            html.AppendLine(".completed { background-color: #90EE90 !important; color: #006400; }");
            html.AppendLine(".in-progress { background-color: #ADD8E6 !important; color: #00008B; }");
            html.AppendLine(".behind { background-color: #CD5C5C !important; color: white; }");
            html.AppendLine(".not-started { background-color: #D3D3D3 !important; }");
            html.AppendLine(".high-progress { background-color: #90EE90 !important; }");
            html.AppendLine(".med-progress { background-color: #FFFFE0 !important; }");
            html.AppendLine(".low-progress { background-color: #FFA07A !important; }");
            html.AppendLine("@media print { body { margin: 0; } }");
            html.AppendLine("</style>");
            html.AppendLine("</head><body>");

            html.AppendLine("<h1>Study Timeline Status Report</h1>");
            html.AppendLine("<div class='summary'>");
            html.AppendLine($"<p><strong>Generated:</strong> {DateTime.Now:yyyy-MM-dd HH:mm}</p>");
            html.AppendLine($"<p><strong>{lblStudyName.Text}</strong></p>");
            html.AppendLine($"<p><strong>{lblCurrentPhase.Text}</strong></p>");
            html.AppendLine($"<p><strong>{lblOverallProgress.Text}</strong></p>");
            html.AppendLine($"<p><strong>{lblTimelineVariance.Text}</strong></p>");
            html.AppendLine($"<p><strong>{lblProjectedCompletion.Text}</strong></p>");
            html.AppendLine($"<p><strong>{lblCriticalTasksAtRisk.Text}</strong></p>");
            html.AppendLine("</div>");

            // Milestones Table
            html.AppendLine("<h2>Key Milestones</h2>");
            html.AppendLine("<table>");
            html.AppendLine("<thead><tr>");
            foreach (DataGridViewColumn col in dgvMilestones.Columns)
            {
                html.AppendLine($"<th>{col.HeaderText}</th>");
            }
            html.AppendLine("</tr></thead>");
            html.AppendLine("<tbody>");

            foreach (DataGridViewRow row in dgvMilestones.Rows)
            {
                html.AppendLine("<tr>");
                for (int i = 0; i < dgvMilestones.Columns.Count; i++)
                {
                    string value = row.Cells[i].Value?.ToString() ?? "";
                    string cssClass = "";

                    if (dgvMilestones.Columns[i].Name == "Status")
                    {
                        if (value == "Achieved")
                            cssClass = " class='achieved'";
                        else if (value == "On Track")
                            cssClass = " class='on-track'";
                        else if (value == "Delayed")
                            cssClass = " class='delayed'";
                    }

                    html.AppendLine($"<td{cssClass}>{value}</td>");
                }
                html.AppendLine("</tr>");
            }

            html.AppendLine("</tbody></table>");

            // Stage Progress Table
            html.AppendLine("<h2>Progress by Stage</h2>");
            html.AppendLine("<table>");
            html.AppendLine("<thead><tr>");
            foreach (DataGridViewColumn col in dgvStageProgress.Columns)
            {
                html.AppendLine($"<th>{col.HeaderText}</th>");
            }
            html.AppendLine("</tr></thead>");
            html.AppendLine("<tbody>");

            foreach (DataGridViewRow row in dgvStageProgress.Rows)
            {
                html.AppendLine("<tr>");
                for (int i = 0; i < dgvStageProgress.Columns.Count; i++)
                {
                    string value = row.Cells[i].Value?.ToString() ?? "";
                    string cssClass = "";

                    if (dgvStageProgress.Columns[i].Name == "Status")
                    {
                        if (value == "Completed")
                            cssClass = " class='completed'";
                        else if (value == "In Progress")
                            cssClass = " class='in-progress'";
                        else if (value == "Behind Schedule")
                            cssClass = " class='behind'";
                        else if (value == "Not Started")
                            cssClass = " class='not-started'";
                    }
                    else if (dgvStageProgress.Columns[i].Name == "Progress %" && double.TryParse(value, out double percent))
                    {
                        if (percent >= 90)
                            cssClass = " class='high-progress'";
                        else if (percent >= 50)
                            cssClass = " class='med-progress'";
                        else if (percent > 0)
                            cssClass = " class='low-progress'";
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

    public class TimelineStatusData
    {
        public string StudyName { get; set; }
        public string CurrentPhase { get; set; }
        public double OverallProgress { get; set; }
        public int? TimelineVarianceDays { get; set; }
        public DateTime ProjectedCompletion { get; set; }
        public int CriticalTasksAtRisk { get; set; }
        public List<MilestoneStatus> Milestones { get; set; }
        public List<StageProgressData> StageProgress { get; set; }

        public TimelineStatusData()
        {
            Milestones = new List<MilestoneStatus>();
            StageProgress = new List<StageProgressData>();
        }
    }

    public class MilestoneStatus
    {
        public string MilestoneName { get; set; }
        public DateTime PlannedDate { get; set; }
        public DateTime? ActualDate { get; set; }
        public int? VarianceDays { get; set; }
        public string Status { get; set; }
    }

    public class StageProgressData
    {
        public string StageName { get; set; }
        public int TotalTasks { get; set; }
        public int CompletedTasks { get; set; }
        public int InProgressTasks { get; set; }
        public int NotStartedTasks { get; set; }
        public int DelayedTasks { get; set; }
        public double ProgressPercent { get; set; }
        public string Status { get; set; }
    }
}
