namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Request model for POST /api/v1/templates/generate
    /// Updated: Removed include_emmes_timelines - all 92 tasks now come from task_ontology.yaml
    /// </summary>
    public class TemplateRequest
    {
        public string country_code { get; set; }
        public string study_phase { get; set; }
        public string therapeutic_area { get; set; }
        public bool include_optional { get; set; }

        public TemplateRequest()
        {
            include_optional = true;
        }
    }
}
