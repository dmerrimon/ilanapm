# Copy-Paste Instructions for Windows VM

## Step 1: Update IlanaPMRibbon.cs

1. Open Visual Studio on your Windows VM
2. Navigate to: `IlanaPM.AddIn` project → `IlanaPMRibbon.cs`
3. **Replace the entire file contents** with the code from: `UPDATED_RIBBON_CODE.cs`

**Location**:
- File to edit: `desktop-addin/IlanaPM.AddIn/IlanaPMRibbon.cs`
- New code: `desktop-addin/UPDATED_RIBBON_CODE.cs`

---

## Step 2: Update SettingsForm.cs

1. In Visual Studio, navigate to: `IlanaPM.AddIn` project → `SettingsForm.cs`
2. **Replace the entire file contents** with the code from: `UPDATED_SETTINGS_CODE.cs`

**Location**:
- File to edit: `desktop-addin/IlanaPM.AddIn/SettingsForm.cs`
- New code: `desktop-addin/UPDATED_SETTINGS_CODE.cs`

---

## Step 3: Rebuild the Solution

1. In Visual Studio: **Build → Rebuild Solution** (or press Ctrl+Shift+B)
2. Wait for build to complete (should say "Build succeeded")
3. Close MS Project if it's open
4. Reopen MS Project

---

## Step 4: Test the Changes

### Test View Report Button:
1. Click **View Report** button on Ilana PM ribbon
2. You should see a dialog with 4 options:
   - Validation Summary
   - Risk Dashboard
   - Executive Summary
   - Checklist Completion
3. Select any option
4. A custom MS Project table should be created and applied
5. You should see a confirmation message

### Test Settings Button:
1. Click **Settings** button on Ilana PM ribbon
2. You should see "Ilana PM - Feedback History" dialog (NOT "Settings")
3. Should show:
   - "Feedback Collection" title
   - "Total Feedback Submitted: 0 tasks"
   - "Last Submission: Never"
   - Privacy note
   - Single "Close" button
4. No General tab, no API settings, no Teams webhook

### Test Multi-Country Button:
1. Click **Multi-Country** button
2. Should show message: "Multi-Country Calculator will be implemented in Phase 2"
3. This is the expected behavior (feature deferred)

---

## What Changed

### IlanaPMRibbon.cs:
- ✅ **View Report** now creates 4 custom MS Project views programmatically
- ✅ **Multi-Country** shows proper Phase 2 message (not just "not implemented")
- ✅ All other buttons remain the same (Validate, Critical Path, Load Template, Settings)

### SettingsForm.cs:
- ✅ Removed General tab (API URL, Teams webhook, auto-update)
- ✅ Simplified to show only feedback history
- ✅ No more AutoFeedbackService dependency (doesn't exist yet)
- ✅ Changed title from "Settings" to "Feedback History"
- ✅ Single Close button instead of Save/Cancel

---

## Troubleshooting

### "ViewManager not found" error:
- Make sure you have the ViewManager.cs file in: `IlanaPM.AddIn/Services/ViewManager.cs`
- If missing, copy it from Mac

### "SubmittedFeedbackTasks not found" error:
- Check `Properties/Settings.settings` has this setting defined
- Type: `System.Collections.Specialized.StringCollection`

### Build errors:
- Make sure all using statements are present at the top
- Check that all referenced classes exist (ValidationResultsForm, TemplateLoaderForm, etc.)

---

## Files You Need

Make sure these files exist in your Windows VM project:

1. `IlanaPM.AddIn/IlanaPMRibbon.cs` ← UPDATE THIS
2. `IlanaPM.AddIn/SettingsForm.cs` ← UPDATE THIS
3. `IlanaPM.AddIn/Services/ViewManager.cs` ← Must exist with table creation code
4. `IlanaPM.AddIn/Services/ProjectDataExtractor.cs` ← Should already exist
5. `IlanaPM.AddIn/Services/ApiClient.cs` ← Should already exist
6. `IlanaPM.AddIn/Services/TemplateLoader.cs` ← Should already exist
7. `IlanaPM.AddIn/Properties/Settings.settings` ← Should have SubmittedFeedbackTasks

---

**Ready to test!**
