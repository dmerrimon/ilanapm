# Template Loading Integration Summary

**Date:** 2026-02-13
**Status:** ✅ API Client Ready - Integration Pending

---

## Overview

We've successfully created 6 templates in the database and added API client methods to retrieve them. Now we need to integrate them into the Clinical Project Manager workflow.

---

## Database Templates (What We Built)

| Template ID | Template Name | Type | Tasks | Duration | Use Case |
|------------|---------------|------|-------|----------|----------|
| **TPL_001** | Study Start-Up | study_startup | 86 | 180 days | Study Award → FPI |
| **TPL_002** | Study Implementation | implementation | 10 | 730 days | FPI → LPLV milestones |
| **TPL_003** | Study Closeout | closeout | 23 | 300 days | LPLV → FDA submission |
| **TPL_004** | Site Activation | site_activation | 34 | 90 days | Site selection → activated |
| **TPL_005** | Site Closeout | site_closeout | 19 | 30 days | Site complete → DB lock ready |
| **TPL_006** | Full Study Timeline | full_study | 119 | 1260 days | Complete study (Startup + Implementation + Closeout) |

---

## New API Methods (What We Added)

### 1. ListTemplatesAsync()
```csharp
// ApiClient.cs - Line ~448
public async Task<Models.TemplateListResponse> ListTemplatesAsync(string orgId = null)
```

**Returns:**
```csharp
{
  "templates": [
    {
      "template_id": "TPL_001",
      "template_name": "Study Start-Up",
      "template_type": "study_startup",
      "total_task_count": 86,
      "estimated_duration_days": 180,
      "is_system_template": true
    },
    // ... more templates
  ],
  "count": 6
}
```

### 2. GetTemplateAsync(templateId)
```csharp
// ApiClient.cs - Line ~475
public async Task<Models.TemplateDetailResponse> GetTemplateAsync(string templateId)
```

**Returns:**
```csharp
{
  "template": { /* metadata */ },
  "tasks": [
    {
      "task_id": "SS_001",
      "task_name": "Internal Transition Meeting",
      "category": "Initiation",
      "typical_duration_days": 7,
      "is_milestone": false,
      "sort_order": 1
    },
    // ... 85 more tasks
  ],
  "dependencies": [
    {
      "predecessor_task_id": "SS_001",
      "successor_task_id": "SS_012",
      "dependency_type": "finish-to-start",
      "lag_days": 0,
      "is_hard_dependency": false
    },
    // ... 51 more dependencies
  ]
}
```

---

## Model Classes (What We Created)

**File:** `Models/TemplateLibrary.cs`

- `TemplateListResponse` - List of templates
- `TemplateMetadata` - Summary info for each template
- `TemplateDetailResponse` - Complete template with tasks/dependencies
- `TemplateTask` - Task definition within template
- `TemplateDependency` - Predecessor relationships

---

## Integration Strategy

### Option 1: Replace Existing Template Generation (Recommended)

**Current Flow:**
```
User clicks "Generate"
  → UnifiedTemplateManager.GenerateTemplates()
  → Calls OLD endpoints:
      - POST /api/v1/templates/generate (Full Study Timeline)
      - POST /api/v1/templates/generate-site-startup
      - POST /api/v1/templates/generate-site-closeout
      - POST /api/v1/templates/generate-study-closeout
```

**New Flow:**
```
User clicks "Generate"
  → UnifiedTemplateManager.GenerateTemplates()
  → Calls NEW endpoints:
      - GET /api/v1/templates/library/TPL_001 (Study Start-Up)
      - GET /api/v1/templates/library/TPL_002 (Implementation)
      - GET /api/v1/templates/library/TPL_003 (Study Closeout)
      - GET /api/v1/templates/library/TPL_004 (Site Activation)
      - GET /api/v1/templates/library/TPL_005 (Site Closeout)
      - GET /api/v1/templates/library/TPL_006 (Full Study Timeline)
```

**Mapping:**

| Old Method | New Method | Template ID |
|-----------|-----------|-------------|
| `GenerateFullStudyTimeline()` | `GetTemplateAsync("TPL_006")` | TPL_006 |
| `GenerateSiteStartup()` | `GetTemplateAsync("TPL_004")` | TPL_004 |
| `GenerateSiteCloseout()` | `GetTemplateAsync("TPL_005")` | TPL_005 |
| `GenerateStudyCloseout()` | `GetTemplateAsync("TPL_003")` | TPL_003 |
| N/A (new) | `GetTemplateAsync("TPL_001")` | TPL_001 Study Start-Up only |
| N/A (new) | `GetTemplateAsync("TPL_002")` | TPL_002 Implementation milestones |

### Option 2: Hybrid Approach

Keep existing template generation for backward compatibility, but add NEW template selection UI:

**Add to Step 3 (Template Selection):**
```
[ ] Full Study Timeline (Legacy - API Generated)
[ ] Full Study Timeline (New - Database Template TPL_006) ✅ RECOMMENDED

[ ] Study Start-Up Only (TPL_001)
[ ] Study Implementation Milestones (TPL_002)
[ ] Study Closeout (TPL_003)

[ ] Site Activation (TPL_004)
[ ] Site Closeout (TPL_005)
```

---

## Implementation Steps

### Step 1: Update UnifiedTemplateManager

**File:** `Services/UnifiedTemplateManager.cs`

Add new methods:

```csharp
/// <summary>
/// Generate timeline from database template
/// </summary>
private static async Task<int> GenerateFromDatabaseTemplate(
    MSProject.Application app,
    string templateId,
    Models.ClinicalProjectConfiguration config,
    string siteId = null
)
{
    var apiClient = new ApiClient();
    var templateDetail = await apiClient.GetTemplateAsync(templateId);

    int taskCount = 0;
    var taskIdToMsTask = new Dictionary<string, MSProject.Task>();

    // Create all tasks
    foreach (var task in templateDetail.tasks)
    {
        var msTask = app.ActiveProject.Tasks.Add(task.task_name);
        msTask.Duration = $"{task.typical_duration_days}d";

        // Set custom fields
        msTask.SetField(MSProject.PjField.pjTaskText4, task.category);
        msTask.SetField(MSProject.PjField.pjTaskText12, templateDetail.template.template_type);
        msTask.SetField(MSProject.PjField.pjTaskText14, $"DB-{templateId}");

        // Site-specific fields
        if (!string.IsNullOrEmpty(siteId))
        {
            msTask.SetField(MSProject.PjField.pjTaskText7, siteId);
            var site = config.Sites.Find(s => s.SiteId == siteId);
            if (site != null)
            {
                msTask.SetField(MSProject.PjField.pjTaskText11, site.SiteName);
            }
        }

        // Mark milestones
        if (task.is_milestone)
        {
            msTask.Milestone = true;
        }

        taskIdToMsTask[task.task_id] = msTask;
        taskCount++;
    }

    // Create dependencies
    foreach (var dep in templateDetail.dependencies)
    {
        if (taskIdToMsTask.ContainsKey(dep.predecessor_task_id) &&
            taskIdToMsTask.ContainsKey(dep.successor_task_id))
        {
            var successorTask = taskIdToMsTask[dep.successor_task_id];
            var predecessorTask = taskIdToMsTask[dep.predecessor_task_id];

            string predecessorString = predecessorTask.ID.ToString();
            if (dep.lag_days != 0)
            {
                predecessorString += $"{(dep.lag_days > 0 ? "+" : "")}{dep.lag_days}";
            }

            successorTask.Predecessors = predecessorString;
        }
    }

    return taskCount;
}
```

### Step 2: Update Template Selection Checkboxes

**File:** `ClinicalProjectManagerForm.cs` - Step 3 Panel

Add new checkboxes:

```csharp
private CheckBox chkDatabaseFullStudy;
private CheckBox chkDatabaseStudyStartup;
private CheckBox chkDatabaseImplementation;

// In InitializeStep3():
chkDatabaseFullStudy = new CheckBox();
chkDatabaseFullStudy.Text = "Full Study Timeline (Database - TPL_006) ✅ NEW";
chkDatabaseFullStudy.AutoSize = true;
chkDatabaseFullStudy.Checked = true; // Default to new template

chkDatabaseStudyStartup = new CheckBox();
chkDatabaseStudyStartup.Text = "Study Start-Up Only (TPL_001)";
chkDatabaseStudyStartup.AutoSize = true;

chkDatabaseImplementation = new CheckBox();
chkDatabaseImplementation.Text = "Study Implementation Milestones (TPL_002)";
chkDatabaseImplementation.AutoSize = true;
```

### Step 3: Update Generate Logic

**File:** `UnifiedTemplateManager.cs` - `GenerateTemplates()`

```csharp
public static async Task<int> GenerateTemplates(
    MSProject.Application app,
    Models.ClinicalProjectConfiguration config
)
{
    int totalTasksCreated = 0;

    // NEW: Database Template Generation
    if (config.Templates.GenerateDatabaseFullStudy)
    {
        totalTasksCreated += await GenerateFromDatabaseTemplate(app, "TPL_006", config);
    }

    if (config.Templates.GenerateDatabaseStudyStartup)
    {
        totalTasksCreated += await GenerateFromDatabaseTemplate(app, "TPL_001", config);
    }

    if (config.Templates.GenerateDatabaseImplementation)
    {
        totalTasksCreated += await GenerateFromDatabaseTemplate(app, "TPL_002", config);
    }

    // Site-specific templates
    if (config.Templates.GenerateSiteActivation && config.Templates.SitesForActivation.Count > 0)
    {
        foreach (var siteId in config.Templates.SitesForActivation)
        {
            totalTasksCreated += await GenerateFromDatabaseTemplate(app, "TPL_004", config, siteId);
        }
    }

    if (config.Templates.GenerateSiteCloseout && config.Templates.SitesForCloseout.Count > 0)
    {
        foreach (var siteId in config.Templates.SitesForCloseout)
        {
            totalTasksCreated += await GenerateFromDatabaseTemplate(app, "TPL_005", config, siteId);
        }
    }

    if (config.Templates.GenerateStudyCloseout)
    {
        totalTasksCreated += await GenerateFromDatabaseTemplate(app, "TPL_003", config);
    }

    return totalTasksCreated;
}
```

---

## Benefits of New Template System

### 1. Consistency
✅ All users get same baseline tasks (86 Study Start-Up tasks, 23 Study Closeout tasks, etc.)
✅ No variations from API generation logic
✅ Single source of truth in database

### 2. Maintainability
✅ Update templates in one place (database)
✅ No code changes needed for task updates
✅ Version control for templates (template.version field)

### 3. Customization
✅ Organizations can create custom templates (org_id NOT NULL)
✅ Mix system + org templates
✅ Template library UI for browsing/selecting

### 4. Dependencies
✅ 52 Study Start-Up dependencies preserved
✅ 23 Study Closeout dependencies preserved
✅ Proper critical path calculation in MS Project

### 5. Performance
✅ Fast database queries vs. complex API generation
✅ No country-specific logic overhead
✅ Cached templates for repeated use

---

## Testing Checklist

- [ ] Compile C# project without errors
- [ ] Verify new API methods work (ListTemplatesAsync, GetTemplateAsync)
- [ ] Test GenerateFromDatabaseTemplate() creates tasks correctly
- [ ] Verify dependencies created properly in MS Project
- [ ] Test site-specific template generation (TPL_004, TPL_005)
- [ ] Verify custom fields populated correctly
- [ ] Test Full Study Timeline (TPL_006) end-to-end
- [ ] Verify milestones marked correctly
- [ ] Test with multiple sites
- [ ] Verify backward compatibility with old templates

---

## Next Steps

1. **Implement GenerateFromDatabaseTemplate()** in UnifiedTemplateManager.cs
2. **Add checkbox UI** in ClinicalProjectManagerForm.cs Step 3
3. **Update config model** (TemplateSelections.cs) with new boolean flags
4. **Test** in Visual Studio with MS Project
5. **Iterate** based on test results
6. **Document** for end users

---

**Status:** Ready for Implementation
**Estimated Time:** 2-3 hours
**Risk:** Low (backward compatible, can run side-by-side with old system)
