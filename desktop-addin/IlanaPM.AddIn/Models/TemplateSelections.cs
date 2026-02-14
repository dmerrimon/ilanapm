using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Template selections for unified Clinical Project Manager (Step 3 of wizard)
    /// Tracks which template types to generate and which sites to include
    /// </summary>
    public class TemplateSelections
    {
        /// <summary>
        /// Generate Full Study Timeline (regulatory phases, 50+ countries via API)
        /// </summary>
        public bool GenerateFullStudyTimeline { get; set; }

        /// <summary>
        /// Generate Site Startup templates (activation tasks from library)
        /// </summary>
        public bool GenerateSiteStartup { get; set; }

        /// <summary>
        /// Generate Site Implementation templates (ongoing tasks like IRB continuing review)
        /// </summary>
        public bool GenerateSiteImplementation { get; set; }

        /// <summary>
        /// Generate Site Closeout templates (shutdown tasks from library)
        /// </summary>
        public bool GenerateSiteCloseout { get; set; }

        /// <summary>
        /// Generate Study Closeout template (study-level closure, no site-specific tasks)
        /// </summary>
        public bool GenerateStudyCloseout { get; set; }

        // DATABASE TEMPLATES (NEW - from template library)

        /// <summary>
        /// Generate Study Start-Up from database (TPL_001 - 86 tasks, Study Award → FPI)
        /// </summary>
        public bool GenerateDatabaseStudyStartup { get; set; }

        /// <summary>
        /// Generate Study Implementation Milestones from database (TPL_002 - 10 milestones, FPI → LPLV)
        /// </summary>
        public bool GenerateDatabaseStudyImplementation { get; set; }

        /// <summary>
        /// Generate Study Closeout from database (TPL_003 - 23 tasks, LPLV → FDA submission)
        /// </summary>
        public bool GenerateDatabaseStudyCloseout { get; set; }

        /// <summary>
        /// Generate Site Activation from database (TPL_004 - 34 tasks per site)
        /// </summary>
        public bool GenerateDatabaseSiteActivation { get; set; }

        /// <summary>
        /// Generate Site Closeout from database (TPL_005 - 19 tasks per site)
        /// </summary>
        public bool GenerateDatabaseSiteCloseout { get; set; }

        // Site-specific selections (Step 4 of wizard)

        /// <summary>
        /// Site IDs to include in Startup templates (e.g., ["SITE-001", "SITE-003"])
        /// Only used if GenerateSiteStartup is true
        /// </summary>
        public List<string> SitesForStartup { get; set; }

        /// <summary>
        /// Site IDs to include in Implementation templates
        /// Only used if GenerateSiteImplementation is true
        /// </summary>
        public List<string> SitesForImplementation { get; set; }

        /// <summary>
        /// Site IDs to include in Closeout templates
        /// Only used if GenerateSiteCloseout is true
        /// </summary>
        public List<string> SitesForCloseout { get; set; }

        /// <summary>
        /// Site IDs to include in Database Site Activation templates (TPL_004)
        /// Only used if GenerateDatabaseSiteActivation is true
        /// </summary>
        public List<string> SitesForDatabaseActivation { get; set; }

        /// <summary>
        /// Site IDs to include in Database Site Closeout templates (TPL_005)
        /// Only used if GenerateDatabaseSiteCloseout is true
        /// </summary>
        public List<string> SitesForDatabaseCloseout { get; set; }

        public TemplateSelections()
        {
            // Legacy API templates
            GenerateFullStudyTimeline = false;
            GenerateSiteStartup = false;
            GenerateSiteImplementation = false;
            GenerateSiteCloseout = false;
            GenerateStudyCloseout = false;

            // Database templates
            GenerateDatabaseStudyStartup = false;
            GenerateDatabaseStudyImplementation = false;
            GenerateDatabaseStudyCloseout = false;
            GenerateDatabaseSiteActivation = false;
            GenerateDatabaseSiteCloseout = false;

            // Site lists
            SitesForStartup = new List<string>();
            SitesForImplementation = new List<string>();
            SitesForCloseout = new List<string>();
            SitesForDatabaseActivation = new List<string>();
            SitesForDatabaseCloseout = new List<string>();
        }

        /// <summary>
        /// Check if any templates are selected for generation
        /// </summary>
        public bool HasAnySelections
        {
            get
            {
                return GenerateFullStudyTimeline ||
                       GenerateSiteStartup ||
                       GenerateSiteImplementation ||
                       GenerateSiteCloseout ||
                       GenerateStudyCloseout ||
                       GenerateDatabaseStudyStartup ||
                       GenerateDatabaseStudyImplementation ||
                       GenerateDatabaseStudyCloseout ||
                       GenerateDatabaseSiteActivation ||
                       GenerateDatabaseSiteCloseout;
            }
        }

        /// <summary>
        /// Get count of total tasks to be generated (approximate)
        /// Note: Does not include cohort milestone tasks - use overload with cohortCount parameter
        /// </summary>
        public int GetEstimatedTaskCount()
        {
            return GetEstimatedTaskCount(0);
        }

        /// <summary>
        /// Get count of total tasks to be generated (approximate) including cohort milestones
        /// </summary>
        /// <param name="cohortCount">Number of cohorts for auto-generated milestone tasks</param>
        public int GetEstimatedTaskCount(int cohortCount)
        {
            int count = 0;

            // Legacy API templates
            if (GenerateFullStudyTimeline) count += 90; // ~90 tasks for full study
            if (GenerateSiteStartup) count += SitesForStartup.Count * 55; // ~55 tasks per site (actual observed from API)
            if (GenerateSiteImplementation)
            {
                count += SitesForImplementation.Count * 55; // ~55 tasks per site
                // Add cohort milestone tasks (auto-generated when Implementation is selected)
                // 5 tasks per cohort: Screened, Enrolled, Dosing Complete, Safety Review Meeting, Safety Committee Decision
                count += cohortCount * 5;
            }
            if (GenerateSiteCloseout) count += SitesForCloseout.Count * 35; // ~35 tasks per site
            if (GenerateStudyCloseout) count += 25; // ~25 study-level tasks

            // Database templates (exact counts from database)
            if (GenerateDatabaseStudyStartup) count += 86; // TPL_001
            if (GenerateDatabaseStudyImplementation) count += 10; // TPL_002
            if (GenerateDatabaseStudyCloseout) count += 23; // TPL_003
            if (GenerateDatabaseSiteActivation) count += SitesForDatabaseActivation.Count * 34; // TPL_004
            if (GenerateDatabaseSiteCloseout) count += SitesForDatabaseCloseout.Count * 19; // TPL_005

            return count;
        }

        /// <summary>
        /// Get human-readable summary of selections
        /// </summary>
        public string GetSummary()
        {
            var selections = new List<string>();

            // Legacy API templates
            if (GenerateFullStudyTimeline)
                selections.Add("Full Study Timeline");

            if (GenerateSiteStartup)
                selections.Add($"Site Startup ({SitesForStartup.Count} sites)");

            if (GenerateSiteImplementation)
                selections.Add($"Site Implementation ({SitesForImplementation.Count} sites)");

            if (GenerateSiteCloseout)
                selections.Add($"Site Closeout ({SitesForCloseout.Count} sites)");

            if (GenerateStudyCloseout)
                selections.Add("Study Closeout");

            // Database templates
            if (GenerateDatabaseStudyStartup)
                selections.Add("DB: Study Start-Up (86 tasks)");

            if (GenerateDatabaseStudyImplementation)
                selections.Add("DB: Study Implementation (10 milestones)");

            if (GenerateDatabaseStudyCloseout)
                selections.Add("DB: Study Closeout (23 tasks)");

            if (GenerateDatabaseSiteActivation)
                selections.Add($"DB: Site Activation ({SitesForDatabaseActivation.Count} sites, 34 tasks each)");

            if (GenerateDatabaseSiteCloseout)
                selections.Add($"DB: Site Closeout ({SitesForDatabaseCloseout.Count} sites, 19 tasks each)");

            return selections.Count > 0
                ? string.Join(", ", selections)
                : "No templates selected";
        }
    }
}
