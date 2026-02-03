using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Country-aware study template with site-level task sets per country
    /// </summary>
    public class StudyTemplate
    {
        public string template_id { get; set; }
        public string name { get; set; }
        public string description { get; set; }
        public List<string> supported_countries { get; set; }
        public string primary_regulatory_authority { get; set; }  // FDA, EMA, PMDA
        public string study_phase { get; set; }  // Phase I, Phase II, Phase III
        public string therapeutic_area { get; set; }
        public string template_type { get; set; }  // Global, Custom
        public string tenant_id { get; set; }  // null for global templates
        public DateTime created_date { get; set; }
        public string created_by { get; set; }

        // Study-level task sets (one-time, country-agnostic)
        public StudyPhaseTaskSet study_startup { get; set; }
        public StudyPhaseTaskSet study_active { get; set; }
        public StudyPhaseTaskSet study_closeout { get; set; }

        // Site-level task sets by country
        public Dictionary<string, SitePhaseTaskSet> site_startup_by_country { get; set; }
        public Dictionary<string, SitePhaseTaskSet> site_active_by_country { get; set; }
        public Dictionary<string, SitePhaseTaskSet> site_closeout_by_country { get; set; }

        public StudyTemplate()
        {
            supported_countries = new List<string>();
            site_startup_by_country = new Dictionary<string, SitePhaseTaskSet>();
            site_active_by_country = new Dictionary<string, SitePhaseTaskSet>();
            site_closeout_by_country = new Dictionary<string, SitePhaseTaskSet>();
            created_date = DateTime.Now;
        }

        /// <summary>
        /// Get site startup tasks for specific country
        /// </summary>
        public SitePhaseTaskSet GetSiteStartupTasks(string countryCode)
        {
            if (site_startup_by_country.ContainsKey(countryCode))
                return site_startup_by_country[countryCode];

            // Fallback to generic if country not found
            if (site_startup_by_country.ContainsKey("GENERIC"))
                return site_startup_by_country["GENERIC"];

            return null;
        }
    }

    /// <summary>
    /// Study-level phase task set (startup, active, closeout)
    /// </summary>
    public class StudyPhaseTaskSet
    {
        public string phase_name { get; set; }
        public string phase_type { get; set; }  // Startup, Active, Closeout
        public List<TemplateTask> tasks { get; set; }
        public List<Milestone> milestones { get; set; }

        public StudyPhaseTaskSet()
        {
            tasks = new List<TemplateTask>();
            milestones = new List<Milestone>();
        }
    }

    /// <summary>
    /// Site-level phase task set with country-specific requirements
    /// </summary>
    public class SitePhaseTaskSet
    {
        public string phase_name { get; set; }
        public string phase_type { get; set; }  // Startup, Active, Closeout
        public string country_code { get; set; }  // USA, DEU, GBR, CAN, JPN
        public string country_name { get; set; }
        public string regulatory_authority { get; set; }  // FDA, BfArM, MHRA, Health Canada, PMDA
        public List<TemplateTask> tasks { get; set; }
        public List<EssentialDocument> essential_documents { get; set; }
        public List<Milestone> milestones { get; set; }

        public SitePhaseTaskSet()
        {
            tasks = new List<TemplateTask>();
            essential_documents = new List<EssentialDocument>();
            milestones = new List<Milestone>();
        }
    }

    /// <summary>
    /// Template task with dependency tracking and parallel execution support
    /// </summary>
    public class TemplateTask
    {
        public string task_id { get; set; }
        public string name { get; set; }
        public string description { get; set; }
        public int duration_days { get; set; }
        public string duration_formula { get; set; }  // "4 weeks after protocol submission"
        public string category { get; set; }  // Regulatory, Clinical, Admin, Lab, Data
        public bool is_mandatory { get; set; }

        // Phase filtering (Phase 1)
        public string phase_type { get; set; }  // Startup, Active, Closeout, Study Closeout, Amendment
        public string subphase { get; set; }  // Essential Documents, IRB Submission, Training, etc.

        // Dependency management
        public List<string> predecessors { get; set; }  // Task IDs that must complete first
        public string dependency_type { get; set; }  // FS (Finish-to-Start), SS (Start-to-Start), FF, SF
        public bool is_blocking { get; set; }  // If true, blocks downstream tasks (critical path)
        public int lag_days { get; set; }  // Days to wait after predecessor completes

        // Parallel execution support
        public string execution_group { get; set; }  // "Parallel-Essential-Docs", "Sequential-IRB"
        public bool can_run_parallel { get; set; }  // True if can overlap with other tasks
        public int parallel_group_id { get; set; }  // Tasks with same ID can run simultaneously

        // Milestone anchoring
        public string anchor_milestone { get; set; }  // "Protocol v1.0", "FPFV", "LSLV"
        public int offset_days_from_anchor { get; set; }  // +14 days after anchor

        // Site-specific flags
        public bool is_site_specific { get; set; }
        public bool requires_irb_approval { get; set; }
        public bool is_amendment_generated { get; set; }

        // Essential document tracking
        public List<string> required_documents { get; set; }  // Document IDs needed for this task

        public TemplateTask()
        {
            predecessors = new List<string>();
            required_documents = new List<string>();
            dependency_type = "FS";  // Default to Finish-to-Start
            is_mandatory = true;
            can_run_parallel = false;
        }

        /// <summary>
        /// Display name for execution group
        /// </summary>
        public string ExecutionGroupDisplay
        {
            get
            {
                if (can_run_parallel)
                    return $"Parallel: {execution_group}";
                else
                    return $"Sequential: {execution_group}";
            }
        }
    }

    /// <summary>
    /// Milestone for phase transitions and critical dates
    /// </summary>
    public class Milestone
    {
        public string milestone_id { get; set; }
        public string name { get; set; }  // "Protocol v1.0", "FPFV", "Database Lock"
        public string description { get; set; }
        public string phase { get; set; }  // Study Startup, Site Active, etc.
        public bool is_study_level { get; set; }  // true for study, false for site
        public DateTime? target_date { get; set; }
        public DateTime? actual_date { get; set; }
        public string status { get; set; }  // Not Started, In Progress, Complete

        public Milestone()
        {
            status = "Not Started";
        }

        /// <summary>
        /// Variance in days (negative = ahead, positive = behind)
        /// </summary>
        public int? VarianceDays
        {
            get
            {
                if (target_date.HasValue && actual_date.HasValue)
                    return (actual_date.Value - target_date.Value).Days;
                return null;
            }
        }
    }

    /// <summary>
    /// Essential regulatory document required for clinical trials
    /// </summary>
    public class EssentialDocument
    {
        public string document_id { get; set; }
        public string document_name { get; set; }
        public string description { get; set; }
        public string country_code { get; set; }  // USA, DEU, GBR, etc.
        public string regulatory_authority { get; set; }  // FDA, BfArM, MHRA
        public bool is_mandatory { get; set; }
        public string regulatory_reference { get; set; }  // "21 CFR 312.53", "ICH-GCP 8.2.2"
        public string collection_task_id { get; set; }  // Links to TemplateTask
        public string document_category { get; set; }  // IRB, Investigator, Lab, Protocol, Other
        public bool is_ind_specific { get; set; }  // Only required for IND studies
        public bool is_ibc_specific { get; set; }  // Only if IBC required

        // Tracking fields (populated during study execution)
        public DateTime? date_collected { get; set; }
        public string collected_by { get; set; }
        public string storage_location { get; set; }
        public string version { get; set; }
        public string status { get; set; }  // Not Collected, Collected, Verified, Filed

        public EssentialDocument()
        {
            is_mandatory = true;
            status = "Not Collected";
        }

        /// <summary>
        /// Display name with country designation
        /// </summary>
        public string DisplayName
        {
            get { return $"[{country_code}] {document_name}"; }
        }
    }

    /// <summary>
    /// Regulatory authority information by country
    /// </summary>
    public class RegulatoryAuthority
    {
        public string country_code { get; set; }
        public string country_name { get; set; }
        public string authority_name { get; set; }
        public string authority_acronym { get; set; }
        public string website { get; set; }
        public string gcp_standard { get; set; }  // "FDA GCP", "EU GCP", "ICH-GCP"
        public bool requires_import_license { get; set; }
        public bool requires_financial_disclosure { get; set; }
        public string ethics_committee_name { get; set; }

        public static List<RegulatoryAuthority> GetAllAuthorities()
        {
            return new List<RegulatoryAuthority>
            {
                new RegulatoryAuthority
                {
                    country_code = "USA",
                    country_name = "United States",
                    authority_name = "Food and Drug Administration",
                    authority_acronym = "FDA",
                    website = "https://www.fda.gov",
                    gcp_standard = "FDA 21 CFR 312",
                    requires_import_license = false,
                    requires_financial_disclosure = true,
                    ethics_committee_name = "Institutional Review Board (IRB)"
                },
                new RegulatoryAuthority
                {
                    country_code = "DEU",
                    country_name = "Germany",
                    authority_name = "Bundesinstitut für Arzneimittel und Medizinprodukte",
                    authority_acronym = "BfArM",
                    website = "https://www.bfarm.de",
                    gcp_standard = "EU GCP Directive 2001/20/EC",
                    requires_import_license = true,
                    requires_financial_disclosure = false,
                    ethics_committee_name = "Ethikkommission"
                },
                new RegulatoryAuthority
                {
                    country_code = "GBR",
                    country_name = "United Kingdom",
                    authority_name = "Medicines and Healthcare products Regulatory Agency",
                    authority_acronym = "MHRA",
                    website = "https://www.gov.uk/mhra",
                    gcp_standard = "UK GCP (post-Brexit)",
                    requires_import_license = true,
                    requires_financial_disclosure = false,
                    ethics_committee_name = "NHS Research Ethics Committee (REC)"
                },
                new RegulatoryAuthority
                {
                    country_code = "CAN",
                    country_name = "Canada",
                    authority_name = "Health Canada",
                    authority_acronym = "HC",
                    website = "https://www.canada.ca/en/health-canada.html",
                    gcp_standard = "ICH-GCP",
                    requires_import_license = true,
                    requires_financial_disclosure = false,
                    ethics_committee_name = "Research Ethics Board (REB)"
                },
                new RegulatoryAuthority
                {
                    country_code = "JPN",
                    country_name = "Japan",
                    authority_name = "Pharmaceuticals and Medical Devices Agency",
                    authority_acronym = "PMDA",
                    website = "https://www.pmda.go.jp/english/",
                    gcp_standard = "J-GCP",
                    requires_import_license = true,
                    requires_financial_disclosure = false,
                    ethics_committee_name = "Institutional Review Board (IRB)"
                }
            };
        }

        public static RegulatoryAuthority GetByCountryCode(string countryCode)
        {
            var authorities = GetAllAuthorities();
            return authorities.Find(a => a.country_code == countryCode);
        }
    }
}
