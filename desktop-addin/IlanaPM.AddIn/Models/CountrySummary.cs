using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Country metadata returned from /api/v1/config/countries endpoint
    /// Used by Multi-Country Calculator for comparing regulatory workflows
    /// </summary>
    public class CountrySummary
    {
        public string code { get; set; }
        public string name { get; set; }
        public string workflow_type { get; set; }
        public double complexity_level { get; set; }
        public int? total_timeline_days { get; set; }

        // Regulatory Authority
        public string regulatory_authority_code { get; set; }
        public string regulatory_authority_name { get; set; }

        // Ethics Authority
        public string ethics_authority_code { get; set; }
        public string ethics_authority_name { get; set; }

        // Additional authorities (for multi-body systems)
        public List<Dictionary<string, string>> additional_authorities { get; set; }

        // Expedited pathways
        public bool has_emergency_pathway { get; set; }
        public bool has_fast_track { get; set; }

        // Workflow description
        public string workflow_description { get; set; }

        // Legacy fields for backward compatibility
        public string regulatory_authority { get; set; }
        public string ethics_authority { get; set; }
    }

    /// <summary>
    /// Response from GET /api/v1/templates/countries
    /// </summary>
    public class CountriesResponse
    {
        public List<CountrySummary> countries { get; set; }
        public int count { get; set; }

        public CountriesResponse()
        {
            countries = new List<CountrySummary>();
        }
    }
}
