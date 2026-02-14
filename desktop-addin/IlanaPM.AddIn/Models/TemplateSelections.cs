using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Template selections for unified Clinical Project Manager (Step 3 of wizard)
    /// Tracks which template types to generate and which sites to include
    /// </summary>
    public class TemplateSelections
    {
        // DATABASE TEMPLATES

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
            // Database templates
            GenerateDatabaseStudyStartup = false;
            GenerateDatabaseStudyImplementation = false;
            GenerateDatabaseStudyCloseout = false;
            GenerateDatabaseSiteActivation = false;
            GenerateDatabaseSiteCloseout = false;

            // Site lists
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
                return GenerateDatabaseStudyStartup ||
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

            // Database templates
            if (GenerateDatabaseStudyStartup)
                selections.Add("Study Start-Up (86 tasks)");

            if (GenerateDatabaseStudyImplementation)
                selections.Add("Study Implementation (10 milestones)");

            if (GenerateDatabaseStudyCloseout)
                selections.Add("Study Closeout (23 tasks)");

            if (GenerateDatabaseSiteActivation)
                selections.Add($"Site Activation ({SitesForDatabaseActivation.Count} sites, 34 tasks each)");

            if (GenerateDatabaseSiteCloseout)
                selections.Add($"Site Closeout ({SitesForDatabaseCloseout.Count} sites, 19 tasks each)");

            return selections.Count > 0
                ? string.Join(", ", selections)
                : "No templates selected";
        }
    }
}
