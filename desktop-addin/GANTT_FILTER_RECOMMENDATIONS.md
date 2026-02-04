# MS Project Gantt Chart Filter Recommendations for Clinical Trial Projects

## Available Custom Fields

Based on your IlanaPM add-in, the following custom fields are available:

| Field | Description | Values |
|-------|-------------|--------|
| **Text1** | Regulatory Authority | "FDA", "MHRA", "NDA", "UNCST", "EC", etc. |
| **Text2** | Study Phase | "Phase I", "Phase II", "Phase III", "Phase IV" |
| **Text3** | Therapeutic Area | "Oncology", "Cardiology", "Infectious Disease", etc. |
| **Text4** | Task Category | "Regulatory", "Operational", "Site", "Data", "Pharmacy", etc. |
| **Text5** | Gating Status | "Blocked", "Ready", "Complete", "Not Applicable" |
| **Text6** | ML Predicted Duration | AI-predicted duration range |
| **Text7** | Site IDs | "SITE-001", "SITE-002", etc. |
| **Text9** | Cohort IDs | Cohort identifiers |
| **Text11** | Site (Name) | Full site name |
| **Text16** | Authority Type | "regulatory", "ethics", "permits" |
| **Text17** | Submission Form | "IRAS Application", "IND", "CTA", etc. |
| **Number1** | Checklist Completion % | 0-100 |
| **Number2** | Risk Score | 0-100 (ML-predicted delay risk) |
| **Number3** | ML Confidence % | 0-100 |
| **Flag1** | Is Mandatory | True/False |

## Top 10 Recommended Filters

### 1. Regulatory Tasks Only
**Purpose:** View only regulatory submission and approval tasks

**Filter Definition:**
- Text4 (Task Category) equals "Regulatory"

**Use Case:** Focus on critical path regulatory activities

---

### 2. Tasks by Authority
**Purpose:** View tasks for a specific regulatory authority

**Filter Definition:**
- Text1 (Regulatory Authority) equals "MHRA" (or "NDA", "FDA", etc.)

**Use Case:** Track progress with specific authorities (e.g., all MHRA tasks)

---

### 3. Mandatory Tasks Only
**Purpose:** View only mandatory tasks (exclude optional tasks)

**Filter Definition:**
- Flag1 (Is Mandatory) equals "Yes"

**Use Case:** Focus on critical required activities

---

### 4. High Risk Tasks
**Purpose:** View tasks with high ML-predicted delay risk

**Filter Definition:**
- Number2 (Risk Score) is greater than or equal to 70

**Use Case:** Proactively manage high-risk tasks

---

### 5. Incomplete Checklists
**Purpose:** View tasks with incomplete checklists

**Filter Definition:**
- Number1 (Checklist Completion %) is less than 100

**Use Case:** Track tasks needing attention

---

### 6. Site-Specific Tasks
**Purpose:** View tasks for a specific site

**Filter Definition:**
- Text7 (Site IDs) equals "SITE-001" (or other site)

**Alternative:**
- Text11 (Site) equals "Kampala Medical Center"

**Use Case:** Focus on single site activities

---

### 7. Blocking Tasks (Critical Path)
**Purpose:** View tasks that are blocking other tasks

**Filter Definition:**
- Text5 (Gating Status) equals "Blocked"

**Use Case:** Identify and resolve blockers

---

### 8. Tasks by Authority Type
**Purpose:** View tasks by authority category

**Filter Definition:**
- Text16 (Authority Type) equals "ethics" (or "regulatory", "permits")

**Use Case:** Group by approval type (all ethics submissions, all permits, etc.)

---

### 9. Multi-Filter: Critical Regulatory Tasks
**Purpose:** Most critical regulatory tasks

**Filter Definition:**
- Text4 (Task Category) equals "Regulatory"
- AND Flag1 (Is Mandatory) equals "Yes"
- AND Number2 (Risk Score) is greater than 70

**Use Case:** Focus on highest-priority regulatory activities

---

### 10. Site Startup Tasks for Specific Country
**Purpose:** View site activation tasks for a country

**Filter Definition:**
- Text4 (Task Category) equals "Site"
- AND Text11 (Site) contains "Uganda" (or other country)

**Use Case:** Track site activation by country

---

## How to Create Filters in MS Project

### Method 1: AutoFilter (Quick Filtering)
1. Click **View** tab → **Filter** → **Display AutoFilter**
2. Click dropdown arrows in column headers
3. Select values to filter

### Method 2: Custom Filter
1. Click **View** tab → **Filter** → **New Filter**
2. Name your filter (e.g., "High Risk Regulatory Tasks")
3. Define criteria:
   - Field Name: Text4
   - Test: equals
   - Value(s): Regulatory
4. Click **Insert Row** to add AND/OR conditions
5. Save filter

### Method 3: Filter Toolbar
1. Right-click toolbar area → select **Filter**
2. Use dropdown to select predefined filters
3. Click **More Filters** to access all filters

## Recommended Filter Sets by Role

### Project Manager
1. ✓ High Risk Tasks
2. ✓ Blocking Tasks
3. ✓ Mandatory Tasks Only
4. ✓ Incomplete Checklists

### Regulatory Affairs
1. ✓ Regulatory Tasks Only
2. ✓ Tasks by Authority (MHRA, FDA, etc.)
3. ✓ Tasks by Authority Type (ethics, regulatory, permits)
4. ✓ Multi-Filter: Critical Regulatory Tasks

### Site Manager
1. ✓ Site-Specific Tasks
2. ✓ Site Startup Tasks for Specific Country
3. ✓ Tasks by Authority (for local authority)

### Data Manager
1. ✓ Filter by Task Category = "Data"
2. ✓ Incomplete Checklists
3. ✓ High Risk Tasks

## Advanced Tips

### 1. Highlight Critical Authority Submissions
Create a filter showing tasks where:
- Text17 (Submission Form) contains "IND" OR "CTA" OR "IRAS"
- Shows major regulatory submissions across all authorities

### 2. Multi-Country Regulatory View
Filter by:
- Text4 (Task Category) equals "Regulatory"
- Group by Text1 (Regulatory Authority)
- Shows all regulatory tasks organized by authority

### 3. Authority-Specific Submission Pipeline
Filter by:
- Text1 (Regulatory Authority) equals "NDA"
- Text16 (Authority Type) equals "regulatory"
- Shows complete submission pipeline for specific authority

### 4. Site Activation Readiness
Filter by:
- Text4 (Task Category) equals "Site"
- Number1 (Checklist Completion %) is greater than or equal to 80
- Shows sites near activation

## Grouping Recommendations

Combine filters with grouping for powerful views:

1. **Group by Regulatory Authority** → Filter by Regulatory Tasks
   - Shows regulatory tasks organized by authority (MHRA, FDA, NDA, etc.)

2. **Group by Site** → Filter by Mandatory Tasks
   - Shows critical tasks organized by site

3. **Group by Task Category** → Filter by High Risk
   - Shows high-risk tasks organized by category

4. **Group by Authority Type** → No filter
   - Shows all tasks grouped by ethics/regulatory/permits

## Color-Coding Recommendations

Apply conditional formatting based on:
- **Red**: Number2 (Risk Score) ≥ 80
- **Yellow**: Number2 (Risk Score) 50-79
- **Green**: Number2 (Risk Score) < 50
- **Blue**: Flag1 (Is Mandatory) = Yes
- **Purple**: Text16 (Authority Type) = "regulatory"
