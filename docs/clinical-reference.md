# Ilana PM Clinical Reference Guide

**Version:** 0.1.0
**Last Updated:** 2026-01-14
**Audience:** Clinical operations professionals, project managers, and domain experts

---

## Table of Contents

1. [Introduction](#introduction)
2. [Clinical Trial Phases](#clinical-trial-phases)
3. [Regulatory Authorities](#regulatory-authorities)
4. [Task Ontology](#task-ontology)
5. [Study Checklists](#study-checklists)
6. [Validation Rules Explained](#validation-rules-explained)
7. [Risk Factors](#risk-factors)
8. [Best Practices](#best-practices)
9. [Glossary](#glossary)

---

## Introduction

This guide provides clinical domain context for Ilana PM's validation rules and advisory services. It explains **why** certain rules exist and **how** they reflect real-world clinical trial operations.

### Purpose

Ilana PM helps clinical teams:
- **Avoid costly timeline errors** before studies start
- **Identify regulatory compliance gaps** early
- **Optimize task sequencing** for faster study completion
- **Assess risk** proactively with data-driven insights

### Scope

This reference covers:
- **Phase I-IV** clinical trials
- **Multi-national** studies (FDA, EMA, MHRA, etc.)
- **Regulatory, operational, site, and data** task categories
- **GCP and ICH** compliance requirements

---

## Clinical Trial Phases

### Phase I: First-in-Human Studies

**Objective**: Assess safety and pharmacokinetics in healthy volunteers or patients.

**Typical Characteristics**:
- **Duration**: 6-12 months
- **Participants**: 20-100
- **Primary Focus**: Safety, dosing, side effects
- **Regulatory Timeline**: ~3-6 months for IND/CTA approval

**Key Tasks**:
- IND/CTA submission
- IRB/Ethics Committee approval
- Investigator's Brochure preparation
- Safety monitoring setup

### Phase II: Efficacy and Safety

**Objective**: Evaluate efficacy and side effects in patients with the condition.

**Typical Characteristics**:
- **Duration**: 1-2 years
- **Participants**: 100-300
- **Primary Focus**: Efficacy signals, dose ranging, safety
- **Regulatory Timeline**: ~4-8 months for approvals

**Key Tasks**:
- Protocol finalization
- Site identification and contracts
- Centralized imaging/lab setup
- Data management system validation

**Ilana PM Focus**: Most examples use Phase II as the reference phase.

### Phase III: Confirmatory Trials

**Objective**: Confirm efficacy and monitor adverse reactions in larger populations.

**Typical Characteristics**:
- **Duration**: 2-4 years
- **Participants**: 300-3,000+
- **Primary Focus**: Statistical proof of efficacy, safety profile
- **Regulatory Timeline**: ~6-12 months for multi-site approvals

**Key Tasks**:
- Multi-site regulatory submissions
- Large-scale site activation
- DSMB (Data Safety Monitoring Board) setup
- Interim analysis planning

### Phase IV: Post-Marketing Studies

**Objective**: Monitor long-term effectiveness and safety post-approval.

**Typical Characteristics**:
- **Duration**: Ongoing (years)
- **Participants**: Thousands
- **Primary Focus**: Real-world effectiveness, rare adverse events
- **Regulatory Timeline**: Simplified for marketed products

---

## Regulatory Authorities

### FDA (United States)

**Full Name**: U.S. Food and Drug Administration

**Jurisdiction**: United States

**Key Regulatory Gates**:

1. **IND (Investigational New Drug) Submission**
   - **Timeline**: 30-day safety review hold
   - **Required Documents**:
     - FDA Form 1571
     - Protocol
     - Investigator's Brochure
     - CMC (Chemistry, Manufacturing, Controls)
   - **Blocking**: Yes - cannot start trial without IND clearance

2. **IRB (Institutional Review Board) Approval**
   - **Timeline**: 30-60 days (varies by institution)
   - **Required Documents**:
     - Protocol
     - Informed Consent Form
     - Investigator's Brochure
   - **Blocking**: Yes - cannot enroll patients without IRB approval

**Typical Timeline to First Patient In**:
- **Phase I**: 3-4 months from IND submission
- **Phase II**: 4-6 months from IND submission
- **Phase III**: 6-9 months (multi-site complexity)

**Ilana PM Validation**:
- Checks for IND submission task
- Verifies IRB approval precedes enrollment
- Flags durations outside typical ranges

### EMA (European Union)

**Full Name**: European Medicines Agency

**Jurisdiction**: European Union (27+ member states)

**Key Regulatory Gates**:

1. **CTA (Clinical Trial Application)**
   - **Timeline**: 60-day review period
   - **Process**: Submit to national competent authority
   - **Complexity**: May require multi-state submissions

2. **REC (Research Ethics Committee)**
   - **Timeline**: 60 days
   - **Process**: Separate from regulatory approval

**Typical Timeline to First Patient In**:
- **Phase I**: 4-5 months from CTA submission
- **Phase II**: 5-7 months from CTA submission
- **Phase III**: 8-12 months (multi-country complexity)

**Key Differences from FDA**:
- Longer review periods (60 vs 30 days)
- Separate ethics and regulatory processes
- Multi-country coordination challenges

### MHRA (United Kingdom)

**Full Name**: Medicines and Healthcare products Regulatory Agency

**Jurisdiction**: United Kingdom (post-Brexit)

**Key Regulatory Gates**:

1. **CTA (Clinical Trial Authorisation)**
   - **Timeline**: 30 days
   - **Process**: UK-specific submission
   - **Note**: Faster than EU post-Brexit

**Typical Timeline to First Patient In**:
- **Phase I**: 3-4 months
- **Phase II**: 4-6 months

### Health Canada

**Full Name**: Health Canada Therapeutic Products Directorate

**Jurisdiction**: Canada

**Key Regulatory Gates**:

1. **CTA (Clinical Trial Application)**
   - **Timeline**: 30 days
   - **Process**: Similar to FDA IND

**Typical Timeline**: Similar to FDA timelines.

### PMDA (Japan)

**Full Name**: Pharmaceuticals and Medical Devices Agency

**Jurisdiction**: Japan

**Key Regulatory Gates**:

1. **Clinical Trial Notification**
   - **Timeline**: 30 days
   - **Process**: Notification system

**Key Differences**:
- Language requirements (Japanese translations)
- Cultural considerations for informed consent
- Different GCP interpretation

---

## Task Ontology

The task ontology defines 25 canonical clinical trial tasks that span regulatory, operational, site, and data management categories.

### Regulatory Tasks (Category: Regulatory)

#### REG-001: IND/CTA Submission

**Purpose**: Submit investigational drug application to regulatory authority.

**Typical Duration**: 60 days
**Min/Max**: 30-90 days

**Components**:
- Protocol
- Investigator's Brochure
- CMC (Chemistry, Manufacturing, Controls)
- Nonclinical study reports
- Clinical study reports (if applicable)

**Authority Variations**:
- **FDA**: 30-day hold (can be extended)
- **EMA**: 60-day review
- **MHRA**: 30-day review

**Validation Rules**:
- Must precede patient enrollment
- Duration cannot be < 30 days (unrealistic)
- Should be marked as mandatory

#### REG-002: IRB/Ethics Committee Approval

**Purpose**: Obtain ethical approval for study conduct.

**Typical Duration**: 45 days
**Min/Max**: 21-90 days

**Components**:
- Protocol
- Informed Consent Form
- Investigator's Brochure
- Recruitment materials

**Variations**:
- **US**: IRB (institutional or central)
- **EU**: Ethics Committee (EC)
- **Expedited Review**: 7-14 days for minimal risk studies

**Validation Rules**:
- Must occur before patient enrollment
- Dependencies: Requires protocol finalization
- Can run partially in parallel with IND/CTA

#### REG-003: Protocol Amendment Submission

**Purpose**: Submit changes to approved protocol.

**Typical Duration**: 30 days
**Min/Max**: 14-60 days

**Types**:
- **Substantial Amendment**: Requires regulatory/ethics re-approval
- **Administrative Amendment**: Notification only

### Operational Tasks (Category: Operational)

#### OPS-001: Site Identification & Feasibility

**Purpose**: Identify and assess potential study sites.

**Typical Duration**: 90 days
**Min/Max**: 60-180 days

**Activities**:
- Feasibility questionnaires
- Site visits
- Budget negotiations
- Contract negotiations

**Risk Factors**:
- Site availability
- Competing trials
- PI (Principal Investigator) bandwidth

#### OPS-002: First Patient In (FPI)

**Purpose**: Enroll first patient in study.

**Typical Duration**: 1 day
**Min/Max**: 1-1 day

**Prerequisites**:
- All regulatory approvals
- Site activation complete
- Drug/device supplies available
- Study team trained

**Critical Milestone**: Often contractually significant.

#### OPS-003: Last Patient Out (LPO)

**Purpose**: Last patient completes last visit.

**Typical Duration**: Depends on enrollment and treatment duration

**Calculation**: FPI + (enrollment period) + (treatment duration) + (follow-up)

### Site Tasks (Category: Site)

#### SITE-001: Site Initiation Visit (SIV)

**Purpose**: Train site staff and activate site for enrollment.

**Typical Duration**: 1-2 days

**Activities**:
- Protocol training
- eCRF training
- Drug accountability training
- Regulatory document review

**Checklist**: See SIV Checklist section below.

#### SITE-002: Site Activation Visit (SAV)

**Purpose**: Final readiness check before enrollment starts.

**Typical Duration**: 1 day

**Verification**:
- All regulatory approvals in place
- Site staff credentialed
- Drug supplies received
- Systems access verified

#### SITE-003: Site Monitoring Visit

**Purpose**: On-site monitoring for compliance and data quality.

**Frequency**: Varies by risk (quarterly to monthly)

**Activities**:
- Source data verification
- Informed consent review
- Drug accountability review
- AE (Adverse Event) review

#### SITE-004: Site Closeout Visit

**Purpose**: Formal site closure and archival.

**Typical Duration**: 1 day

**Activities**:
- Final data queries resolution
- Drug accountability reconciliation
- Essential documents archival
- Payment reconciliation

### Data Management Tasks (Category: Data)

#### DATA-001: Database Lock

**Purpose**: Freeze database for statistical analysis.

**Typical Duration**: 14 days
**Min/Max**: 7-30 days

**Prerequisites**:
- All data entered
- All queries resolved
- Data cleaning complete

**Critical Milestone**: Cannot run final analysis until lock.

#### DATA-002: Statistical Analysis

**Purpose**: Perform pre-specified statistical analyses.

**Typical Duration**: 30-60 days

**Dependencies**: Must follow database lock.

---

## Study Checklists

### STARTUP Checklist

**Purpose**: Ensure study readiness before First Patient In.

**Mandatory Items**:

1. **Protocol finalized and approved**
   - Rationale: Cannot train sites without approved protocol
   - Risk if incomplete: Protocol deviations, retraining

2. **Informed Consent Form approved by IRB/EC**
   - Rationale: Legal requirement for enrollment
   - Risk if incomplete: Cannot enroll patients legally

3. **Investigator's Brochure current**
   - Rationale: Safety information for investigators
   - Risk if incomplete: Sites lack critical safety data

4. **Site contracts executed**
   - Rationale: Legal/financial protection
   - Risk if incomplete: Payment disputes, liability issues

5. **eCRF system validated**
   - Rationale: Data quality and GCP compliance
   - Risk if incomplete: Data integrity issues, audit findings

6. **Drug/device supplies shipped to site**
   - Rationale: Cannot treat patients without supplies
   - Risk if incomplete: Study delays, missed enrollment window

7. **Site staff training completed**
   - Rationale: Protocol compliance requires training
   - Risk if incomplete: Protocol deviations, data errors

**Usage in Ilana PM**:
- Checklist completeness tracked per task
- Warnings issued if checklist < 100% before enrollment
- Risk scores increased for incomplete checklists

### SIV (Site Initiation Visit) Checklist

**Purpose**: Standardize site training and activation.

**Mandatory Items**:

1. **Review protocol with site staff**
   - Sections: Objectives, design, endpoints, procedures

2. **Review Informed Consent process**
   - Elements: Regulatory requirements, documentation, re-consent

3. **Review eligibility criteria**
   - Focus: Inclusion/exclusion criteria, screening logs

4. **eCRF training completed**
   - Hands-on: Data entry, query resolution, system navigation

5. **Drug accountability procedures reviewed**
   - Process: Receipt, dispensing, return, destruction

**Timeline**: Typically 1 day on-site.

### SAV (Site Activation Visit) Checklist

**Purpose**: Final verification before enrollment authorization.

**Mandatory Items**:

1. **All regulatory approvals in place**
   - Verification: IRB approval letter, regulatory authority clearance

2. **Site staff trained and credentialed**
   - Evidence: Training logs, CVs, licenses

3. **Systems access verified**
   - Testing: eCRF login, IVRS/IWRS, lab portal

**Timeline**: Typically 4 hours on-site or remote.

### CLOSEOUT Checklist

**Purpose**: Formal study closure at site.

**Mandatory Items**:

1. **All CRFs completed and queries resolved**
   - Verification: 100% data entry, zero open queries

2. **Drug accountability reconciled**
   - Documentation: All drug disposition accounted for

3. **Essential documents archived**
   - Requirement: Regulatory inspection readiness

4. **Final payments processed**
   - Settlement: Per-patient payments, closeout payment

**Timeline**: Typically 1 day on-site.

---

## Validation Rules Explained

### 1. Regulatory Gating Validator

**Rule**: Required regulatory gates must be present and properly sequenced.

**Rationale**: Regulatory compliance is non-negotiable. Starting a study without proper approvals risks:
- Regulatory citations
- Study shutdown
- Data invalidation
- Legal liability

**Examples**:

- **Missing IND/CTA**: Error - cannot conduct study without regulatory clearance
- **IND after patient enrollment**: Error - illegal to enroll patients before IND clearance
- **Missing IRB approval**: Error - ethical and legal requirement

### 2. Duration Bounds Validator

**Rule**: Task durations must fall within acceptable ranges based on historical data.

**Rationale**: Unrealistic durations indicate:
- Planning errors
- Insufficient buffer time
- Unrealistic sponsor expectations

**Examples**:

- **IND submission in 15 days**: Warning - typical is 60 days, minimum 30 days
- **IRB approval in 7 days**: Warning - unlikely unless expedited review
- **Site initiation in 0 days**: Error - physically impossible

**Configuration**: Bounds defined in `duration_bounds.yaml`.

### 3. Operational Sequences Validator

**Rule**: Tasks must follow logical operational order.

**Rationale**: Some tasks have intrinsic dependencies:
- Cannot train site staff before protocol exists
- Cannot ship drug before drug manufactured
- Cannot analyze data before database locked

**Examples**:

- **Site contract after patient enrollment**: Warning - financial risk
- **Database lock before last patient out**: Error - data incomplete
- **Statistical analysis before database lock**: Error - analysis invalid

### 4. Dependency Validator

**Rule**: Dependency graph must be acyclic (no circular dependencies).

**Rationale**: Circular dependencies are logically impossible:
- Task A depends on Task B
- Task B depends on Task A
- → Neither can start

**Examples**:

- **Protocol depends on ICF, ICF depends on Protocol**: Error - circular
- **Orphan tasks**: Warning - tasks with no dependencies may be incorrectly isolated

### 5. Checklist Completeness Validator

**Rule**: Mandatory checklists must be complete before critical milestones.

**Rationale**: Checklists ensure GCP compliance and operational readiness.

**Examples**:

- **STARTUP checklist 50% complete before FPI**: Warning - high risk of study issues
- **SIV checklist missing**: Error - site not properly trained

### 6. Parallelization Validator

**Rule**: Identifies tasks that could run in parallel to optimize timeline.

**Rationale**: Serial execution when parallelization is possible delays studies and increases costs.

**Examples**:

- **Site contracts and drug manufacturing**: Can run in parallel
- **Multiple site initiations**: Can overlap
- **Independent site monitoring visits**: Can occur simultaneously

---

## Risk Factors

### Duration Risk (Weight: 30%)

**Description**: Task duration is aggressive compared to historical benchmarks.

**Assessment**:
- Compare task duration to typical/min/max from ontology
- Flag durations < typical as "aggressive"
- Flag durations < minimum as "high risk"

**Example**:
- **IND submission in 20 days** (typical: 60 days)
  - Risk: +30 points
  - Mitigation: Add buffer time, engage regulatory consultant

### Category Risk (Weight: 20%)

**Description**: Certain task categories historically face more delays.

**Risk Levels**:
- **Regulatory**: +20 points (authority review unpredictable)
- **Site**: +15 points (third-party coordination)
- **Data**: +10 points (data quality issues common)
- **Operational**: +5 points (internal control)

**Rationale**:
- Regulatory: External dependency, can't control review time
- Site: Third-party performance variable
- Data: Quality issues often discovered late

### Mandatory Task Risk (Weight: 15%)

**Description**: Mandatory tasks on critical path have no flexibility.

**Assessment**:
- Is task marked as mandatory?
- Is task on critical path?

**Impact**: +15 points if both true

**Rationale**: Delays to mandatory critical path tasks delay entire study.

### Checklist Completion Risk (Weight: 20%)

**Description**: Incomplete checklists indicate operational unreadiness.

**Assessment**:
- < 50% complete: +20 points (high risk)
- < 80% complete: +10 points (medium risk)
- 100% complete: +0 points (low risk)

**Rationale**: Incomplete checklists correlate with:
- Study delays at startup
- Protocol deviations
- Data quality issues
- Regulatory findings

### Timeline Context Risk (Weight: 15%)

**Description**: Position in dependency graph affects risk.

**Factors**:
- **On critical path**: +15 points
- **High dependency fan-in**: +10 points (many predecessors)
- **High dependency fan-out**: +10 points (many successors)

**Rationale**: Critical path tasks have no slack - any delay directly impacts study completion.

---

## Best Practices

### Timeline Planning

1. **Start with regulatory milestones**
   - Work backwards from desired first patient date
   - Add authority-specific review times
   - Include buffer for questions/re-submissions

2. **Build in operational realism**
   - Use typical durations, not minimums
   - Account for site activation challenges
   - Plan for enrollment ramp-up time

3. **Validate dependencies**
   - Ensure logical task order
   - Check for circular dependencies
   - Verify critical path makes sense

4. **Monitor checklist completion**
   - Track STARTUP checklist completion
   - Address gaps early
   - Don't start until 100% complete

### Risk Mitigation

**For Regulatory Tasks**:
- Engage regulatory consultant early
- Pre-submission meetings with authorities
- Parallel country submissions where possible

**For Aggressive Timelines**:
- Add buffer time (20-30%)
- Have contingency plans
- Monitor progress closely

**For Site Tasks**:
- Over-recruit sites (plan for 20-30% dropout)
- Start site identification early
- Use experienced sites when possible

**For Data Tasks**:
- Ongoing data review (don't wait for end)
- Automated data cleaning rules
- Adequate data management staffing

### Using Ilana PM Effectively

1. **Validate early and often**
   - Check timeline before finalizing
   - Re-validate after changes
   - Address errors/warnings promptly

2. **Use advisory services**
   - Get duration predictions for new tasks
   - Review risk scores for red flags
   - Follow mitigation suggestions

3. **Leverage analytics**
   - Review critical path regularly
   - Optimize parallel execution
   - Monitor slack for flexibility

4. **Maintain configuration**
   - Update ontology with lessons learned
   - Adjust duration benchmarks over time
   - Add authority-specific rules as needed

---

## Glossary

**AE**: Adverse Event - Undesirable medical occurrence in study participant

**CMC**: Chemistry, Manufacturing, and Controls - Drug quality documentation

**CRF**: Case Report Form - Form for collecting clinical study data

**CTA**: Clinical Trial Application - Regulatory submission (EU, UK, Canada)

**DSMB**: Data Safety Monitoring Board - Independent safety monitoring committee

**eCRF**: Electronic Case Report Form - Electronic data collection system

**EMA**: European Medicines Agency - EU regulatory authority

**FDA**: Food and Drug Administration - US regulatory authority

**FPI**: First Patient In - First patient enrolled in study

**GCP**: Good Clinical Practice - Ethical and scientific quality standard

**ICF**: Informed Consent Form - Document explaining study to participants

**ICH**: International Council for Harmonisation - Clinical trial standards body

**IND**: Investigational New Drug - FDA regulatory submission

**IRB**: Institutional Review Board - US ethics committee

**IVRS/IWRS**: Interactive Voice/Web Response System - Patient randomization system

**LPO**: Last Patient Out - Last patient completes last visit

**MHRA**: Medicines and Healthcare products Regulatory Agency - UK authority

**PI**: Principal Investigator - Lead physician at study site

**PMDA**: Pharmaceuticals and Medical Devices Agency - Japan authority

**REC**: Research Ethics Committee - EU ethics approval body

**SAE**: Serious Adverse Event - Life-threatening or fatal adverse event

**SAV**: Site Activation Visit - Final readiness check before enrollment

**SIV**: Site Initiation Visit - Site training and activation

---

**Document Version**: 1.0
**Author**: Ilana PM Clinical Team
**Last Review**: 2026-01-14
**Next Review**: 2026-07-14 (6 months)

For clinical questions or updates to this guide, please update this file and commit changes.
