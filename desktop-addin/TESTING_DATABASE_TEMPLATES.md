# Testing Database Template Integration

**Date:** 2026-02-13
**Status:** Ready for Testing

---

## Prerequisites

### Required Software
- ✅ Windows 10/11
- ✅ Microsoft Project (Desktop version)
- ✅ Visual Studio 2019/2022 with VSTO development tools
- ✅ Backend API running on `localhost:8000`

### Before Testing

1. **Start Backend API** (if not already running):
   ```bash
   cd backend
   source venv/bin/activate  # or: venv\Scripts\activate on Windows
   python -m uvicorn main:app --reload --port 8000
   ```

2. **Verify API is responding**:
   ```bash
   curl http://localhost:8000/api/v1/templates/library
   ```
   Should return JSON with 6 templates (TPL_001 through TPL_006)

3. **Build the Desktop Add-in**:
   - Open `desktop-addin/IlanaPM.AddIn/IlanaPM.AddIn.sln` in Visual Studio
   - Build → Rebuild Solution
   - Check for compilation errors
   - If successful, the add-in will auto-register with MS Project

---

## Test Plan

### Test 1: Full Study Timeline (TPL_006)

**Purpose:** Test the most comprehensive database template

**Steps:**
1. Open Microsoft Project (blank project)
2. Click **Seleen** ribbon → **Clinical Project Manager** button
3. **Step 1 - Study Configuration:**
   - Study Name: `TEST-DB-001`
   - Study Phase: `Phase III`
   - Therapeutic Area: `Oncology`
   - Countries: Check `United States`
   - Click **Next**

4. **Step 2 - Sites:**
   - Click **Next** (no sites needed for Full Study Timeline)

5. **Step 3 - Template Selection:**
   - Scroll down to "Database Templates (NEW - Recommended)" section
   - Check: **DB: Full Study Timeline (119 tasks, 1260 days) - TPL_006**
   - Click **Next**

6. **Step 4 - Configuration:**
   - No sites to select (Full Study Timeline is not site-specific)
   - Click **Next**

7. **Step 5 - Preview:**
   - Verify preview shows: "DB: Full Study Timeline" with 119 tasks
   - Click **Generate**

**Expected Results:**
- ✅ Progress dialog appears ("Fetching template from database...")
- ✅ Success message: "Successfully generated 119 tasks!"
- ✅ MS Project shows 119 tasks with:
  - Proper task hierarchy (outline levels)
  - Durations populated
  - Task names from database
  - Categories visible in custom fields

**Verification:**
```
Total Tasks: 119
Duration Range: 1260 days (3.5 years)
Hierarchy: Multiple outline levels
Dependencies: Should have predecessor relationships
```

---

### Test 2: Study Start-Up (TPL_001)

**Purpose:** Test template with complex dependencies

**Steps:**
1. **New blank project** in MS Project
2. Open Clinical Project Manager
3. **Step 1:** Study Name: `TEST-DB-002`, Phase III, Oncology, US
4. **Step 2:** Skip (no sites)
5. **Step 3:** Check **DB: Study Start-Up (86 tasks, 180 days) - TPL_001**
6. **Step 4:** Skip
7. **Step 5:** Generate

**Expected Results:**
- ✅ 86 tasks created
- ✅ 52 dependencies created (check Predecessor column)
- ✅ Tasks organized by category:
  - Initiation (Study Award, Protocol Development)
  - Legal/Finance (Budgets, Contracts)
  - Meetings (Kick-off, Planning)
  - Project Plans (Study Plan, Monitoring Plan)
  - Systems Setup (CTMS, EDC, IWRS)
  - Drug Supply (IMP Manufacturing, Labeling)
  - Vendors (CRO, Lab, Imaging)
  - Training (Investigator Training)

**Verification:**
```
Total Tasks: 86
Dependencies: 52 predecessor relationships
Duration: 180 days
Last Task: "First Patient In (FPI)"
```

---

### Test 3: Site Activation (TPL_004)

**Purpose:** Test site-specific template with multiple sites

**Steps:**
1. **New blank project** in MS Project
2. Open Clinical Project Manager
3. **Step 1:** Study Name: `TEST-DB-003`, Phase III, Oncology, US
4. **Step 2 - Add Sites:**
   - Click **Add Site**
   - Site ID: `SITE-001`, Name: `Memorial Hospital`, Country: `US`, Status: `Pending`, PI: `Dr. Smith`
   - Click OK
   - Click **Add Site** again
   - Site ID: `SITE-002`, Name: `City Medical Center`, Country: `US`, Status: `Pending`, PI: `Dr. Jones`
   - Click OK
   - Click **Next**

5. **Step 3:** Check **DB: Site Activation (34 tasks per site, 90 days) - TPL_004**
6. **Step 4 - Site Selection:**
   - **Sites for DB: Site Activation** group should be visible
   - Check both `SITE-001` and `SITE-002`
   - Click **Next**

7. **Step 5:**
   - Verify preview shows: "DB: Site Activation" for SITE-001 (34 tasks)
   - Verify preview shows: "DB: Site Activation" for SITE-002 (34 tasks)
   - Total: 68 tasks
   - Click **Generate**

**Expected Results:**
- ✅ 68 tasks created (34 per site × 2 sites)
- ✅ Tasks grouped by site (check Text11 custom field for Site ID)
- ✅ Each site has same task structure:
  - Site Selection
  - Feasibility Assessment
  - Site Contract Negotiation
  - IRB/Ethics Committee Submission
  - IRB/Ethics Committee Approval
  - Site Initiation Visit
  - Investigator Training
  - Site Activation Complete

**Verification:**
```
Total Tasks: 68 (34 × 2 sites)
Site Groups: 2 (SITE-001, SITE-002)
Duration per site: 90 days
Text11 field: Contains site IDs
```

---

### Test 4: Multiple Database Templates

**Purpose:** Test combining multiple database templates

**Steps:**
1. **New blank project**
2. Open Clinical Project Manager
3. **Step 1:** Study Name: `TEST-DB-004`, Phase III, Oncology, US
4. **Step 2:** Add SITE-001
5. **Step 3:** Check:
   - **DB: Study Start-Up (86 tasks)** - TPL_001
   - **DB: Study Implementation (10 milestones)** - TPL_002
   - **DB: Study Closeout (23 tasks)** - TPL_003
   - **DB: Site Activation (34 tasks per site)** - TPL_004
6. **Step 4:** Select SITE-001 for Site Activation
7. **Step 5:** Generate

**Expected Results:**
- ✅ Total tasks: 86 + 10 + 23 + 34 = 153 tasks
- ✅ All templates integrated into single timeline
- ✅ Each template maintains its structure

---

## Test Checklist

### Functionality Tests

- [ ] **Test 1:** Full Study Timeline (119 tasks) generates successfully
- [ ] **Test 2:** Study Start-Up (86 tasks, 52 dependencies) generates with predecessors
- [ ] **Test 3:** Site Activation (34 tasks × 2 sites = 68 tasks) generates per site
- [ ] **Test 4:** Multiple templates combine correctly (153 tasks total)
- [ ] **Test 5:** Study Implementation (10 milestones) generates correctly
- [ ] **Test 6:** Study Closeout (23 tasks) generates correctly
- [ ] **Test 7:** Site Closeout (19 tasks per site) generates correctly

### Data Validation Tests

- [ ] Task names match database template definitions
- [ ] Durations populated correctly (typical_duration_days)
- [ ] Outline levels preserved (task hierarchy)
- [ ] Dependencies created (check Predecessor column)
- [ ] Lag days applied to dependencies (if any)
- [ ] Custom fields populated (Text11=Site, Text4=Category)
- [ ] Milestones marked correctly (is_milestone flag)

### UI Tests

- [ ] Step 3: Database template checkboxes appear below legacy templates
- [ ] Step 3: Panel scrolls to show all 6 database templates
- [ ] Step 4: Database site selection groups appear when templates checked
- [ ] Step 4: Groups hidden when templates unchecked
- [ ] Step 5: Preview shows database templates with accurate counts
- [ ] Step 5: Total task count includes database templates
- [ ] Validation: Error if site template checked but no sites selected

### Error Handling Tests

- [ ] Backend API offline: User gets clear error message
- [ ] Invalid template ID: Graceful error handling
- [ ] Network timeout: Appropriate timeout message
- [ ] Zero tasks returned: Error message displayed
- [ ] Template conversion failure: Error logged and shown

---

## Expected API Responses

### List Templates (GET /api/v1/templates/library)
```json
{
  "templates": [
    {
      "template_id": "TPL_001",
      "template_name": "Study Start-Up",
      "total_task_count": 86,
      "estimated_duration_days": 180
    },
    ... (5 more templates)
  ],
  "count": 6
}
```

### Get Template (GET /api/v1/templates/library/TPL_001)
```json
{
  "template": {
    "template_id": "TPL_001",
    "template_name": "Study Start-Up",
    "total_task_count": 86
  },
  "tasks": [
    {
      "task_id": "SS_INI_001",
      "task_name": "Study Award Received",
      "typical_duration_days": 1,
      "is_milestone": true,
      "outline_level": 1
    },
    ... (85 more tasks)
  ],
  "dependencies": [
    {
      "predecessor_task_id": "SS_INI_001",
      "successor_task_id": "SS_INI_002",
      "dependency_type": "finish-to-start",
      "lag_days": 0
    },
    ... (51 more dependencies)
  ]
}
```

---

## Debugging

### If tasks don't generate:

1. **Check API connection:**
   ```csharp
   // In Visual Studio, add breakpoint in:
   // UnifiedTemplateManager.cs line 283 (LoadFromDatabaseTemplateAsync)
   ```

2. **Check API response:**
   - Debug Output window should show: "Fetching template from database..."
   - Should show: "Received 86 tasks from Study Start-Up"

3. **Check backend logs:**
   ```bash
   # In backend terminal, look for:
   INFO:     127.0.0.1:xxxxx - "GET /api/v1/templates/library/TPL_001 HTTP/1.1" 200 OK
   ```

4. **Verify database:**
   ```bash
   cd backend
   sqlite3 database/feedback.db
   SELECT COUNT(*) FROM timeline_templates;  # Should return 6
   SELECT COUNT(*) FROM template_tasks;      # Should return 291
   SELECT COUNT(*) FROM template_dependencies; # Should return 75
   ```

### If dependencies don't appear:

1. **Check MS Project Predecessor column:**
   - Right-click any column header
   - Click "Insert Column"
   - Type "Predecessors"
   - Press Enter

2. **Verify dependency conversion:**
   ```csharp
   // Breakpoint in LoadFromDatabaseTemplateAsync line ~350
   // Check: templateDetail.dependencies.Count
   // Check: timeline.dependencies.Count
   ```

### If custom fields blank:

1. **Add custom field columns:**
   - Insert Column → Type "Text11" (Site)
   - Insert Column → Type "Text4" (Category)
   - Insert Column → Type "Text12" (Stage)

2. **Check ApplyToProject() call:**
   ```csharp
   // Breakpoint in GenerateFromDatabaseTemplate line ~1502
   // Verify: result.TemplateType is set
   // Verify: result.Timeline has tasks
   ```

---

## Success Criteria

### Minimum Viable Test (MVP)
- ✅ Test 1 passes: TPL_006 generates 119 tasks
- ✅ Tasks visible in MS Project
- ✅ Durations populated
- ✅ No compilation errors

### Full Success
- ✅ All 7 functionality tests pass
- ✅ All data validation tests pass
- ✅ All UI tests pass
- ✅ Error handling works correctly

---

## Known Limitations

1. **Cold Start:** First API call may take 5-10 seconds (FastAPI startup)
2. **Recurring Tasks:** TPL_002 Implementation template has recurring tasks (IRB Annual Review) - ensure these are created correctly
3. **Hard Dependencies:** TPL_003 Closeout template has hard dependencies (blocking) - verify critical path
4. **Site ID Substitution:** Site-specific templates (TPL_004, TPL_005) replace {site_id} placeholder in task names

---

## Reporting Issues

If you encounter issues, please collect:

1. **Error Message:** Exact text from error dialog
2. **Debug Output:** Visual Studio Output window (Debug category)
3. **Backend Logs:** Terminal output from uvicorn
4. **Steps to Reproduce:** Exactly what you clicked
5. **Expected vs. Actual:** What should happen vs. what happened
6. **Screenshots:** MS Project before/after generation

---

**Status:** Ready for Windows + MS Project Testing
**Next Step:** Open project in Visual Studio on Windows, rebuild, and test with MS Project
