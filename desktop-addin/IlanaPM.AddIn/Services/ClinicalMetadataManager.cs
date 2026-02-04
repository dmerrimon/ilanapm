using System;
using System.Collections.Generic;
using System.Linq;
using IlanaPM.AddIn.Models;
using Newtonsoft.Json;
using MSProject = Microsoft.Office.Interop.MSProject;
using Site = IlanaPM.AddIn.Models.Site;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Manages clinical metadata (sites, amendments, cohorts) storage and task tagging
    /// Stores entity definitions as JSON in ProjectSummaryTask.Notes field
    /// Tags individual tasks using custom fields Text7-10, Flag2-4, Date1-2
    /// </summary>
    public class ClinicalMetadataManager
    {
        private const string METADATA_MARKER_START = "===ILANA_CLINICAL_METADATA_START===";
        private const string METADATA_MARKER_END = "===ILANA_CLINICAL_METADATA_END===";

        #region Storage Methods

        /// <summary>
        /// Load clinical metadata from MS Project file
        /// Returns null if no metadata exists
        /// </summary>
        public ClinicalMetadata LoadMetadata(MSProject.Project project)
        {
            if (project == null)
                return null;

            try
            {
                // Get project summary task notes
                var summaryTask = project.ProjectSummaryTask;
                if (summaryTask == null)
                    return null;

                string notes = summaryTask.Notes ?? "";

                // Look for metadata JSON between markers
                int startIndex = notes.IndexOf(METADATA_MARKER_START);
                if (startIndex == -1)
                    return null;

                int endIndex = notes.IndexOf(METADATA_MARKER_END, startIndex);
                if (endIndex == -1)
                    return null;

                // Extract JSON
                startIndex += METADATA_MARKER_START.Length;
                string json = notes.Substring(startIndex, endIndex - startIndex).Trim();

                if (string.IsNullOrWhiteSpace(json))
                    return null;

                // Deserialize
                var metadata = JsonConvert.DeserializeObject<ClinicalMetadata>(json);
                return metadata;
            }
            catch (JsonException ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error parsing clinical metadata JSON: {ex.Message}");
                return null;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error loading clinical metadata: {ex.Message}");
                return null;
            }
        }

        /// <summary>
        /// Save clinical metadata to MS Project file
        /// Stores as JSON in ProjectSummaryTask.Notes field
        /// </summary>
        public void SaveMetadata(MSProject.Project project, ClinicalMetadata metadata)
        {
            if (project == null || metadata == null)
                return;

            try
            {
                var summaryTask = project.ProjectSummaryTask;
                if (summaryTask == null)
                    return;

                // Serialize to JSON
                string json = JsonConvert.SerializeObject(metadata, Formatting.Indented);

                // Get existing notes
                string existingNotes = summaryTask.Notes ?? "";

                // Remove old metadata if exists
                int startIndex = existingNotes.IndexOf(METADATA_MARKER_START);
                if (startIndex != -1)
                {
                    int endIndex = existingNotes.IndexOf(METADATA_MARKER_END, startIndex);
                    if (endIndex != -1)
                    {
                        // Remove old metadata section
                        int removeLength = (endIndex + METADATA_MARKER_END.Length) - startIndex;
                        existingNotes = existingNotes.Remove(startIndex, removeLength).Trim();
                    }
                }

                // Append new metadata
                string newNotes = existingNotes;
                if (!string.IsNullOrWhiteSpace(existingNotes))
                    newNotes += "\r\n\r\n";

                newNotes += $"{METADATA_MARKER_START}\r\n{json}\r\n{METADATA_MARKER_END}";

                summaryTask.Notes = newNotes;

                System.Diagnostics.Debug.WriteLine("Clinical metadata saved successfully");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error saving clinical metadata: {ex.Message}");
                throw new Exception($"Failed to save clinical metadata: {ex.Message}");
            }
        }

        #endregion

        #region Task Tagging Methods

        /// <summary>
        /// Tag task with clinical entities (sites, amendments, cohorts)
        /// Sets custom fields: Text7 (sites), Text8 (amendments), Text9 (cohorts), Text10 (summary)
        /// Also sets Flag2 (is site-specific), Flag3 (is amendment-generated)
        /// </summary>
        public void TagTaskWithEntities(
            MSProject.Task task,
            List<string> siteIds,
            List<string> amendmentIds,
            List<string> cohortIds)
        {
            if (task == null)
                return;

            try
            {
                // Set entity ID fields (comma-separated)
                task.SetField(MSProject.PjField.pjTaskText7, string.Join(",", siteIds ?? new List<string>()));
                task.SetField(MSProject.PjField.pjTaskText8, string.Join(",", amendmentIds ?? new List<string>()));
                task.SetField(MSProject.PjField.pjTaskText9, string.Join(",", cohortIds ?? new List<string>()));

                // Set summary field for display
                string summary = GenerateClinicalSummary(siteIds, amendmentIds, cohortIds);
                task.SetField(MSProject.PjField.pjTaskText10, summary);

                // Set boolean flags
                task.SetField(MSProject.PjField.pjTaskFlag2, siteIds != null && siteIds.Count > 0 ? "Yes" : "No");
                task.SetField(MSProject.PjField.pjTaskFlag3, amendmentIds != null && amendmentIds.Count > 0 ? "Yes" : "No");

                System.Diagnostics.Debug.WriteLine($"Tagged task '{task.Name}' with {siteIds?.Count ?? 0} sites, {amendmentIds?.Count ?? 0} amendments, {cohortIds?.Count ?? 0} cohorts");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error tagging task: {ex.Message}");
                throw;
            }
        }

        /// <summary>
        /// Generate human-readable clinical summary for Text10 field
        /// Example: "Site 001, Site 005 | Amendment 3 | Cohort 1"
        /// </summary>
        private string GenerateClinicalSummary(List<string> siteIds, List<string> amendmentIds, List<string> cohortIds)
        {
            var parts = new List<string>();

            if (siteIds != null && siteIds.Count > 0)
                parts.Add(string.Join(", ", siteIds));

            if (amendmentIds != null && amendmentIds.Count > 0)
                parts.Add(string.Join(", ", amendmentIds));

            if (cohortIds != null && cohortIds.Count > 0)
                parts.Add(string.Join(", ", cohortIds));

            return string.Join(" | ", parts);
        }

        #endregion

        #region Filtering Methods

        /// <summary>
        /// Get all tasks tagged with specified site ID
        /// </summary>
        public List<MSProject.Task> GetTasksBySite(MSProject.Project project, string siteId)
        {
            return GetTasksByEntity(project, siteId, MSProject.PjField.pjTaskText7);
        }

        /// <summary>
        /// Get all tasks tagged with specified amendment ID
        /// </summary>
        public List<MSProject.Task> GetTasksByAmendment(MSProject.Project project, string amendmentId)
        {
            return GetTasksByEntity(project, amendmentId, MSProject.PjField.pjTaskText8);
        }

        /// <summary>
        /// Get all tasks tagged with specified cohort ID
        /// </summary>
        public List<MSProject.Task> GetTasksByCohort(MSProject.Project project, string cohortId)
        {
            return GetTasksByEntity(project, cohortId, MSProject.PjField.pjTaskText9);
        }

        /// <summary>
        /// Generic method to get tasks by entity ID
        /// Searches specified custom field for entity ID (supports comma-separated lists)
        /// </summary>
        private List<MSProject.Task> GetTasksByEntity(MSProject.Project project, string entityId, MSProject.PjField field)
        {
            var results = new List<MSProject.Task>();

            if (project == null || string.IsNullOrWhiteSpace(entityId))
                return results;

            try
            {
                foreach (MSProject.Task task in project.Tasks)
                {
                    if (task == null)
                        continue;

                    string fieldValue = task.GetField(field)?.ToString() ?? "";

                    // Check if entity ID exists in comma-separated list
                    if (ContainsEntityId(fieldValue, entityId))
                    {
                        results.Add(task);
                    }
                }

                System.Diagnostics.Debug.WriteLine($"Found {results.Count} tasks for entity {entityId}");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error filtering tasks: {ex.Message}");
            }

            return results;
        }

        /// <summary>
        /// Check if comma-separated field value contains specific entity ID
        /// </summary>
        private bool ContainsEntityId(string fieldValue, string entityId)
        {
            if (string.IsNullOrWhiteSpace(fieldValue) || string.IsNullOrWhiteSpace(entityId))
                return false;

            // Split by comma and check each ID
            string[] ids = fieldValue.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries);
            return ids.Any(id => id.Trim().Equals(entityId, StringComparison.OrdinalIgnoreCase));
        }

        #endregion

        #region Validation Methods

        /// <summary>
        /// Validate clinical entities and return warnings
        /// Implements 3 core validation rules:
        /// 1. Site has enrollment tasks but no IRB approval
        /// 2. Amendment affects N sites but less than N approval tasks exist
        /// 3. Cohort 2 tasks scheduled before Cohort 1 safety review
        /// </summary>
        public List<ClinicalWarning> ValidateClinicalEntities(MSProject.Project project, ClinicalMetadata metadata)
        {
            var warnings = new List<ClinicalWarning>();

            if (project == null || metadata == null)
                return warnings;

            try
            {
                // Rule 1: Check sites for enrollment without IRB approval
                warnings.AddRange(ValidateSiteIRBApproval(project, metadata.sites));

                // Rule 2: Check amendments have approval tasks for all affected sites
                warnings.AddRange(ValidateAmendmentSiteCoverage(project, metadata.amendments));

                // Rule 3: Check cohort dependencies (Cohort 2 before Cohort 1 safety review)
                warnings.AddRange(ValidateCohortDependencies(project, metadata.cohorts));

                System.Diagnostics.Debug.WriteLine($"Clinical validation complete: {warnings.Count} warnings");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error during clinical validation: {ex.Message}");
            }

            return warnings;
        }

        /// <summary>
        /// Rule 1: Check if sites have enrollment tasks but no IRB approval
        /// </summary>
        private List<ClinicalWarning> ValidateSiteIRBApproval(MSProject.Project project, List<Site> sites)
        {
            var warnings = new List<ClinicalWarning>();

            foreach (var site in sites)
            {
                var siteTasks = GetTasksBySite(project, site.id);

                // Check for enrollment-related tasks
                bool hasEnrollmentTasks = siteTasks.Any(t =>
                    t.Name.ToLower().Contains("enroll") ||
                    t.Name.ToLower().Contains("recruit") ||
                    t.Name.ToLower().Contains("patient"));

                // Check for IRB approval tasks
                bool hasIRBApproval = siteTasks.Any(t =>
                    t.Name.ToLower().Contains("irb") &&
                    (t.Name.ToLower().Contains("approval") || t.Name.ToLower().Contains("approve")));

                if (hasEnrollmentTasks && !hasIRBApproval)
                {
                    warnings.Add(new ClinicalWarning(
                        "Site",
                        site.id,
                        $"Site {site.id} ({site.name}) has enrollment tasks but no IRB approval task",
                        $"Add 'IRB Approval - {site.name}' task before enrollment tasks",
                        "Warning"
                    ));
                }
            }

            return warnings;
        }

        /// <summary>
        /// Rule 2: Check if amendments have approval tasks for all affected sites
        /// </summary>
        private List<ClinicalWarning> ValidateAmendmentSiteCoverage(MSProject.Project project, List<Amendment> amendments)
        {
            var warnings = new List<ClinicalWarning>();

            foreach (var amendment in amendments)
            {
                if (amendment.affected_sites == null || amendment.affected_sites.Count == 0)
                    continue;

                var amendmentTasks = GetTasksByAmendment(project, amendment.id);

                // Count how many of the affected sites have approval tasks
                int sitesWithApproval = 0;
                foreach (var siteId in amendment.affected_sites)
                {
                    bool hasApprovalTask = amendmentTasks.Any(t =>
                        (t.GetField(MSProject.PjField.pjTaskText7)?.ToString()?.Contains(siteId) ?? false) &&
                        (t.Name.ToLower().Contains("irb") || t.Name.ToLower().Contains("approval")));

                    if (hasApprovalTask)
                        sitesWithApproval++;
                }

                if (sitesWithApproval < amendment.affected_sites.Count)
                {
                    warnings.Add(new ClinicalWarning(
                        "Amendment",
                        amendment.id,
                        $"{amendment.number} affects {amendment.affected_sites.Count} sites but only {sitesWithApproval} have approval tasks",
                        $"Add IRB approval tasks for missing sites: {string.Join(", ", amendment.affected_sites.Skip(sitesWithApproval))}",
                        "Error"
                    ));
                }
            }

            return warnings;
        }

        /// <summary>
        /// Rule 3: Check if Cohort 2 tasks are scheduled before Cohort 1 safety review
        /// </summary>
        private List<ClinicalWarning> ValidateCohortDependencies(MSProject.Project project, List<Cohort> cohorts)
        {
            var warnings = new List<ClinicalWarning>();

            // Find Cohort 1 and Cohort 2 (or similar patterns)
            var cohort1 = cohorts.FirstOrDefault(c =>
                c.id.Contains("001") || c.name.ToLower().Contains("cohort 1"));
            var cohort2 = cohorts.FirstOrDefault(c =>
                c.id.Contains("002") || c.name.ToLower().Contains("cohort 2"));

            if (cohort1 == null || cohort2 == null)
                return warnings; // Can't validate if both cohorts don't exist

            // Get tasks for each cohort
            var cohort1Tasks = GetTasksByCohort(project, cohort1.id);
            var cohort2Tasks = GetTasksByCohort(project, cohort2.id);

            // Find Cohort 1 safety review task
            var cohort1SafetyReview = cohort1Tasks.FirstOrDefault(t =>
                t.Name.ToLower().Contains("safety") &&
                (t.Name.ToLower().Contains("review") || t.Name.ToLower().Contains("complete")));

            if (cohort1SafetyReview == null)
                return warnings; // No safety review task to check against

            // Check if any Cohort 2 tasks start before Cohort 1 safety review completes
            DateTime? cohort1SafetyFinish = cohort1SafetyReview.Finish;
            if (cohort1SafetyFinish == null)
                return warnings;

            foreach (var cohort2Task in cohort2Tasks)
            {
                DateTime? cohort2Start = cohort2Task.Start;
                if (cohort2Start != null && cohort2Start < cohort1SafetyFinish)
                {
                    warnings.Add(new ClinicalWarning(
                        "Cohort",
                        cohort2.id,
                        $"Cohort 2 task '{cohort2Task.Name}' starts before Cohort 1 safety review completes",
                        $"Ensure Cohort 2 tasks start after '{cohort1SafetyReview.Name}' (finishes {cohort1SafetyFinish:yyyy-MM-dd})",
                        "Warning"
                    ));
                    break; // Only report once per cohort
                }
            }

            return warnings;
        }

        #endregion
    }
}
