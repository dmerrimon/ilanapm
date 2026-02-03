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

        public TemplateSelections()
        {
            GenerateFullStudyTimeline = false;
            GenerateSiteStartup = false;
            GenerateSiteImplementation = false;
            GenerateSiteCloseout = false;
            GenerateStudyCloseout = false;

            SitesForStartup = new List<string>();
            SitesForImplementation = new List<string>();
            SitesForCloseout = new List<string>();
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
                       GenerateStudyCloseout;
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

            return count;
        }

        /// <summary>
        /// Get human-readable summary of selections
        /// </summary>
        public string GetSummary()
        {
            var selections = new List<string>();

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

            return selections.Count > 0
                ? string.Join(", ", selections)
                : "No templates selected";
        }
    }
}
