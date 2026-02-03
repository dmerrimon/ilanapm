using Microsoft.Office.Interop.MSProject;
using System;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Manages custom field assignments for filtering and categorization
    /// Handles Text11-14 for site/phase filtering introduced in consolidation
    /// </summary>
    public class CustomFieldManager
    {
        /// <summary>
        /// Set filtering fields on a task (Text11-14)
        /// </summary>
        public void SetFilteringFields(Task task,
            string site = null,
            string phaseType = null,
            string subphase = null,
            string templateSource = null)
        {
            if (task == null) return;

            // Text11: Site (e.g., "SITE-001", "SITE-002")
            if (!string.IsNullOrEmpty(site))
            {
                task.SetField(PjField.pjTaskText11, site);
            }

            // Text12: Stage (e.g., "Site Activation", "Implementation", "Site Closeout", "Study Closeout")
            if (!string.IsNullOrEmpty(phaseType))
            {
                task.SetField(PjField.pjTaskText12, phaseType);
            }

            // Text13: Subphase (e.g., "Essential Docs", "IRB Submission", "Training")
            if (!string.IsNullOrEmpty(subphase))
            {
                task.SetField(PjField.pjTaskText13, subphase);
            }

            // Text14: Template Source (e.g., "API", "Library-USA", "Library-UK")
            if (!string.IsNullOrEmpty(templateSource))
            {
                task.SetField(PjField.pjTaskText14, templateSource);
            }
        }

        /// <summary>
        /// Get site from task
        /// </summary>
        public string GetSite(Task task)
        {
            if (task == null) return null;
            return task.GetField(PjField.pjTaskText11)?.ToString();
        }

        /// <summary>
        /// Get phase type from task
        /// </summary>
        public string GetPhaseType(Task task)
        {
            if (task == null) return null;
            return task.GetField(PjField.pjTaskText12)?.ToString();
        }

        /// <summary>
        /// Get subphase from task
        /// </summary>
        public string GetSubphase(Task task)
        {
            if (task == null) return null;
            return task.GetField(PjField.pjTaskText13)?.ToString();
        }

        /// <summary>
        /// Get template source from task
        /// </summary>
        public string GetTemplateSource(Task task)
        {
            if (task == null) return null;
            return task.GetField(PjField.pjTaskText14)?.ToString();
        }

        /// <summary>
        /// Clear filtering fields from a task
        /// </summary>
        public void ClearFilteringFields(Task task)
        {
            if (task == null) return;

            task.SetField(PjField.pjTaskText11, string.Empty);
            task.SetField(PjField.pjTaskText12, string.Empty);
            task.SetField(PjField.pjTaskText13, string.Empty);
            task.SetField(PjField.pjTaskText14, string.Empty);
        }

        /// <summary>
        /// Check if task has filtering fields populated
        /// </summary>
        public bool HasFilteringFields(Task task)
        {
            if (task == null) return false;

            string site = task.GetField(PjField.pjTaskText11)?.ToString();
            string phaseType = task.GetField(PjField.pjTaskText12)?.ToString();

            return !string.IsNullOrEmpty(site) || !string.IsNullOrEmpty(phaseType);
        }

        /// <summary>
        /// Set clinical entity fields (Text7-10, Flag2-4, Date1-2)
        /// These are used for site, amendment, cohort tracking
        /// </summary>
        public void SetClinicalEntityFields(Task task,
            string siteIds = null,
            string amendmentIds = null,
            string cohortIds = null,
            string clinicalSummary = null,
            bool? isSiteSpecific = null,
            bool? isAmendmentGenerated = null,
            bool? requiresIRB = null,
            DateTime? amendmentEffectiveDate = null,
            DateTime? cohortEnrollmentStart = null)
        {
            if (task == null) return;

            // Text7: Site IDs (comma-separated)
            if (!string.IsNullOrEmpty(siteIds))
            {
                task.SetField(PjField.pjTaskText7, siteIds);
            }

            // Text8: Amendment IDs (comma-separated)
            if (!string.IsNullOrEmpty(amendmentIds))
            {
                task.SetField(PjField.pjTaskText8, amendmentIds);
            }

            // Text9: Cohort IDs (comma-separated)
            if (!string.IsNullOrEmpty(cohortIds))
            {
                task.SetField(PjField.pjTaskText9, cohortIds);
            }

            // Text10: Clinical Summary (display-only)
            if (!string.IsNullOrEmpty(clinicalSummary))
            {
                task.SetField(PjField.pjTaskText10, clinicalSummary);
            }

            // Flag2: Is Site-Specific Task
            if (isSiteSpecific.HasValue)
            {
                task.Flag2 = isSiteSpecific.Value;
            }

            // Flag3: Is Amendment-Generated Task
            if (isAmendmentGenerated.HasValue)
            {
                task.Flag3 = isAmendmentGenerated.Value;
            }

            // Flag4: Requires IRB Approval
            if (requiresIRB.HasValue)
            {
                task.Flag4 = requiresIRB.Value;
            }

            // Date1: Amendment Effective Date
            if (amendmentEffectiveDate.HasValue)
            {
                task.Date1 = amendmentEffectiveDate.Value;
            }

            // Date2: Cohort Enrollment Start Date
            if (cohortEnrollmentStart.HasValue)
            {
                task.Date2 = cohortEnrollmentStart.Value;
            }
        }

        /// <summary>
        /// Validate stage value
        /// </summary>
        public bool IsValidPhaseType(string phaseType)
        {
            if (string.IsNullOrEmpty(phaseType)) return false;

            string[] validStages = { "Site Activation", "Implementation", "Site Closeout", "Study Closeout", "Amendment" };
            return Array.Exists(validStages, pt => pt.Equals(phaseType, StringComparison.OrdinalIgnoreCase));
        }
    }
}
