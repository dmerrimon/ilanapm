# Missing Study Startup and Closeout Dependencies

## Current State

The backend currently has **MINIMAL dependencies**:

### Dependencies That Exist (4 per country):
1. ✅ Regulatory Approval → Site Activation
2. ✅ Regulatory Approval → First Patient In (FPI)
3. ✅ Regulatory Approval → Patient Enrollment Period
4. ✅ Regulatory Approval → Data System Opens

### Dependencies That Are MISSING:

#### Study Startup Chain:
- ❌ Protocol Development → Data Collection Forms
- ❌ Protocol Development → MOP
- ❌ Data Collection Forms → Database Configuration
- ❌ Database Configuration → Database Deployed
- ❌ Database Deployed → Site Training
- ❌ Site Training → Site Initiation Visit
- ❌ Site Initiation Visit → Site Activation
- ❌ Site Activation → First Patient In (FPI)

#### Study Execution Chain:
- ❌ First Patient In → Patient Enrollment Period
- ❌ Patient Enrollment Period → Last Patient Last Visit (LPLV)

#### Study Closeout Chain:
- ❌ Last Patient Last Visit → Clinical Data Entry
- ❌ Clinical Data Entry → Data Cleaning
- ❌ Data Cleaning → Clinical Database Lock
- ❌ Clinical Database Lock → Statistical Analysis
- ❌ Statistical Analysis → CSR Writing
- ❌ CSR Writing → Final Regulatory Submissions

## Impact

### Without These Dependencies:
- ❌ Tasks appear to start simultaneously (unrealistic)
- ❌ Critical path only shows regulatory + enrollment
- ❌ No visibility into startup timeline (protocol → database → site readiness)
- ❌ No visibility into closeout timeline (LPLV → data lock → CSR)
- ❌ Timeline appears to be 365 days (enrollment only)

### With These Dependencies:
- ✅ Realistic sequence: Protocol (180d) → Database (42d) → Site Activation (7d) → Enrollment (365d) → Closeout (90d)
- ✅ Critical path shows full study lifecycle
- ✅ Timeline appears to be ~680+ days (realistic)
- ✅ PMs can see dependencies between phases

## Realistic Timeline Example (Phase III)

**With Full Dependencies:**
```
Day 0-180:    Protocol Development (180 days)
Day 180-208:  Data Collection Forms (28 days)
Day 208-250:  Database Configuration (42 days)
Day 250-257:  Site Training (7 days)
Day 257-264:  Site Initiation Visit (7 days)

              [Regulatory Approval: Day 0-90 in parallel]

Day 264-271:  Site Activation (7 days) - GATE: needs regulatory + site readiness
Day 271-272:  First Patient In (1 day)
Day 272-637:  Patient Enrollment Period (365 days)
Day 637-638:  Last Patient Last Visit (1 day)
Day 638-680:  Data Entry & Cleaning (42 days)
Day 680-681:  Clinical Database Lock (1 day)
Day 681-891:  CSR Writing (210 days)
Day 891-920:  Final Regulatory Submissions (30 days)

TOTAL: ~920 days (2.5 years) - REALISTIC for Phase III trial
```

**Currently Without Dependencies:**
```
Day 0-90:  Regulatory Approval
Day 90-455: Patient Enrollment Period (365 days)

TOTAL: 455 days (1.2 years) - UNREALISTIC (missing startup and closeout)
```

## Priority Missing Dependencies

### CRITICAL (Must Have):
1. Site Activation → First Patient In (can't enroll without activated site)
2. First Patient In → Enrollment Period (enrollment starts after FPI)
3. Enrollment Period → LPLV (LPLV marks end of enrollment)
4. LPLV → Clinical Data Entry (can't enter data until patients complete)
5. Clinical Database Lock → CSR Writing (can't write report until data locked)

### IMPORTANT (Should Have):
6. Protocol Development → Data Collection Forms
7. Data Collection Forms → Database Configuration
8. Database Configuration → Site Training
9. Site Training → Site Initiation Visit
10. Site Initiation Visit → Site Activation

### NICE TO HAVE:
11. Statistical Analysis Plan → Statistical Analysis
12. Data Cleaning → Statistical Analysis
13. Site Closeout Visits → Study Archival

## Recommendation

Add comprehensive dependencies in template_generator.py's _build_dependencies() method for ontology-based tasks.
