using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Task completion feedback data sent to backend for ML learning
    /// </summary>
    public class TaskCompletionFeedback
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public string category { get; set; }

        // Predicted values (what the model estimated)
        public int predicted_duration_days { get; set; }
        public double predicted_confidence { get; set; }
        public string model_version { get; set; }

        // Actual values (what really happened)
        public int actual_duration_days { get; set; }
        public string actual_start_date { get; set; }  // YYYY-MM-DD format (ISO 8601)
        public string actual_end_date { get; set; }    // YYYY-MM-DD format (ISO 8601)

        // Context for learning
        public string country_code { get; set; }
        public string authority { get; set; }
        public string study_phase { get; set; }
        public string therapeutic_area { get; set; }

        // Metadata
        public string project_id { get; set; }
        public string recorded_by { get; set; }
    }

    /// <summary>
    /// Batch request for submitting multiple task completions
    /// </summary>
    public class TaskCompletionBatchRequest
    {
        public List<TaskCompletionFeedback> task_completions { get; set; }

        public TaskCompletionBatchRequest()
        {
            task_completions = new List<TaskCompletionFeedback>();
        }
    }

    /// <summary>
    /// Response from feedback submission
    /// </summary>
    public class TaskCompletionResponse
    {
        public bool success { get; set; }
        public int recorded_count { get; set; }
        public string message { get; set; }
    }
}
