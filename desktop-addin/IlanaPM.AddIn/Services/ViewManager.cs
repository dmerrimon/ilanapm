using System;
using System.Windows.Forms;
using MSProject = Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Services
{
    public class ViewManager
    {
        public void CreateValidationSummaryView(MSProject.Application app)
        {
            ShowViewInstructions("Validation Summary", new string[] {
                  "Name",
                  "Task Category",
                  "Risk Score",
                  "Gating Status",
                  "Is Mandatory",
                  "Duration"
              });
        }

        public void CreateRiskDashboardView(MSProject.Application app)
        {
            ShowViewInstructions("Risk Dashboard", new string[] {
                  "Name",
                  "Risk Score",
                  "ML Predicted Duration",
                  "ML Confidence %",
                  "Task Category"
              });
        }

        public void CreateExecutiveSummaryView(MSProject.Application app)
        {
            ShowViewInstructions("Executive Summary", new string[] {
                  "Name",
                  "Start",
                  "Finish",
                  "Task Category",
                  "Gating Status"
              });
        }

        public void CreateChecklistCompletionView(MSProject.Application app)
        {
            ShowViewInstructions("Checklist Completion", new string[] {
                  "Name",
                  "Checklist Completion %",
                  "Task Category",
                  "% Complete"
              });
        }

        private void ShowViewInstructions(string viewName, string[] fields)
        {
            string fieldList = string.Join("\n   • ", fields);

            MessageBox.Show(
                "To create the " + viewName + " view:\n\n" +
                "1. In MS Project, go to: View → Tables → More Tables\n" +
                "2. Click 'New' to create a new table\n" +
                "3. Name it: Ilana PM " + viewName + "\n" +
                "4. Add these columns:\n   • " + fieldList + "\n\n" +
                "Your custom fields (Risk Score, Task Category, etc.) are already populated with data!",
                "Ilana PM - " + viewName,
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
    }
}