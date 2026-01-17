using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    // Duration prediction for a single task
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

    // Risk score for a single task
    public class RiskScore
    {
        public int risk_score { get; set; }
        public string risk_level { get; set; }
        public List<string> risk_factors { get; set; }
        public List<string> mitigation_suggestions { get; set; }
        public string model_version { get; set; }
    }

    // Duration predictions wrapper (matches backend "duration_predictions" structure)
    public class DurationPredictionsWrapper
    {
        public List<TaskDurationPrediction> predictions { get; set; }
        public double average_confidence { get; set; }
        public int total_tasks { get; set; }
        public string model_version { get; set; }
    }

    // Risk analysis wrapper (matches backend "risk_analysis" structure)
    public class RiskAnalysisWrapper
    {
        public List<TaskRiskScore> risk_scores { get; set; }
        public List<HighRiskTask> high_risk_tasks { get; set; }
        public double average_risk { get; set; }
        public int high_risk_count { get; set; }
    }

    // Task with duration prediction
    public class TaskDurationPrediction
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public int current_duration { get; set; }
        public DurationPrediction prediction { get; set; }
    }

    // Task with risk score
    public class TaskRiskScore
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public RiskScore risk { get; set; }
    }

    // High risk task summary
    public class HighRiskTask
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public int risk_score { get; set; }
        public List<string> risk_factors { get; set; }
    }

    // Summary statistics
    public class SummaryStatistics
    {
        public int total_tasks { get; set; }
        public double avg_predicted_duration { get; set; }
        public double avg_risk_score { get; set; }
        public int critical_risk_count { get; set; }
        public int high_risk_count { get; set; }
        public int medium_risk_count { get; set; }
        public int aggressive_duration_count { get; set; }
        public double avg_prediction_confidence { get; set; }
    }

    // COMPLETE timeline advisory response (matches backend exactly)
    public class TimelineAdvisory
    {
        public string study_name { get; set; }
        public string phase { get; set; }
        public string authority { get; set; }
        public DurationPredictionsWrapper duration_predictions { get; set; }
        public RiskAnalysisWrapper risk_analysis { get; set; }
        public SummaryStatistics summary_statistics { get; set; }
        public List<string> recommendations { get; set; }
        public string model_version { get; set; }
    }
}