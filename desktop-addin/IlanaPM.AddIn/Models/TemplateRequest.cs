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

    /// <summary>
    /// Request model for site-specific template generation
    /// Used for: POST /api/v1/templates/generate-site-startup
    ///          POST /api/v1/templates/generate-site-closeout
    ///          POST /api/v1/templates/generate-study-closeout
    /// </summary>
    public class SiteTemplateRequest
    {
        public string country_code { get; set; }
        public string template_type { get; set; }  // "site_startup", "site_closeout", "study_closeout"
        public string site_id { get; set; }
        public string study_phase { get; set; }
        public string therapeutic_area { get; set; }
        public bool include_optional { get; set; }

        public SiteTemplateRequest()
        {
            include_optional = true;
        }
    }
}
