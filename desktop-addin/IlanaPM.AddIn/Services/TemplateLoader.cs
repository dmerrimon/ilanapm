using System;
using System.Collections.Generic;
using Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Service for loading country-specific timeline templates into MS Project
    /// </summary>
    public class TemplateLoader
    {
        /// <summary>
        /// Load a generated template into MS Project
        /// </summary>
        /// <param name="template">Template timeline from API</param>
        /// <param name="projectApp">MS Project application</param>
        /// <param name="customColumnNames">Optional custom column names for Text5, Text6, Text7</param>
        public void LoadTemplateIntoProject(Models.Timeline template, Application projectApp,
            Dictionary<string, string> customColumnNames = null)
        {
            if (projectApp.ActiveProject == null)
            {
                // Create new project if no active project
                projectApp.FileNew(Type.Missing, Type.Missing, Type.Missing, Type.Missing);
            }

            Project project = projectApp.ActiveProject;

            // Set project name (wrap in try-catch - may fail with special characters)
            try
            {
                if (!string.IsNullOrEmpty(template.study_name))
                {
                    project.Name = template.study_name;
                }
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Warning: Could not set project name to '{template.study_name}': {ex.Message}");
            }

            // Map template task IDs to MS Project task IDs
            Dictionary<string, int> taskIdMap = new Dictionary<string, int>();

            // Create tasks with proper hierarchy (summary tasks + children)
            foreach (var templateTask in template.tasks)
            {
                try
                {
                    // Sanitize task name - MS Project doesn't support newlines in task names
                    string sanitizedName = templateTask.name
                        .Replace("\r\n", " ")
                        .Replace("\n", " ")
                        .Replace("\r", " ")
                        .Trim();

                    // Remove multiple consecutive spaces
                    while (sanitizedName.Contains("  "))
                    {
                        sanitizedName = sanitizedName.Replace("  ", " ");
                    }

                    System.Diagnostics.Debug.WriteLine($"Creating task: {sanitizedName}");
                    var msTask = project.Tasks.Add(sanitizedName);

                    // Set duration (summary tasks will auto-calculate from children)
                    if (!templateTask.is_summary && templateTask.duration_days > 0)
                    {
                        try
                        {
                            msTask.Duration = templateTask.duration_days + "d";
                        }
                        catch (System.Exception ex)
                        {
                            System.Diagnostics.Debug.WriteLine($"Warning: Could not set duration for task '{sanitizedName}': {ex.Message}");
                        }
                    }

                    // Set outline level for proper indentation
                    try
                    {
                        if (templateTask.outline_level >= 1 && templateTask.outline_level <= 9)
                        {
                            msTask.OutlineLevel = (short)templateTask.outline_level;
                        }
                    }
                    catch (System.Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Warning: Could not set outline level for task '{sanitizedName}': {ex.Message}");
                    }

                    // Set custom fields based on template metadata (skip for summary tasks)
                    if (!templateTask.is_summary)
                    {
                        try
                        {
                            SetTaskCustomFields(msTask, templateTask);
                        }
                        catch (System.Exception ex)
                        {
                            System.Diagnostics.Debug.WriteLine($"Warning: Could not set custom fields on task '{sanitizedName}': {ex.Message}");
                        }
                    }

                    // Store mapping for dependency creation (ALL tasks)
                    taskIdMap[templateTask.id] = msTask.ID;
                    System.Diagnostics.Debug.WriteLine($"  Added to task map: {templateTask.id} -> MS Project ID {msTask.ID}");
                }
                catch (System.Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"ERROR: Failed to create task '{templateTask.name}': {ex.Message}");
                    System.Diagnostics.Debug.WriteLine($"Stack trace: {ex.StackTrace}");
                }
            }

            // Create dependencies
            System.Diagnostics.Debug.WriteLine($"=== Creating Dependencies ===");
            System.Diagnostics.Debug.WriteLine($"Total dependencies to create: {template.dependencies.Count}");
            System.Diagnostics.Debug.WriteLine($"Tasks in ID map: {taskIdMap.Count}");
            CreateDependencies(project, template.dependencies, taskIdMap);

            // Rename custom column headers if provided
            if (customColumnNames != null && customColumnNames.Count > 0)
            {
                RenameCustomColumns(project, customColumnNames);
            }

            // MS Project auto-calculates schedules - no manual update needed
        }

        /// <summary>
        /// Set custom fields on MS Project task from template task
        /// </summary>
        private void SetTaskCustomFields(Task msTask, Models.Task templateTask)
        {
            try
            {
                // Text1: Regulatory Authority
                msTask.SetField(PjField.pjTaskText1, templateTask.authority ?? "");

                // Text2: Study Phase
                msTask.SetField(PjField.pjTaskText2, templateTask.phase ?? "");

                // Text3: Therapeutic Area
                msTask.SetField(PjField.pjTaskText3, templateTask.category ?? "");

                // Text4: Task Category
                msTask.SetField(PjField.pjTaskText4, templateTask.category ?? "");

                // Text16: Authority Type (NEW - authority-specific ontology)
                if (!string.IsNullOrEmpty(templateTask.authority_type))
                {
                    msTask.SetField(PjField.pjTaskText16, templateTask.authority_type);
                }

                // Text17: Submission Form (NEW - authority-specific ontology)
                if (!string.IsNullOrEmpty(templateTask.submission_form))
                {
                    msTask.SetField(PjField.pjTaskText17, templateTask.submission_form);
                }

                // Flag1: Is Mandatory
                msTask.SetField(PjField.pjTaskFlag1, templateTask.is_mandatory ? "Yes" : "No");

                // Add notes with template metadata
                string notes = "";

                // If original task name contains newlines, preserve full text in notes
                if (templateTask.name.Contains("\n") || templateTask.name.Contains("\r"))
                {
                    notes += $"Full Task Description:\n{templateTask.name}\n\n";
                }

                notes += $"Template Task ID: {templateTask.id}\n";
                if (!string.IsNullOrEmpty(templateTask.authority))
                    notes += $"Authority: {templateTask.authority}\n";

                // Add authority-specific details to notes (NEW)
                if (!string.IsNullOrEmpty(templateTask.authority_full_name))
                    notes += $"Authority Full Name: {templateTask.authority_full_name}\n";
                if (!string.IsNullOrEmpty(templateTask.authority_type))
                    notes += $"Authority Type: {templateTask.authority_type}\n";
                if (!string.IsNullOrEmpty(templateTask.submission_form))
                    notes += $"Submission Form: {templateTask.submission_form}\n";

                notes += $"Category: {templateTask.category}\n";
                notes += $"Mandatory: {(templateTask.is_mandatory ? "Yes" : "No")}\n";

                msTask.Notes = notes;
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error setting custom fields for task {templateTask.id}: {ex.Message}");
            }
        }

        /// <summary>
        /// Create task dependencies from template
        /// </summary>
        private void CreateDependencies(Project project, List<Models.Dependency> dependencies, Dictionary<string, int> taskIdMap)
        {
            int successCount = 0;
            int skipCount = 0;
            int errorCount = 0;

            foreach (var dep in dependencies)
            {
                if (!taskIdMap.ContainsKey(dep.predecessor_id))
                {
                    System.Diagnostics.Debug.WriteLine($"Skipping dependency: predecessor '{dep.predecessor_id}' not found in task map");
                    skipCount++;
                    continue;
                }

                if (!taskIdMap.ContainsKey(dep.successor_id))
                {
                    System.Diagnostics.Debug.WriteLine($"Skipping dependency: successor '{dep.successor_id}' not found in task map");
                    skipCount++;
                    continue;
                }

                try
                {
                    int predecessorId = taskIdMap[dep.predecessor_id];
                    int successorId = taskIdMap[dep.successor_id];

                    var predecessorTask = project.Tasks[predecessorId];
                    var successorTask = project.Tasks[successorId];

                    // Convert dependency type
                    PjTaskLinkType linkType = ConvertDependencyType(dep.type);

                    // Add dependency with lag
                    string lag = dep.lag_days > 0 ? dep.lag_days + "d" : "0d";
                    successorTask.TaskDependencies.Add(predecessorTask, linkType, lag);
                    successCount++;
                }
                catch (System.Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"ERROR creating dependency {dep.predecessor_id} → {dep.successor_id}: {ex.Message}");
                    errorCount++;
                }
            }

            System.Diagnostics.Debug.WriteLine($"=== Dependency Creation Summary ===");
            System.Diagnostics.Debug.WriteLine($"Success: {successCount}, Skipped: {skipCount}, Errors: {errorCount}");
        }

        /// <summary>
        /// Convert template dependency type to MS Project link type
        /// </summary>
        private PjTaskLinkType ConvertDependencyType(string depType)
        {
            if (string.IsNullOrEmpty(depType))
                return PjTaskLinkType.pjFinishToStart;

            switch (depType.ToLower())
            {
                case "finish-to-start":
                    return PjTaskLinkType.pjFinishToStart;
                case "finish-to-finish":
                    return PjTaskLinkType.pjFinishToFinish;
                case "start-to-start":
                    return PjTaskLinkType.pjStartToStart;
                case "start-to-finish":
                    return PjTaskLinkType.pjStartToFinish;
                default:
                    return PjTaskLinkType.pjFinishToStart;
            }
        }

        /// <summary>
        /// Rename custom column headers in MS Project
        /// </summary>
        /// <param name="project">MS Project project</param>
        /// <param name="customColumnNames">Dictionary of field names to custom names</param>
        private void RenameCustomColumns(Project project, Dictionary<string, string> customColumnNames)
        {
            try
            {
                // Map custom field names to MS Project custom field constants
                var fieldMapping = new Dictionary<string, PjCustomField>
                {
                    { "Text5", PjCustomField.pjCustomTaskText5 },
                    { "Text6", PjCustomField.pjCustomTaskText6 },
                    { "Text7", PjCustomField.pjCustomTaskText7 }
                };

                foreach (var customField in customColumnNames)
                {
                    if (fieldMapping.ContainsKey(customField.Key))
                    {
                        // Rename the column header by setting the custom field name
                        PjCustomField field = fieldMapping[customField.Key];

                        // Use CustomFieldRename to rename the column
                        // This changes how the column appears in Insert Column dialogs and views
                        project.Application.CustomFieldRename(
                            field,
                            customField.Value
                        );

                        System.Diagnostics.Debug.WriteLine($"Renamed {customField.Key} to '{customField.Value}'");
                    }
                }
            }
            catch (System.Exception ex)
            {
                // Non-critical error - log but don't fail template load
                System.Diagnostics.Debug.WriteLine($"Error configuring columns: {ex.Message}");
            }
        }
    }
}
