namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Request model for POST /api/v1/templates/generate
    /// </summary>
    public class TemplateRequest
    {
        public string country_code { get; set; }
        public string study_phase { get; set; }
        public string therapeutic_area { get; set; }
        public bool include_optional { get; set; }
        public bool include_emmes_timelines { get; set; }

        public TemplateRequest()
        {
            include_optional = true;
            include_emmes_timelines = true;
        }
    }
}
