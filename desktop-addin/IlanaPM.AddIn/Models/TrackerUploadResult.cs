using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Result from tracker upload operation
    /// Contains upload status, signal extraction summary, and study health score
    /// </summary>
    public class TrackerUploadResult
    {
        public bool success { get; set; }
        public string upload_id { get; set; }
        public int rows_processed { get; set; }
        public int signals_extracted { get; set; }
        public int escalations_detected { get; set; }
        public double health_score { get; set; }
        public string health_status { get; set; }  // "healthy", "warning", "critical"
        public string error_type { get; set; }
        public string error_message { get; set; }
        public List<ValidationError> validation_errors { get; set; }
    }

    /// <summary>
    /// Validation error in tracker upload
    /// </summary>
    public class ValidationError
    {
        public int row_number { get; set; }
        public string field { get; set; }
        public string error_message { get; set; }
    }
}
