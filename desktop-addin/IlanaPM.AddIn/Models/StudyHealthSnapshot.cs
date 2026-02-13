using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Study health snapshot with signals, correlations, and escalations
    /// </summary>
    public class StudyHealthSnapshot
    {
        public string project_id { get; set; }
        public string project_name { get; set; }
        public double overall_health_score { get; set; }
        public string health_status { get; set; }  // "healthy", "warning", "critical"

        public double timeline_score { get; set; }
        public double risk_score { get; set; }
        public double tmf_score { get; set; }
        public double enrollment_score { get; set; }

        public List<Signal> active_signals { get; set; }
        public List<Correlation> correlations { get; set; }
        public List<Escalation> escalations { get; set; }
        public List<string> recommended_actions { get; set; }

        public string snapshot_date { get; set; }
    }

    /// <summary>
    /// Signal extracted from tracker data
    /// </summary>
    public class Signal
    {
        public string signal_id { get; set; }
        public string signal_type { get; set; }
        public string signal_category { get; set; }
        public string signal_description { get; set; }
        public int priority { get; set; }
        public string status { get; set; }
        public string signal_source { get; set; }
        public string date_identified { get; set; }
    }

    /// <summary>
    /// Correlation between signal and timeline milestone
    /// </summary>
    public class Correlation
    {
        public string correlation_id { get; set; }
        public string signal_id { get; set; }
        public string affected_milestone_name { get; set; }
        public string correlation_type { get; set; }  // "blocker", "risk", "informational"
        public double confidence_score { get; set; }
        public int estimated_delay_days { get; set; }
        public double estimated_cost_impact { get; set; }
        public string correlation_reasoning { get; set; }
    }

    /// <summary>
    /// Escalation requiring director or VP attention
    /// </summary>
    public class Escalation
    {
        public string escalation_id { get; set; }
        public string escalation_level { get; set; }  // "director", "vp"
        public string escalation_reason { get; set; }
        public string status { get; set; }  // "open", "acknowledged", "resolved"
        public int priority { get; set; }
        public string intervention_recommended { get; set; }
        public string created_at { get; set; }
    }
}
