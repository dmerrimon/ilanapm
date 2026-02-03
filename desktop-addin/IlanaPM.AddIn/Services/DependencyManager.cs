using IlanaPM.AddIn.Models;
using Microsoft.Office.Interop.MSProject;
using System;
using System.Collections.Generic;
using System.Linq;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Manages task dependencies and parallel execution groups in MS Project
    /// </summary>
    public class DependencyManager
    {
        /// <summary>
        /// Build dependency map from template tasks
        /// Maps task_id to actual MS Project task UID
        /// </summary>
        public Dictionary<string, int> BuildTaskMap(List<TemplateTask> templateTasks, List<Task> msTasks)
        {
            var taskMap = new Dictionary<string, int>();

            for (int i = 0; i < templateTasks.Count && i < msTasks.Count; i++)
            {
                var templateTask = templateTasks[i];
                var msTask = msTasks[i];
                taskMap[templateTask.task_id] = msTask.UniqueID;
            }

            return taskMap;
        }

        /// <summary>
        /// Apply dependencies to MS Project tasks based on template task predecessors
        /// </summary>
        public void ApplyDependencies(
            Application app,
            List<TemplateTask> templateTasks,
            Dictionary<string, int> taskMap)
        {
            if (app.ActiveProject == null)
                return;

            var project = app.ActiveProject;

            foreach (var templateTask in templateTasks)
            {
                if (templateTask.predecessors == null || templateTask.predecessors.Count == 0)
                    continue;

                if (!taskMap.ContainsKey(templateTask.task_id))
                    continue;

                int taskUID = taskMap[templateTask.task_id];
                var msTask = FindTaskByUID(project, taskUID);

                if (msTask == null)
                    continue;

                // Build predecessor string
                var predecessorString = BuildPredecessorString(
                    templateTask.predecessors,
                    taskMap,
                    templateTask.dependency_type,
                    templateTask.lag_days);

                if (!string.IsNullOrEmpty(predecessorString))
                {
                    try
                    {
                        msTask.Predecessors = predecessorString;
                    }
                    catch (System.Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine(
                            $"Error setting predecessor for task {templateTask.name}: {ex.Message}");
                    }
                }

                // Mark as critical if blocking
                if (templateTask.is_blocking)
                {
                    msTask.Critical = true;
                }
            }
        }

        /// <summary>
        /// Build predecessor string for MS Project (e.g., "5FS+3d", "7SS-2d")
        /// </summary>
        private string BuildPredecessorString(
            List<string> predecessorTaskIds,
            Dictionary<string, int> taskMap,
            string dependencyType,
            int lagDays)
        {
            var predecessorParts = new List<string>();

            foreach (var predTaskId in predecessorTaskIds)
            {
                if (!taskMap.ContainsKey(predTaskId))
                    continue;

                int predUID = taskMap[predTaskId];

                // Format: TaskUID + DependencyType + Lag
                // Example: "5FS+3d" means "Task 5, Finish-to-Start, +3 day lag"
                string depType = dependencyType ?? "FS";
                string lagString = "";

                if (lagDays != 0)
                {
                    lagString = lagDays > 0 ? $"+{lagDays}d" : $"{lagDays}d";
                }

                predecessorParts.Add($"{predUID}{depType}{lagString}");
            }

            return string.Join(",", predecessorParts);
        }

        /// <summary>
        /// Group tasks by parallel execution group for scheduling optimization
        /// </summary>
        public Dictionary<string, List<TemplateTask>> GroupTasksByExecutionGroup(List<TemplateTask> templateTasks)
        {
            var groups = new Dictionary<string, List<TemplateTask>>();

            foreach (var task in templateTasks)
            {
                string groupKey = task.execution_group ?? "Ungrouped";

                if (!groups.ContainsKey(groupKey))
                {
                    groups[groupKey] = new List<TemplateTask>();
                }

                groups[groupKey].Add(task);
            }

            return groups;
        }

        /// <summary>
        /// Analyze critical path and return tasks on critical path
        /// </summary>
        public List<TemplateTask> GetCriticalPathTasks(List<TemplateTask> templateTasks)
        {
            return templateTasks.Where(t => t.is_blocking).ToList();
        }

        /// <summary>
        /// Calculate estimated duration considering parallel vs sequential execution
        /// </summary>
        public int CalculateEstimatedDuration(List<TemplateTask> templateTasks)
        {
            var groups = GroupTasksByExecutionGroup(templateTasks);
            int totalDuration = 0;

            foreach (var group in groups.Values)
            {
                if (group.Count == 0)
                    continue;

                // Check if tasks in group can run in parallel
                bool isParallel = group.All(t => t.can_run_parallel);

                if (isParallel)
                {
                    // Parallel group: duration = max duration of any task in group
                    totalDuration += group.Max(t => t.duration_days);
                }
                else
                {
                    // Sequential group: duration = sum of all task durations
                    totalDuration += group.Sum(t => t.duration_days);
                }
            }

            return totalDuration;
        }

        /// <summary>
        /// Validate dependencies for circular references
        /// </summary>
        public List<string> ValidateDependencies(List<TemplateTask> templateTasks)
        {
            var errors = new List<string>();

            foreach (var task in templateTasks)
            {
                if (task.predecessors == null || task.predecessors.Count == 0)
                    continue;

                // Check if any predecessor references itself
                if (task.predecessors.Contains(task.task_id))
                {
                    errors.Add($"Task {task.task_id} ({task.name}) has circular reference to itself");
                }

                // Check if predecessors exist
                foreach (var predId in task.predecessors)
                {
                    bool predExists = templateTasks.Any(t => t.task_id == predId);
                    if (!predExists)
                    {
                        errors.Add($"Task {task.task_id} ({task.name}) references non-existent predecessor {predId}");
                    }
                }

                // Detect circular dependencies (simple check - Task A → Task B → Task A)
                foreach (var predId in task.predecessors)
                {
                    var predTask = templateTasks.FirstOrDefault(t => t.task_id == predId);
                    if (predTask != null && predTask.predecessors != null)
                    {
                        if (predTask.predecessors.Contains(task.task_id))
                        {
                            errors.Add($"Circular dependency detected: {task.task_id} ↔ {predId}");
                        }
                    }
                }
            }

            return errors;
        }

        /// <summary>
        /// Generate dependency graph visualization (text format)
        /// </summary>
        public string GenerateDependencyGraph(List<TemplateTask> templateTasks)
        {
            var graph = new System.Text.StringBuilder();
            graph.AppendLine("=== Task Dependency Graph ===");
            graph.AppendLine();

            foreach (var task in templateTasks)
            {
                graph.AppendLine($"{task.task_id}: {task.name}");

                if (task.predecessors != null && task.predecessors.Count > 0)
                {
                    graph.AppendLine($"  Predecessors: {string.Join(", ", task.predecessors)}");
                }

                if (task.can_run_parallel)
                {
                    graph.AppendLine($"  Execution: Parallel ({task.execution_group})");
                }
                else
                {
                    graph.AppendLine($"  Execution: Sequential ({task.execution_group})");
                }

                if (task.is_blocking)
                {
                    graph.AppendLine("  ⚠ CRITICAL PATH");
                }

                graph.AppendLine();
            }

            return graph.ToString();
        }

        /// <summary>
        /// Sort tasks in topological order (respecting dependencies)
        /// </summary>
        public List<TemplateTask> TopologicalSort(List<TemplateTask> templateTasks)
        {
            var sorted = new List<TemplateTask>();
            var visited = new HashSet<string>();
            var taskDict = templateTasks.ToDictionary(t => t.task_id);

            void Visit(TemplateTask task)
            {
                if (visited.Contains(task.task_id))
                    return;

                visited.Add(task.task_id);

                // Visit all predecessors first
                if (task.predecessors != null)
                {
                    foreach (var predId in task.predecessors)
                    {
                        if (taskDict.ContainsKey(predId))
                        {
                            Visit(taskDict[predId]);
                        }
                    }
                }

                sorted.Add(task);
            }

            foreach (var task in templateTasks)
            {
                Visit(task);
            }

            return sorted;
        }

        /// <summary>
        /// Find MS Project task by UniqueID
        /// </summary>
        private Task FindTaskByUID(Project project, int uniqueID)
        {
            foreach (Task task in project.Tasks)
            {
                if (task != null && task.UniqueID == uniqueID)
                    return task;
            }
            return null;
        }

        /// <summary>
        /// Color-code tasks by execution group in MS Project
        /// TODO: Implement color coding using correct MS Project Interop API
        /// PjColor enum and pjTaskGanttBarColor field need verification on Windows
        /// </summary>
        public void ApplyColorCodingByGroup(
            Application app,
            List<TemplateTask> templateTasks,
            Dictionary<string, int> taskMap)
        {
            // COMMENTED OUT: PjColor enum doesn't exist in MS Project Interop
            // Need to research correct API for setting Gantt bar colors
            //
            // Possible solutions:
            // 1. Use integer color constants instead of PjColor enum
            // 2. Use Task.TextStyles property
            // 3. Use direct COM interop with color integers
            //
            // For now, this method does nothing to avoid compilation errors

            System.Diagnostics.Debug.WriteLine("Color coding not yet implemented - need to verify MS Project API");

            /* ORIGINAL CODE (COMMENTED OUT DUE TO COMPILATION ERRORS):

            if (app.ActiveProject == null)
                return;

            var project = app.ActiveProject;
            var colorMap = new Dictionary<string, PjColor>
            {
                { "Parallel-Essential-Docs", PjColor.pjBlue },
                { "Parallel-Site-Prep", PjColor.pjAqua },
                { "Parallel-Training-Prep", PjColor.pjGreen },
                { "Parallel-Systems-Setup", PjColor.pjLime },
                { "Sequential-IRB-Prep", PjColor.pjYellow },
                { "Sequential-IRB-Review", PjColor.pjRed },
                { "Sequential-Training", PjColor.pjFuchsia },
                { "Sequential-Activation", PjColor.pjMaroon }
            };

            foreach (var templateTask in templateTasks)
            {
                if (!taskMap.ContainsKey(templateTask.task_id))
                    continue;

                int taskUID = taskMap[templateTask.task_id];
                var msTask = FindTaskByUID(project, taskUID);

                if (msTask == null)
                    continue;

                string execGroup = templateTask.execution_group ?? "Ungrouped";

                if (colorMap.ContainsKey(execGroup))
                {
                    try
                    {
                        msTask.SetField(PjField.pjTaskGanttBarColor, colorMap[execGroup]);
                    }
                    catch (System.Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Error setting color: {ex.Message}");
                    }
                }
            }
            */
        }

        /// <summary>
        /// Generate execution timeline summary
        /// </summary>
        public string GenerateExecutionTimeline(List<TemplateTask> templateTasks)
        {
            var timeline = new System.Text.StringBuilder();
            timeline.AppendLine("=== Execution Timeline ===");
            timeline.AppendLine();

            var groups = GroupTasksByExecutionGroup(templateTasks);
            int currentDay = 0;

            foreach (var groupName in groups.Keys.OrderBy(k => k))
            {
                var tasks = groups[groupName];
                if (tasks.Count == 0)
                    continue;

                bool isParallel = tasks.All(t => t.can_run_parallel);
                int groupDuration = isParallel ? tasks.Max(t => t.duration_days) : tasks.Sum(t => t.duration_days);

                timeline.AppendLine($"Days {currentDay}-{currentDay + groupDuration}: {groupName}");
                timeline.AppendLine($"  Type: {(isParallel ? "Parallel" : "Sequential")}");
                timeline.AppendLine($"  Tasks: {tasks.Count}");
                timeline.AppendLine($"  Duration: {groupDuration} days");
                timeline.AppendLine();

                currentDay += groupDuration;
            }

            timeline.AppendLine($"Total Estimated Duration: {currentDay} days");

            return timeline.ToString();
        }
    }
}
