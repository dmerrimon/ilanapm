using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Types of templates supported by Unified Template Manager
    /// </summary>
    public enum TemplateType
    {
        /// <summary>
        /// Full study timeline from API (50+ countries, all regulatory phases)
        /// </summary>
        FullStudyTimeline,

        /// <summary>
        /// Site activation tasks from CountryTemplateLibrary (23 countries)
        /// </summary>
        SiteStartup,

        /// <summary>
        /// Implementation/Active phase tasks (IRB continuing review, etc.)
        /// </summary>
        SiteImplementation,

        /// <summary>
        /// Site shutdown tasks from CountryTemplateLibrary
        /// </summary>
        SiteCloseout,

        /// <summary>
        /// Study-level closure tasks (no site-specific tasks)
        /// </summary>
        StudyCloseout,

        /// <summary>
        /// Protocol amendment workflow tasks (future)
        /// </summary>
        AmendmentWorkflow
    }

    /// <summary>
    /// Phase type for filtering and categorization
    /// Maps to Text12 custom field
    /// </summary>
    public enum PhaseType
    {
        Startup,              // Site activation
        Active,               // Actively enrolling
        SiteCloseout,         // Site shutdown
        StudyCloseout,        // Study-level shutdown
        Amendment             // Protocol amendment
    }

    /// <summary>
    /// Subphase for site startup tasks
    /// Maps to Text13 custom field
    /// </summary>
    public enum StartupSubphase
    {
        EssentialDocuments,   // Document collection
        IRBSubmission,        // IRB package prep + submit
        IRBReview,            // Waiting for IRB
        Training,             // Site training
        Activation            // Final activation steps
    }

    /// <summary>
    /// Subphase for site closeout tasks
    /// Maps to Text13 custom field
    /// </summary>
    public enum CloseoutSubphase
    {
        PatientCloseout,      // Final patient visits
        DocumentCollection,   // Collect final docs
        Archival,             // Archive site files
        Closure               // Close site
    }

    /// <summary>
    /// Filter options for template task generation
    /// Used in preview step to allow users to filter tasks before generation
    /// </summary>
    public class FilterOptions
    {
        /// <summary>
        /// Phase types to include (null = include all)
        /// </summary>
        public List<string> IncludedPhaseTypes { get; set; }

        /// <summary>
        /// Task categories to include (null = include all)
        /// Examples: "Regulatory", "Clinical", "Admin", "Lab", "Data"
        /// </summary>
        public List<string> IncludedCategories { get; set; }

        /// <summary>
        /// Whether to include optional (non-mandatory) tasks
        /// </summary>
        public bool IncludeOptional { get; set; }

        /// <summary>
        /// Specific task IDs to exclude (for custom filtering)
        /// </summary>
        public List<string> ExcludedTaskIds { get; set; }

        public FilterOptions()
        {
            IncludedPhaseTypes = new List<string>();
            IncludedCategories = new List<string>();
            IncludeOptional = true;
            ExcludedTaskIds = new List<string>();
        }

        /// <summary>
        /// Check if a task passes the filter criteria
        /// </summary>
        public bool PassesFilter(TemplateTask task, string subphase = null)
        {
            if (task == null) return false;

            // Check excluded task IDs
            if (ExcludedTaskIds.Contains(task.task_id))
            {
                return false;
            }

            // Check optional tasks
            if (!IncludeOptional && !task.is_mandatory)
            {
                return false;
            }

            // Check phase types (if specified)
            if (IncludedPhaseTypes.Count > 0 && !string.IsNullOrEmpty(subphase))
            {
                if (!IncludedPhaseTypes.Contains(subphase))
                {
                    return false;
                }
            }

            // Check categories (if specified)
            if (IncludedCategories.Count > 0 && !string.IsNullOrEmpty(task.category))
            {
                if (!IncludedCategories.Contains(task.category))
                {
                    return false;
                }
            }

            return true;
        }
    }

    /// <summary>
    /// Configuration for template loading
    /// </summary>
    public class TemplateConfiguration
    {
        /// <summary>
        /// Type of template to load
        /// </summary>
        public TemplateType TemplateType { get; set; }

        /// <summary>
        /// Country code (ISO 3166-1 alpha-3)
        /// Required for all template types except StudyCloseout
        /// </summary>
        public string CountryCode { get; set; }

        /// <summary>
        /// Site ID (for site-specific templates)
        /// Required for SiteStartup and SiteCloseout
        /// </summary>
        public string SiteId { get; set; }

        /// <summary>
        /// Study phase (for full study timeline)
        /// Examples: "Phase I", "Phase II", "Phase III", "Phase IV"
        /// </summary>
        public string StudyPhase { get; set; }

        /// <summary>
        /// Therapeutic area (for full study timeline)
        /// Examples: "Oncology", "Infectious Disease", "Cardiology"
        /// </summary>
        public string TherapeuticArea { get; set; }

        /// <summary>
        /// Custom column names (for full study timeline)
        /// </summary>
        public Dictionary<string, string> CustomColumnNames { get; set; }

        public TemplateConfiguration()
        {
            CustomColumnNames = new Dictionary<string, string>();
        }
    }

    /// <summary>
    /// Result of template loading operation
    /// </summary>
    public class TemplateResult
    {
        /// <summary>
        /// Template type that was loaded
        /// </summary>
        public TemplateType TemplateType { get; set; }

        /// <summary>
        /// Timeline with tasks and dependencies
        /// </summary>
        public Timeline Timeline { get; set; }

        /// <summary>
        /// Number of tasks generated
        /// </summary>
        public int TaskCount { get; set; }

        /// <summary>
        /// Estimated duration in days
        /// </summary>
        public int EstimatedDuration { get; set; }

        /// <summary>
        /// Site ID (if applicable)
        /// </summary>
        public string SiteId { get; set; }

        /// <summary>
        /// Country code
        /// </summary>
        public string CountryCode { get; set; }

        /// <summary>
        /// Template source (API, Library-USA, etc.)
        /// </summary>
        public string TemplateSource { get; set; }

        /// <summary>
        /// Phase type for all tasks
        /// </summary>
        public string PhaseType { get; set; }

        /// <summary>
        /// Whether filters were applied
        /// </summary>
        public bool FiltersApplied { get; set; }

        /// <summary>
        /// Number of tasks before filtering (if filters applied)
        /// </summary>
        public int? TaskCountBeforeFiltering { get; set; }
    }
}
