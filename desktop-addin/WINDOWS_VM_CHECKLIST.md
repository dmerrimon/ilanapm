# Windows VM Integration Checklist

**Last Updated:** 2026-01-15
**Status:** Phase 3 - 75% Complete (Backend + Services ✅, Windows UI Forms ⏳)

---

## Prerequisites

✅ Backend deployed: https://ilanapm.azurewebsites.net
✅ All 7 service files created on Mac and ready for sync
⏳ Windows VM with Visual Studio 2022 + MS Project

---

## Step-by-Step Integration Tasks

### TASK 1: Sync Files from Mac to Windows VM

**Method:** Git pull or manual copy

**Files to sync:**
```
Mac → Windows
desktop-addin/ThisAddIn.cs                          → IlanaPM.AddIn\ThisAddIn.cs
desktop-addin/ApiClient.cs                          → IlanaPM.AddIn\Services\ApiClient.cs
desktop-addin/Services/ProjectDataExtractor.cs      → IlanaPM.AddIn\Services\ProjectDataExtractor.cs
desktop-addin/Services/ProjectDataWriter.cs         → IlanaPM.AddIn\Services\ProjectDataWriter.cs (NEW)
desktop-addin/Services/ViewManager.cs               → IlanaPM.AddIn\Services\ViewManager.cs (NEW)
desktop-addin/Models/MLModels.cs                    → IlanaPM.AddIn\Models\MLModels.cs (NEW)
desktop-addin/Models/TeamsNotification.cs           → IlanaPM.AddIn\Models\TeamsNotification.cs (NEW)
```

**Add new files to Visual Studio project:**
- Right-click project → Add → Existing Item
- Select each NEW file and add to project

---

### TASK 2: Create MLAdvisoryForm.cs

**In Visual Studio:**
1. Right-click `IlanaPM.AddIn` project
2. Add → New Item → Windows Form
3. Name: `MLAdvisoryForm.cs`
4. Replace code with content from WINDOWS_INTEGRATION_GUIDE.md (lines 62-169)

**What it does:**
- Displays ML duration predictions
- Shows risk scores and explanations
- Presents high-risk task warnings
- Read-only scrollable text display

---

### TASK 3: Create SettingsForm.cs

**In Visual Studio:**
1. Right-click `IlanaPM.AddIn` project
2. Add → New Item → Windows Form
3. Name: `SettingsForm.cs`
4. Replace code with content from WINDOWS_INTEGRATION_GUIDE.md (lines 185-349)

**What it does:**
- Configure API base URL
- Set Teams webhook URL
- Enable/disable auto-update
- Test API connection

---

### TASK 4: Add Settings.settings File

**In Visual Studio:**
1. Right-click `IlanaPM.AddIn` project
2. Add → New Item → Search "Settings File"
3. Name: `Settings.settings`

**In Settings Designer, add 3 properties:**

| Name | Type | Scope | Default Value |
|------|------|-------|---------------|
| ApiBaseUrl | string | User | https://ilanapm.azurewebsites.net |
| TeamsWebhookUrl | string | User | (empty) |
| AutoUpdateEnabled | bool | User | True |

---

### TASK 5: Update IlanaPMRibbon.cs with 4 New Buttons

**Add these 4 button handlers to IlanaPMRibbon.cs:**

Copy code from WINDOWS_INTEGRATION_GUIDE.md lines 375-566:

1. **btnMLAdvisory_Click** (lines 376-408)
   - Calls `/api/v1/advisory/timeline` endpoint
   - Writes ML predictions to custom fields
   - Shows MLAdvisoryForm

2. **btnExportTeams_Click** (lines 411-500)
   - Prompts for webhook URL
   - Sends validation summary to Teams
   - Uses Adaptive Card format

3. **btnViewReport_Click** (lines 503-558)
   - Shows view selection menu
   - Creates custom MS Project views
   - 4 views: Validation Summary, Risk Dashboard, Executive Summary, Checklist

4. **btnSettings_Click** (lines 561-565)
   - Opens SettingsForm
   - Allows configuration management

**Also update:** Add `using System.Collections.Generic;` at top of file

---

### TASK 6: Update ApiClient.cs with ML and Teams Methods

**Add these 3 methods to Services/ApiClient.cs:**

```csharp
public async Task<Models.TimelineAdvisory> GetTimelineAdvisoryAsync(Models.Timeline timeline)
{
    string jsonContent = JsonConvert.SerializeObject(timeline);
    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
    HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/advisory/timeline", content);
    response.EnsureSuccessStatusCode();
    string responseBody = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<Models.TimelineAdvisory>(responseBody);
}

public async Task<Models.DurationPrediction> GetDurationPredictionAsync(Models.Task task)
{
    string jsonContent = JsonConvert.SerializeObject(task);
    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
    HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/advisory/duration", content);
    response.EnsureSuccessStatusCode();
    string responseBody = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<Models.DurationPrediction>(responseBody);
}

public async Task<Models.RiskScore> GetRiskScoreAsync(Models.Task task)
{
    string jsonContent = JsonConvert.SerializeObject(task);
    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
    HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/advisory/risk", content);
    response.EnsureSuccessStatusCode();
    string responseBody = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<Models.RiskScore>(responseBody);
}

public async Task<bool> SendTeamsNotificationAsync(Models.TeamsNotificationRequest notification)
{
    string jsonContent = JsonConvert.SerializeObject(notification);
    var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
    HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/teams/notify", content);
    return response.IsSuccessStatusCode;
}
```

---

### TASK 7: Update ProjectDataWriter.cs with ML Write-Back

**Add this method to Services/ProjectDataWriter.cs:**

```csharp
public void WriteMLAdvisory(Application projectApp, string taskId, Models.DurationPrediction prediction, Models.RiskScore riskScore)
{
    if (projectApp.ActiveProject == null)
        throw new System.Exception("No active project found.");

    Project activeProject = projectApp.ActiveProject;
    var task = FindTaskById(activeProject, taskId);

    if (task != null)
    {
        try
        {
            if (prediction != null)
            {
                string durationRange = string.Format("{0}-{1} days",
                    prediction.confidence_interval.lower,
                    prediction.confidence_interval.upper);
                SetTaskText(task, PjCustomField.pjCustomTaskText6, durationRange);
                SetTaskNumber(task, PjCustomField.pjCustomTaskNumber3, (int)(prediction.confidence_score * 100));

                string note = string.Format("ML Duration Prediction: {0}\r\n\r\n", prediction.explanation);
                AppendTaskNote(task, note);
            }

            if (riskScore != null)
            {
                SetTaskNumber(task, PjCustomField.pjCustomTaskNumber2, riskScore.risk_score);

                string riskFactors = string.Join("\r\n- ", riskScore.risk_factors);
                string note = string.Format("Risk Analysis [{0}]:\r\n- {1}\r\n\r\n",
                    riskScore.risk_level.ToUpper(), riskFactors);
                AppendTaskNote(task, note);
            }
        }
        catch (System.Exception ex)
        {
            System.Diagnostics.Debug.WriteLine("Error writing ML advisory: " + ex.Message);
        }
    }
}
```

---

## Build Checklist

**Before building:**
- [ ] All files synced from Mac
- [ ] All new files added to VS project
- [ ] MLAdvisoryForm.cs created
- [ ] SettingsForm.cs created
- [ ] Settings.settings created with 3 properties
- [ ] IlanaPMRibbon.cs updated with 4 button handlers
- [ ] ApiClient.cs updated with ML/Teams methods
- [ ] ProjectDataWriter.cs updated with WriteMLAdvisory method

**Build steps:**
1. Build → Clean Solution
2. Build → Rebuild Solution
3. Check Error List for issues
4. Fix any missing references (Ctrl+. for quick actions)

**Expected result:** 0 Errors, 0 Warnings

---

## Testing Checklist

### Test 1: Custom Fields ✅ (Already Working)
- [x] Fields created on demand
- [x] Risk Score populated
- [x] Task notes populated
- [x] Gating Status functional

### Test 2: ML Advisory (NEW)
- [ ] Click "ML Advisory" button
- [ ] Verify MLAdvisoryForm displays
- [ ] Check duration predictions shown
- [ ] Check risk scores shown
- [ ] Verify "ML Predicted Duration" custom field populated
- [ ] Verify "ML Confidence %" custom field populated
- [ ] Check task notes include ML explanations

### Test 3: Teams Export (NEW)
- [ ] Get Teams incoming webhook URL
- [ ] Click "Export to Teams" button
- [ ] Enter webhook URL in prompt
- [ ] Check Teams channel for notification
- [ ] Verify Adaptive Card displays validation summary
- [ ] Verify high-risk tasks listed

### Test 4: View Reports (NEW)
- [ ] Click "View Report" button
- [ ] Select "Validation Summary" view
- [ ] Verify custom fields visible in table
- [ ] Test "Risk Dashboard" view
- [ ] Test "Executive Summary" view
- [ ] Test "Checklist Completion" view

### Test 5: Settings (NEW)
- [ ] Click "Settings" button
- [ ] Modify API URL
- [ ] Click "Test Connection" - should succeed
- [ ] Enter Teams webhook URL
- [ ] Toggle auto-update checkbox
- [ ] Click "Save"
- [ ] Reopen Settings - verify values persisted

---

## Common Issues & Solutions

### Issue: Duplicate InitializeComponent
**Solution:** Use Visual Studio designer, don't manually add InitializeComponent()

### Issue: 'PjField' does not contain 'pjTaskField'
**Solution:** Already fixed - using ConvertCustomFieldToPjField() mapping

### Issue: Ambiguous Exception reference
**Solution:** Already fixed - using System.Exception fully qualified

### Issue: Custom fields not showing
**Solution:** Already fixed - EnsureCustomFields() called before validation

### Issue: ML endpoints return 404
**Solution:** Verify backend deployment at https://ilanapm.azurewebsites.net/docs

### Issue: Teams notification fails
**Solution:** Test webhook URL in Postman first, verify JSON format

---

## After Successful Testing

**Commit to Git:**
```bash
git add .
git commit -m "Complete Phase 3 desktop add-in - all SOW requirements met

- Custom fields: 10 fields created and populated ✅
- Data write-back: validation + ML results ✅
- ML advisory: duration predictions + risk scoring ✅
- Teams integration: webhook notifications ✅
- Custom views: 4 views for different stakeholders ✅
- Settings UI: API configuration ✅
- Ribbon UI: All 5 buttons functional ✅

Phase 3 Status: 100% Complete
Ready for internal testing and pilot distribution."

git push origin main
```

---

## Next Phase: Packaging & Distribution

After Windows VM integration complete:

1. **Internal Testing** (1 week)
   - Use daily in real projects
   - Document any bugs or UX issues
   - Test all features end-to-end

2. **Create MSI Installer**
   - Use ClickOnce or WiX installer
   - Include all dependencies
   - Auto-update capability

3. **User Documentation**
   - Quick start guide
   - Feature overview
   - Troubleshooting section

4. **Pilot Distribution**
   - 3-5 trusted users
   - Gather feedback
   - Iterate based on usage

---

## Progress Tracking

**Phase 3 Milestones:**
- [x] Milestone 1: Custom Fields (Days 1-2)
- [x] Milestone 2: Data Write-Back (Days 3-4)
- [ ] Milestone 3: ML Advisory Integration (Days 5-6) ← **YOU ARE HERE**
- [ ] Milestone 4: Teams Integration (Day 7)
- [ ] Milestone 5: Custom Views (Days 8-9)
- [ ] Milestone 6: Settings UI (Day 10)

**Overall Progress:** 75% → Target: 100%

---

## Backend Endpoints Available

All endpoints are live at https://ilanapm.azurewebsites.net:

✅ POST /api/v1/validate
✅ POST /api/v1/advisory/timeline
✅ POST /api/v1/advisory/duration
✅ POST /api/v1/advisory/risk
✅ POST /api/v1/teams/notify
✅ GET  /api/v1/health
✅ GET  /docs (API documentation)

**Test health endpoint:**
```
curl https://ilanapm.azurewebsites.net/api/v1/health
```

---

## Summary

**What's working:** Backend (100%), Core services (100%), Basic validation (100%)
**What's next:** Windows UI forms (MLAdvisory, Settings, Views, Teams export)
**Time estimate:** 2-3 hours on Windows VM
**Expected outcome:** Complete Phase 3, ready for packaging

**Key principle:** Copy code exactly from WINDOWS_INTEGRATION_GUIDE.md to avoid API compatibility issues.

Good luck with the Windows VM integration! 🚀
