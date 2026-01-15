using System;
using System.Collections.Generic;
using Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Services
{
    public class ProjectDataExtractor
    {
        public Models.Timeline ExtractTimeline(Application projectApp)
        {
            if (projectApp.ActiveProject == null)
            {
                throw new System.Exception("No active project found. Please open a project file first.");
            }

            Project activeProject = projectApp.ActiveProject;
            Models.Timeline timeline = new Models.Timeline
            {
                study_name = activeProject.Name,
                phase = "Phase II",
                authority = "FDA",
                therapeutic_area = "Oncology"
            };

            foreach (Microsoft.Office.Interop.MSProject.Task task in activeProject.Tasks)
            {
                if (task != null && !task.Summary)
                {
                    var taskModel = new Models.Task
                    {
                        id = task.ID.ToString(),
                        name = task.Name,
                        duration_days = ConvertMinutesToDays(task.Duration),
                        start_date = task.Start.ToString("yyyy-MM-dd"),
                        end_date = task.Finish.ToString("yyyy-MM-dd"),
                        category = DetermineCategoryFromName(task.Name),
                        phase = timeline.phase,
                        authority = timeline.authority,
                        is_mandatory = task.Critical,
                        checklist_completion_pct = (int)task.PercentComplete
                    };

                    timeline.tasks.Add(taskModel);
                }
            }

            foreach (Microsoft.Office.Interop.MSProject.Task task in activeProject.Tasks)
            {
                if (task != null && task.TaskDependencies != null)
                {
                    foreach (TaskDependency dep in task.TaskDependencies)
                    {
                        var dependency = new Models.Dependency
                        {
                            predecessor_id = dep.From.ID.ToString(),
                            successor_id = task.ID.ToString(),
                            type = ConvertDependencyType(dep.Type),
                            lag_days = ConvertMinutesToDays(dep.Lag)
                        };

                        timeline.dependencies.Add(dependency);
                    }
                }
            }

            return timeline;
        }

        private int ConvertMinutesToDays(double minutes)
        {
            return (int)Math.Ceiling(minutes / (8.0 * 60.0));
        }

        private string DetermineCategoryFromName(string taskName)
        {
            string lowerName = taskName.ToLower();

            if (lowerName.Contains("irb") || lowerName.Contains("ind") ||
                lowerName.Contains("regulatory") || lowerName.Contains("approval"))
                return "Regulatory";

            if (lowerName.Contains("data") || lowerName.Contains("database") ||
                lowerName.Contains("lock"))
                return "Data";

            if (lowerName.Contains("site") || lowerName.Contains("siv") ||
                lowerName.Contains("visit"))
                return "Site";

            if (lowerName.Contains("close") || lowerName.Contains("archive"))
                return "Closeout";

            return "Operational";
        }

        private string ConvertDependencyType(PjTaskLinkType linkType)
        {
            switch (linkType)
            {
                case PjTaskLinkType.pjFinishToStart:
                    return "finish-to-start";
                case PjTaskLinkType.pjStartToStart:
                    return "start-to-start";
                case PjTaskLinkType.pjFinishToFinish:
                    return "finish-to-finish";
                case PjTaskLinkType.pjStartToFinish:
                    return "start-to-finish";
                default:
                    return "finish-to-start";
            }
        }
    }
}
