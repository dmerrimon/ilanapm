using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Response from GET /api/v1/templates/library
    /// Lists all available timeline templates
    /// </summary>
    public class TemplateListResponse
    {
        public List<TemplateMetadata> templates { get; set; }
        public int count { get; set; }

        public TemplateListResponse()
        {
            templates = new List<TemplateMetadata>();
            count = 0;
        }
    }

    /// <summary>
    /// Template metadata (summary information)
    /// </summary>
    public class TemplateMetadata
    {
        public string template_id { get; set; }           // "TPL_001"
        public string template_name { get; set; }         // "Study Start-Up"
        public string template_type { get; set; }         // "study_startup", "implementation", "closeout", etc.
        public string version { get; set; }               // "1.0"
        public string description { get; set; }           // Human-readable description
        public int total_task_count { get; set; }         // Number of tasks in template
        public int estimated_duration_days { get; set; }  // Estimated total duration
        public bool is_system_template { get; set; }      // true = system template, false = org custom

        // Optional fields
        public List<string> applicable_phases { get; set; }       // Study phases this template applies to
        public List<string> applicable_authorities { get; set; }  // Regulatory authorities
    }

    /// <summary>
    /// Response from GET /api/v1/templates/library/{template_id}
    /// Complete template with all tasks and dependencies
    /// </summary>
    public class TemplateDetailResponse
    {
        public TemplateMetadata template { get; set; }
        public List<DatabaseTemplateTask> tasks { get; set; }
        public List<TemplateDependency> dependencies { get; set; }

        public TemplateDetailResponse()
        {
            tasks = new List<DatabaseTemplateTask>();
            dependencies = new List<TemplateDependency>();
        }
    }

    /// <summary>
    /// Task definition within a database template (from template library API)
    /// Renamed to DatabaseTemplateTask to avoid conflict with existing TemplateTask in CountrySpecificTemplate.cs
    /// </summary>
    public class DatabaseTemplateTask
    {
        public string task_id { get; set; }              // "SS_001", "CDB_001", etc.
        public string task_name { get; set; }            // "Clinical data entry completed"
        public string task_code { get; set; }            // Optional task code
        public string category { get; set; }             // "Data Management", "Regulatory", etc.

        // Duration with variance
        public int typical_duration_days { get; set; }   // Typical duration
        public int? min_duration_days { get; set; }      // Minimum duration
        public int? max_duration_days { get; set; }      // Maximum duration

        // Task properties
        public bool is_milestone { get; set; }           // true = milestone, false = task
        public bool is_critical_path { get; set; }       // true = on critical path
        public string description { get; set; }          // Detailed description
        public string responsible_role { get; set; }     // "Project Manager", "Data Manager", etc.

        // Hierarchy
        public string parent_task_id { get; set; }       // Parent task ID (for subtasks)
        public int sort_order { get; set; }              // Display order
        public int outline_level { get; set; }           // Outline level (1 = summary, 2+ = detail)

        // Recurring tasks
        public bool is_recurring { get; set; }           // true = recurring task
        public int? recurrence_interval_days { get; set; }  // Interval in days (e.g., 365 for annual)
    }

    /// <summary>
    /// Dependency between template tasks
    /// </summary>
    public class TemplateDependency
    {
        public string predecessor_task_id { get; set; }  // Predecessor task ID
        public string successor_task_id { get; set; }    // Successor task ID
        public string dependency_type { get; set; }      // "finish-to-start", "start-to-start", etc.
        public int lag_days { get; set; }                // Lag in days (can be negative for lead)
        public bool is_hard_dependency { get; set; }     // true = hard blocking dependency

        public TemplateDependency()
        {
            dependency_type = "finish-to-start";
            lag_days = 0;
            is_hard_dependency = true;
        }
    }
}
