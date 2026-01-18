using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Critical path analysis result
    /// </summary>
    public class CriticalPathResult
    {
        public List<string> path { get; set; }
        public int total_duration { get; set; }
        public int task_count { get; set; }
        public List<CriticalPathTask> tasks { get; set; }
    }

    /// <summary>
    /// Critical path task details
    /// </summary>
    public class CriticalPathTask
    {
        public string id { get; set; }
        public string name { get; set; }
        public int duration_days { get; set; }
        public string category { get; set; }
        public bool is_mandatory { get; set; }
        public int earliest_start { get; set; }
        public int earliest_finish { get; set; }
    }
}
