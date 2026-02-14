using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    public class Timeline
    {
        public string study_name { get; set; }
        public string phase { get; set; }
        public string authority { get; set; }
        public string therapeutic_area { get; set; }
        public List<Task> tasks { get; set; }
        public List<Dependency> dependencies { get; set; }

        public Timeline()
        {
            tasks = new List<Task>();
            dependencies = new List<Dependency>();
        }
    }

    public class Task
    {
        public string id { get; set; }
        public string name { get; set; }
        public int duration_days { get; set; }
        public string start_date { get; set; }
        public string end_date { get; set; }
        public string category { get; set; }
        public string phase { get; set; }
        public string authority { get; set; }
        public bool is_mandatory { get; set; }
        public int checklist_completion_pct { get; set; }

        // Summary task fields (for category dividers)
        public bool is_summary { get; set; }
        public int outline_level { get; set; } = 2; // Default to level 2 (normal task)

        // NEW: Authority-specific fields for rich ontology
        public string authority_full_name { get; set; }    // "National Drug Authority"
        public string authority_type { get; set; }         // "regulatory", "ethics", "permits"
        public string submission_form { get; set; }        // "IRAS", "IND", "CTA"
        public List<string> required_documents { get; set; }  // Authority-specific docs
    }

    public class Dependency
    {
        public string predecessor_id { get; set; }
        public string successor_id { get; set; }
        public string type { get; set; }
        public int lag_days { get; set; }

        public Dependency()
        {
            type = "finish-to-start";
            lag_days = 0;
        }
    }

    public class ValidationResult
    {
        public string status { get; set; }
        public List<ValidationIssue> issues { get; set; }
        public int error_count { get; set; }
        public int warning_count { get; set; }
        public int info_count { get; set; }
        public int total_tasks_analyzed { get; set; }

        public ValidationResult()
        {
            // Initialize all properties to prevent null reference exceptions
            status = "unknown";
            issues = new List<ValidationIssue>();
            error_count = 0;
            warning_count = 0;
            info_count = 0;
            total_tasks_analyzed = 0;
        }
    }

    public class ValidationIssue
    {
        public string rule_id { get; set; }
        public string severity { get; set; }
        public string category { get; set; }
        public string task_id { get; set; }
        public string message { get; set; }
        public string detail { get; set; }
        public string suggested_fix { get; set; }
        public double confidence { get; set; }
    }

    /// <summary>
    /// Regulatory workflow metadata for multi-authority systems
    /// </summary>
    public class RegulatoryWorkflow
    {
        public string workflow_type { get; set; }  // "parallel", "sequential", "multi_layer_sequential"
        public List<Authority> authorities { get; set; }

        public RegulatoryWorkflow()
        {
            authorities = new List<Authority>();
        }
    }

    /// <summary>
    /// Regulatory authority metadata
    /// </summary>
    public class Authority
    {
        public string code { get; set; }           // "NDA", "MHRA", "FDA"
        public string name { get; set; }           // "National Drug Authority"
        public string type { get; set; }           // "regulatory", "ethics", "permits"
        public int review_duration_days { get; set; }
    }
}
