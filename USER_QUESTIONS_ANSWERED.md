# Your Questions Answered

## Question 1: Can the Template Launcher Add Custom Columns?

### Answer: YES - Feature Just Added! ✅

I've implemented custom column functionality in the Template Launcher. You can now define up to **3 custom columns** when loading a template.

**How It Works:**

1. Click "Load Template"
2. Select country, phase, therapeutic area
3. **NEW:** Define custom columns:
   - Text5 Column: `Responsible Person`
   - Text6 Column: `Budget Code`
   - Text7 Column: `Department`
4. Load template
5. Columns automatically renamed in MS Project!

**Example Use:**
```
Instead of seeing:           You'll see:
- Text5                      - Responsible Person
- Text6                      - Budget Code
- Text7                      - Department
```

**Files Modified:**
- `TemplateLoaderForm.cs` - Added custom column inputs
- `TemplateLoader.cs` - Added column renaming logic
- `IlanaPMRibbon.cs` - Pass custom names to loader

**Ready for Testing:** Yes, needs build on Windows VM

**Full Documentation:** See `CUSTOM_COLUMNS_FEATURE.md`

---

## Question 2: How Are Templates Organized?

### Answer: Three-Source Dynamic Generation System

Templates are **NOT pre-built files**. They're dynamically generated from 3 data sources based on your selections.

---

## The Three Data Sources

### 1. **Task Ontology** (92 Universal Tasks)
**File:** `backend/config/task_ontology.yaml`

**What It Is:** A library of ALL possible clinical trial tasks

**Categories (9 total):**
- Regulatory (25 tasks) - Approvals, submissions, amendments
- Operational (15 tasks) - Protocol, planning, MOPs
- Site (5 tasks) - Initiation, activation, enrollment, LPLV
- Data (17 tasks) - Database, cleaning, lock, analysis
- Pharmacy (3 tasks) - Randomization, blinding, study product
- Laboratory (13 tasks) - Specimens, assays, central lab
- Closeout (5 tasks) - Final monitoring, archival
- Documents (3 tasks) - eTMF, agreements
- Safety (6 tasks) - DSMB, SAE reporting

**Think of it as:** Building blocks that can be combined for any trial

---

### 2. **Regulatory Workflows** (23 Countries)
**File:** `backend/config/regulatory_workflows.yaml`

**What It Is:** Country-specific approval processes

**Your Example: Kenya**
```yaml
country_code: KE
workflow_type: three_layer_sequential

Layer 1: Institutional Ethics Committee (EC)
         ↓ (30 days)
Layer 2: Pharmacy and Poisons Board (PPB)
         ↓ (30 days)
Layer 3: NACOSTI Research License
         ↓
         Site Activation
```

**Other Examples:**
- **US**: FDA || IRB (parallel, 30 days each)
- **Vietnam**: CEBRGL → ASTT → NECBR → Minister (4 layers, 85 days)
- **UK**: MHRA || REC (parallel integrated, 30 days)

**Think of it as:** Country-specific regulatory rules

---

### 3. **Industry-Standard Milestones** (9 Key Tasks)
**Generated in:** `backend/services/template_generator.py`

**What It Is:** Fundamental project phases missing from ontology

**The 9 Milestones:**
1. Protocol Development (180 days)
2. Data Collection Forms (28 days)
3. Manual of Procedures (14 days)
4. Data System Configuration (42 days)
5. Site Training (3 days)
6. Clinical Data Entry (4 days)
7. Data Cleaning (14 days)
8. Database Lock (1 day)
9. Clinical Study Report (56 days)

**Think of it as:** High-level project structure

---

## How Templates Are Generated

### Your Selection:
```
Country: Kenya
Phase: Phase III
Therapeutic Area: Infectious Disease
Include Optional: Yes
```

### Behind the Scenes:

**Step 1: Build Kenya's 3-Layer Regulatory Workflow**
```
Creates 3 country-specific tasks:
✅ Institutional Ethics Committee (EC) Approval - Kenya
✅ Pharmacy and Poisons Board Approval - Kenya
✅ NACOSTI Clearance - Kenya

With sequential dependencies:
EC → PPB → NACOSTI
```

**Step 2: Filter 92 Ontology Tasks**
```
Include:
✅ All Operational tasks (15)
✅ All Site tasks (5)
✅ All Data tasks (17)
✅ All Laboratory tasks (13)
✅ All Closeout tasks (5)
✅ All Documents tasks (3)
✅ All Safety tasks (6)
✅ Generic Regulatory tasks (21)

Exclude:
❌ US-only tasks (IND/CTA, FDA submissions)
❌ Tasks for other countries
❌ Generic "Ministerial Approval" (Kenya has 3-layer instead)

Result: ~85 ontology tasks
```

**Step 3: Add 9 Industry-Standard Milestones**
```
Adds:
IND-100: Protocol Development
IND-101: Data Collection Forms
IND-102: MOP
... through IND-108: CSR
```

**Step 4: Build 22 Dependencies**
```
Study Startup Chain (7 deps):
Protocol → DCF → Data System → Database → Site Training → SIV → Site Activation

Study Execution Chain (3 deps):
Site Activation → First Patient In → Enrollment → LPLV

Study Closeout Chain (6 deps):
LPLV → Data Entry → Data Cleaning → DB Lock → CSR → FDA Submission

Regulatory Gates (4 deps):
NACOSTI → Site Activation, FPI, Enrollment, Data System

Country-Specific Chain (2 deps):
EC → PPB → NACOSTI
```

**Step 5: Return Complete Timeline**
```
Result:
✅ 100 tasks total
   - 3 Kenya-specific regulatory
   - 85 ontology tasks
   - 9 industry milestones
   - 3 additional regulatory

✅ 22 dependencies (complete lifecycle)

✅ 959 days total duration (2.6 years)

✅ 16 tasks on critical path
```

---

## Task Naming Convention

### Country-Specific Tasks:
```
REG-{COUNTRY}-{AUTHORITY}

Examples:
- REG-KE-EC (Kenya Ethics Committee)
- REG-KE-REG (Kenya PPB)
- REG-KE-NACOSTI (Kenya NACOSTI)
```

### Ontology Tasks:
```
{CATEGORY}-{NUMBER}

Examples:
- REG-001 through REG-031 (Regulatory)
- SITE-001 through SITE-005 (Site)
- DATA-001 through DATA-020 (Data)
```

### Industry Milestones:
```
IND-{100+}

Examples:
- IND-100 (Protocol Development)
- IND-101 (Data Collection Forms)
- IND-105 (Clinical Data Entry)
```

---

## Why Templates Differ by Country

### Kenya (Your Example):
```
Regulatory Tasks:
✅ Institutional EC Approval - Kenya
✅ Pharmacy and Poisons Board Approval - Kenya
✅ NACOSTI Research License - Kenya
✅ ClinicalTrials.gov Registration (generic)
✅ IRB/EC Continuing Review (generic)
❌ IND/CTA Submission (US-only, excluded)
❌ FDA submissions (US-only, excluded)

Workflow: Sequential 3-layer
Timeline: ~959 days
```

### United States:
```
Regulatory Tasks:
✅ IND/CTA Submission & Review (US-specific)
✅ IND Submission to FDA (US-specific)
✅ ClinicalTrials.gov Registration (generic)
✅ IRB/EC Continuing Review (generic)
❌ Kenya PPB/NACOSTI (not applicable)

Workflow: Parallel (FDA || IRB)
Timeline: ~959 days
```

### Vietnam:
```
Regulatory Tasks:
✅ CEBRGL Approval - Vietnam (Layer 1)
✅ ASTT Review - Vietnam (Layer 2)
✅ NECBR Approval - Vietnam (Layer 3)
✅ Minister of Health - Vietnam (Layer 4)
✅ ClinicalTrials.gov Registration (generic)
❌ US FDA tasks (not applicable)
❌ Kenya PPB/NACOSTI (not applicable)

Workflow: Sequential 4-layer
Timeline: ~959 days
```

---

## Current Custom Field Mapping

When you load a template, these fields are automatically filled:

| MS Project Field | Contains | Example |
|------------------|----------|---------|
| **Text1** | Regulatory Authority | "PPB Kenya" |
| **Text2** | Study Phase | "Phase III" |
| **Text3** | Therapeutic Area | "Infectious Disease" |
| **Text4** | Task Category | "Regulatory" |
| **Text5** | Your Custom Column | "Responsible Person" |
| **Text6** | Your Custom Column | "Budget Code" |
| **Text7** | Your Custom Column | "Department" |
| **Flag1** | Is Mandatory | "Yes" |
| **Number2** | Risk Score | 0.75 |

**Available for Future Use:**
- Text8-30 (23 more text fields)
- Number3-30 (28 number fields)
- Flag2-30 (29 yes/no fields)
- Date1-10 (10 date fields)

---

## Summary

**Templates are organized as:**

1. **Task Ontology** = 92 building blocks (universal tasks)
2. **Regulatory Workflows** = 23 country rules (approval processes)
3. **Industry Milestones** = 9 key phases (project structure)

**Dynamically combined based on your selections** to create country-specific, phase-appropriate timelines with realistic dependencies.

**Result for Kenya Phase III:**
- 100 tasks (Kenya-specific + ontology + milestones)
- 22 dependencies (complete lifecycle)
- 959 days (2.6 years realistic timeline)
- 16 critical path tasks

---

## Documentation Files

1. **`TEMPLATE_ORGANIZATION_EXPLAINED.md`** - Complete explanation of template structure
2. **`CUSTOM_COLUMNS_FEATURE.md`** - Custom column functionality guide
3. **`COUNTRY_SPECIFIC_TEMPLATES_FIX.md`** - How we made templates country-specific
4. **`COMPREHENSIVE_DEPENDENCIES_IMPLEMENTATION.md`** - Study lifecycle dependencies

---

*Questions answered: January 22, 2026*
