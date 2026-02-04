# Testing Guide - Authority-Specific Templates

## Pre-Testing: Deployment

### Backend Deployment (if using Render)
1. Push triggers automatic deployment on Render
2. Wait for deployment to complete (~5-10 minutes)
3. Check deployment status at: https://dashboard.render.com
4. Verify backend is running: https://ilanapm.onrender.com/docs

### Desktop Build
1. Open solution in Visual Studio (Windows)
2. Build → Rebuild Solution
3. Verify no compilation errors
4. Install/Update add-in:
   - Close MS Project
   - Run installer or copy DLL to add-in directory
   - Reopen MS Project
5. Verify add-in loaded: Check "IlanaPM" tab appears

## Test Scenario 1: Country List in Wizard (22 Countries)

**Goal:** Verify all 22 countries appear in Clinical Project Manager Wizard

### Steps:
1. Open MS Project
2. Click **IlanaPM** tab → **Clinical Project Manager**
3. Step 1: Study Configuration
4. Scroll through "Countries (Select all that apply):" list

### Expected Results:
✓ Should see **22 countries** including:
- United States
- Canada
- Mexico
- Peru
- United Kingdom
- South Africa
- Kenya
- **Uganda** ⭐
- Tanzania
- Zimbabwe
- Malawi
- Liberia
- Mali
- Sierra Leone
- Guinea
- DRC
- Australia
- Bangladesh
- China
- India
- Thailand
- Vietnam

### What to Check:
- [ ] All 22 countries listed
- [ ] Uganda is in the list
- [ ] Countries are readable (not codes)

---

## Test Scenario 2: Add Site with Country Dropdown

**Goal:** Verify country input is now a dropdown with ISO codes

### Steps:
1. In Clinical Project Manager Wizard, go to Step 2: Site Management
2. Click **Add Site**
3. Look at the "Country Code" field

### Expected Results:
✓ Should see **dropdown** (not text box)
✓ Dropdown should contain **22 country codes**: US, CA, MX, PE, GB, ZA, KE, UG, TZ, ZW, MW, LR, ML, SL, GN, CD, AU, BD, CN, IN, TH, VN

### What to Check:
- [ ] Field is dropdown (not text input)
- [ ] Label says "Country Code:" (not "Country:")
- [ ] All 22 codes visible in dropdown
- [ ] Can select "UG" for Uganda
- [ ] Can select "GB" for United Kingdom

### Test Adding a Uganda Site:
1. Site ID: `SITE-UG-001`
2. Site Name: `Kampala Medical Center`
3. Country Code: Select **UG** from dropdown
4. Status: Active
5. Principal Investigator: Dr. John Doe
6. Click OK

### Expected Results:
✓ Site added successfully
✓ Site grid shows:
  - Site ID: SITE-UG-001
  - Site Name: Kampala Medical Center
  - Country: UG (or "Uganda")

---

## Test Scenario 3: Uganda Site Startup Template

**Goal:** Verify Uganda templates show NDA, UNCST, and EC with specific task names

### Steps:
1. Continue wizard to Step 3: Template Selection
2. Check **Site Startup**
3. Continue to Step 4: Configuration
4. In "Sites for Startup", check **SITE-UG-001**
5. Click **Generate**

### Expected Results:

#### Critical: Authority-Specific Task Names
You should see these **specific** task names (not generic):

✓ **"Submit to Institutional Ethics Committee (EC)"**
  - NOT "Submit to Ethics Committee"

✓ **"Submit to National Drug Authority (NDA)"**
  - NOT "Submit to Regulatory Authority"

✓ **"Obtain UNCST Research Permit"**
  - This is a separate task (not combined)
  - Should be gated (dependent) on NDA approval

✓ **Site Readiness Tasks:**
  - Site Assessment Visit - SITE-UG-001
  - Essential Documents Collection - SITE-UG-001
  - Site Initiation Visit (SIV) - SITE-UG-001
  - GCP Training Completion - SITE-UG-001
  - Site Activation - SITE-UG-001

#### Task Count:
- **Total tasks: 9** (4 regulatory + 5 site readiness)

### What to Check:
- [ ] Task names mention "NDA" specifically
- [ ] Task names mention "UNCST" specifically
- [ ] Task names mention "EC" or "Ethics Committee"
- [ ] "Obtain UNCST Research Permit" is separate task
- [ ] UNCST task depends on NDA task (check predecessors)

### Custom Fields to Check:

Open **Add Columns** and verify these custom fields are populated:

| Field | Expected Value |
|-------|----------------|
| **Regulatory Authority (Text1)** | Should show "NDA", "UNCST", "EC" on different tasks |
| **Authority Type (Text16)** | Should show "regulatory", "ethics", "permits" |
| **Submission Form (Text17)** | Should show "Clinical Trial Application", "UNCST Research Permit Application", "Ethics Application" |
| **Site IDs (Text7)** | Should show "SITE-UG-001" |
| **Site (Text11)** | Should show "Kampala Medical Center" |
| **Task Category (Text4)** | Should show "Regulatory", "Site" |
| **Is Mandatory (Flag1)** | Should show "Yes" |

### Screenshot Checklist:
- [ ] Take screenshot of gantt chart showing task names
- [ ] Take screenshot of custom field columns
- [ ] Take screenshot of task dependencies

---

## Test Scenario 4: UK Site Startup Template

**Goal:** Verify UK templates show MHRA and REC with IRAS Application

### Steps:
1. Add a new site:
   - Site ID: `SITE-GB-001`
   - Site Name: `London Clinical Research Centre`
   - Country Code: **GB**
2. Generate Site Startup template for SITE-GB-001

### Expected Results:

#### Critical: Authority-Specific Task Names
You should see these **specific** task names:

✓ **"Submit IRAS Application to REC"**
  - NOT "Submit to Ethics Committee"
  - Should mention "IRAS" specifically

✓ **"Submit Clinical Trial Authorization (CTA) to MHRA"**
  - NOT "Submit to Regulatory Authority"
  - Should mention "MHRA" specifically

✓ **Site Readiness Tasks** (5 tasks)

#### Task Count:
- **Total tasks: 7** (2 regulatory + 5 site readiness)

### Custom Fields to Check:

| Field | Expected Value |
|-------|----------------|
| **Regulatory Authority (Text1)** | Should show "MHRA", "REC" |
| **Authority Type (Text16)** | Should show "regulatory", "ethics" |
| **Submission Form (Text17)** | Should show "IRAS Application", "Clinical Trial Authorization (CTA)" |
| **Site IDs (Text7)** | Should show "SITE-GB-001" |

### What to Check:
- [ ] Task mentions "IRAS Application"
- [ ] Task mentions "MHRA"
- [ ] Task mentions "REC" (Research Ethics Committee)
- [ ] Custom fields populated

---

## Test Scenario 5: Kenya Site Startup (Three-Layer Workflow)

**Goal:** Verify Kenya shows three-layer sequential workflow (EC → PPB → NACOSTI)

### Steps:
1. Add Kenya site:
   - Site ID: `SITE-KE-001`
   - Site Name: `Nairobi Research Institute`
   - Country Code: **KE**
2. Generate Site Startup template

### Expected Results:

#### Three Regulatory Tasks (Sequential):
1. **Submit to Institutional Ethics Committee (EC)**
2. **Submit to Pharmacy and Poisons Board (PPB)**
   - Should depend on EC task
3. **Obtain NACOSTI Research Clearance**
   - Should depend on PPB task

#### Task Count:
- **Total tasks: 8** (3 regulatory + 5 site readiness)

### What to Check:
- [ ] Three regulatory tasks visible
- [ ] PPB task depends on EC task (check predecessors)
- [ ] NACOSTI task depends on PPB task
- [ ] All three authorities show in Regulatory Authority column

---

## Test Scenario 6: Apply Filters

**Goal:** Verify custom field filtering works

### Filter 1: Regulatory Tasks Only
1. Click **View** tab → **Filter** → **New Filter**
2. Name: "Regulatory Tasks"
3. Field: Text4 (Task Category)
4. Test: equals
5. Value: Regulatory
6. Apply filter

### Expected Results:
✓ Should see only regulatory tasks (EC, NDA, UNCST, etc.)
✓ Site readiness tasks should be hidden

### Filter 2: Tasks by Authority
1. Create new filter
2. Name: "NDA Tasks"
3. Field: Text1 (Regulatory Authority)
4. Test: equals
5. Value: NDA
6. Apply filter

### Expected Results:
✓ Should see only tasks with "NDA" in Regulatory Authority field

### Filter 3: Uganda Tasks Only
1. Create new filter
2. Field: Text7 (Site IDs)
3. Test: equals
4. Value: SITE-UG-001
5. Apply filter

### Expected Results:
✓ Should see only Uganda site tasks

---

## Test Scenario 7: Group by Authority

**Goal:** Verify grouping works with new custom fields

### Steps:
1. Remove all filters (show all tasks)
2. Click **View** tab → **Group By** → **Customize Group By**
3. Group by: Text1 (Regulatory Authority)
4. Apply grouping

### Expected Results:
✓ Tasks should be grouped by authority:
  - EC group
  - NDA group
  - UNCST group
  - MHRA group (if UK site exists)
  - etc.

---

## Test Scenario 8: Site Closeout Template

**Goal:** Verify closeout templates also have authority-specific details

### Steps:
1. Go back to wizard or start new project
2. Select **Site Closeout** template
3. Select SITE-UG-001
4. Generate

### Expected Results:

#### Uganda Site Closeout Tasks:
✓ **"Submit Completion Report to NDA"**
  - NOT "Submit to Regulatory Authority"

✓ **"Submit Final Report to UNCST"**
  - Separate task for UNCST

✓ **"Notify Institutional Ethics Committee"** or **"Submit Final Report to EC"**

✓ **Closeout monitoring tasks:**
  - Final Monitoring Visit
  - IP Accountability & Return
  - Essential Documents Archiving

### What to Check:
- [ ] Authority names are specific (NDA, UNCST, EC)
- [ ] Custom fields populated
- [ ] Authority Type shows "regulatory", "ethics", "permits"

---

## Common Issues & Troubleshooting

### Issue 1: Templates still show generic names
**Symptom:** Tasks say "Submit to Regulatory Authority" instead of "Submit to National Drug Authority (NDA)"

**Possible Causes:**
- Backend not deployed yet
- Desktop still calling old CountryTemplateLibrary
- API connection issue

**Troubleshooting:**
1. Check backend URL: https://ilanapm.onrender.com/docs
2. Open browser dev tools → Network tab
3. Generate template
4. Look for API call to `/api/v1/templates/generate-site-startup`
5. If no API call, desktop may not be using new code

### Issue 2: Country dropdown doesn't appear
**Symptom:** Add Site dialog still has text box for country

**Possible Causes:**
- Desktop not rebuilt
- Using old version of add-in

**Troubleshooting:**
1. Close MS Project completely
2. Rebuild solution in Visual Studio
3. Check build output for errors
4. Reinstall add-in
5. Reopen MS Project

### Issue 3: Custom fields not populated
**Symptom:** Text16 and Text17 are empty

**Possible Causes:**
- Backend not sending authority metadata
- Desktop not setting fields

**Troubleshooting:**
1. Check API response in browser dev tools
2. Look for `authority_full_name`, `authority_type`, `submission_form` in response
3. If missing in response, backend issue
4. If present in response but not in MS Project, desktop issue

### Issue 4: Only 7-15 countries in list
**Symptom:** Country list doesn't show all 22 countries

**Possible Causes:**
- Old version of ClinicalProjectManagerForm.Designer.cs

**Troubleshooting:**
1. Check file: `ClinicalProjectManagerForm.Designer.cs` line ~277
2. Should see 22 countries in Items.AddRange
3. If only 15 countries, file wasn't updated
4. Rebuild solution

---

## Success Criteria

### ✅ Checklist

- [ ] All 22 countries appear in wizard country list
- [ ] Add Site has country dropdown (not text box)
- [ ] Uganda template shows "NDA", "UNCST", "EC" in task names
- [ ] UK template shows "MHRA", "REC", "IRAS Application"
- [ ] Kenya template shows three-layer workflow (EC → PPB → NACOSTI)
- [ ] Custom fields populated: Text1, Text16, Text17
- [ ] Site IDs and Site Names appear in gantt chart
- [ ] Filters work (Regulatory Tasks, Tasks by Authority)
- [ ] Grouping by authority works
- [ ] Site Closeout templates also show authority-specific details

### 🎉 You'll Know It Works When:

1. **You see "Submit to National Drug Authority (NDA)"** instead of "Submit to Regulatory Authority"
2. **You see "Obtain UNCST Research Permit"** as a separate task
3. **You see "Submit IRAS Application to REC"** for UK sites
4. **Custom field columns show specific authorities** (NDA, MHRA, UNCST, etc.)
5. **Filters and grouping work** with the new authority fields

---

## Reporting Issues

If something doesn't work:

1. **Take screenshots** of:
   - Task names in gantt chart
   - Custom field columns
   - Add Site dialog
   - Country list in wizard

2. **Check browser dev tools** (if API issue):
   - Network tab → Look for API calls
   - Copy API request/response

3. **Check MS Project version** and OS version

4. **Note exact steps** that reproduce the issue

Good luck with testing! 🚀
