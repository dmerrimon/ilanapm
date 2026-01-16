using System;
using System.Windows.Forms;

namespace IlanaPM.AddIn.Services
{
    public class ViewManager
    {
        public void CreateValidationSummaryView(Microsoft.Office.Interop.MSProject.Application app)
        {
            string message = "Custom view creation is not supported in this version of MS Project." +
                Environment.NewLine + Environment.NewLine +
                "You can manually add custom fields to any view using:" +
                Environment.NewLine +
                "View → Tables → More Tables → Modify";

            MessageBox.Show(message,
                "Feature Not Available",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information);
        }

        public void CreateRiskDashboardView(Microsoft.Office.Interop.MSProject.Application app)
        {
            CreateValidationSummaryView(app);
        }

        public void CreateExecutiveSummaryView(Microsoft.Office.Interop.MSProject.Application app)
        {
            CreateValidationSummaryView(app);
        }

        public void CreateChecklistCompletionView(Microsoft.Office.Interop.MSProject.Application app)
        {
            CreateValidationSummaryView(app);
        }
    }
}