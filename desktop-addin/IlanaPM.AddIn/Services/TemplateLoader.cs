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

            // Set project name
            project.Name = template.study_name;

            // Map template task IDs to MS Project task IDs
            Dictionary<string, int> taskIdMap = new Dictionary<string, int>();

            // Create tasks with proper hierarchy (summary tasks + children)
            foreach (var templateTask in template.tasks)
            {
                var msTask = project.Tasks.Add(templateTask.name);

                // Set duration (summary tasks will auto-calculate from children)
                if (!templateTask.is_summary)
                {
                    msTask.Duration = templateTask.duration_days + "d";
                }

                // Set outline level for proper indentation
                // Level 1 = Summary task (not indented)
                // Level 2 = Normal task (indented under summary)
                msTask.OutlineLevel = templateTask.outline_level;

                // Mark as summary task if needed (MS Project will auto-detect based on children)
                if (templateTask.is_summary)
                {
                    msTask.Summary = true;
                }

                // Set custom fields based on template metadata (skip for summary tasks)
                if (!templateTask.is_summary)
                {
                    SetTaskCustomFields(msTask, templateTask);
                }

                // Store mapping for dependency creation (skip summary tasks)
                if (!templateTask.is_summary)
                {
                    taskIdMap[templateTask.id] = msTask.ID;
                }
            }

            // Create dependencies
            CreateDependencies(project, template.dependencies, taskIdMap);

            // Rename custom column headers if provided
            if (customColumnNames != null && customColumnNames.Count > 0)
            {
                RenameCustomColumns(project, customColumnNames);
            }

            // Auto-schedule the project
            project.UpdateProject();
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

                // Flag1: Is Mandatory
                msTask.SetField(PjField.pjTaskFlag1, templateTask.is_mandatory ? "Yes" : "No");

                // Add notes with template metadata
                string notes = $"Template Task ID: {templateTask.id}\n";
                if (!string.IsNullOrEmpty(templateTask.authority))
                    notes += $"Authority: {templateTask.authority}\n";
                notes += $"Category: {templateTask.category}\n";
                notes += $"Mandatory: {(templateTask.is_mandatory ? "Yes" : "No")}\n";

                msTask.Notes = notes;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error setting custom fields for task {templateTask.id}: {ex.Message}");
            }
        }

        /// <summary>
        /// Create task dependencies from template
        /// </summary>
        private void CreateDependencies(Project project, List<Models.Dependency> dependencies, Dictionary<string, int> taskIdMap)
        {
            foreach (var dep in dependencies)
            {
                if (taskIdMap.ContainsKey(dep.predecessor_id) && taskIdMap.ContainsKey(dep.successor_id))
                {
                    try
                    {
                        int predecessorId = taskIdMap[dep.predecessor_id];
                        int successorId = taskIdMap[dep.successor_id];

                        var predecessorTask = project.Tasks[predecessorId];
                        var successorTask = project.Tasks[successorId];

                        // Convert dependency type
                        PjTaskLinkType linkType = ConvertDependencyType(dep.type);

                        // Add dependency with lag
                        string lag = dep.lag_days + "d";
                        successorTask.TaskDependencies.Add(predecessorTask, linkType, lag);
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Error creating dependency {dep.predecessor_id} → {dep.successor_id}: {ex.Message}");
                    }
                }
            }
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
                // Map custom field names to MS Project field constants
                var fieldMapping = new Dictionary<string, PjField>
                {
                    { "Text5", PjField.pjTaskText5 },
                    { "Text6", PjField.pjTaskText6 },
                    { "Text7", PjField.pjTaskText7 }
                };

                foreach (var customField in customColumnNames)
                {
                    if (fieldMapping.ContainsKey(customField.Key))
                    {
                        // Rename the column header by setting the custom field name
                        PjField field = fieldMapping[customField.Key];

                        // Use CustomFieldSetName to rename the column
                        // This changes how the column appears in Insert Column dialogs and views
                        project.Application.CustomFieldSetName(
                            field,
                            customField.Value
                        );

                        System.Diagnostics.Debug.WriteLine($"Renamed {customField.Key} to '{customField.Value}'");
                    }
                }
            }
            catch (Exception ex)
            {
                // Non-critical error - log but don't fail template load
                System.Diagnostics.Debug.WriteLine($"Warning: Could not rename custom columns: {ex.Message}");
            }
        }
    }
}
