using System;
using Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn
{
    public partial class ThisAddIn
    {
        private void ThisAddIn_Startup(object sender, System.EventArgs e)
        {
            // Create custom fields if they don't exist
            CreateCustomFields();

            // Check for updates
            _ = CheckForUpdatesAsync();
        }

        private void ThisAddIn_Shutdown(object sender, System.EventArgs e)
        {
            // Cleanup code if needed
        }

        private void CreateCustomFields()
        {
            try
            {
                Project activeProject = Application.ActiveProject;
                if (activeProject == null) return;

                // Text fields
                CreateCustomFieldIfNotExists(PjCustomField.pjCustomTaskText1, "Regulatory Authority");
                CreateCustomFieldIfNotExists(PjCustomField.pjCustomTaskText2, "Study Phase");
                CreateCustomFieldIfNotExists(PjCustomField.pjCustomTaskText3, "Therapeutic Area");
                CreateCustomFieldIfNotExists(PjCustomField.pjCustomTaskText4, "Task Category");
                CreateCustomFieldIfNotExists(PjCustomField.pjCustomTaskText5, "Gating Status");
                CreateCustomFieldIfNotExists(PjCustomField.pjCustomTaskText6, "ML Predicted Duration");

                // Number fields
                CreateCustomFieldIfNotExists(PjCustomField.pjCustomTaskNumber1, "Checklist Completion %");
                CreateCustomFieldIfNotExists(PjCustomField.pjCustomTaskNumber2, "Risk Score");
                CreateCustomFieldIfNotExists(PjCustomField.pjCustomTaskNumber3, "ML Confidence %");

                // Yes/No fields
                CreateCustomFieldIfNotExists(PjCustomField.pjCustomTaskFlag1, "Is Mandatory");
            }
            catch (Exception ex)
            {
                // Log but don't crash on custom field creation
                System.Diagnostics.Debug.WriteLine($"Custom field creation error: {ex.Message}");
            }
        }

        private void CreateCustomFieldIfNotExists(PjCustomField fieldType, string fieldName)
        {
            try
            {
                // Try to get the field to see if it exists
                var field = Application.ActiveProject.ProjectSummaryTask.GetField(fieldType);

                // Check if already named
                try
                {
                    var existingName = Application.CustomFieldGetName(fieldType);
                    if (string.IsNullOrEmpty(existingName) || existingName == fieldType.ToString())
                    {
                        // Field exists but is unnamed, so rename it
                        Application.CustomFieldRename(fieldType, fieldName);
                    }
                }
                catch
                {
                    // Field might not be named yet, try to rename it
                    Application.CustomFieldRename(fieldType, fieldName);
                }
            }
            catch (Exception ex)
            {
                // Field might already exist or not be available
                System.Diagnostics.Debug.WriteLine($"Could not create/rename custom field {fieldName}: {ex.Message}");
            }
        }

        private async System.Threading.Tasks.Task CheckForUpdatesAsync()
        {
            try
            {
                // TODO: Implement version checking logic
                // For now, just a placeholder
                await System.Threading.Tasks.Task.CompletedTask;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Update check error: {ex.Message}");
            }
        }

        #region VSTO generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InternalStartup()
        {
            this.Startup += new System.EventHandler(ThisAddIn_Startup);
            this.Shutdown += new System.EventHandler(ThisAddIn_Shutdown);
        }

        #endregion
    }
}
