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
        public void LoadTemplateIntoProject(Models.Timeline template, Application projectApp)
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

            // Create tasks
            foreach (var templateTask in template.tasks)
            {
                var msTask = project.Tasks.Add(templateTask.name);

                // Set duration
                msTask.Duration = templateTask.duration_days + "d";

                // Set custom fields based on template metadata
                SetTaskCustomFields(msTask, templateTask);

                // Store mapping for dependency creation
                taskIdMap[templateTask.id] = msTask.ID;
            }

            // Create dependencies
            CreateDependencies(project, template.dependencies, taskIdMap);

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
    }
}
