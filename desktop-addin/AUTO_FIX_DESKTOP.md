# Auto-Fix Desktop - Implementation Guide

**Feature**: One-click automatic fix for common validation errors
**Estimated Time**: 1.5 hours
**Backend**: Already implemented ✅ (`POST /api/v1/validate/autofix`)

---

## Overview

This feature adds an "Auto-Fix" button to the ValidationResultsForm that:
1. Sends current timeline to auto-fix endpoint
2. Backend fixes 4 types of errors automatically
3. Receives fixed timeline back
4. Applies fixes to MS Project
5. Re-validates and shows updated results

**Auto-Fixable Issues**:
1. **Self-dependencies** - Task depends on itself (removed)
2. **Invalid task references** - Dependency to non-existent task (removed)
3. **Duration bounds violations** - Too short/long for task type (adjusted to min/max)
4. **Invalid percentages** - Checklist completion <0 or >100 (clamped to 0-100)

**User Workflow**:
1. PM clicks "Validate Timeline"
2. Sees errors: "5 errors found"
3. PM clicks "Auto-Fix" button
4. Backend fixes errors automatically
5. Desktop applies fixes to MS Project
6. Shows: "Auto-Fix Applied 5 Fixes" with details
7. Validation re-runs automatically
8. Shows: "0 errors remaining"

---

## Files to Create/Modify

### 1. Create `Models/AutoFixResult.cs` [NEW]

```csharp
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    /// <summary>
    /// Result from auto-fix operation
    /// </summary>
    public class AutoFixResult
    {
        public int fixes_applied { get; set; }
        public List<string> issues_fixed { get; set; }
        public int remaining_issues { get; set; }
        public Timeline modified_timeline { get; set; }
    }
}
```

---

### 2. Add to `Services/ApiClient.cs` [MODIFY]

Add this method:

```csharp
/// <summary>
/// Auto-fix timeline validation errors
/// </summary>
public async Task<AutoFixResult> AutoFixTimelineAsync(Timeline timeline)
{
    string jsonContent = JsonConvert.SerializeObject(timeline);
    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

    HttpResponseMessage response = await httpClient.PostAsync(
        API_BASE_URL + "/api/v1/validate/autofix",
        content
    );

    response.EnsureSuccessStatusCode();
    string responseBody = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<AutoFixResult>(responseBody);
}
```

---

### 3. Add to `Services/ProjectDataWriter.cs` [MODIFY]

Add this method to apply auto-fix results back to MS Project:

```csharp
/// <summary>
/// Apply auto-fixed timeline back to MS Project
/// </summary>
public void ApplyAutoFixedTimeline(
    Microsoft.Office.Interop.MSProject.Application projectApp,
    Timeline fixedTimeline)
{
    if (projectApp.ActiveProject == null)
        throw new Exception("No active project found.");

    Project activeProject = projectApp.ActiveProject;

    // Update task durations
    foreach (var fixedTask in fixedTimeline.tasks)
    {
        var msTask = FindTaskById(activeProject, fixedTask.id);
        if (msTask != null)
        {
            // Update duration if changed
            int currentDurationDays = ConvertMinutesToDays(msTask.Duration);
            if (currentDurationDays != fixedTask.duration_days)
            {
                msTask.Duration = fixedTask.duration_days + "d";

                // Add note about duration change
                string note = $"[AUTO-FIX] Duration adjusted from {currentDurationDays} to {fixedTask.duration_days} days\\n\\n";
                AppendTaskNote(msTask, note);
            }

            // Update checklist completion percentage if changed
            if (fixedTask.checklist_completion_pct.HasValue)
            {
                double currentPct = GetTaskCustomFieldNumber(msTask, "Checklist Completion %") ?? 0;
                if (Math.Abs(currentPct - fixedTask.checklist_completion_pct.Value) > 0.01)
                {
                    SetTaskCustomFieldNumber(msTask, "Checklist Completion %",
                        fixedTask.checklist_completion_pct.Value);
                }
            }
        }
    }

    // Clear and rebuild dependencies (removes invalid ones)
    foreach (Microsoft.Office.Interop.MSProject.Task task in activeProject.Tasks)
    {
        if (task != null && task.TaskDependencies != null)
        {
            // Remove all existing dependencies
            while (task.TaskDependencies.Count > 0)
            {
                task.TaskDependencies[1].Delete();
            }
        }
    }

    // Add back valid dependencies (self-deps and invalid refs already removed by backend)
    foreach (var dep in fixedTimeline.dependencies)
    {
        var successorTask = FindTaskById(activeProject, dep.successor_id);
        var predecessorTask = FindTaskById(activeProject, dep.predecessor_id);

        if (successorTask != null && predecessorTask != null)
        {
            try
            {
                successorTask.TaskDependencies.Add(
                    predecessorTask,
                    ConvertDependencyType(dep.type),
                    dep.lag_days + "d"
                );
            }
            catch (Exception ex)
            {
                // Log but continue (some dependencies may fail to add)
                System.Diagnostics.Debug.WriteLine($"Failed to add dependency: {ex.Message}");
            }
        }
    }
}

private Microsoft.Office.Interop.MSProject.Task FindTaskById(
    Project project,
    string taskId)
{
    foreach (Microsoft.Office.Interop.MSProject.Task task in project.Tasks)
    {
        if (task != null && task.ID.ToString() == taskId)
        {
            return task;
        }
    }
    return null;
}

private int ConvertMinutesToDays(int minutes)
{
    return minutes / 480; // 480 minutes = 8 hour workday
}

private PjTaskLinkType ConvertDependencyType(string depType)
{
    switch (depType?.ToLower())
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

private void AppendTaskNote(Microsoft.Office.Interop.MSProject.Task task, string note)
{
    string existingNotes = task.Notes ?? "";
    task.Notes = existingNotes + note;
}

private double? GetTaskCustomFieldNumber(
    Microsoft.Office.Interop.MSProject.Task task,
    string fieldName)
{
    try
    {
        switch (fieldName)
        {
            case "Checklist Completion %":
                return task.Number3 > 0 ? (double?)task.Number3 : null;
            default:
                return null;
        }
    }
    catch
    {
        return null;
    }
}

private void SetTaskCustomFieldNumber(
    Microsoft.Office.Interop.MSProject.Task task,
    string fieldName,
    double value)
{
    switch (fieldName)
    {
        case "Checklist Completion %":
            task.Number3 = value;
            break;
    }
}
```

---

### 4. Update `ValidationResultsForm.cs` [MODIFY]

Add Auto-Fix button and handler:

```csharp
// Add to class fields
private System.Windows.Forms.Button btnAutoFix;

// Add to InitializeComponent() method
private void InitializeAutoFixButton()
{
    this.btnAutoFix = new System.Windows.Forms.Button();
    this.btnAutoFix.Location = new System.Drawing.Point(12, 496);
    this.btnAutoFix.Size = new System.Drawing.Size(120, 30);
    this.btnAutoFix.Text = "Auto-Fix Issues";
    this.btnAutoFix.Anchor = AnchorStyles.Bottom | AnchorStyles.Left;
    this.btnAutoFix.Click += new System.EventHandler(this.btnAutoFix_Click);
    this.Controls.Add(this.btnAutoFix);
}

// Add event handler
private async void btnAutoFix_Click(object sender, EventArgs e)
{
    try
    {
        btnAutoFix.Enabled = false;
        btnAutoFix.Text = "Fixing...";

        // Extract current timeline
        var extractor = new Services.ProjectDataExtractor();
        var timeline = extractor.ExtractTimeline(Globals.ThisAddIn.Application);

        // Call auto-fix endpoint
        var apiClient = new Services.ApiClient();
        var result = await apiClient.AutoFixTimelineAsync(timeline);

        btnAutoFix.Enabled = true;
        btnAutoFix.Text = "Auto-Fix Issues";

        if (result.fixes_applied > 0)
        {
            // Apply fixes back to MS Project
            var writer = new Services.ProjectDataWriter();
            writer.ApplyAutoFixedTimeline(Globals.ThisAddIn.Application, result.modified_timeline);

            // Build success message
            string message = $"Auto-Fix Applied {result.fixes_applied} Fixes:\\n\\n";
            foreach (var fix in result.issues_fixed)
            {
                message += $"✓ {fix}\\n";
            }
            message += $"\\nRemaining Issues: {result.remaining_issues}";

            MessageBox.Show(
                message,
                "Auto-Fix Complete",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );

            // Re-validate automatically
            var validationResult = await apiClient.ValidateTimelineAsync(result.modified_timeline);
            DisplayResults(validationResult);
        }
        else
        {
            MessageBox.Show(
                "No auto-fixable issues found.\\n\\n" +
                "All validation errors require manual review.",
                "Auto-Fix",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );
        }
    }
    catch (Exception ex)
    {
        btnAutoFix.Enabled = true;
        btnAutoFix.Text = "Auto-Fix Issues";

        MessageBox.Show(
            $"Auto-Fix Error:\\n\\n{ex.Message}",
            "Auto-Fix Error",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error
        );
    }
}

// Call in InitializeComponent()
InitializeAutoFixButton();
```

---

## Testing Instructions

### Test 1: Self-Dependency Fix

1. Create task "T1"
2. Add dependency: T1 → T1 (predecessor and successor same)
3. Click "Validate Timeline"
4. Verify error: "Self-referencing dependency"
5. Click "Auto-Fix Issues"
6. Verify message: "✓ Removed 1 self-referencing dependencies"
7. Check MS Project: Dependency removed
8. Verify: "0 errors remaining"

### Test 2: Invalid Task Reference Fix

1. Create tasks: T1, T2
2. Add dependency: T1 → T3 (T3 doesn't exist)
3. Click "Validate Timeline"
4. Verify error: "Invalid task reference: T3"
5. Click "Auto-Fix Issues"
6. Verify message: "✓ Removed 1 dependencies with invalid task references"
7. Check MS Project: Invalid dependency removed

### Test 3: Duration Bounds Fix (Too Short)

1. Create task "IND/CTA Submission" with duration = 1 day
2. Click "Validate Timeline"
3. Verify warning: "Duration too short (minimum 30 days)"
4. Click "Auto-Fix Issues"
5. Verify message: "✓ Increased 'IND/CTA Submission' duration from 1 to 30 days (minimum)"
6. Check MS Project: Task duration = 30 days
7. Check task notes: "[AUTO-FIX] Duration adjusted from 1 to 30 days"

### Test 4: Duration Bounds Fix (Too Long)

1. Create task "IRB/EC Approval" with duration = 500 days
2. Click "Validate Timeline"
3. Verify warning: "Duration too long (maximum 90 days)"
4. Click "Auto-Fix Issues"
5. Verify message: "✓ Decreased 'IRB/EC Approval' duration from 500 to 90 days (maximum)"
6. Check MS Project: Task duration = 90 days

### Test 5: Multiple Fixes at Once

1. Create project with:
   - Self-dependency (T1 → T1)
   - Invalid reference (T1 → T999)
   - Duration too short (IND = 1 day)
   - Duration too long (IRB = 500 days)
2. Click "Validate Timeline"
3. Verify: "4 errors found"
4. Click "Auto-Fix Issues"
5. Verify message shows all 4 fixes:
   ```
   Auto-Fix Applied 4 Fixes:

   ✓ Removed 1 self-referencing dependencies
   ✓ Removed 1 dependencies with invalid task references
   ✓ Increased 'IND/CTA Submission' duration from 1 to 30 days
   ✓ Decreased 'IRB/EC Approval' duration from 500 to 90 days

   Remaining Issues: 0
   ```
6. Verify all fixes applied to MS Project
7. Verify validation re-runs and shows 0 errors

### Test 6: No Auto-Fixable Issues

1. Create project with only manual-review errors (e.g., missing mandatory tasks)
2. Click "Validate Timeline"
3. Verify errors shown
4. Click "Auto-Fix Issues"
5. Verify message: "No auto-fixable issues found. All validation errors require manual review."

---

## Expected Behavior

**When user clicks "Auto-Fix Issues"**:
1. ✅ Button changes to "Fixing..." and disables
2. ✅ Timeline extracted from MS Project
3. ✅ API call to `/api/v1/validate/autofix`
4. ✅ Backend identifies and fixes issues
5. ✅ Desktop receives fixed timeline
6. ✅ Applies fixes back to MS Project:
   - Removes invalid dependencies
   - Adjusts task durations
   - Clamps percentages to 0-100
   - Adds notes to modified tasks
7. ✅ Shows success message with details
8. ✅ Re-validates automatically
9. ✅ Displays updated validation results
10. ✅ Button re-enables

**Fixes Applied**:
- ✅ Self-dependencies → Removed
- ✅ Invalid task references → Removed
- ✅ Duration < minimum → Increased to minimum
- ✅ Duration > maximum → Decreased to maximum
- ✅ Checklist % < 0 → Set to 0
- ✅ Checklist % > 100 → Set to 100

**Not Auto-Fixable** (require manual review):
- ❌ Missing mandatory tasks
- ❌ Wrong task category
- ❌ Incorrect operational sequence
- ❌ Circular dependencies (complex)
- ❌ Critical path issues

---

## UI Layout

Update ValidationResultsForm layout:

```
┌─ Validation Results ─────────────────────────────┐
│                                                   │
│  [Validation results text box]                   │
│                                                   │
│                                                   │
│                                                   │
│                                                   │
│ ┌──────────────┐                    ┌─────────┐  │
│ │ Auto-Fix     │                    │  Close  │  │
│ │ Issues       │                    └─────────┘  │
│ └──────────────┘                                  │
└───────────────────────────────────────────────────┘
```

**Button Location**: Bottom-left (below results)
**Button Size**: 120×30 pixels
**Button State**:
- Enabled: When validation errors exist
- Disabled: "Fixing..." (during operation)
- Hidden: Never (always show, but may say "No auto-fixable issues")

---

## Error Handling

**Backend offline**:
```
Auto-Fix Error:

No connection could be made because the target machine actively refused it.
```

**Invalid timeline data**:
```
Auto-Fix Error:

Validation error: tasks must be an array
```

**Partial fix failure**:
```
Auto-Fix Applied 3 Fixes:

✓ Removed 1 self-referencing dependencies
✓ Removed 1 invalid task references
✓ Increased 'IND Submission' duration from 1 to 30 days

Remaining Issues: 2

(Some issues require manual review)
```

**MS Project update failure**:
```
Auto-Fix Error:

Failed to update MS Project: Task with ID 5 not found.

Backend fixes were successful, but could not apply to project.
Please save and retry.
```

---

## Performance

**Operation Time**:
- Small project (<50 tasks): ~1 second
- Medium project (50-200 tasks): ~2-3 seconds
- Large project (200+ tasks): ~5-10 seconds

**Memory**:
- Timeline serialization: ~100KB for 100 tasks
- Network overhead: Minimal (local backend)
- MS Project updates: Instant (in-memory)

---

## Next Steps

After implementing this feature:
1. ✅ Test with project having all 4 error types
2. ✅ Verify fixes apply correctly to MS Project
3. ✅ Verify task notes added for duration changes
4. ✅ Test re-validation happens automatically
5. ✅ Implement Critical Path Highlighting (next guide)

---

**Implementation Time**: 1.5 hours
**Complexity**: Medium
**Dependencies**:
- Validation Results Form (already exists)
- Backend auto-fix endpoint (already implemented ✅)
