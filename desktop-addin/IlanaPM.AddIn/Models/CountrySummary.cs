using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Country metadata returned from /api/v1/templates/countries endpoint
    /// </summary>
    public class CountrySummary
    {
        public string code { get; set; }
        public string name { get; set; }
        public string workflow_type { get; set; }
        public double complexity_level { get; set; }
        public int? total_timeline_days { get; set; }
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
