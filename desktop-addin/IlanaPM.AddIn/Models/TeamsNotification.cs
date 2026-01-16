using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    public class TeamsNotificationRequest
    {
        public string webhook_url { get; set; }
        public string study_name { get; set; }
        public ValidationSummary validation_summary { get; set; }
        public List<HighRiskTaskSummary> high_risk_tasks { get; set; }
    }

    public class ValidationSummary
    {
        public string status { get; set; }
        public int error_count { get; set; }
        public int warning_count { get; set; }
        public int total_tasks { get; set; }
    }

    public class HighRiskTaskSummary
    {
        public string name { get; set; }
        public int risk_score { get; set; }
    }
}