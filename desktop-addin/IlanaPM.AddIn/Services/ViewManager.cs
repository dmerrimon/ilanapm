using System;
using System.Windows.Forms;
using MSProject = Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Services
{
    public class ViewManager
    {
        public void CreateValidationSummaryView(MSProject.Application app)
        {
            try
            {
                CreateCustomTable(app, "Ilana PM Validation Summary", new[]
                {
                    (MSProject.PjField.pjTaskName, "Name", 30),
                    (MSProject.PjField.pjTaskText4, "Task Category", 15),
                    (MSProject.PjField.pjTaskNumber2, "Risk Score", 10),
                    (MSProject.PjField.pjTaskText5, "Gating Status", 12),
                    (MSProject.PjField.pjTaskFlag1, "Is Mandatory", 10),
                    (MSProject.PjField.pjTaskDuration, "Duration", 10)
                });

                app.ViewApply("Ilana PM Validation Summary");

                MessageBox.Show(
                    "Validation Summary view created and applied!\n\n" +
                    "This view shows:\n" +
                    "• Task names and categories\n" +
                    "• Risk scores (ML predictions)\n" +
                    "• Gating status and mandatory flags\n" +
                    "• Task durations",
                    "View Created",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error creating Validation Summary view: " + ex.Message,
                    "View Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        public void CreateRiskDashboardView(MSProject.Application app)
        {
            try
            {
                CreateCustomTable(app, "Ilana PM Risk Dashboard", new[]
                {
                    (MSProject.PjField.pjTaskName, "Name", 30),
                    (MSProject.PjField.pjTaskNumber2, "Risk Score", 10),
                    (MSProject.PjField.pjTaskText6, "ML Predicted Duration", 15),
                    (MSProject.PjField.pjTaskNumber3, "ML Confidence %", 12),
                    (MSProject.PjField.pjTaskText4, "Task Category", 15)
                });

                app.ViewApply("Ilana PM Risk Dashboard");

                MessageBox.Show(
                    "Risk Dashboard view created and applied!\n\n" +
                    "This view shows:\n" +
                    "• Task names\n" +
                    "• Risk scores (higher = more risk)\n" +
                    "• ML predicted durations\n" +
                    "• ML confidence percentages\n" +
                    "• Task categories",
                    "View Created",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error creating Risk Dashboard view: " + ex.Message,
                    "View Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        public void CreateExecutiveSummaryView(MSProject.Application app)
        {
            try
            {
                CreateCustomTable(app, "Ilana PM Executive Summary", new[]
                {
                    (MSProject.PjField.pjTaskName, "Name", 35),
                    (MSProject.PjField.pjTaskStart, "Start", 12),
                    (MSProject.PjField.pjTaskFinish, "Finish", 12),
                    (MSProject.PjField.pjTaskText4, "Task Category", 15),
                    (MSProject.PjField.pjTaskText5, "Gating Status", 12)
                });

                app.ViewApply("Ilana PM Executive Summary");

                MessageBox.Show(
                    "Executive Summary view created and applied!\n\n" +
                    "This view shows:\n" +
                    "• Task names\n" +
                    "• Start and finish dates\n" +
                    "• Task categories\n" +
                    "• Gating status (critical milestones)",
                    "View Created",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error creating Executive Summary view: " + ex.Message,
                    "View Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        public void CreateChecklistCompletionView(MSProject.Application app)
        {
            try
            {
                CreateCustomTable(app, "Ilana PM Checklist Completion", new[]
                {
                    (MSProject.PjField.pjTaskName, "Name", 35),
                    (MSProject.PjField.pjTaskNumber1, "Checklist Completion %", 15),
                    (MSProject.PjField.pjTaskText4, "Task Category", 15),
                    (MSProject.PjField.pjTaskPercentComplete, "% Complete", 10)
                });

                app.ViewApply("Ilana PM Checklist Completion");

                MessageBox.Show(
                    "Checklist Completion view created and applied!\n\n" +
                    "This view shows:\n" +
                    "• Task names\n" +
                    "• Checklist completion percentages\n" +
                    "• Task categories\n" +
                    "• Overall task completion",
                    "View Created",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error creating Checklist Completion view: " + ex.Message,
                    "View Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        public void CreateIlanaPMWorkflowView(MSProject.Application app)
        {
            try
            {
                CreateCustomTable(app, "Ilana PM Workflow", new[]
                {
                    (MSProject.PjField.pjTaskMode, "Task Mode", 15),
                    (MSProject.PjField.pjTaskText4, "Task Category", 12),
                    (MSProject.PjField.pjTaskName, "Task Name", 30),
                    (MSProject.PjField.pjTaskDuration, "Duration", 10),
                    (MSProject.PjField.pjTaskBaselineFinish, "Original Projected Completion Date", 15),
                    (MSProject.PjField.pjTaskStart, "Start", 15),
                    (MSProject.PjField.pjTaskFinish, "Finish", 15),
                    (MSProject.PjField.pjTaskNumber2, "Risk Score", 10)
                });

                app.ViewApply("Ilana PM Workflow");

                MessageBox.Show(
                    "Ilana PM Workflow view created and applied!\n\n" +
                    "This view shows:\n" +
                    "• Task mode (Auto/Manual scheduled)\n" +
                    "• Task category\n" +
                    "• Task name and duration\n" +
                    "• Original and current completion dates\n" +
                    "• Risk score (from validation)",
                    "View Created",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error creating Ilana PM Workflow view: " + ex.Message,
                    "View Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void CreateCustomTable(MSProject.Application app, string tableName,
            (MSProject.PjField field, string title, int width)[] columns)
        {
            if (app.ActiveProject == null)
            {
                throw new Exception("No active project. Please open or create a project first.");
            }

            // Check if table already exists, delete it if so
            try
            {
                app.TableEditEx(tableName, true, false, null, null, null, null, null, null, null, null);
            }
            catch
            {
                // Table doesn't exist, which is fine
            }

            // Build arrays for TableEditEx
            object[] fieldArray = new object[columns.Length];
            object[] titleArray = new object[columns.Length];
            object[] widthArray = new object[columns.Length];
            object[] alignArray = new object[columns.Length];
            object[] showInMenuArray = new object[columns.Length];
            object[] wrapTextArray = new object[columns.Length];

            for (int i = 0; i < columns.Length; i++)
            {
                fieldArray[i] = columns[i].field;
                titleArray[i] = columns[i].title;
                widthArray[i] = columns[i].width;
                alignArray[i] = MSProject.PjAlignment.pjLeft;
                showInMenuArray[i] = true;
                wrapTextArray[i] = false;
            }

            // Create the table
            app.TableEditEx(
                Name: tableName,
                TaskTable: true,
                Create: true,
                OverwriteExisting: true,
                NewName: tableName,
                FieldName: fieldArray,
                Title: titleArray,
                Width: widthArray,
                Align: alignArray,
                ShowInMenu: true,
                LockFirstColumn: true,
                DateFormat: MSProject.PjDateFormat.pjDateDefault,
                RowHeight: 1,
                ColumnPosition: null,
                AlignTitle: alignArray,
                HeaderAutoRowHeightAdjustment: true,
                HeaderTextWrap: false
            );
        }
    }
}