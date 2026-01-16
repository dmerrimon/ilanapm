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
}