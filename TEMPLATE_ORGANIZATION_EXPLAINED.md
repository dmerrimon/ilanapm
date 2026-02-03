# How Ilana PM Templates Are Organized

## Overview

Ilana PM templates are **dynamically generated** based on country, phase, and therapeutic area. They combine three data sources to create country-specific, phase-appropriate clinical trial timelines.

---

## Three-Source Template System

### 1. **Task Ontology** (92 Canonical Tasks)
**File:** `backend/config/task_ontology.yaml`

**Purpose:** Universal library of clinical trial tasks across all categories

**Categories (9 total):**
- **Regulatory** (25 tasks): Protocol approvals, amendments, continuing review, CSR submissions
- **Operational** (15 tasks): Protocol development, planning, coordination, MOPs
- **Site** (5 tasks): Site initiation, activation, first patient in, enrollment, LPLV
- **Data** (17 tasks): Database configuration, data entry, cleaning, lock, analysis
- **Pharmacy** (3 tasks): Randomization, blinding, study product (interventional trials only)
- **Laboratory** (13 tasks): Specimen handling, assays, central lab, database
- **Closeout** (5 tasks): Final monitoring, SAE reconciliation, archival
- **Documents** (3 tasks): eTMF, agreements, essential documents
- **Safety** (6 tasks): DSMB/SMC, SAE reporting, pharmacovigilance

**Example Tasks:**
```yaml
- id: SITE-001
  name: "Site Initiation Visit (SIV)"
  category: Site
  typical_duration_days: 1

- id: DATA-001
  name: "Clinical Database Lock"
  category: Data
  typical_duration_days: 42

- id: REG-012
  name: "IRB/EC Continuing Review"
  category: Regulatory
  typical_duration_days: 365
```

---

### 2. **Regulatory Workflows** (23 Countries)
**File:** `backend/config/regulatory_workflows.yaml`

**Purpose:** Country-specific regulatory approval processes

**Workflow Types:**
1. **Parallel** (US, UK, Canada, Australia)
   - FDA || IRB (both run simultaneously)
   - ~30 days each

2. **Sequential** (Bangladesh, Guinea, Mali, Malawi, Mexico, Peru)
   - Ethics → Regulatory (one after another)
   - ~60-90 days total

3. **Three-Layer Sequential** (Kenya)
   - EC → PPB → NACOSTI
   - ~60-90 days total

4. **Four-Layer Sequential** (Vietnam)
   - CEBRGL → ASTT → NECBR → Minister
   - ~85 days total

5. **Concurrent-Sequential** (DRC, India, Liberia, Thailand, Uganda)
   - Submit both, but regulatory waits for ethics
   - ~45-90 days

6. **Multi-Body Systems** (Tanzania, Zimbabwe)
   - Multiple oversight bodies
   - ~60-120 days

**Example: Kenya Workflow**
```yaml
- country_code: KE
  country_name: Kenya
  workflow_type: three_layer_sequential

  ethics_authority:
    code: EC
    name: "Institutional Ethics Committee (EC)"
    review_days: 30

  regulatory_authority:
    code: PPB
    name: "Pharmacy and Poisons Board"
    review_days: 30

  additional_bodies:
    - code: NACOSTI
      name: "National Commission for Science, Technology and Innovation"
      review_days: 30
```

---

### 3. **Industry-Standard Milestones** (9 Key Tasks)
**Generated in:** `backend/services/template_generator.py`

**Purpose:** Fill gaps in ontology with fundamental project milestones

**The 9 Milestones (IND-100 series):**
```
IND-100: Protocol Development (180 days)
IND-101: Data Collection Forms Development (28 days)
IND-102: Manual of Procedures (MOP) v1.0 (14 days)
IND-103: Data System Configuration (42 days)
IND-104: Site Training (3 days)
IND-105: Clinical Data Entry (4 days)
IND-106: Data Cleaning (14 days)
IND-107: Database Lock (1 day milestone)
IND-108: Clinical Study Report (CSR) (56 days)
```

**Why Separate from Ontology?**
- Ontology = detailed operational tasks (92 tasks)
- Industry milestones = high-level project phases (9 tasks)
- Both coexist: IND-107 (milestone) → DATA-001 (detailed implementation)

---

## Template Generation Process

### Step 1: User Selection
**Desktop Add-In → Load Template Button**

User selects:
- Country: Kenya
- Phase: Phase III
- Therapeutic Area: Infectious Disease
- Include Optional: Yes

### Step 2: Backend Processing
**API Call:** `POST /api/v1/templates/generate`

```json
{
  "country_code": "KE",
  "study_phase": "Phase III",
  "therapeutic_area": "Infectious Disease",
  "include_optional": true
}
```

### Step 3: Build Country-Specific Regulatory Tasks

**For Kenya (three_layer_sequential):**

Creates 3 country-specific tasks:
```
REG-KE-EC: Institutional Ethics Committee (EC) Approval - Kenya
REG-KE-REG: Pharmacy and Poisons Board Approval - Kenya
REG-KE-NACOSTI: National Commission for Science, Technology and Innovation Clearance - Kenya
```

**Dependencies:**
```
EC → PPB → NACOSTI (sequential, not parallel)
```

### Step 4: Build Ontology Tasks

**Filters from 92 ontology tasks:**

**Include:**
- All Operational tasks (15)
- All Site tasks (5)
- All Data tasks (17)
- All Laboratory tasks (13)
- All Closeout tasks (5)
- All Documents tasks (3)
- All Safety tasks (6)
- Generic Regulatory tasks (21 applicable to all countries)

**Exclude:**
- US-only tasks (REG-001: IND/CTA, REG-011: IND Submission to FDA)
- Country-specific tasks for other countries (REG-US-xxx, REG-VN-xxx)
- Generic "Ministerial Approval" (Kenya has 3-layer instead)

**Result:** ~85 ontology tasks for Kenya

### Step 5: Build Industry-Standard Milestones

Adds 9 milestone tasks (IND-100 through IND-108)

### Step 6: Build Comprehensive Dependencies

**Total: 22 dependencies**

**Study Startup Chain (7):**
```
IND-100 (Protocol Development)
  ↓
IND-101 (Data Collection Forms)
  ↓
IND-103 (Data System Configuration)
  ↓
DATA-016 (Database Deployed)
  ↓
IND-104 (Site Training)
  ↓
SITE-001 (Site Initiation Visit)
  ↓
SITE-002 (Site Activation)
```

**Study Execution Chain (3):**
```
SITE-002 (Site Activation)
  ↓
SITE-003 (First Patient In)
  ↓
SITE-004 (Patient Enrollment Period)
  ↓
SITE-005 (Last Patient Last Visit)
```

**Study Closeout Chain (6):**
```
SITE-005 (LPLV)
  ↓
IND-105 (Clinical Data Entry)
  ↓
IND-106 (Data Cleaning)
  ↓
IND-107 (Database Lock)
  ↓
DATA-001 (Clinical Database Lock)
  ↓
DATA-004 (CSR Writing)
  ↓
REG-031 (Final CSR Submission)
```

**Regulatory Gate Dependencies (4):**
```
REG-KE-NACOSTI (Final Approval)
  ↓ [GATE: Cannot start without approval]
  ├→ SITE-002 (Site Activation)
  ├→ SITE-003 (First Patient In)
  ├→ SITE-004 (Patient Enrollment Period)
  └→ IND-018 (Data System Opens)
```

**Country-Specific Regulatory Chain (2):**
```
REG-KE-EC → REG-KE-REG → REG-KE-NACOSTI
```

### Step 7: Return Timeline Object

**API Response:**
```json
{
  "study_name": "Kenya Phase III - Infectious Disease",
  "phase": "Phase III",
  "authority": "PPB Kenya",
  "therapeutic_area": "Infectious Disease",
  "tasks": [
    {
      "id": "REG-KE-EC",
      "name": "Institutional Ethics Committee (EC) Approval - Kenya",
      "duration_days": 30,
      "category": "Regulatory",
      "is_mandatory": true,
      ...
    },
    ... 99 more tasks
  ],
  "dependencies": [
    {
      "predecessor_id": "REG-KE-EC",
      "successor_id": "REG-KE-REG",
      "type": "finish-to-start",
      "lag_days": 0
    },
    ... 21 more dependencies
  ]
}
```

### Step 8: Load into MS Project

**Desktop Add-In Loads:**
- 100 tasks
- 22 dependencies
- Custom fields populated:
  - Text1 = "PPB Kenya"
  - Text2 = "Phase III"
  - Text3 = "Infectious Disease"
  - Text4 = Task Category
  - Flag1 = Is Mandatory

**Result:** Complete 959-day (2.6 year) Phase III clinical trial timeline for Kenya

---

## Task ID Naming Convention

### Country-Specific Regulatory Tasks
Format: `REG-{COUNTRY}-{AUTHORITY}`

Examples:
- `REG-KE-EC` - Kenya Ethics Committee
- `REG-KE-REG` - Kenya Pharmacy and Poisons Board
- `REG-KE-NACOSTI` - Kenya NACOSTI
- `REG-VN-EC` - Vietnam CEBRGL
- `REG-VN-Minister` - Vietnam Minister of Health

### Ontology Tasks
Format: `{CATEGORY}-{NUMBER}`

Examples:
- `REG-001` through `REG-031` - Regulatory tasks
- `SITE-001` through `SITE-005` - Site tasks
- `DATA-001` through `DATA-020` - Data tasks
- `LAB-001` through `LAB-013` - Laboratory tasks

### Industry-Standard Milestones
Format: `IND-{100+}`

Examples:
- `IND-100` - Protocol Development
- `IND-101` - Data Collection Forms
- `IND-105` - Clinical Data Entry

---

## Template Customization by Country

### Example 1: United States (Parallel Workflow)

**US-Specific:**
- `REG-001`: IND/CTA Submission & Review (US-specific, appears ONLY in US templates)
- `REG-011`: IND Submission to FDA (US-specific)

**Workflow:**
```
FDA Review (30 days)
      ||  (parallel)
IRB Review (30 days)
      ↓
Final Approval → Site Activation
```

**Total Tasks:** ~100 (includes US-specific regulatory tasks)
**Timeline:** ~959 days

### Example 2: Kenya (Three-Layer Sequential)

**Kenya-Specific:**
- `REG-KE-EC`: Institutional Ethics Committee
- `REG-KE-REG`: Pharmacy and Poisons Board
- `REG-KE-NACOSTI`: NACOSTI Research License

**Workflow:**
```
EC Review (30 days)
      ↓
PPB Review (30 days)
      ↓
NACOSTI License (30 days)
      ↓
Site Activation
```

**Excluded:** REG-001 (IND/CTA), REG-011 (FDA submission)

**Total Tasks:** ~100
**Timeline:** ~959 days

### Example 3: Vietnam (Four-Layer Sequential)

**Vietnam-Specific:**
- `REG-VN-EC`: CEBRGL (Institutional EC)
- `REG-VN-REG`: ASTT (Technical Review)
- `REG-VN-NECBR`: NECBR (National Ethics)
- `REG-VN-Minister`: Minister of Health

**Workflow:**
```
CEBRGL (30 days)
      ↓
ASTT (25 days)
      ↓
NECBR (25 days)
      ↓
Minister (5 days)
      ↓
Site Activation
```

**Total Tasks:** ~101
**Timeline:** ~959 days

---

## Custom Field Mapping

When a template is loaded into MS Project, these fields are automatically populated:

| MS Project Field | Contains | Example Value |
|------------------|----------|---------------|
| **Text1** | Regulatory Authority | "PPB Kenya" |
| **Text2** | Study Phase | "Phase III" |
| **Text3** | Therapeutic Area | "Infectious Disease" |
| **Text4** | Task Category | "Regulatory" |
| **Flag1** | Is Mandatory | "Yes" |
| **Number2** | Risk Score | 0.75 (if available) |
| **Notes** | Task metadata | Template Task ID, Authority, Category |

**Available for Custom Use:**
- Text5-30 (26 additional text fields)
- Number3-30 (28 additional number fields)
- Flag2-30 (29 additional yes/no fields)
- Date1-10 (10 date fields)

---

## How Templates Differ by Phase

### Phase I (First-in-Human)
- Shorter enrollment (30-80 patients)
- More safety monitoring tasks
- Stricter laboratory requirements
- Dose-escalation dependencies

### Phase II (Proof-of-Concept)
- Medium enrollment (100-300 patients)
- Efficacy endpoints added
- Interim analyses common

### Phase III (Confirmatory)
- Large enrollment (300-3,000 patients)
- Longer timelines (2.5+ years typical)
- Multiple sites common
- Regulatory focus on efficacy

### Phase IV (Post-Marketing)
- Real-world effectiveness
- Long-term safety monitoring
- Simplified protocols

**Template Adjusts:**
- Default enrollment durations
- Number of interim analyses
- Regulatory reporting frequency
- Safety monitoring intensity

---

## How Templates Differ by Therapeutic Area

### Oncology
- Shorter patient follow-up (tumor response)
- Complex dosing schedules
- Specialized safety monitoring
- Early stopping rules common

### Infectious Disease
- Endemic area considerations
- Vaccination schedules
- Longer follow-up for efficacy
- Country-specific disease burden affects enrollment

### Cardiovascular
- Long-term endpoints (mortality, MACE)
- Multiple year follow-up common
- Large sample sizes
- DSMB oversight critical

**Template Adjusts:**
- Default durations
- Safety monitoring frequency
- Endpoint-specific tasks

---

## Critical Path Calculation

Once the template is loaded, the **Critical Path Method (CPM)** algorithm calculates which tasks cannot be delayed:

**Algorithm:**
1. Forward pass: Calculate earliest start/finish for each task
2. Backward pass: Calculate latest start/finish for each task
3. Calculate slack: slack = latest start - earliest start
4. Critical path = tasks with ZERO slack

**For Kenya Phase III:**

Critical Path (16 tasks, 959 days):
1. Protocol Development (Day 0-180)
2. Data Collection Forms (Day 180-208)
3. Data System Configuration (Day 208-250)
4. Database Deployed (Day 250-251)
5. Site Training (Day 251-254)
6. Site Initiation Visit (Day 254-255)
7. Site Activation (Day 255-262)
8. First Patient In (Day 262-292)
9. Patient Enrollment Period (Day 292-657)
10. LPLV (Day 657-658)
11. Clinical Data Entry (Day 658-662)
12. Data Cleaning (Day 662-676)
13. Database Lock (Day 676-677)
14. Clinical Database Lock (Day 677-719)
15. CSR Writing (Day 719-929)
16. Final CSR Submission (Day 929-959)

**Any delay in these 16 tasks delays the entire project.**

---

## Summary

**Templates are organized as:**

1. **Task Ontology** = 92 universal tasks (building blocks)
2. **Regulatory Workflows** = 23 country-specific approval processes
3. **Industry Milestones** = 9 fundamental project phases

**Generated dynamically based on:**
- Country (determines regulatory workflow)
- Phase (determines default durations and task relevance)
- Therapeutic Area (determines endpoint-specific tasks)

**Result:** Country-specific, phase-appropriate, therapeutically relevant clinical trial timeline with realistic dependencies and accurate critical path.

**Total for Kenya Phase III Infectious Disease:**
- 100 tasks
- 22 dependencies
- 959 days (2.6 years)
- 16 tasks on critical path

---

*Last Updated: January 22, 2026*
