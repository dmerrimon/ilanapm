# Quick TODO - Windows VM Integration

**Status:** Settings.settings ✅ | SettingsForm ✅ | 3 tasks remaining

---

## ✅ Already Done
- [x] Settings.settings created with 3 properties
- [x] SettingsForm.cs created

---

## ⏳ TODO (3 Tasks)

### 1. Create MLAdvisoryForm.cs ⭐

**In Visual Studio:**
1. Right-click `IlanaPM.AddIn` project
2. Add → New Item → Windows Form
3. Name: `MLAdvisoryForm.cs`
4. Delete all the generated code
5. Copy the entire contents from: `desktop-addin/MLAdvisoryForm.cs`
6. Paste into the Windows file
7. Save

**What it does:** Displays ML duration predictions and risk scores

---

### 2. Update IlanaPMRibbon.cs ⭐⭐

**In Visual Studio:**
1. Open `IlanaPMRibbon.cs`
2. At the top, add: `using System.Collections.Generic;`
3. At the bottom of the class (before the closing `}`), copy and paste ALL the code from: `desktop-addin/RIBBON_BUTTONS_TO_ADD.cs`

**This adds 4 button handlers:**
- btnMLAdvisory_Click
- btnExportTeams_Click
- btnViewReport_Click
- btnSettings_Click
- PromptForWebhookUrl (helper method)

---

### 3. Update ApiClient.cs ⭐

**In Visual Studio:**
1. Open `Services/ApiClient.cs`
2. Find the existing `ValidateTimelineAsync()` method
3. After it (before the closing `}`), copy and paste ALL the code from: `desktop-addin/APICLIENT_METHODS_TO_ADD.cs`

**This adds 4 API methods:**
- GetTimelineAdvisoryAsync
- GetDurationPredictionAsync
- GetRiskScoreAsync
- SendTeamsNotificationAsync

---

### 4. Update ProjectDataWriter.cs ⭐

**In Visual Studio:**
1. Open `Services/ProjectDataWriter.cs`
2. Find the existing `WriteValidationResults()` method
3. After it (before the closing `}`), copy and paste ALL the code from: `desktop-addin/PROJECTDATAWRITER_METHOD_TO_ADD.cs`

**This adds 1 method:**
- WriteMLAdvisory (writes ML predictions to custom fields)

---

## Build & Test

### Build:
1. Build → Clean Solution
2. Build → Rebuild Solution
3. Check for 0 errors

### Test:
1. Press F5 to run
2. Open a project file in MS Project
3. Test all 5 ribbon buttons:
   - ✅ Validate Timeline (should already work)
   - ⭐ ML Advisory (NEW)
   - ⭐ Export to Teams (NEW)
   - ⭐ View Report (NEW)
   - ⭐ Settings (NEW)

---

## Files Created for You

All code is ready in these files - just copy and paste:

```
desktop-addin/
├── MLAdvisoryForm.cs                        ← Full form code
├── RIBBON_BUTTONS_TO_ADD.cs                 ← 4 button handlers
├── APICLIENT_METHODS_TO_ADD.cs              ← 4 API methods
└── PROJECTDATAWRITER_METHOD_TO_ADD.cs       ← 1 write-back method
```

---

## After Completion

When all 3 tasks are done and tested:

✅ Phase 3 will be 100% complete!
✅ All SOW requirements met
✅ Ready for packaging and distribution

**Estimated time:** 30-45 minutes

Good luck! 🚀
