using System;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Site configuration for unified Clinical Project Manager
    /// Extends basic site info with template generation preferences
    /// </summary>
    public class SiteConfiguration
    {
        /// <summary>
        /// Unique site identifier (e.g., "SITE-001")
        /// </summary>
        public string SiteId { get; set; }

        /// <summary>
        /// Site name (e.g., "Memorial Hospital Boston")
        /// </summary>
        public string SiteName { get; set; }

        /// <summary>
        /// ISO 3166-1 alpha-3 country code (e.g., "USA", "GBR", "DEU")
        /// </summary>
        public string CountryCode { get; set; }

        /// <summary>
        /// Full country name (e.g., "United States")
        /// </summary>
        public string CountryName { get; set; }

        /// <summary>
        /// Principal Investigator name
        /// </summary>
        public string PrincipalInvestigator { get; set; }

        /// <summary>
        /// Institution/Hospital name
        /// </summary>
        public string Institution { get; set; }

        /// <summary>
        /// IRB/Ethics Committee name
        /// </summary>
        public string IrbName { get; set; }

        /// <summary>
        /// Site status (Active, Pending, Closed)
        /// </summary>
        public string Status { get; set; }

        /// <summary>
        /// IRB approval date (if applicable)
        /// </summary>
        public DateTime? IrbApprovalDate { get; set; }

        // Template generation flags (used in Step 3/4 of wizard)

        /// <summary>
        /// Generate Site Startup template for this site
        /// </summary>
        public bool IncludeInStartup { get; set; }

        /// <summary>
        /// Generate Site Implementation template for this site
        /// </summary>
        public bool IncludeInImplementation { get; set; }

        /// <summary>
        /// Generate Site Closeout template for this site
        /// </summary>
        public bool IncludeInCloseout { get; set; }

        public SiteConfiguration()
        {
            Status = "Pending";
            IncludeInStartup = false;
            IncludeInImplementation = false;
            IncludeInCloseout = false;
        }

        /// <summary>
        /// Display format for ComboBox/ListBox: "SITE-001 (USA, Dr. Smith)"
        /// </summary>
        public string DisplayText
        {
            get
            {
                if (!string.IsNullOrEmpty(SiteId) && !string.IsNullOrEmpty(CountryCode))
                {
                    string pi = !string.IsNullOrEmpty(PrincipalInvestigator)
                        ? $", {PrincipalInvestigator}"
                        : "";
                    return $"{SiteId} ({CountryCode}{pi})";
                }
                return SiteId ?? "Unknown Site";
            }
        }

        /// <summary>
        /// Convert from existing Site model to SiteConfiguration
        /// </summary>
        public static SiteConfiguration FromSite(Site site)
        {
            if (site == null) return null;

            return new SiteConfiguration
            {
                SiteId = site.id,
                SiteName = site.name,
                CountryCode = site.country,
                CountryName = site.country, // Will be enriched from CountryRegulatoryInfo
                PrincipalInvestigator = site.principal_investigator,
                Status = site.status,
                IrbApprovalDate = site.irb_approval_date,
                Institution = site.name // Use site name as institution fallback
            };
        }

        /// <summary>
        /// Convert to existing Site model for backward compatibility
        /// </summary>
        public Site ToSite()
        {
            return new Site
            {
                id = this.SiteId,
                name = this.SiteName ?? this.Institution,
                country = this.CountryCode,
                status = this.Status,
                irb_approval_date = this.IrbApprovalDate,
                principal_investigator = this.PrincipalInvestigator
            };
        }
    }
}
