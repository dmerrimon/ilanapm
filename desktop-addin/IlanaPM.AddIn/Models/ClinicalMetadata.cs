using System;
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Container for all clinical entity definitions (sites, amendments, cohorts)
    /// Stored as JSON in MS Project ProjectSummaryTask.Notes field
    /// </summary>
    public class ClinicalMetadata
    {
        public string clinical_metadata_version { get; set; }
        public List<Site> sites { get; set; }
        public List<Amendment> amendments { get; set; }
        public List<Cohort> cohorts { get; set; }

        public ClinicalMetadata()
        {
            clinical_metadata_version = "1.0";
            sites = new List<Site>();
            amendments = new List<Amendment>();
            cohorts = new List<Cohort>();
        }
    }

    /// <summary>
    /// Clinical trial site entity
    /// Represents physical locations where trials are conducted
    /// </summary>
    public class Site
    {
        public string id { get; set; }  // e.g., "SITE-001"
        public string name { get; set; }  // e.g., "Memorial Hospital Boston"
        public string country { get; set; }  // e.g., "USA"
        public string status { get; set; }  // Active, Pending, Closed
        public DateTime? irb_approval_date { get; set; }
        public string principal_investigator { get; set; }  // PI name

        public Site()
        {
            status = "Pending";
        }

        /// <summary>
        /// Display name for UI (ID + Name)
        /// </summary>
        public string DisplayName
        {
            get { return $"{id} - {name}"; }
        }
    }

    /// <summary>
    /// Protocol amendment entity
    /// Represents changes to study protocol requiring regulatory approval
    /// </summary>
    public class Amendment
    {
        public string id { get; set; }  // e.g., "AMD-001"
        public string number { get; set; }  // e.g., "Amendment 3"
        public DateTime date { get; set; }
        public string description { get; set; }
        public List<string> affected_sites { get; set; }  // Site IDs affected by this amendment
        public string amendment_type { get; set; }  // substantial, administrative

        public Amendment()
        {
            affected_sites = new List<string>();
            amendment_type = "substantial";
            date = DateTime.Now;
        }

        /// <summary>
        /// Display name for UI (Number + Description)
        /// </summary>
        public string DisplayName
        {
            get { return $"{number} - {description}"; }
        }
    }

    /// <summary>
    /// Patient cohort entity
    /// Represents groups of patients enrolled in specific study phases/doses
    /// </summary>
    public class Cohort
    {
        public string id { get; set; }  // e.g., "COH-001"
        public string name { get; set; }  // e.g., "Cohort 1 - Low Dose"
        public int enrollment_target { get; set; }  // Target number of patients
        public List<string> prerequisites { get; set; }  // What must complete before this cohort starts
        public List<string> participating_sites { get; set; }  // Site IDs participating in this cohort

        public Cohort()
        {
            prerequisites = new List<string>();
            participating_sites = new List<string>();
            enrollment_target = 0;
        }

        /// <summary>
        /// Display name for UI (ID + Name)
        /// </summary>
        public string DisplayName
        {
            get { return $"{id} - {name}"; }
        }
    }
}
