using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using MSProject = Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Unified configuration for Clinical Project Manager
    /// Replaces separate ClinicalMetadata and TemplateConfiguration
    /// Stored as JSON in ProjectSummaryTask.Notes field
    /// </summary>
    public class ClinicalProjectConfiguration
    {
        /// <summary>
        /// Configuration version for backward compatibility
        /// </summary>
        public string Version { get; set; }

        // STEP 1: Study Metadata (captured for ML feedback loop)

        /// <summary>
        /// Study name/identifier (e.g., "ACME-001-Phase-III")
        /// </summary>
        public string StudyName { get; set; }

        /// <summary>
        /// Study phase: Phase I, Phase II, Phase III, Phase IV
        /// Used for ML learning and task duration predictions
        /// </summary>
        public string StudyPhase { get; set; }

        /// <summary>
        /// Therapeutic area: Oncology, Infectious Disease, Cardiology, etc.
        /// Used for ML learning and regulatory timeline predictions
        /// </summary>
        public string TherapeuticArea { get; set; }

        /// <summary>
        /// Countries involved in the study (ISO 3166-1 alpha-3 codes)
        /// Used for ML learning and country-specific predictions
        /// </summary>
        public List<string> Countries { get; set; }

        // STEP 2: Sites

        /// <summary>
        /// Clinical trial sites with template generation preferences
        /// </summary>
        public List<SiteConfiguration> Sites { get; set; }

        // Future: Amendments and Cohorts (for backward compatibility with ClinicalMetadata)

        /// <summary>
        /// Protocol amendments (for future Phase 3 implementation)
        /// </summary>
        public List<Amendment> Amendments { get; set; }

        /// <summary>
        /// Patient cohorts (for future implementation)
        /// </summary>
        public List<Cohort> Cohorts { get; set; }

        // STEP 3 & 4: Template Selections

        /// <summary>
        /// Which template types to generate and site-specific selections
        /// </summary>
        public TemplateSelections Templates { get; set; }

        // STEP 4: Filters

        /// <summary>
        /// Filter options for task preview (optional tasks, categories, etc.)
        /// </summary>
        public FilterOptions Filters { get; set; }

        // Metadata

        /// <summary>
        /// When this configuration was last modified
        /// </summary>
        public DateTime LastModified { get; set; }

        /// <summary>
        /// User who last modified (for audit trail)
        /// </summary>
        public string LastModifiedBy { get; set; }

        public ClinicalProjectConfiguration()
        {
            Version = "2.0"; // Version 2.0 = Unified wizard format
            StudyName = "";
            StudyPhase = "";
            TherapeuticArea = "";
            Countries = new List<string>();
            Sites = new List<SiteConfiguration>();
            Amendments = new List<Amendment>();
            Cohorts = new List<Cohort>();
            Templates = new TemplateSelections();
            Filters = new FilterOptions();
            LastModified = DateTime.Now;
            LastModifiedBy = Environment.UserName;
        }

        // Persistence methods

        /// <summary>
        /// Save configuration to MS Project ProjectSummaryTask.Notes field as JSON
        /// Same storage location as legacy ClinicalMetadata for backward compatibility
        /// </summary>
        public void SaveToProject(MSProject.Application app)
        {
            if (app?.ActiveProject == null)
                throw new InvalidOperationException("No active project to save to");

            try
            {
                var project = app.ActiveProject;
                var summaryTask = project.ProjectSummaryTask;

                // Update metadata
                this.LastModified = DateTime.Now;
                this.LastModifiedBy = Environment.UserName;

                // Serialize to JSON with indentation for readability
                string json = JsonConvert.SerializeObject(this, Formatting.Indented);

                // Save to Notes field
                summaryTask.Notes = json;

                System.Diagnostics.Debug.WriteLine($"Saved ClinicalProjectConfiguration to project: {StudyName}");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error saving configuration: {ex.Message}");
                throw new InvalidOperationException($"Failed to save configuration: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Load configuration from MS Project ProjectSummaryTask.Notes field
        /// Returns new empty config if none exists
        /// </summary>
        public static ClinicalProjectConfiguration LoadFromProject(MSProject.Application app)
        {
            if (app?.ActiveProject == null)
                return new ClinicalProjectConfiguration();

            try
            {
                var project = app.ActiveProject;
                var summaryTask = project.ProjectSummaryTask;

                if (string.IsNullOrWhiteSpace(summaryTask.Notes))
                {
                    System.Diagnostics.Debug.WriteLine("No configuration found in project, returning new config");
                    return new ClinicalProjectConfiguration();
                }

                // Try to deserialize as ClinicalProjectConfiguration (version 2.0)
                try
                {
                    var config = JsonConvert.DeserializeObject<ClinicalProjectConfiguration>(summaryTask.Notes);
                    if (config != null && config.Version == "2.0")
                    {
                        System.Diagnostics.Debug.WriteLine($"Loaded ClinicalProjectConfiguration v2.0: {config.StudyName}");
                        return config;
                    }
                }
                catch (JsonException)
                {
                    // Not version 2.0, try legacy format
                }

                // Try to deserialize as legacy ClinicalMetadata (version 1.0)
                try
                {
                    var legacyMetadata = JsonConvert.DeserializeObject<ClinicalMetadata>(summaryTask.Notes);
                    if (legacyMetadata != null && legacyMetadata.clinical_metadata_version == "1.0")
                    {
                        System.Diagnostics.Debug.WriteLine("Migrating legacy ClinicalMetadata v1.0 to v2.0");
                        return MigrateFromLegacy(legacyMetadata);
                    }
                }
                catch (JsonException)
                {
                    // Not legacy format either
                }

                // Unrecognized format, return new config
                System.Diagnostics.Debug.WriteLine("Unrecognized configuration format, returning new config");
                return new ClinicalProjectConfiguration();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading configuration: {ex.Message}");
                return new ClinicalProjectConfiguration();
            }
        }

        /// <summary>
        /// Migrate legacy ClinicalMetadata (v1.0) to ClinicalProjectConfiguration (v2.0)
        /// </summary>
        private static ClinicalProjectConfiguration MigrateFromLegacy(ClinicalMetadata legacy)
        {
            var config = new ClinicalProjectConfiguration
            {
                Version = "2.0",
                Sites = new List<SiteConfiguration>(),
                Amendments = legacy.amendments ?? new List<Amendment>(),
                Cohorts = legacy.cohorts ?? new List<Cohort>()
            };

            // Convert legacy Site to SiteConfiguration
            if (legacy.sites != null)
            {
                foreach (var site in legacy.sites)
                {
                    config.Sites.Add(SiteConfiguration.FromSite(site));
                }
            }

            return config;
        }

        /// <summary>
        /// Export to legacy ClinicalMetadata format for backward compatibility
        /// Used when accessing from old forms (ClinicalSetupForm, etc.)
        /// </summary>
        public ClinicalMetadata ToLegacyMetadata()
        {
            var metadata = new ClinicalMetadata
            {
                clinical_metadata_version = "1.0",
                sites = new List<Site>(),
                amendments = this.Amendments ?? new List<Amendment>(),
                cohorts = this.Cohorts ?? new List<Cohort>()
            };

            // Convert SiteConfiguration back to Site
            if (this.Sites != null)
            {
                foreach (var siteConfig in this.Sites)
                {
                    metadata.sites.Add(siteConfig.ToSite());
                }
            }

            return metadata;
        }

        /// <summary>
        /// Check if configuration has any data
        /// </summary>
        public bool IsEmpty
        {
            get
            {
                return string.IsNullOrWhiteSpace(StudyName) &&
                       (Sites == null || Sites.Count == 0) &&
                       (Amendments == null || Amendments.Count == 0);
            }
        }

        /// <summary>
        /// Get summary for display (e.g., "ACME-001: Phase III Oncology, 5 sites")
        /// </summary>
        public string GetSummary()
        {
            int siteCount = Sites?.Count ?? 0;
            string phase = !string.IsNullOrEmpty(StudyPhase) ? StudyPhase : "Unknown Phase";
            string area = !string.IsNullOrEmpty(TherapeuticArea) ? TherapeuticArea : "Unknown Area";

            return $"{StudyName}: {phase} {area}, {siteCount} site(s)";
        }
    }
}
