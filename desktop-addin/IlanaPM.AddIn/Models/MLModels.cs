using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    public class DurationPrediction
    {
        public int predicted_duration_days { get; set; }
        public ConfidenceInterval confidence_interval { get; set; }
        public double confidence_score { get; set; }
        public string explanation { get; set; }
        public List<ComparableTask> comparable_tasks { get; set; }
        public string model_version { get; set; }
    }

    public class ConfidenceInterval
    {
        public int lower { get; set; }
        public int upper { get; set; }
    }

    public class ComparableTask
    {
        public string name { get; set; }
        public int typical_duration { get; set; }
        public string authority { get; set; }
    }

    public class RiskScore
    {
        public int risk_score { get; set; }
        public string risk_level { get; set; }
        public List<string> risk_factors { get; set; }
        public List<string> mitigation_suggestions { get; set; }
        public string model_version { get; set; }
    }

    public class TimelineAdvisory
    {
        public List<TaskDurationPrediction> duration_predictions { get; set; }
        public List<TaskRiskScore> risk_scores { get; set; }
        public List<HighRiskTask> high_risk_tasks { get; set; }
    }

    public class TaskDurationPrediction
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public DurationPrediction prediction { get; set; }
    }

    public class TaskRiskScore
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public RiskScore risk { get; set; }
    }

    public class HighRiskTask
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public int risk_score { get; set; }
        public List<string> risk_factors { get; set; }
    }
}