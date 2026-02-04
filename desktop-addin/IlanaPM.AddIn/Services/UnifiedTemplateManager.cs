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
            foreach (Microsoft.Office.Interop.MSProject.Task task in project.Tasks)
            {
                if (task == null) continue;

                // Find matching API task by name
                var apiTask = result.Timeline.tasks.FirstOrDefault(t => t.name == task.Name);
                if (apiTask == null) continue;

                // Determine subphase from category/phase
                string subphase = apiTask.category ?? "Unspecified";

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
            System.Diagnostics.Debug.WriteLine($"Templates.GenerateSiteStartup: {config.Templates?.GenerateSiteStartup}");
            System.Diagnostics.Debug.WriteLine($"Templates.SitesForStartup count: {config.Templates?.SitesForStartup?.Count ?? 0}");
            if (config.Templates?.SitesForStartup != null)
            {
                foreach (var siteId in config.Templates.SitesForStartup)
                {
                    System.Diagnostics.Debug.WriteLine($"  SitesForStartup includes: '{siteId}'");
                }
            }

            int totalTasksCreated = 0;

            try
            {
                var project = app.ActiveProject;
                if (project == null)
                    throw new InvalidOperationException("No active project");

                // Generate each selected template type
                if (config.Templates.GenerateFullStudyTimeline)
                {
                    totalTasksCreated += GenerateFullStudyTimeline(app, config);
                }

                if (config.Templates.GenerateSiteStartup && config.Templates.SitesForStartup.Count > 0)
                {
                    System.Diagnostics.Debug.WriteLine($">>> Calling GenerateSiteStartup with {config.Templates.SitesForStartup.Count} sites");
                    totalTasksCreated += await GenerateSiteStartup(app, config);
                }

                if (config.Templates.GenerateSiteImplementation && config.Templates.SitesForImplementation.Count > 0)
                {
                    totalTasksCreated += GenerateSiteImplementation(app, config);
                }

                if (config.Templates.GenerateSiteCloseout && config.Templates.SitesForCloseout.Count > 0)
                {
                    totalTasksCreated += await GenerateSiteCloseout(app, config);
                }

                if (config.Templates.GenerateStudyCloseout)
                {
                    totalTasksCreated += GenerateStudyCloseout(app, config);
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
        /// Generate Full Study Timeline (API-based regulatory phases)
        /// </summary>
        private int GenerateFullStudyTimeline(MSProject.Application app, ClinicalProjectConfiguration config)
        {
            int tasksCreated = 0;

            System.Diagnostics.Debug.WriteLine("=== GenerateFullStudyTimeline START ===");
            System.Diagnostics.Debug.WriteLine($"Config.Sites count: {config.Sites?.Count ?? 0}");
            if (config.Sites != null && config.Sites.Count > 0)
            {
                foreach (var site in config.Sites)
                {
                    System.Diagnostics.Debug.WriteLine($"  Site available: {site.SiteId} | {site.SiteName} | {site.CountryCode}");
                }
            }
            else
            {
                System.Diagnostics.Debug.WriteLine("  WARNING: No sites in config!");
            }

            try
            {
                // Check if user has activated license
                string token = Services.SecureStorage.ReadToken();
                if (string.IsNullOrEmpty(token))
                {
                    throw new InvalidOperationException("License not activated. Please activate your license in Settings before generating templates.");
                }

                // Validate study phase format (backend requires "Phase I", "Phase II", "Phase III", or "Phase IV")
                if (config.StudyPhase == "Phase I/II")
                {
                    throw new InvalidOperationException("Study phase 'Phase I/II' is not supported by the API. Please select either 'Phase I' or 'Phase II'.");
                }

                // Validate country codes (must be 2-letter ISO codes)
                foreach (string code in config.Countries)
                {
                    if (code.Length > 2)
                    {
                        throw new InvalidOperationException($"Invalid country code '{code}'. API requires 2-letter ISO codes (e.g., 'US', 'CA', 'GB').");
                    }
                }

                // Call API to generate full study timeline
                var apiClient = new ApiClient();

                // Create template request for each selected country
                int countryIndex = 0;
                foreach (string countryCode in config.Countries)
                {
                    countryIndex++;
                    ReportProgress(
                        $"Generating timeline for {countryCode} ({countryIndex}/{config.Countries.Count})",
                        "Calling API... This may take 30-60 seconds on first request (cold start)");

                    var templateRequest = new Models.TemplateRequest
                    {
                        country_code = countryCode,
                        study_phase = config.StudyPhase,
                        therapeutic_area = config.TherapeuticArea,
                        include_optional = config.Filters?.IncludeOptional ?? true
                    };

                    System.Diagnostics.Debug.WriteLine($"[Full Study Timeline] Calling API for {countryCode}");
                    System.Diagnostics.Debug.WriteLine($"  Study Phase: {config.StudyPhase}");
                    System.Diagnostics.Debug.WriteLine($"  Therapeutic Area: {config.TherapeuticArea}");
                    System.Diagnostics.Debug.WriteLine($"  Include Optional: {templateRequest.include_optional}");

                    // Call API to generate timeline
                    var timeline = apiClient.GenerateTemplateAsync(templateRequest).Result;

                    if (timeline != null && timeline.tasks != null && timeline.tasks.Count > 0)
                    {
                        System.Diagnostics.Debug.WriteLine($"Received {timeline.tasks.Count} tasks from API for {countryCode}");
                        System.Diagnostics.Debug.WriteLine($"Received {timeline.dependencies?.Count ?? 0} dependencies from API");

                        ReportProgress(
                            $"Creating {timeline.tasks.Count} tasks for {countryCode}",
                            "Adding tasks to MS Project...");

                        // Disable screen updating for performance
                        app.ScreenUpdating = false;

                        try
                        {
                            // Map task IDs to MS Project task objects for dependency creation
                            var taskIdToMsTask = new Dictionary<string, MSProject.Task>();

                            // Create tasks in MS Project
                            int taskIndex = 0;
                            foreach (var task in timeline.tasks)
                            {
                                // API already applied filters based on include_optional parameter
                                // Additional filtering based on category if specified
                                if (config.Filters != null &&
                                    config.Filters.IncludedCategories.Count > 0 &&
                                    !string.IsNullOrEmpty(task.category) &&
                                    !config.Filters.IncludedCategories.Contains(task.category))
                                {
                                    continue;
                                }

                                var msTask = app.ActiveProject.Tasks.Add(task.name);
                                msTask.Duration = $"{task.duration_days}d";

                                // Populate custom fields
                                msTask.SetField(MSProject.PjField.pjTaskText7, ""); // Site IDs (empty for Full Study Timeline)
                                msTask.SetField(MSProject.PjField.pjTaskText9, ""); // Cohort IDs (empty for study-level tasks)
                                msTask.SetField(MSProject.PjField.pjTaskText11, ""); // Site Name (empty for Full Study Timeline - country-level, not site-specific)
                                msTask.SetField(MSProject.PjField.pjTaskText1, task.authority ?? ""); // Regulatory Authority (NEW)
                                msTask.SetField(MSProject.PjField.pjTaskText4, task.category ?? ""); // Category
                                msTask.SetField(MSProject.PjField.pjTaskText12, task.phase ?? ""); // Stage/Phase
                                msTask.SetField(MSProject.PjField.pjTaskText13, ""); // Substage (not provided by API)
                                msTask.SetField(MSProject.PjField.pjTaskText14, $"API-{countryCode}"); // Template Source
                                msTask.SetField(MSProject.PjField.pjTaskText16, task.authority_type ?? ""); // Authority Type (NEW)
                                msTask.SetField(MSProject.PjField.pjTaskText17, task.submission_form ?? ""); // Submission Form (NEW)

                                // Add authority info to task notes if available
                                if (!string.IsNullOrEmpty(task.authority_full_name))
                                {
                                    string notes = msTask.Notes ?? "";
                                    msTask.Notes = $"Authority: {task.authority_full_name} ({task.authority})\n\n{notes}";
                                }

                                // Set task properties
                                msTask.Notes = ""; // Task model doesn't have description field
                                if (task.is_mandatory)
                                {
                                    msTask.Priority = (int)MSProject.PjPriority.pjPriorityHigh;
                                }

                                // Store mapping for dependency creation
                                if (!string.IsNullOrEmpty(task.id))
                                {
                                    taskIdToMsTask[task.id] = msTask;
                                }

                                tasksCreated++;
                                taskIndex++;

                                // Process Windows messages every 20 tasks to prevent "Server Busy" dialog
                                if (taskIndex % 20 == 0)
                                {
                                    System.Windows.Forms.Application.DoEvents();
                                }
                            }

                            // Create dependencies (predecessors) after all tasks are created
                            if (timeline.dependencies != null && timeline.dependencies.Count > 0)
                            {
                                ReportProgress(
                                    $"Creating {timeline.dependencies.Count} dependencies for {countryCode}",
                                    "Establishing critical path relationships...");

                                System.Diagnostics.Debug.WriteLine($"Creating {timeline.dependencies.Count} dependencies");

                                int dependenciesCreated = 0;
                                foreach (var dep in timeline.dependencies)
                                {
                                    try
                                    {
                                        if (taskIdToMsTask.ContainsKey(dep.predecessor_id) &&
                                            taskIdToMsTask.ContainsKey(dep.successor_id))
                                        {
                                            var predecessorTask = taskIdToMsTask[dep.predecessor_id];
                                            var successorTask = taskIdToMsTask[dep.successor_id];

                                            // Add predecessor relationship (format: "TaskID" or "TaskID+lag" for lag days)
                                            string predecessorString = predecessorTask.ID.ToString();
                                            if (dep.lag_days != 0)
                                            {
                                                predecessorString += (dep.lag_days > 0 ? "+" : "") + dep.lag_days;
                                            }

                                            // Append to existing predecessors (if any)
                                            string existingPreds = successorTask.Predecessors;
                                            if (string.IsNullOrEmpty(existingPreds))
                                            {
                                                successorTask.Predecessors = predecessorString;
                                            }
                                            else
                                            {
                                                successorTask.Predecessors = existingPreds + "," + predecessorString;
                                            }

                                            dependenciesCreated++;
                                        }
                                        else
                                        {
                                            System.Diagnostics.Debug.WriteLine($"Warning: Could not find tasks for dependency {dep.predecessor_id} -> {dep.successor_id}");
                                        }
                                    }
                                    catch (Exception depEx)
                                    {
                                        System.Diagnostics.Debug.WriteLine($"Error creating dependency: {depEx.Message}");
                                    }
                                }

                                System.Diagnostics.Debug.WriteLine($"Created {dependenciesCreated} dependencies for {countryCode}");
                            }
                        }
                        finally
                        {
                            // Re-enable screen updating
                            app.ScreenUpdating = true;
                        }

                        System.Diagnostics.Debug.WriteLine($"Created {tasksCreated} Full Study Timeline tasks for {countryCode}");

                        // NOW ADD SITE-SPECIFIC TASKS FOR THIS COUNTRY
                        System.Diagnostics.Debug.WriteLine($"Checking for sites in country: {countryCode}");
                        if (config.Sites != null && config.Sites.Count > 0)
                        {
                            System.Diagnostics.Debug.WriteLine($"Total sites in config: {config.Sites.Count}");
                            foreach (var s in config.Sites)
                            {
                                System.Diagnostics.Debug.WriteLine($"  Site {s.SiteId}: CountryCode='{s.CountryCode}' vs searching for '{countryCode}'");
                            }

                            var sitesInCountry = config.Sites.Where(s => s.CountryCode.Equals(countryCode, StringComparison.OrdinalIgnoreCase)).ToList();
                            System.Diagnostics.Debug.WriteLine($"Found {sitesInCountry.Count} sites matching country code '{countryCode}'");

                            if (sitesInCountry.Count > 0)
                            {
                                System.Diagnostics.Debug.WriteLine($"Generating site-specific tasks for {sitesInCountry.Count} sites in {countryCode}");

                                foreach (var site in sitesInCountry)
                                {
                                    System.Diagnostics.Debug.WriteLine($"  Creating site tasks for: {site.SiteId} ({site.SiteName})");

                                    // Create site activation task
                                    var siteActivationTask = app.ActiveProject.Tasks.Add($"Site Activation - {site.SiteName}");
                                    siteActivationTask.Duration = "60d"; // Typical site activation duration
                                    siteActivationTask.SetField(MSProject.PjField.pjTaskText7, site.SiteId); // Site IDs
                                    siteActivationTask.SetField(MSProject.PjField.pjTaskText11, site.SiteName); // Site Name
                                    siteActivationTask.SetField(MSProject.PjField.pjTaskText4, "Site Management");
                                    siteActivationTask.SetField(MSProject.PjField.pjTaskText12, "Site Activation");
                                    siteActivationTask.SetField(MSProject.PjField.pjTaskText14, $"FullStudy-{countryCode}");
                                    siteActivationTask.Notes = $"Site activation for {site.SiteName} ({site.SiteId})";
                                    tasksCreated++;

                                    // Create first patient enrolled task
                                    var firstPatientTask = app.ActiveProject.Tasks.Add($"First Patient Enrolled - {site.SiteName}");
                                    firstPatientTask.Duration = "0d";
                                    firstPatientTask.Milestone = true;
                                    firstPatientTask.SetField(MSProject.PjField.pjTaskText7, site.SiteId); // Site IDs
                                    firstPatientTask.SetField(MSProject.PjField.pjTaskText11, site.SiteName); // Site Name
                                    firstPatientTask.SetField(MSProject.PjField.pjTaskText4, "Enrollment");
                                    firstPatientTask.SetField(MSProject.PjField.pjTaskText12, "Patient Enrollment");
                                    firstPatientTask.SetField(MSProject.PjField.pjTaskText14, $"FullStudy-{countryCode}");
                                    firstPatientTask.Notes = $"First patient enrolled at {site.SiteName} ({site.SiteId})";
                                    firstPatientTask.Predecessors = siteActivationTask.ID.ToString();
                                    tasksCreated++;
                                }

                                System.Diagnostics.Debug.WriteLine($"Created {sitesInCountry.Count * 2} site-specific tasks for {countryCode}");
                            }
                        }
                    }
                    else
                    {
                        System.Diagnostics.Debug.WriteLine($"No tasks returned from API for {countryCode}");
                    }
                }
            }
            catch (System.AggregateException aggEx)
            {
                // Handle async exceptions from .Result
                var innerEx = aggEx.InnerException ?? aggEx;
                System.Diagnostics.Debug.WriteLine($"[Full Study Timeline ERROR] {innerEx.GetType().Name}: {innerEx.Message}");
                System.Diagnostics.Debug.WriteLine($"Stack trace: {innerEx.StackTrace}");

                string errorMessage = innerEx.Message;

                // Check for specific error types
                if (innerEx is System.Net.Http.HttpRequestException)
                {
                    errorMessage = "Network error - unable to connect to API. Check your internet connection.";
                }
                else if (innerEx is Models.UnauthorizedException ||
                         innerEx.Message.Contains("401") ||
                         innerEx.Message.Contains("Unauthorized"))
                {
                    errorMessage = "License authentication failed. Please reactivate your license in Settings.";
                }
                else if (innerEx.Message.Contains("422") || innerEx.Message.Contains("validation"))
                {
                    errorMessage = $"API validation error: {innerEx.Message}\n\nPlease check that:\n" +
                                 $"- Study Phase is 'Phase I', 'Phase II', 'Phase III', or 'Phase IV'\n" +
                                 $"- Country codes are valid 2-letter ISO codes\n" +
                                 $"- Therapeutic area is specified";
                }
                else if (innerEx.Message.Contains("400"))
                {
                    errorMessage = $"Invalid request: {innerEx.Message}\n\nThe selected country or study configuration may not be supported.";
                }
                else if (innerEx.Message.Contains("500"))
                {
                    errorMessage = "API server error. The backend service encountered an error. Please try again later.";
                }

                throw new InvalidOperationException($"Failed to generate Full Study Timeline:\n\n{errorMessage}", innerEx);
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[Full Study Timeline ERROR] {ex.GetType().Name}: {ex.Message}");
                System.Diagnostics.Debug.WriteLine($"Stack trace: {ex.StackTrace}");
                throw new InvalidOperationException($"Failed to generate Full Study Timeline:\n\n{ex.Message}", ex);
            }

            return tasksCreated;
        }

        /// <summary>
        /// Generate Site Startup templates for selected sites using API for authority-specific details
        /// </summary>
        private async System.Threading.Tasks.Task<int> GenerateSiteStartup(MSProject.Application app, ClinicalProjectConfiguration config)
        {
            int tasksCreated = 0;

            System.Diagnostics.Debug.WriteLine($"=== GenerateSiteStartup START (API-based) ===");
            System.Diagnostics.Debug.WriteLine($"Config.Sites: {config.Sites?.Count ?? 0}");
            System.Diagnostics.Debug.WriteLine($"Templates.SitesForStartup: {config.Templates.SitesForStartup?.Count ?? 0}");

            if (config.Templates.SitesForStartup == null || config.Templates.SitesForStartup.Count == 0)
            {
                System.Diagnostics.Debug.WriteLine("ERROR: No sites selected for startup!");
                return 0;
            }

            foreach (string siteId in config.Templates.SitesForStartup)
            {
                System.Diagnostics.Debug.WriteLine($"Looking for site: {siteId}");
                var site = config.Sites.FirstOrDefault(s => s.SiteId == siteId);
                if (site == null)
                {
                    System.Diagnostics.Debug.WriteLine($"ERROR: Site {siteId} not found in config.Sites!");
                    continue;
                }

                System.Diagnostics.Debug.WriteLine($"FOUND Site: {site.SiteId} | Name: {site.SiteName} | Country: {site.CountryCode}");

                // Call async API method for authority-specific template
                var templateConfig = new TemplateConfiguration
                {
                    TemplateType = TemplateType.SiteStartup,
                    CountryCode = site.CountryCode,
                    SiteId = site.SiteId,
                    StudyPhase = config.StudyPhase,
                    TherapeuticArea = config.TherapeuticArea
                };

                TemplateResult result = await LoadSiteStartupTemplateAsync(templateConfig, config.Filters);
                Timeline timeline = result.Timeline;

                System.Diagnostics.Debug.WriteLine($"Received {timeline.tasks.Count} tasks from API for {site.SiteId}");

                // Create tasks with BOTH country-specific AND site-specific details
                foreach (var task in timeline.tasks)
                {
                    // Apply filters (if any)
                    if (config.Filters != null && config.Filters.IncludedCategories.Count > 0 &&
                        !string.IsNullOrEmpty(task.category) &&
                        !config.Filters.IncludedCategories.Contains(task.category))
                    {
                        continue;
                    }

                    var msTask = app.ActiveProject.Tasks.Add(task.name);  // Authority-specific name from API
                    msTask.Duration = $"{task.duration_days}d";

                    // Site-specific fields (hybrid approach)
                    msTask.SetField(MSProject.PjField.pjTaskText7, site.SiteId); // Site IDs
                    msTask.SetField(MSProject.PjField.pjTaskText11, site.SiteName); // Site Name

                    // Authority-specific fields (from API)
                    msTask.SetField(MSProject.PjField.pjTaskText1, task.authority ?? ""); // Regulatory Authority
                    msTask.SetField(MSProject.PjField.pjTaskText16, task.authority_type ?? ""); // Authority Type
                    msTask.SetField(MSProject.PjField.pjTaskText17, task.submission_form ?? ""); // Submission Form
                    msTask.SetField(MSProject.PjField.pjTaskText4, task.category ?? ""); // Category
                    msTask.SetField(MSProject.PjField.pjTaskText12, "Site Activation"); // Stage
                    msTask.SetField(MSProject.PjField.pjTaskText14, $"API-{site.CountryCode}"); // Template Source

                    // Add authority info to notes
                    if (!string.IsNullOrEmpty(task.authority_full_name))
                    {
                        string notes = $"Authority: {task.authority_full_name} ({task.authority})\n";
                        if (!string.IsNullOrEmpty(task.authority_type))
                            notes += $"Authority Type: {task.authority_type}\n";
                        if (!string.IsNullOrEmpty(task.submission_form))
                            notes += $"Submission Form: {task.submission_form}\n";
                        msTask.Notes = notes;
                    }

                    if (task.is_mandatory)
                    {
                        msTask.Priority = (int)MSProject.PjPriority.pjPriorityHigh;
                    }

                    tasksCreated++;
                }

                System.Diagnostics.Debug.WriteLine($"Created {tasksCreated} Site Startup tasks for {site.SiteId}");
            }

            return tasksCreated;
        }

        /// <summary>
        /// Generate Site Implementation templates for selected sites
        /// </summary>
        private int GenerateSiteImplementation(MSProject.Application app, ClinicalProjectConfiguration config)
        {
            int tasksCreated = 0;

            foreach (string siteId in config.Templates.SitesForImplementation)
            {
                var site = config.Sites.FirstOrDefault(s => s.SiteId == siteId);
                if (site == null) continue;

                // Get template for country
                SitePhaseTaskSet taskSet = null;
                var countryInfo = CountryRegulatoryInfo.GetCountryInfo(site.CountryCode);

                if (site.CountryCode.ToUpper() == "USA")
                {
                    taskSet = CountryTemplateLibrary.GetUSA_Implementation();
                }
                else
                {
                    taskSet = CountryTemplateLibrary.GetInternational_Implementation(countryInfo);
                }

                if (taskSet != null && taskSet.tasks != null)
                {
                    foreach (var task in taskSet.tasks)
                    {
                        if (config.Filters != null && !config.Filters.PassesFilter(task))
                            continue;

                        var msTask = app.ActiveProject.Tasks.Add(task.name);
                        msTask.Duration = $"{task.duration_days}d";

                        // Populate custom fields
                        msTask.SetField(MSProject.PjField.pjTaskText7, site.SiteId); // Site IDs (e.g., "SITE-001")
                        msTask.SetField(MSProject.PjField.pjTaskText11, site.SiteName); // Site Name (e.g., "Memorial Hospital")
                        msTask.SetField(MSProject.PjField.pjTaskText4, task.category);
                        msTask.SetField(MSProject.PjField.pjTaskText12, "Implementation");
                        msTask.SetField(MSProject.PjField.pjTaskText13, task.subphase);
                        msTask.SetField(MSProject.PjField.pjTaskText14, $"Library-{site.CountryCode}");

                        msTask.Notes = task.description;
                        if (task.is_mandatory)
                            msTask.Priority = (int)MSProject.PjPriority.pjPriorityHigh;

                        tasksCreated++;
                    }
                }
            }

            // Auto-generate cohort-specific milestone tasks if cohorts are defined
            if (config.Cohorts != null && config.Cohorts.Count > 0)
            {
                tasksCreated += GenerateCohortMilestoneTasks(app, config);
            }

            return tasksCreated;
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
        private async System.Threading.Tasks.Task<int> GenerateSiteCloseout(MSProject.Application app, ClinicalProjectConfiguration config)
        {
            int tasksCreated = 0;

            System.Diagnostics.Debug.WriteLine($"=== GenerateSiteCloseout START (API-based) ===");

            foreach (string siteId in config.Templates.SitesForCloseout)
            {
                var site = config.Sites.FirstOrDefault(s => s.SiteId == siteId);
                if (site == null)
                {
                    System.Diagnostics.Debug.WriteLine($"ERROR: Site {siteId} not found in config.Sites!");
                    continue;
                }

                System.Diagnostics.Debug.WriteLine($"FOUND Site: {site.SiteId} | Name: {site.SiteName} | Country: {site.CountryCode}");

                // Call async API method for authority-specific template
                var templateConfig = new TemplateConfiguration
                {
                    TemplateType = TemplateType.SiteCloseout,
                    CountryCode = site.CountryCode,
                    SiteId = site.SiteId,
                    StudyPhase = config.StudyPhase,
                    TherapeuticArea = config.TherapeuticArea
                };

                TemplateResult result = await LoadSiteCloseoutTemplateAsync(templateConfig, config.Filters);
                Timeline timeline = result.Timeline;

                System.Diagnostics.Debug.WriteLine($"Received {timeline.tasks.Count} tasks from API for {site.SiteId}");

                // Create tasks with BOTH country-specific AND site-specific details
                foreach (var task in timeline.tasks)
                {
                    // Apply filters (if any)
                    if (config.Filters != null && config.Filters.IncludedCategories.Count > 0 &&
                        !string.IsNullOrEmpty(task.category) &&
                        !config.Filters.IncludedCategories.Contains(task.category))
                    {
                        continue;
                    }

                    var msTask = app.ActiveProject.Tasks.Add(task.name);  // Authority-specific name from API
                    msTask.Duration = $"{task.duration_days}d";

                    // Site-specific fields (hybrid approach)
                    msTask.SetField(MSProject.PjField.pjTaskText7, site.SiteId); // Site IDs
                    msTask.SetField(MSProject.PjField.pjTaskText11, site.SiteName); // Site Name

                    // Authority-specific fields (from API)
                    msTask.SetField(MSProject.PjField.pjTaskText1, task.authority ?? ""); // Regulatory Authority
                    msTask.SetField(MSProject.PjField.pjTaskText16, task.authority_type ?? ""); // Authority Type
                    msTask.SetField(MSProject.PjField.pjTaskText17, task.submission_form ?? ""); // Submission Form
                    msTask.SetField(MSProject.PjField.pjTaskText4, task.category ?? ""); // Category
                    msTask.SetField(MSProject.PjField.pjTaskText12, "Site Closeout"); // Stage
                    msTask.SetField(MSProject.PjField.pjTaskText14, $"API-{site.CountryCode}"); // Template Source

                    // Add authority info to notes
                    if (!string.IsNullOrEmpty(task.authority_full_name))
                    {
                        string notes = $"Authority: {task.authority_full_name} ({task.authority})\n";
                        if (!string.IsNullOrEmpty(task.authority_type))
                            notes += $"Authority Type: {task.authority_type}\n";
                        if (!string.IsNullOrEmpty(task.submission_form))
                            notes += $"Submission Form: {task.submission_form}\n";
                        msTask.Notes = notes;
                    }

                    if (task.is_mandatory)
                        msTask.Priority = (int)MSProject.PjPriority.pjPriorityHigh;

                    tasksCreated++;
                }

                System.Diagnostics.Debug.WriteLine($"Created {tasksCreated} Site Closeout tasks for {site.SiteId}");
            }

            return tasksCreated;
        }

        /// <summary>
        /// Generate Study Closeout template (study-level, no sites)
        /// </summary>
        private int GenerateStudyCloseout(MSProject.Application app, ClinicalProjectConfiguration config)
        {
            int tasksCreated = 0;

            var taskSet = CountryTemplateLibrary.GetStudyCloseout();

            if (taskSet != null && taskSet.tasks != null)
            {
                foreach (var task in taskSet.tasks)
                {
                    if (config.Filters != null && !config.Filters.PassesFilter(task))
                        continue;

                    var msTask = app.ActiveProject.Tasks.Add(task.name);
                    msTask.Duration = $"{task.duration_days}d";

                    // Populate custom fields (no site for study-level closeout)
                    msTask.SetField(MSProject.PjField.pjTaskText7, ""); // Site IDs (empty - study-level)
                    msTask.SetField(MSProject.PjField.pjTaskText11, ""); // Site (empty - study-level)
                    msTask.SetField(MSProject.PjField.pjTaskText4, task.category);
                    msTask.SetField(MSProject.PjField.pjTaskText12, "Study Closeout");
                    msTask.SetField(MSProject.PjField.pjTaskText13, task.subphase);
                    msTask.SetField(MSProject.PjField.pjTaskText14, "Library-StudyLevel");

                    msTask.Notes = task.description;
                    if (task.is_mandatory)
                        msTask.Priority = (int)MSProject.PjPriority.pjPriorityHigh;

                    tasksCreated++;
                }

                System.Diagnostics.Debug.WriteLine($"Created {tasksCreated} Study Closeout tasks");
            }

            return tasksCreated;
        }

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
