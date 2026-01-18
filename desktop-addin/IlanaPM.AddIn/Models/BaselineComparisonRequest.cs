using System;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Request model for baseline comparison
    /// </summary>
    public class BaselineComparisonRequest
    {
        public Timeline current { get; set; }
        public Timeline baseline { get; set; }
    }
}
