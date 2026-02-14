using System;
using System.Collections.Generic;
using System.Linq;
using IlanaPM.AddIn.Models;
using MSProject = Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Helper for saving and loading study metadata to/from MS Project custom fields
    ///
    /// Storage Strategy:
    /// - ProjectSummaryTask.Text1 = Phase
    /// - ProjectSummaryTask.Text2 = Therapeutic Area
    /// - ProjectSummaryTask.Text3 = Primary Country
    /// - ProjectSummaryTask.Text4 = Additional Countries (comma-separated)
    /// - ProjectSummaryTask.Text5 = Study ID
    ///
    /// Benefits:
    /// - Persists in .mpp file (survives file save/open)
    /// - Automatically saved after template generation
    /// - Automatically loaded before validation
    /// - No duplicate data entry
    /// - Auditable (can see in MS Project UI)
    /// </summary>
    public static class MetadataHelper
    {
        // Custom field mappings (using Text fields on Project Summary Task)
        private const MSProject.PjField FIELD_PHASE = MSProject.PjField.pjTaskText1;
        private const MSProject.PjField FIELD_THERAPEUTIC_AREA = MSProject.PjField.pjTaskText2;
        private const MSProject.PjField FIELD_PRIMARY_COUNTRY = MSProject.PjField.pjTaskText3;
        private const MSProject.PjField FIELD_ADDITIONAL_COUNTRIES = MSProject.PjField.pjTaskText4;
        private const MSProject.PjField FIELD_STUDY_ID = MSProject.PjField.pjTaskText5;

        /// <summary>
        /// Save study metadata to MS Project custom fields
        ///
        /// Called automatically after template generation
        /// Can also be called manually after user fills metadata form
        /// </summary>
        /// <param name="metadata">Study metadata to save</param>
        /// <returns>True if successful</returns>
        public static bool SaveToProject(StudyMetadata metadata)
        {
            try
            {
                var project = Globals.ThisAddIn.Application.ActiveProject;
                if (project == null)
                {
                    System.Diagnostics.Debug.WriteLine("MetadataHelper: No active project");
                    return false;
                }

                // Get project summary task (task 0)
                var summaryTask = project.ProjectSummaryTask;
                if (summaryTask == null)
                {
                    System.Diagnostics.Debug.WriteLine("MetadataHelper: No project summary task");
                    return false;
                }

                // Save core metadata fields
                summaryTask.SetField(FIELD_PHASE, metadata.Phase ?? "");
                summaryTask.SetField(FIELD_THERAPEUTIC_AREA, metadata.TherapeuticArea ?? "");
                summaryTask.SetField(FIELD_PRIMARY_COUNTRY, metadata.PrimaryCountry ?? "");

                // Save additional countries as comma-separated string
                if (metadata.AdditionalCountries != null && metadata.AdditionalCountries.Any())
                {
                    summaryTask.SetField(FIELD_ADDITIONAL_COUNTRIES, string.Join(",", metadata.AdditionalCountries));
                }
                else
                {
                    summaryTask.SetField(FIELD_ADDITIONAL_COUNTRIES, "");
                }

                // Save study ID if provided
                if (!string.IsNullOrWhiteSpace(metadata.StudyId))
                {
                    summaryTask.SetField(FIELD_STUDY_ID, metadata.StudyId);
                }

                System.Diagnostics.Debug.WriteLine($"MetadataHelper: Saved metadata - {metadata}");
                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"MetadataHelper: Error saving metadata - {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Load study metadata from MS Project custom fields
        ///
        /// Called automatically before validation
        /// Returns null if no metadata found or project not open
        /// </summary>
        /// <returns>StudyMetadata or null if not found</returns>
        public static StudyMetadata LoadFromProject()
        {
            try
            {
                var project = Globals.ThisAddIn.Application.ActiveProject;
                if (project == null)
                {
                    System.Diagnostics.Debug.WriteLine("MetadataHelper: No active project");
                    return null;
                }

                var summaryTask = project.ProjectSummaryTask;
                if (summaryTask == null)
                {
                    System.Diagnostics.Debug.WriteLine("MetadataHelper: No project summary task");
                    return null;
                }

                // Read core metadata fields
                var phase = GetFieldValue(summaryTask, FIELD_PHASE);
                var therapeuticArea = GetFieldValue(summaryTask, FIELD_THERAPEUTIC_AREA);
                var primaryCountry = GetFieldValue(summaryTask, FIELD_PRIMARY_COUNTRY);

                // Check if any metadata exists
                if (string.IsNullOrWhiteSpace(phase) &&
                    string.IsNullOrWhiteSpace(therapeuticArea) &&
                    string.IsNullOrWhiteSpace(primaryCountry))
                {
                    System.Diagnostics.Debug.WriteLine("MetadataHelper: No metadata found in project");
                    return null;
                }

                // Read additional countries
                var additionalCountriesStr = GetFieldValue(summaryTask, FIELD_ADDITIONAL_COUNTRIES);
                var additionalCountries = new List<string>();
                if (!string.IsNullOrWhiteSpace(additionalCountriesStr))
                {
                    additionalCountries = additionalCountriesStr
                        .Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries)
                        .Select(c => c.Trim())
                        .Where(c => !string.IsNullOrWhiteSpace(c))
                        .ToList();
                }

                // Read study ID
                var studyId = GetFieldValue(summaryTask, FIELD_STUDY_ID);

                var metadata = new StudyMetadata
                {
                    Phase = phase,
                    TherapeuticArea = therapeuticArea,
                    PrimaryCountry = primaryCountry,
                    AdditionalCountries = additionalCountries,
                    StudyId = studyId,
                    StudyName = project.Name,
                    MetadataSource = "project_file"
                };

                System.Diagnostics.Debug.WriteLine($"MetadataHelper: Loaded metadata - {metadata}");
                return metadata;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"MetadataHelper: Error loading metadata - {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Check if project has valid study metadata
        /// </summary>
        /// <returns>True if metadata exists and is valid</returns>
        public static bool HasValidMetadata()
        {
            var metadata = LoadFromProject();
            return metadata != null && metadata.IsValid();
        }

        /// <summary>
        /// Clear all study metadata from project
        /// </summary>
        public static bool ClearMetadata()
        {
            try
            {
                var project = Globals.ThisAddIn.Application.ActiveProject;
                if (project == null) return false;

                var summaryTask = project.ProjectSummaryTask;
                if (summaryTask == null) return false;

                summaryTask.SetField(FIELD_PHASE, "");
                summaryTask.SetField(FIELD_THERAPEUTIC_AREA, "");
                summaryTask.SetField(FIELD_PRIMARY_COUNTRY, "");
                summaryTask.SetField(FIELD_ADDITIONAL_COUNTRIES, "");
                summaryTask.SetField(FIELD_STUDY_ID, "");

                System.Diagnostics.Debug.WriteLine("MetadataHelper: Cleared all metadata");
                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"MetadataHelper: Error clearing metadata - {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Create metadata from template configuration (used after template generation)
        /// </summary>
        /// <param name="config">Template configuration from wizard</param>
        /// <returns>StudyMetadata</returns>
        public static StudyMetadata FromTemplateConfiguration(TemplateConfiguration config)
        {
            return new StudyMetadata
            {
                Phase = config.StudyPhase,
                TherapeuticArea = config.TherapeuticArea,
                PrimaryCountry = config.CountryCode,
                MetadataSource = "template_wizard"
            };
        }

        /// <summary>
        /// Safely get string value from custom field
        /// </summary>
        private static string GetFieldValue(MSProject.Task task, MSProject.PjField field)
        {
            try
            {
                var value = task.GetField(field);
                return value?.ToString()?.Trim() ?? "";
            }
            catch
            {
                return "";
            }
        }

        /// <summary>
        /// Get metadata display string for UI (e.g., status bar, validation results)
        /// </summary>
        /// <returns>Formatted string or "Not configured" if no metadata</returns>
        public static string GetMetadataDisplayString()
        {
            var metadata = LoadFromProject();
            if (metadata == null || !metadata.IsValid())
            {
                return "Study metadata not configured";
            }
            return metadata.ToString();
        }

        /// <summary>
        /// Validate metadata and return user-friendly error message
        /// </summary>
        /// <returns>Error message or null if valid</returns>
        public static string ValidateMetadata()
        {
            var metadata = LoadFromProject();
            if (metadata == null)
            {
                return "Study metadata not found. Please configure study information.";
            }

            return metadata.GetValidationError();
        }
    }
}
