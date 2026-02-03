using System;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Represents a clinical validation warning
    /// Generated when clinical entity rules are violated
    /// (e.g., Site has enrollment tasks but no IRB approval)
    /// </summary>
    public class ClinicalWarning
    {
        public string warning_id { get; set; }
        public string severity { get; set; }  // Error, Warning, Info
        public string entity_type { get; set; }  // Site, Amendment, Cohort
        public string entity_id { get; set; }  // ID of the entity with the issue
        public string message { get; set; }  // Human-readable warning message
        public string suggested_fix { get; set; }  // Actionable fix suggestion

        public ClinicalWarning()
        {
            warning_id = Guid.NewGuid().ToString().Substring(0, 8);
            severity = "Warning";
        }

        public ClinicalWarning(string entityType, string entityId, string message, string suggestedFix, string severity = "Warning")
        {
            this.warning_id = Guid.NewGuid().ToString().Substring(0, 8);
            this.entity_type = entityType;
            this.entity_id = entityId;
            this.message = message;
            this.suggested_fix = suggestedFix;
            this.severity = severity;
        }

        /// <summary>
        /// Formatted warning text for display
        /// </summary>
        public string DisplayText
        {
            get
            {
                return $"[{severity.ToUpper()}] {entity_type} {entity_id}: {message}";
            }
        }
    }
}
