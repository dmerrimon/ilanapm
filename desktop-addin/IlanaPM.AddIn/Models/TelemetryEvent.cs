using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Telemetry event types for ML learning and usage analytics
    /// </summary>
    public enum TelemetryEventType
    {
        // Feature Usage
        FeatureOpened,              // User opened a feature
        FeatureClosed,              // User closed a feature
        ButtonClicked,              // Specific button clicked

        // Template Loading
        TemplateLoaded,             // Template loaded (type, country, source)
        TemplateFiltered,           // User applied filters
        TasksGenerated,             // Tasks created in MS Project

        // Validation
        ValidationStarted,          // Timeline validation initiated
        ValidationCompleted,        // Validation finished
        ValidationIssueAccepted,    // User accepted a suggestion
        ValidationIssueIgnored,     // User ignored a warning

        // Analysis
        CriticalPathAnalyzed,       // Critical path analysis run
        RiskAnalysisViewed,         // Risk dashboard viewed

        // Clinical Management
        SiteAdded,                  // Site added to metadata
        AmendmentCreated,           // Amendment created
        DocumentCollected,          // Essential document collected

        // User Workflow
        SessionStarted,             // Add-in session started
        SessionEnded,               // Add-in session ended
        FeatureSequence,            // Track feature usage order

        // ML Learning Events
        TaskCompleted,              // Task marked complete (for ML learning)
        ProjectOpened,              // Project opened (for ML context)

        // Phase 5: Intelligence Layer Events
        TrackerUploaded,            // Tracker file uploaded (Risk Log, TMF, etc.)
        LeadershipDashboardOpened,  // Leadership Dashboard viewed
        DashboardExported,          // Dashboard data exported
        StudyHealthViewed           // Study health snapshot viewed
    }

    /// <summary>
    /// Telemetry event for ML learning
    /// Privacy-focused: User IDs are hashed, no PII collected
    /// </summary>
    public class TelemetryEvent
    {
        /// <summary>
        /// Unique event identifier
        /// </summary>
        public string event_id { get; set; }

        /// <summary>
        /// Session identifier (tracks feature sequences within a session)
        /// </summary>
        public string session_id { get; set; }

        /// <summary>
        /// Hashed user identifier (SHA-256 of email - irreversible)
        /// </summary>
        public string user_id { get; set; }

        /// <summary>
        /// Optional tenant/organization identifier
        /// </summary>
        public string tenant_id { get; set; }

        /// <summary>
        /// Type of telemetry event
        /// </summary>
        public string event_type { get; set; }

        /// <summary>
        /// UTC timestamp when event occurred
        /// </summary>
        public DateTime timestamp { get; set; }

        /// <summary>
        /// Event-specific properties (JSON serializable)
        /// Examples:
        /// - TemplateLoaded: { "template_type": "SiteStartup", "country_code": "USA", "task_count": 45 }
        /// - ValidationCompleted: { "total_tasks": 120, "issues_found": 7, "errors": 2 }
        /// </summary>
        public Dictionary<string, object> properties { get; set; }

        /// <summary>
        /// Whether this event contains personally identifiable information
        /// Should always be false - we don't collect PII
        /// </summary>
        public bool contains_pii { get; set; }

        /// <summary>
        /// Whether user has consented to telemetry tracking
        /// </summary>
        public bool user_consented { get; set; }

        /// <summary>
        /// Constructor initializes event with defaults
        /// </summary>
        public TelemetryEvent()
        {
            event_id = Guid.NewGuid().ToString();
            timestamp = DateTime.UtcNow;
            properties = new Dictionary<string, object>();
            contains_pii = false;
            user_consented = false;
        }

        /// <summary>
        /// Constructor with event type
        /// </summary>
        public TelemetryEvent(TelemetryEventType eventType) : this()
        {
            event_type = eventType.ToString();
        }

        /// <summary>
        /// Add property to event
        /// </summary>
        public void AddProperty(string key, object value)
        {
            if (properties == null)
            {
                properties = new Dictionary<string, object>();
            }
            properties[key] = value;
        }

        /// <summary>
        /// Get property from event
        /// </summary>
        public object GetProperty(string key)
        {
            if (properties == null || !properties.ContainsKey(key))
            {
                return null;
            }
            return properties[key];
        }
    }

    /// <summary>
    /// Batch of telemetry events for efficient API transmission
    /// </summary>
    public class TelemetryBatch
    {
        /// <summary>
        /// Batch identifier
        /// </summary>
        public string batch_id { get; set; }

        /// <summary>
        /// Events in this batch
        /// </summary>
        public List<TelemetryEvent> events { get; set; }

        /// <summary>
        /// When batch was created
        /// </summary>
        public DateTime created_at { get; set; }

        public TelemetryBatch()
        {
            batch_id = Guid.NewGuid().ToString();
            events = new List<TelemetryEvent>();
            created_at = DateTime.UtcNow;
        }
    }
}
