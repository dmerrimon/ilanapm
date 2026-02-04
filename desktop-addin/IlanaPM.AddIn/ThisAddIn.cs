using System;
using Microsoft.Office.Interop.MSProject;
using IlanaPM.AddIn.Models;

namespace IlanaPM.AddIn
{
    public partial class ThisAddIn
    {
        // Telemetry service for ML learning (opt-in consent required)
        public Services.TelemetryService TelemetryService { get; private set; }

        private void ThisAddIn_Startup(object sender, System.EventArgs e)
        {
            try
            {
                // Initialize telemetry service
                TelemetryService = new Services.TelemetryService(Application);
                System.Diagnostics.Debug.WriteLine("Telemetry service initialized");

                // Track session start
                if (TelemetryService != null)
                {
                    var properties = new System.Collections.Generic.Dictionary<string, object>
                    {
                        { "ms_project_version", Application.Version },
                        { "addin_version", System.Reflection.Assembly.GetExecutingAssembly().GetName().Version.ToString() }
                    };
                    TelemetryService.TrackEvent(TelemetryEventType.SessionStarted, properties);
                }

                System.Threading.Thread.Sleep(1000);
                CreateCustomFields();
            }
            catch (System.Exception ex)
            {
                System.Windows.Forms.MessageBox.Show(
                    "Custom field creation error: " + ex.Message,
                    "Ilana PM Startup",
                    System.Windows.Forms.MessageBoxButtons.OK,
                    System.Windows.Forms.MessageBoxIcon.Warning);
            }
        }

        private void ThisAddIn_Shutdown(object sender, System.EventArgs e)
        {
            try
            {
                // Dispose telemetry service (flushes remaining events)
                if (TelemetryService != null)
                {
                    TelemetryService.Dispose();
                    System.Diagnostics.Debug.WriteLine("Telemetry service disposed");
                }
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error disposing telemetry on shutdown: {ex.Message}");
            }
        }

        private void CreateCustomFields()
        {
            try
            {
                Project activeProject = Application.ActiveProject;
                if (activeProject == null)
                {
                    System.Diagnostics.Debug.WriteLine("No active project at startup");
                    return;
                }

                System.Diagnostics.Debug.WriteLine("Creating custom fields...");

                CreateCustomField(PjCustomField.pjCustomTaskText1, "Regulatory Authority");
                CreateCustomField(PjCustomField.pjCustomTaskText2, "Study Phase");
                CreateCustomField(PjCustomField.pjCustomTaskText3, "Therapeutic Area");
                CreateCustomField(PjCustomField.pjCustomTaskText4, "Task Category");
                CreateCustomField(PjCustomField.pjCustomTaskText5, "Gating Status");
                CreateCustomField(PjCustomField.pjCustomTaskText6, "ML Predicted Duration");

                CreateCustomField(PjCustomField.pjCustomTaskNumber1, "Checklist Completion %");
                CreateCustomField(PjCustomField.pjCustomTaskNumber2, "Risk Score");
                CreateCustomField(PjCustomField.pjCustomTaskNumber3, "ML Confidence %");

                CreateCustomField(PjCustomField.pjCustomTaskFlag1, "Is Mandatory");

                System.Diagnostics.Debug.WriteLine("Custom fields created successfully");
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("Error in CreateCustomFields: " + ex.Message);
            }
        }

        private void CreateCustomField(PjCustomField fieldType, string fieldName)
        {
            try
            {
                Application.CustomFieldRename(fieldType, fieldName);
                System.Diagnostics.Debug.WriteLine("Created field: " + fieldName);
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("Could not create " + fieldName + ": " +
ex.Message);
            }
        }

        #region VSTO generated code                                                                    

        private void InternalStartup()
        {
            this.Startup += new System.EventHandler(ThisAddIn_Startup);
            this.Shutdown += new System.EventHandler(ThisAddIn_Shutdown);
        }

        #endregion
    }
}