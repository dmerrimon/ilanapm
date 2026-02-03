# Industry-Standard Timeline Dependencies - Complete Mapping

Based on **Standard CRO Study Startup Overview Timeline** and **Standard CRO CSR Preparation Timeline**

## Study Lifecycle Phases

### Phase 1: Protocol Development & Planning
**Key Milestone:** Protocol v1.0 finalized

### Phase 2: Study Startup & Site Preparation
**Key Milestone:** Site Activation complete

### Phase 3: Patient Enrollment & Execution
**Key Milestone:** Last Patient Last Visit (LPLV)

### Phase 4: Study Closeout & Reporting
**Key Milestone:** CSR submitted to FDA

---

## Detailed Dependencies from Emmes PDFs

### PHASE 1: PROTOCOL DEVELOPMENT (Ontology Tasks)

```
Protocol Development
  ├─→ (4 weeks) Data Collection Forms - First Draft
  ├─→ (4 weeks) Manual of Procedures - First Draft
  └─→ Finalization to Protocol v1.0
        ├─→ (2 weeks) Data Collection Forms - Final
        ├─→ (2 weeks) MOP v1.0
        ├─→ (2 weeks) eCRF Instructions (concurrent with final forms)
        └─→ (6 weeks) Interim SAP (if required)
```

**Ontology Mapping:**
- No exact "Protocol Development" task in ontology currently
- Could use OPS-001 or create new task
- Data Collection Forms = EMMES-002 or DATA-xxx task
- MOP = EMMES-003 or OPS-xxx task

### PHASE 2: STUDY STARTUP (From Emmes Page 1)

```
Protocol v1.0
  └─→ (2 weeks) Final Data Collection Forms
        └─→ (6 weeks) Database Configuration (EMMES-004 / DATA-xxx)
              └─→ Database Deployed
                    ├─→ (4 weeks before activation) Site Training (EMMES-005 / SITE-xxx)
                    ├─→ (2 weeks before activation) Barcode Labels Shipped
                    ├─→ (1 week before activation) Randomization Materials
                    └─→ Site Initiation Visit (SITE-001)
                          └─→ Site Activation (SITE-002)
                                ├─→ (same day) Data System Opens (IND-018)
                                ├─→ (1 month later) Programmatic Queries Setup
                                └─→ First Patient In (SITE-003)
```

**Parallel Track - Regulatory:**
```
IND Submission
  └─→ (30 days) IND Review Complete
        └─→ IRB Approval
              └─→ [GATE for Site Activation]
```

**Parallel Track - DSMB:**
```
DSMB Charter Received
  └─→ (1 week) Review Charter
        └─→ (2 weeks) Prepare DSMB Report Shell
              └─→ DSMB Organizational Meeting
                    └─→ [GATE for Site Activation]
```

**Ontology Mapping:**
- Database Configuration = EMMES-004 or DATA-017
- Site Training = EMMES-005 or SITE-xxx
- Site Initiation Visit = SITE-001
- Site Activation = SITE-002
- First Patient In = SITE-003
- Data System Opens = IND-018

### PHASE 3: PATIENT ENROLLMENT (From Emmes Page 2)

```
Site Activation
  └─→ First Patient In (SITE-003) [Day 0]
        └─→ Patient Enrollment Period (SITE-004) [e.g., 365 days]
              └─→ Last Patient Last Visit (SITE-005) [LPLV]
```

**Ontology Mapping:**
- First Patient In = SITE-003
- Patient Enrollment Period = SITE-004
- Last Patient Last Visit = SITE-005

### PHASE 4: STUDY CLOSEOUT (From CSR Preparation PDF Pages 1-3)

#### 4A: Clinical Database Finalization

```
LPLV (SITE-005)
  └─→ (4 days) Clinical Data Entry Complete (EMMES-006 / DATA-xxx)
        ├─→ (2 weeks) Data Cleaning & Querying (EMMES-007 / DATA-xxx)
        │     └─→ (1 day after monitoring) Resolve All Queries
        │           └─→ (1 day) Clinical Database Lock (EMMES-008 / DATA-001)
        │
        ├─→ (3 weeks) SAE Reconciliation (CLOSE-010)
        │
        └─→ (5 weeks) Final Monitoring Visit (CLOSE-011)
```

**Ontology Mapping:**
- Clinical Data Entry = EMMES-006 or DATA-xxx
- Data Cleaning = EMMES-007 or DATA-xxx
- Clinical Database Lock = EMMES-008 or DATA-001
- SAE Reconciliation = CLOSE-010
- Final Monitoring Visit = CLOSE-011

#### 4B: Laboratory Database Finalization (Parallel to Clinical)

```
Last Specimen Collection Time Point
  └─→ (12 weeks) Lab Assay Completion & Transfer (LAB-010)
        └─→ (4 days) QC of Lab Data & Query Distribution (LAB-011)
              └─→ (1 week) Resolution of Lab Queries (LAB-012)
                    └─→ (1 day) Laboratory Database Lock (LAB-013)
```

**Ontology Mapping:**
- Lab Assay Completion = LAB-010
- Lab QC = LAB-011
- Lab Query Resolution = LAB-012
- Lab Database Lock = LAB-013

#### 4C: CSR Preparation & Submission

```
[Clinical DB Lock] + [Lab DB Lock]
  └─→ (12 weeks) Preparation of Draft CSR (REG-020 / EMMES-009 / DATA-004)
        │
        ├─→ (30 days after Clinical DB Lock) PVG Provides SAE Narratives (SAFETY-010)
        │
        └─→ (1 day) Distribute Draft CSR to PI (REG-021)
              └─→ (4-6 weeks = 35 days) PI Reviews & Completes CSR (REG-022)
                    └─→ (1 week = 7 days) Incorporate PI Text (REG-023)
                          └─→ (1 day) Distribute to Sponsor for Review (REG-024)
                                └─→ (4 weeks = 28 days) Sponsor Reviews (REG-025)
                                      └─→ (1 week = 7 days) Incorporate Sponsor Comments (REG-026)
                                            └─→ (3 days) Receive Approval to Finalize (REG-027)
                                                  └─→ (3 days) Prepare Approved CSR (REG-028)
                                                        └─→ (3 days) PI Signs Signature Page (REG-029)
                                                              └─→ (1 day) Distribute Approved CSR (REG-030)
                                                                    └─→ (2-3 weeks = 17 days) RAS Submits to FDA (REG-031)
```

**Ontology Mapping:**
- Draft CSR Preparation = REG-020 or EMMES-009 or DATA-004
- Distribute to PI = REG-021
- PI Reviews = REG-022
- Incorporate PI Text = REG-023
- Distribute to Sponsor = REG-024
- Sponsor Reviews = REG-025
- Incorporate Sponsor Comments = REG-026
- Approval to Finalize = REG-027
- Prepare Approved CSR = REG-028
- PI Signs = REG-029
- Distribute Approved = REG-030
- Submit to FDA = REG-031

---

## Complete Dependency Chain

### Sequential Flow:

```
Day 0-180:    Protocol Development (180d)
  ↓
Day 180-194:  Data Collection Forms Final (14d = 2 weeks)
  ↓
Day 194-236:  Database Configuration (42d = 6 weeks)
  ↓
Day 236-243:  Site Training (7d)
  ↓
Day 243-250:  Site Initiation Visit (7d)
  ↓
[GATE: Regulatory Approval - runs in parallel Day 0-90]
  ↓
Day 250-257:  Site Activation (7d)
  ↓
Day 257-258:  First Patient In (1d)
  ↓
Day 258-623:  Patient Enrollment Period (365d)
  ↓
Day 623-624:  Last Patient Last Visit (1d)
  ↓
Day 624-628:  Clinical Data Entry (4d)
  ↓
Day 628-642:  Data Cleaning (14d = 2 weeks)
  ↓ (parallel: SAE Reconciliation Day 628-649 = 21d)
  ↓ (parallel: Final Monitoring Visit Day 624-659 = 35d)
  ↓
Day 642-643:  Clinical Database Lock (1d)

[PARALLEL: Lab Processing]
Last Specimen Collection
  ↓
  (12 weeks = 84d) Lab Assay Completion
  ↓
  (4d) Lab QC
  ↓
  (7d) Lab Query Resolution
  ↓
  (1d) Lab Database Lock

[BOTH DATABASES LOCKED]
  ↓
Day 643-727:  Draft CSR Preparation (84d = 12 weeks)
  ↓
Day 727-728:  Distribute to PI (1d)
  ↓
Day 728-763:  PI Review (35d = 5 weeks)
  ↓
Day 763-770:  Incorporate PI Text (7d)
  ↓
Day 770-771:  Distribute to Sponsor (1d)
  ↓
Day 771-799:  Sponsor Review (28d = 4 weeks)
  ↓
Day 799-806:  Incorporate Comments (7d)
  ↓
Day 806-809:  Approval (3d)
  ↓
Day 809-812:  Prepare Final (3d)
  ↓
Day 812-815:  PI Signs (3d)
  ↓
Day 815-816:  Distribute (1d)
  ↓
Day 816-833:  Submit to FDA (17d = 2.5 weeks)

TOTAL: ~833 days (2.3 years) for complete study lifecycle
```

## Critical Dependencies to Implement

### Priority 1 (CRITICAL):
1. ✅ Regulatory Approval → Site Activation (DONE)
2. **Site Activation → First Patient In**
3. **First Patient In → Enrollment Period**
4. **Enrollment Period → LPLV**
5. **LPLV → Clinical Data Entry**
6. **Clinical DB Lock → Draft CSR**

### Priority 2 (IMPORTANT):
7. **Data Collection Forms → Database Config**
8. **Database Config → Site Training**
9. **Site Training → Site Initiation Visit**
10. **Site Initiation Visit → Site Activation**
11. **Draft CSR → PI Review → Sponsor Review → FDA Submission** (entire chain)

### Priority 3 (NICE TO HAVE):
12. Protocol Development → Data Collection Forms
13. Last Specimen → Lab Assay → Lab DB Lock
14. Clinical DB Lock + Lab DB Lock → Draft CSR (both required)

---

## Implementation Notes

1. **Task ID Conflicts**: Some tasks have multiple potential IDs (EMMES-xxx vs ontology tasks like DATA-xxx, SITE-xxx, REG-xxx)
2. **Current Status**: Only 4 dependencies exist (Regulatory → Operational tasks)
3. **Target**: Add 20-30 comprehensive dependencies covering full study lifecycle
4. **Complexity**: Need to handle both sequential and parallel dependencies (e.g., Clinical DB Lock AND Lab DB Lock both required before CSR)
