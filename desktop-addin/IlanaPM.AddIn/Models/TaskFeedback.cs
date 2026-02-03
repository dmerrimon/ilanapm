using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Task completion feedback for ML learning
    /// Tracks predicted vs actual durations to improve future predictions
    /// </summary>
    public class TaskFeedback
    {
        // Task identification
        public string task_id { get; set; }
        public string task_name { get; set; }
        public string category { get; set; }

        // Prediction data (what ML predicted)
        public int? predicted_duration_days { get; set; }
        public double? predicted_confidence { get; set; }
        public string model_version { get; set; }

        // Actual outcome (what really happened)
        public int actual_duration_days { get; set; }
        public string actual_start_date { get; set; }  // YYYY-MM-DD format
        public string actual_end_date { get; set; }    // YYYY-MM-DD format

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
    /// Response from feedback submission
    /// </summary>
    public class TaskFeedbackResponse
    {
        public bool success { get; set; }
        public string message { get; set; }
        public int recorded_count { get; set; }
        public AccuracySummary accuracy_summary { get; set; }
    }

    /// <summary>
    /// ML prediction accuracy summary
    /// </summary>
    public class AccuracySummary
    {
        public int total_tasks_with_predictions { get; set; }
        public int accurate_predictions { get; set; }
        public double accuracy_percentage { get; set; }
        public double avg_prediction_error_days { get; set; }
    }
}
