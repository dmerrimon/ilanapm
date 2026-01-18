using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Result from baseline comparison analysis
    /// </summary>
    public class BaselineComparisonResult
    {
        public int total_tasks { get; set; }
        public int on_track { get; set; }
        public int ahead { get; set; }
        public int delayed { get; set; }
        public double avg_duration_variance { get; set; }
        public double avg_schedule_variance_days { get; set; }
        public List<BaselineComparison> tasks { get; set; }
    }

    /// <summary>
    /// Individual task comparison between baseline and current
    /// </summary>
    public class BaselineComparison
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public int baseline_duration { get; set; }
        public int current_duration { get; set; }
        public int duration_variance { get; set; }
        public string baseline_start { get; set; }
        public string current_start { get; set; }
        public int? start_variance_days { get; set; }
        public string baseline_finish { get; set; }
        public string current_finish { get; set; }
        public int? finish_variance_days { get; set; }
        public string status { get; set; }  // "on_track", "ahead", "delayed"
    }
}
