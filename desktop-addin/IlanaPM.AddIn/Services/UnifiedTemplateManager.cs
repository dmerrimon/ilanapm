using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;
using IlanaPM.AddIn.Models;
using MSProject = Microsoft.Office.Interop.MSProject;
using Site = IlanaPM.AddIn.Models.Site;
using Exception = System.Exception;

namespace IlanaPM.AddIn.Services
{
    /// <summary>
    /// Unified Template Manager - consolidates TemplateLoader and SitePhaseManager
    /// Handles all template types: Full Study, Site Startup, Site Closeout, Study Closeout
    /// </summary>
    public class UnifiedTemplateManager
    {
        private ApiClient apiClient;
        private CustomFieldManager fieldManager;

        /// <summary>
        /// Progress callback for reporting generation status
        /// Parameters: (statusMessage, detailMessage)
        /// </summary>
        public Action<string, string> ProgressCallback { get; set; }

        public UnifiedTemplateManager()
        {
            apiClient = new ApiClient();
            fieldManager = new CustomFieldManager();
        }

        /// <summary>
        /// Report progress to callback if available
        /// </summary>
        private void ReportProgress(string status, string detail = "")
        {
            ProgressCallback?.Invoke(status, detail);
        }

        /// <summary>
        /// Load template based on type and configuration
        /// </summary>
        public async System.Threading.Tasks.Task<TemplateResult> LoadTemplateAsync(
            TemplateConfiguration config,
            FilterOptions filters = null)
        {
            switch (config.TemplateType)
            {
                case TemplateType.FullStudyTimeline:
                    return await LoadFullStudyTimelineAsync(config, filters);

                case TemplateType.SiteStartup:
                    return await LoadSiteStartupTemplateAsync(config, filters);

                case TemplateType.SiteImplementation:
                    return LoadSiteImplementationTemplate(config, filters);

                case TemplateType.SiteCloseout:
                    return await LoadSiteCloseoutTemplateAsync(config, filters);

                case TemplateType.StudyCloseout:
                    return await LoadStudyCloseoutTemplateAsync(config, filters);

                case TemplateType.AmendmentWorkflow:
                    throw new NotImplementedException("Amendment workflow templates will be available in Phase 2");

                default:
                    throw new ArgumentException($"Unknown template type: {config.TemplateType}");
            }
        }

        /// <summary>
        /// Load full study timeline from API
        /// </summary>
        private async System.Threading.Tasks.Task<TemplateResult> LoadFullStudyTimelineAsync(
            TemplateConfiguration config,
            FilterOptions filters)
        {
            // Call API to generate template
            var request = new TemplateRequest
            {
                country_code = config.CountryCode,
                study_phase = config.StudyPhase,
                therapeutic_area = config.TherapeuticArea,
                include_optional = filters?.IncludeOptional ?? true
            };

            Models.Timeline timeline = await apiClient.GenerateTemplateAsync(request);

            // Note: API templates come pre-filtered from backend based on include_optional
            // Additional filtering not implemented for API templates yet
            int originalTaskCount = timeline.tasks.Count;

            return new TemplateResult
            {
                TemplateType = TemplateType.FullStudyTimeline,
                Timeline = timeline,
                TaskCount = timeline.tasks.Count,
                EstimatedDuration = CalculateEstimatedDurationFromApiTasks(timeline.tasks),
                CountryCode = config.CountryCode,
                TemplateSource = "API",
                PhaseType = "Full Study",
                FiltersApplied = filters != null,
                TaskCountBeforeFiltering = null
            };
        }

        /// <summary>
        /// Load site startup template from CountryTemplateLibrary
        /// </summary>
        /// <summary>
        /// Load site startup template from API with authority-specific details
        /// </summary>
        private async System.Threading.Tasks.Task<TemplateResult> LoadSiteStartupTemplateAsync(
            TemplateConfiguration config,
            FilterOptions filters)
        {
            ReportProgress("Generating Site Startup Template", $"Requesting template for {config.CountryCode}...");

            // Call API to generate authority-rich site startup template
            var request = new SiteTemplateRequest
            {
                country_code = config.CountryCode,
                template_type = "site_startup",
                site_id = config.SiteId ?? "SITE-001",
                study_phase = config.StudyPhase,
                therapeutic_area = config.TherapeuticArea,
                include_optional = filters?.IncludeOptional ?? true
            };

            Models.Timeline timeline = await apiClient.GenerateSiteStartupTemplateAsync(request);

            ReportProgress("Template Generated", $"Received {timeline.tasks.Count} tasks from API");

            int originalTaskCount = timeline.tasks.Count;

            return new TemplateResult
            {
                TemplateType = TemplateType.SiteStartup,
                Timeline = timeline,
                TaskCount = timeline.tasks.Count,
                EstimatedDuration = CalculateEstimatedDurationFromApiTasks(timeline.tasks),
                SiteId = config.SiteId,
                CountryCode = config.CountryCode,
                TemplateSource = $"API-{config.CountryCode}",
                PhaseType = "Site Activation",
                FiltersApplied = filters != null,
                TaskCountBeforeFiltering = filters != null ? originalTaskCount : (int?)null
            };
        }

        /// <summary>
        /// Load site implementation template from CountryTemplateLibrary
        /// </summary>
        private TemplateResult LoadSiteImplementationTemplate(
            TemplateConfiguration config,
            FilterOptions filters)
        {
            // Get country info
            var countryInfo = CountryRegulatoryInfo.GetCountryInfo(config.CountryCode);

            // Load template based on country
            SitePhaseTaskSet taskSet;
            if (config.CountryCode.ToUpper() == "USA")
            {
                taskSet = CountryTemplateLibrary.GetUSA_Implementation();
            }
            else
            {
                taskSet = CountryTemplateLibrary.GetInternational_Implementation(countryInfo);
            }

            // Apply filters if provided (before conversion)
            int originalTaskCount = taskSet.tasks.Count;
            if (filters != null)
            {
                taskSet.tasks = taskSet.tasks
                    .Where(t => filters.PassesFilter(t))
                    .ToList();
            }

            // Convert to Timeline
            var timeline = ConvertTaskSetToTimeline(taskSet, config.SiteId);

            return new TemplateResult
            {
                TemplateType = TemplateType.SiteImplementation,
                Timeline = timeline,
                TaskCount = timeline.tasks.Count,
                EstimatedDuration = CalculateEstimatedDuration(taskSet.tasks),
                SiteId = config.SiteId,
                CountryCode = config.CountryCode,
                TemplateSource = config.CountryCode.ToUpper() == "USA" ? "Library-USA" : $"Library-{config.CountryCode}",
                PhaseType = "Implementation",
                FiltersApplied = filters != null,
                TaskCountBeforeFiltering = filters != null ? originalTaskCount : (int?)null
            };
        }

        /// <summary>
        /// Load site closeout template from API with authority-specific details
        /// </summary>
        private async System.Threading.Tasks.Task<TemplateResult> LoadSiteCloseoutTemplateAsync(
            TemplateConfiguration config,
            FilterOptions filters)
        {
            ReportProgress("Generating Site Closeout Template", $"Requesting template for {config.CountryCode}...");

            // Call API to generate authority-rich site closeout template
            var request = new SiteTemplateRequest
            {
                country_code = config.CountryCode,
                template_type = "site_closeout",
                site_id = config.SiteId ?? "SITE-001",
                study_phase = config.StudyPhase,
                therapeutic_area = config.TherapeuticArea,
                include_optional = filters?.IncludeOptional ?? true
            };

            Models.Timeline timeline = await apiClient.GenerateSiteCloseoutTemplateAsync(request);

            ReportProgress("Template Generated", $"Received {timeline.tasks.Count} tasks from API");

            int originalTaskCount = timeline.tasks.Count;

            return new TemplateResult
            {
                TemplateType = TemplateType.SiteCloseout,
                Timeline = timeline,
                TaskCount = timeline.tasks.Count,
                EstimatedDuration = CalculateEstimatedDurationFromApiTasks(timeline.tasks),
                SiteId = config.SiteId,
                CountryCode = config.CountryCode,
                TemplateSource = $"API-{config.CountryCode}",
                PhaseType = "Site Closeout",
                FiltersApplied = filters != null,
                TaskCountBeforeFiltering = filters != null ? originalTaskCount : (int?)null
            };
        }

        /// <summary>
        /// Load study closeout template from API (study-level, no site)
        /// </summary>
        private async System.Threading.Tasks.Task<TemplateResult> LoadStudyCloseoutTemplateAsync(
            TemplateConfiguration config,
            FilterOptions filters)
        {
            ReportProgress("Generating Study Closeout Template", "Requesting study-level closeout tasks...");

            // Call API to generate study closeout template
            var request = new SiteTemplateRequest
            {
                country_code = config.CountryCode ?? "US",  // Default to US if no country specified
                template_type = "study_closeout",
                site_id = "STUDY-LEVEL",  // Study-level (not site-specific)
                study_phase = config.StudyPhase,
                therapeutic_area = config.TherapeuticArea,
                include_optional = filters?.IncludeOptional ?? true
            };

            Models.Timeline timeline = await apiClient.GenerateStudyCloseoutTemplateAsync(request);

            ReportProgress("Template Generated", $"Received {timeline.tasks.Count} study-level closeout tasks");

            int originalTaskCount = timeline.tasks.Count;

            return new TemplateResult
            {
                TemplateType = TemplateType.StudyCloseout,
                Timeline = timeline,
                TaskCount = timeline.tasks.Count,
                EstimatedDuration = CalculateEstimatedDurationFromApiTasks(timeline.tasks),
                SiteId = null,  // Study-level, no site
                CountryCode = config.CountryCode,
                TemplateSource = $"API-Study",
                PhaseType = "Study Closeout",
                FiltersApplied = filters != null,
                TaskCountBeforeFiltering = filters != null ? originalTaskCount : (int?)null
            };
        }

        /// <summary>
        /// Load template from database template library (new database-backed templates)
        /// Uses GET /api/v1/templates/library/{templateId} to retrieve template with all tasks and dependencies
        /// </summary>
        /// <param name="templateId">Template ID (e.g., "TPL_001" for Study Start-Up)</param>
        /// <param name="config">Template configuration with study metadata</param>
        /// <param name="filters">Optional filters (currently not applied to database templates)</param>
        /// <returns>Template result ready to apply to MS Project</returns>
        public async System.Threading.Tasks.Task<TemplateResult> LoadFromDatabaseTemplateAsync(
            string templateId,
            TemplateConfiguration config,
            FilterOptions filters = null)
        {
            ReportProgress($"Loading Template {templateId}", $"Fetching template from database...");

            // Get template details from API
            Models.TemplateDetailResponse templateDetail = await apiClient.GetTemplateAsync(templateId);

            ReportProgress("Template Retrieved", $"Received {templateDetail.tasks.Count} tasks from {templateDetail.template.template_name}");

            // Convert TemplateDetailResponse to Timeline format (for compatibility with existing code)
            var timeline = new Models.Timeline
            {
                study_name = templateDetail.template.template_name,  // Use template name instead
                phase = config.StudyPhase,
                therapeutic_area = config.TherapeuticArea,
                tasks = new List<Models.Task>(),
                dependencies = new List<Models.Dependency>()
            };

            // Convert template tasks to Timeline tasks
            foreach (var templateTask in templateDetail.tasks)
            {
                // Sanitize task name - MS Project doesn't support newlines in task names
                string sanitizedName = SanitizeTaskName(templateTask.task_name);

                var task = new Models.Task
                {
                    id = templateTask.task_id,
                    name = sanitizedName,
                    duration_days = templateTask.typical_duration_days,
                    category = templateTask.category,
                    phase = templateDetail.template.template_type,
                    is_mandatory = true,  // All database tasks are considered mandatory
                    is_summary = templateTask.outline_level == 1,
                    outline_level = templateTask.outline_level
                };

                timeline.tasks.Add(task);
            }

            // Convert template dependencies to Timeline dependencies
            foreach (var templateDep in templateDetail.dependencies)
            {
                var dependency = new Models.Dependency
                {
                    predecessor_id = templateDep.predecessor_task_id,
                    successor_id = templateDep.successor_task_id,
                    type = templateDep.dependency_type,
                    lag_days = templateDep.lag_days
                };

                timeline.dependencies.Add(dependency);
            }

            ReportProgress("Template Converted", $"Converted {timeline.tasks.Count} tasks and {timeline.dependencies.Count} dependencies");

            // Determine template type based on template_type field
            TemplateType resultType = TemplateType.FullStudyTimeline;  // Default
            string phaseType = "Unknown";

            switch (templateDetail.template.template_type)
            {
                case "study_startup":
                    resultType = TemplateType.FullStudyTimeline;
                    phaseType = "Study Start-Up";
                    break;
                case "implementation":
                    resultType = TemplateType.SiteImplementation;
                    phaseType = "Study Implementation";
                    break;
                case "closeout":
                    resultType = TemplateType.StudyCloseout;
                    phaseType = "Study Closeout";
                    break;
                case "site_activation":
                    resultType = TemplateType.SiteStartup;
                    phaseType = "Site Activation";
                    break;
                case "site_closeout":
                    resultType = TemplateType.SiteCloseout;
                    phaseType = "Site Closeout";
                    break;
                case "full_study":
                    resultType = TemplateType.FullStudyTimeline;
                    phaseType = "Full Study Timeline";
                    break;
            }

            return new TemplateResult
            {
                TemplateType = resultType,
                Timeline = timeline,
                TaskCount = timeline.tasks.Count,
                EstimatedDuration = templateDetail.template.estimated_duration_days,
                SiteId = config.SiteId,  // May be null for study-level templates
                CountryCode = config.CountryCode,
                TemplateSource = $"DB-{templateId}",
                PhaseType = phaseType,
                FiltersApplied = false,  // Database templates not filtered yet
                TaskCountBeforeFiltering = null
            };
        }

        /// <summary>
        /// Apply template result to MS Project
        /// Sets custom fields Text11-14 for filtering
        /// </summary>
        public void ApplyToProject(
            MSProject.Application app,
            TemplateResult result,
            Dictionary<string, string> customColumnNames = null)
        {
            if (app.ActiveProject == null)
            {
                throw new InvalidOperationException("No active project");
            }

            Project project = app.ActiveProject;

            // Load timeline into project
            var templateLoader = new TemplateLoader();
            templateLoader.LoadTemplateIntoProject(result.Timeline, app);

            // Set custom fields (Text11-14) for filtering
            try
            {
                foreach (Microsoft.Office.Interop.MSProject.Task task in project.Tasks)
                {
                    if (task == null) continue;

                    // Find matching API task by name
                    var apiTask = result.Timeline.tasks.FirstOrDefault(t => t.name == task.Name);
                    if (apiTask == null) continue;

                    // Determine subphase from category/phase
                    string subphase = apiTask.category ?? "Unspecified";

                    try
                    {
                        // Set filtering fields
                        fieldManager.SetFilteringFields(
                            task,
                            site: result.SiteId,
                            phaseType: result.PhaseType,
                            subphase: subphase,
                            templateSource: result.TemplateSource
                        );

                        // If site-specific, also set clinical entity fields
                        if (!string.IsNullOrEmpty(result.SiteId))
                        {
                            fieldManager.SetClinicalEntityFields(
                                task,
                                siteIds: result.SiteId,
                                isSiteSpecific: true
                            );
                        }
                    }
                    catch (System.Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Warning: Could not set custom fields for task '{task.Name}': {ex.Message}");
                    }
                }
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Warning: Could not set custom fields: {ex.Message}");
            }

            // Configure the MS Project view to show the custom columns
            // DISABLED: MS Project COM API for column insertion is version-dependent and unreliable
            // Custom fields ARE set on all tasks - users can insert columns manually
            // ConfigureProjectColumns(app);

            System.Diagnostics.Debug.WriteLine($"Applied {result.TaskCount} tasks to project with filtering fields and configured columns");
        }

        /// <summary>
        /// Configure MS Project view to display custom columns
        /// DISABLED: MS Project COM API for column insertion is version-dependent
        /// Different MS Project versions have incompatible ColumnInsert signatures
        /// Custom fields ARE populated on all tasks - users can insert columns manually
        /// TODO Phase 2: Research version-specific API or use VSTO controls
        /// </summary>
        private void ConfigureProjectColumns(MSProject.Application app)
        {
            // This feature is disabled due to MS Project API version incompatibility
            // The custom fields (Text11, Text12, Text4, etc.) ARE populated on all tasks
            // Users can manually insert columns: Right-click header > Insert Column > Text11
            System.Diagnostics.Debug.WriteLine("ConfigureProjectColumns disabled - manual column insertion required");
        }

        /// <summary>
        /// Convert TemplateTask to API Task model
        /// </summary>
        private Models.Task ConvertTemplateTaskToTask(TemplateTask templateTask)
        {
            return new Models.Task
            {
                id = templateTask.task_id,
                name = templateTask.name,
                duration_days = templateTask.duration_days,
                category = templateTask.category,
                is_mandatory = templateTask.is_mandatory,
                phase = templateTask.phase_type
            };
        }

        /// <summary>
        /// Convert SitePhaseTaskSet to Timeline for consistency with API templates
        /// </summary>
        private Models.Timeline ConvertTaskSetToTimeline(SitePhaseTaskSet taskSet, string siteId)
        {
            var timeline = new Models.Timeline
            {
                study_name = taskSet.phase_name,
                phase = taskSet.phase_type,
                authority = taskSet.regulatory_authority,
                tasks = new List<Models.Task>(),
                dependencies = new List<Dependency>()
            };

            // Convert TemplateTask to API Task
            foreach (var templateTask in taskSet.tasks)
            {
                timeline.tasks.Add(ConvertTemplateTaskToTask(templateTask));
            }

            return timeline;
        }

        /// <summary>
        /// Determine subphase from template task properties
        /// Returns subphase if available, otherwise maps execution group
        /// </summary>
        private string DetermineSubphase(TemplateTask task)
        {
            // If subphase is already set (Phase 1 update), use it
            if (!string.IsNullOrEmpty(task.subphase))
            {
                return task.subphase;
            }

            // Otherwise map from execution_group
            if (string.IsNullOrEmpty(task.execution_group))
            {
                return task.category ?? "Unspecified";
            }

            // Map execution groups to subphases
            string execGroup = task.execution_group.ToLower();

            if (execGroup.Contains("essential") || execGroup.Contains("docs"))
                return "Essential Documents";
            if (execGroup.Contains("irb") || execGroup.Contains("ethics"))
                return "IRB Submission";
            if (execGroup.Contains("training"))
                return "Training";
            if (execGroup.Contains("activation") || execGroup.Contains("startup"))
                return "Activation";
            if (execGroup.Contains("patient") || execGroup.Contains("enrollment"))
                return "Patient Closeout";
            if (execGroup.Contains("archiv"))
                return "Archival";
            if (execGroup.Contains("closeout") || execGroup.Contains("closure"))
                return "Closure";

            // Default to category
            return task.category ?? "Unspecified";
        }

        /// <summary>
        /// Sanitize task name for MS Project compatibility
        /// MS Project doesn't support newlines in task names
        /// </summary>
        private string SanitizeTaskName(string taskName)
        {
            if (string.IsNullOrEmpty(taskName))
                return taskName;

            // Replace newlines with spaces
            string sanitized = taskName
                .Replace("\r\n", " ")
                .Replace("\n", " ")
                .Replace("\r", " ")
                .Trim();

            // Remove multiple consecutive spaces
            while (sanitized.Contains("  "))
            {
                sanitized = sanitized.Replace("  ", " ");
            }

            return sanitized;
        }

        /// <summary>
        /// Calculate estimated duration from template tasks (library)
        /// </summary>
        private int CalculateEstimatedDuration(List<TemplateTask> tasks)
        {
            if (tasks == null || tasks.Count == 0) return 0;

            // Simple calculation: max of (task duration + predecessor durations)
            // More accurate: use critical path calculation
            return tasks.Max(t => t.duration_days);
        }

        /// <summary>
        /// Calculate estimated duration from API tasks
        /// </summary>
        private int CalculateEstimatedDurationFromApiTasks(List<Models.Task> tasks)
        {
            if (tasks == null || tasks.Count == 0) return 0;

            // Simple calculation: sum all task durations
            // More accurate would use critical path from dependencies
            return tasks.Sum(t => t.duration_days);
        }

        /// <summary>
        /// Preview tasks before generation (for Step 3 of wizard)
        /// Loads tasks directly from library without Timeline conversion for efficiency
        /// </summary>
        public List<TemplateTask> PreviewTasks(
            TemplateConfiguration config,
            FilterOptions filters = null)
        {
            SitePhaseTaskSet taskSet = null;

            switch (config.TemplateType)
            {
                case TemplateType.SiteStartup:
                    // Load directly from library
                    var countryInfoStartup = CountryRegulatoryInfo.GetCountryInfo(config.CountryCode);
                    if (config.CountryCode.ToUpper() == "USA")
                    {
                        taskSet = CountryTemplateLibrary.GetUSA_SiteStartup();
                    }
                    else
                    {
                        taskSet = CountryTemplateLibrary.GetInternational_SiteStartup(countryInfoStartup);
                    }
                    break;

                case TemplateType.SiteImplementation:
                    // Load directly from library
                    var countryInfoImplementation = CountryRegulatoryInfo.GetCountryInfo(config.CountryCode);
                    if (config.CountryCode.ToUpper() == "USA")
                    {
                        taskSet = CountryTemplateLibrary.GetUSA_Implementation();
                    }
                    else
                    {
                        taskSet = CountryTemplateLibrary.GetInternational_Implementation(countryInfoImplementation);
                    }
                    break;

                case TemplateType.SiteCloseout:
                    // Load directly from library
                    var countryInfoCloseout = CountryRegulatoryInfo.GetCountryInfo(config.CountryCode);
                    if (config.CountryCode.ToUpper() == "USA")
                    {
                        taskSet = CountryTemplateLibrary.GetUSA_SiteCloseout();
                    }
                    else
                    {
                        taskSet = CountryTemplateLibrary.GetInternational_SiteCloseout(countryInfoCloseout);
                    }
                    break;

                case TemplateType.StudyCloseout:
                    taskSet = CountryTemplateLibrary.GetStudyCloseout();
                    break;

                case TemplateType.FullStudyTimeline:
                    // API calls need async - return empty for now, wizard will handle differently
                    return new List<TemplateTask>();

                default:
                    return new List<TemplateTask>();
            }

            // Return tasks (with filters applied if provided)
            if (taskSet != null && taskSet.tasks != null)
            {
                if (filters != null)
                {
                    return taskSet.tasks.Where(t => filters.PassesFilter(t)).ToList();
                }
                return taskSet.tasks;
            }

            return new List<TemplateTask>();
        }

        /// <summary>
        /// Generate all selected templates based on ClinicalProjectConfiguration (unified wizard)
        /// This is the main entry point from ClinicalProjectManagerForm
        /// </summary>
        public async System.Threading.Tasks.Task<int> GenerateTemplates(MSProject.Application app, ClinicalProjectConfiguration config)
        {
            if (app == null || config == null)
                throw new ArgumentNullException("Application and configuration are required");

            System.Diagnostics.Debug.WriteLine("=== GenerateTemplates (PUBLIC) START ===");
            System.Diagnostics.Debug.WriteLine($"Config.Sites count: {config.Sites?.Count ?? 0}");
            if (config.Sites != null)
            {
                foreach (var site in config.Sites)
                {
                    System.Diagnostics.Debug.WriteLine($"  Site: {site.SiteId} | Name: '{site.SiteName}' | Country: {site.CountryCode}");
                }
            }
            int totalTasksCreated = 0;

            try
            {
                var project = app.ActiveProject;
                if (project == null)
                    throw new InvalidOperationException("No active project");

                // DATABASE TEMPLATES
                if (config.Templates.GenerateDatabaseStudyStartup)
                {
                    System.Diagnostics.Debug.WriteLine(">>> Generating Database Study Start-Up (TPL_001)");
                    totalTasksCreated += await GenerateFromDatabaseTemplate(app, config, "TPL_001", null);
                }

                if (config.Templates.GenerateDatabaseStudyImplementation)
                {
                    System.Diagnostics.Debug.WriteLine(">>> Generating Database Study Implementation (TPL_002)");
                    totalTasksCreated += await GenerateFromDatabaseTemplate(app, config, "TPL_002", null);
                }

                if (config.Templates.GenerateDatabaseStudyCloseout)
                {
                    System.Diagnostics.Debug.WriteLine(">>> Generating Database Study Closeout (TPL_003)");
                    totalTasksCreated += await GenerateFromDatabaseTemplate(app, config, "TPL_003", null);
                }

                if (config.Templates.GenerateDatabaseSiteActivation && config.Templates.SitesForDatabaseActivation.Count > 0)
                {
                    System.Diagnostics.Debug.WriteLine($">>> Generating Database Site Activation (TPL_004) for {config.Templates.SitesForDatabaseActivation.Count} sites");
                    foreach (string siteId in config.Templates.SitesForDatabaseActivation)
                    {
                        totalTasksCreated += await GenerateFromDatabaseTemplate(app, config, "TPL_004", siteId);
                    }
                }

                if (config.Templates.GenerateDatabaseSiteCloseout && config.Templates.SitesForDatabaseCloseout.Count > 0)
                {
                    System.Diagnostics.Debug.WriteLine($">>> Generating Database Site Closeout (TPL_005) for {config.Templates.SitesForDatabaseCloseout.Count} sites");
                    foreach (string siteId in config.Templates.SitesForDatabaseCloseout)
                    {
                        totalTasksCreated += await GenerateFromDatabaseTemplate(app, config, "TPL_005", siteId);
                    }
                }

                // Generate cohort milestone tasks if cohorts are defined
                if (config.Cohorts != null && config.Cohorts.Count > 0)
                {
                    totalTasksCreated += GenerateCohortMilestones(app, config);
                }

                // Apply custom column configuration once after all tasks generated
                // DISABLED: See comment above - column insertion API is unreliable
                // ConfigureProjectColumns(app);

                return totalTasksCreated;
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error in GenerateTemplates: {ex.Message}");
                throw new InvalidOperationException($"Failed to generate templates: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Generate tasks from database template and apply to MS Project
        /// Helper method that loads template from database and creates tasks in MS Project
        /// </summary>
        /// <param name="app">MS Project application</param>
        /// <param name="config">Clinical project configuration</param>
        /// <param name="templateId">Template ID (e.g., "TPL_001")</param>
        /// <param name="siteId">Optional site ID for site-specific templates</param>
        /// <returns>Number of tasks created</returns>
        private async System.Threading.Tasks.Task<int> GenerateFromDatabaseTemplate(
            MSProject.Application app,
            ClinicalProjectConfiguration config,
            string templateId,
            string siteId)
        {
            try
            {
                // Create template configuration
                var templateConfig = new TemplateConfiguration
                {
                    StudyPhase = config.StudyPhase,
                    TherapeuticArea = config.TherapeuticArea,
                    CountryCode = config.Countries.Count > 0 ? config.Countries[0] : "US",
                    SiteId = siteId
                };

                // Load template from database
                var result = await LoadFromDatabaseTemplateAsync(templateId, templateConfig, null);

                // Apply template to MS Project
                ApplyToProject(app, result);

                System.Diagnostics.Debug.WriteLine($"✓ Applied {result.TaskCount} tasks from {templateId} to MS Project");

                return result.TaskCount;
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error generating from database template {templateId}: {ex.Message}");
                throw new InvalidOperationException($"Failed to generate template {templateId}: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Auto-generate cohort-specific participant milestone tasks with safety review meetings
        /// Creates per-cohort tracking tasks with dependencies to ensure sequential dose escalation
        /// </summary>
        private int GenerateCohortMilestoneTasks(MSProject.Application app, ClinicalProjectConfiguration config)
        {
            int tasksCreated = 0;
            MSProject.Task previousCohortSafetyDecision = null;

            for (int i = 0; i < config.Cohorts.Count; i++)
            {
                var cohort = config.Cohorts[i];
                bool isFirstCohort = (i == 0);

                // First Participant Screened/Consented for this cohort
                var taskScreened = app.ActiveProject.Tasks.Add($"First Participant Screened/Consented ({cohort.name})");
                taskScreened.Duration = "1d";
                taskScreened.SetField(MSProject.PjField.pjTaskText11, ""); // No specific site - applies to all sites in cohort
                taskScreened.SetField(MSProject.PjField.pjTaskText4, "Enrollment");
                taskScreened.SetField(MSProject.PjField.pjTaskText12, "Implementation");
                taskScreened.SetField(MSProject.PjField.pjTaskText13, $"Cohort Milestones - {cohort.name}");
                taskScreened.SetField(MSProject.PjField.pjTaskText14, $"Auto-Generated-Cohort");
                taskScreened.Notes = $"First participant in {cohort.name} completes informed consent and screening.\nTarget enrollment: {cohort.enrollment_target} participants";
                taskScreened.Priority = (int)MSProject.PjPriority.pjPriorityHigh;

                // If not first cohort, this depends on previous cohort's safety approval
                if (!isFirstCohort && previousCohortSafetyDecision != null)
                {
                    taskScreened.Predecessors = previousCohortSafetyDecision.ID.ToString();
                }
                tasksCreated++;

                // First Participant Enrolled/Randomized for this cohort
                var taskEnrolled = app.ActiveProject.Tasks.Add($"First Participant Enrolled/Randomized ({cohort.name})");
                taskEnrolled.Duration = "1d";
                taskEnrolled.SetField(MSProject.PjField.pjTaskText11, "");
                taskEnrolled.SetField(MSProject.PjField.pjTaskText4, "Enrollment");
                taskEnrolled.SetField(MSProject.PjField.pjTaskText12, "Implementation");
                taskEnrolled.SetField(MSProject.PjField.pjTaskText13, $"Cohort Milestones - {cohort.name}");
                taskEnrolled.SetField(MSProject.PjField.pjTaskText14, $"Auto-Generated-Cohort");
                taskEnrolled.Notes = $"First participant in {cohort.name} meets eligibility criteria and is enrolled/randomized.\nTarget enrollment: {cohort.enrollment_target} participants";
                taskEnrolled.Priority = (int)MSProject.PjPriority.pjPriorityHigh;
                taskEnrolled.Predecessors = taskScreened.ID.ToString();
                tasksCreated++;

                // Expanded Dosing Complete for this cohort
                var taskExpanded = app.ActiveProject.Tasks.Add($"Expanded Dosing Complete ({cohort.name})");
                taskExpanded.Duration = "1d";
                taskExpanded.SetField(MSProject.PjField.pjTaskText11, "");
                taskExpanded.SetField(MSProject.PjField.pjTaskText4, "Enrollment");
                taskExpanded.SetField(MSProject.PjField.pjTaskText12, "Implementation");
                taskExpanded.SetField(MSProject.PjField.pjTaskText13, $"Cohort Milestones - {cohort.name}");
                taskExpanded.SetField(MSProject.PjField.pjTaskText14, $"Auto-Generated-Cohort");
                taskExpanded.Notes = $"All participants in {cohort.name} have completed dosing phase.\nTarget enrollment: {cohort.enrollment_target} participants";
                taskExpanded.Priority = (int)MSProject.PjPriority.pjPriorityHigh;
                taskExpanded.Predecessors = taskEnrolled.ID.ToString();
                tasksCreated++;

                // Safety Review Meeting - held after cohort completes dosing
                var taskSafetyReview = app.ActiveProject.Tasks.Add($"Safety Review Meeting - {cohort.name}");
                taskSafetyReview.Duration = "3d"; // Typically 2-3 days for data compilation and meeting
                taskSafetyReview.SetField(MSProject.PjField.pjTaskText11, "");
                taskSafetyReview.SetField(MSProject.PjField.pjTaskText4, "Safety Review");
                taskSafetyReview.SetField(MSProject.PjField.pjTaskText12, "Implementation");
                taskSafetyReview.SetField(MSProject.PjField.pjTaskText13, $"Cohort Safety Reviews - {cohort.name}");
                taskSafetyReview.SetField(MSProject.PjField.pjTaskText14, $"Auto-Generated-Cohort");
                taskSafetyReview.Notes = $"Safety review meeting for {cohort.name} to evaluate safety data before dose escalation.\n" +
                    $"Target enrollment: {cohort.enrollment_target} participants\n\n" +
                    $"Meeting typically includes:\n" +
                    $"- Review of adverse events\n" +
                    $"- Assessment of dose-limiting toxicities (DLTs)\n" +
                    $"- Evaluation of pharmacokinetic data\n" +
                    $"- Decision on dose escalation safety";
                taskSafetyReview.Priority = (int)MSProject.PjPriority.pjPriorityHigh;
                taskSafetyReview.Predecessors = taskExpanded.ID.ToString();
                tasksCreated++;

                // Safety Committee Decision - approval to proceed or modify
                var taskSafetyDecision = app.ActiveProject.Tasks.Add($"Safety Committee Decision - {cohort.name}");
                taskSafetyDecision.Duration = "1d";
                taskSafetyDecision.SetField(MSProject.PjField.pjTaskText11, "");
                taskSafetyDecision.SetField(MSProject.PjField.pjTaskText4, "Safety Review");
                taskSafetyDecision.SetField(MSProject.PjField.pjTaskText12, "Implementation");
                taskSafetyDecision.SetField(MSProject.PjField.pjTaskText13, $"Cohort Safety Reviews - {cohort.name}");
                taskSafetyDecision.SetField(MSProject.PjField.pjTaskText14, $"Auto-Generated-Cohort");
                taskSafetyDecision.Notes = $"Formal safety committee decision for {cohort.name}.\n" +
                    $"Target enrollment: {cohort.enrollment_target} participants\n\n" +
                    $"Possible outcomes:\n" +
                    $"- Approve dose escalation to next cohort\n" +
                    $"- Modify dose for next cohort\n" +
                    $"- Expand current cohort\n" +
                    $"- Hold or terminate study";
                taskSafetyDecision.Priority = (int)MSProject.PjPriority.pjPriorityHigh;
                taskSafetyDecision.Predecessors = taskSafetyReview.ID.ToString();
                tasksCreated++;

                // Store this cohort's safety decision for next cohort's dependency
                previousCohortSafetyDecision = taskSafetyDecision;

                System.Diagnostics.Debug.WriteLine($"Generated 5 cohort milestone tasks with safety reviews for {cohort.name}");
            }

            return tasksCreated;
        }

        /// <summary>
        /// Generate Site Closeout templates for selected sites using API for authority-specific details
        /// </summary>


        /// <summary>
        /// Generate cohort milestone tasks for tracking enrollment phases
        /// Creates key milestones for each cohort: First Patient Dosed, Enrollment Complete, Safety Review
        /// </summary>
        private int GenerateCohortMilestones(MSProject.Application app, ClinicalProjectConfiguration config)
        {
            int tasksCreated = 0;

            try
            {
                ReportProgress("Generating cohort milestones", $"Creating milestones for {config.Cohorts.Count} cohorts");

                MSProject.Task previousCohortSafetyReview = null;

                foreach (var cohort in config.Cohorts.OrderBy(c => c.id))
                {
                    System.Diagnostics.Debug.WriteLine($"Creating milestones for cohort: {cohort.id} ({cohort.name})");

                    // Milestone 1: First Patient Dosed
                    var firstPatientTask = app.ActiveProject.Tasks.Add($"{cohort.name} - First Patient Dosed");
                    firstPatientTask.Duration = "0d"; // Milestone (zero duration)
                    firstPatientTask.Milestone = true;
                    firstPatientTask.SetField(MSProject.PjField.pjTaskText7, ""); // Site IDs (empty - cohort is multi-site)
                    firstPatientTask.SetField(MSProject.PjField.pjTaskText9, cohort.id); // Cohort IDs (visible column)
                    System.Diagnostics.Debug.WriteLine($"  Set Text9 (Cohort IDs) = {cohort.id} on task: {firstPatientTask.Name}");
                    firstPatientTask.SetField(MSProject.PjField.pjTaskText11, ""); // Site Name (empty - cohort is multi-site)
                    firstPatientTask.SetField(MSProject.PjField.pjTaskText4, "Enrollment");
                    firstPatientTask.SetField(MSProject.PjField.pjTaskText12, "Patient Enrollment");
                    firstPatientTask.SetField(MSProject.PjField.pjTaskText13, "First Patient");
                    firstPatientTask.SetField(MSProject.PjField.pjTaskText14, "Cohort Milestone");
                    firstPatientTask.SetField(MSProject.PjField.pjTaskText15, cohort.id); // Cohort ID (internal reference)
                    firstPatientTask.Notes = $"First patient dosed in {cohort.name}. Target enrollment: {cohort.enrollment_target} patients.";
                    firstPatientTask.Priority = (int)MSProject.PjPriority.pjPriorityHigh;

                    // Create dependency on previous cohort's safety review (if exists)
                    if (previousCohortSafetyReview != null)
                    {
                        firstPatientTask.Predecessors = previousCohortSafetyReview.ID.ToString();
                    }

                    tasksCreated++;

                    // Milestone 2: Enrollment Complete
                    var enrollmentCompleteTask = app.ActiveProject.Tasks.Add($"{cohort.name} - Enrollment Complete");
                    enrollmentCompleteTask.Duration = $"{cohort.enrollment_target * 7}d"; // Estimate: 7 days per patient
                    enrollmentCompleteTask.SetField(MSProject.PjField.pjTaskText7, ""); // Site IDs (empty)
                    enrollmentCompleteTask.SetField(MSProject.PjField.pjTaskText9, cohort.id); // Cohort IDs (visible column)
                    enrollmentCompleteTask.SetField(MSProject.PjField.pjTaskText11, ""); // Site Name (empty)
                    enrollmentCompleteTask.SetField(MSProject.PjField.pjTaskText4, "Enrollment");
                    enrollmentCompleteTask.SetField(MSProject.PjField.pjTaskText12, "Patient Enrollment");
                    enrollmentCompleteTask.SetField(MSProject.PjField.pjTaskText13, "Enrollment Complete");
                    enrollmentCompleteTask.SetField(MSProject.PjField.pjTaskText14, "Cohort Milestone");
                    enrollmentCompleteTask.SetField(MSProject.PjField.pjTaskText15, cohort.id); // Cohort ID (internal reference)
                    enrollmentCompleteTask.Notes = $"All {cohort.enrollment_target} patients enrolled in {cohort.name}.";
                    enrollmentCompleteTask.Priority = (int)MSProject.PjPriority.pjPriorityHigh;

                    // Enrollment complete depends on first patient dosed
                    enrollmentCompleteTask.Predecessors = firstPatientTask.ID.ToString();

                    tasksCreated++;

                    // Milestone 3: Safety Review Complete
                    var safetyReviewTask = app.ActiveProject.Tasks.Add($"{cohort.name} - Safety Review Complete");
                    safetyReviewTask.Duration = "14d"; // Typical safety review period
                    safetyReviewTask.SetField(MSProject.PjField.pjTaskText7, ""); // Site IDs (empty)
                    safetyReviewTask.SetField(MSProject.PjField.pjTaskText9, cohort.id); // Cohort IDs (visible column)
                    safetyReviewTask.SetField(MSProject.PjField.pjTaskText11, ""); // Site Name (empty)
                    safetyReviewTask.SetField(MSProject.PjField.pjTaskText4, "Safety");
                    safetyReviewTask.SetField(MSProject.PjField.pjTaskText12, "Safety Review");
                    safetyReviewTask.SetField(MSProject.PjField.pjTaskText13, "DSMB Review");
                    safetyReviewTask.SetField(MSProject.PjField.pjTaskText14, "Cohort Milestone");
                    safetyReviewTask.SetField(MSProject.PjField.pjTaskText15, cohort.id); // Cohort ID (internal reference)
                    safetyReviewTask.Notes = $"Data Safety Monitoring Board (DSMB) review for {cohort.name}. Required before next cohort can begin.";
                    safetyReviewTask.Priority = (int)MSProject.PjPriority.pjPriorityHigh;

                    // Safety review depends on enrollment complete
                    safetyReviewTask.Predecessors = enrollmentCompleteTask.ID.ToString();

                    // Store for next cohort's dependency
                    previousCohortSafetyReview = safetyReviewTask;

                    tasksCreated++;
                }

                System.Diagnostics.Debug.WriteLine($"Created {tasksCreated} cohort milestone tasks");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error generating cohort milestones: {ex.Message}");
                // Don't throw - cohort milestones are optional
            }

            return tasksCreated;
        }
    }
}
