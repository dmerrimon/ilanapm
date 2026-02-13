# Seleen Intelligence Layer - Complete Architecture Plan

**Date:** 2026-02-12
**Status:** Approved & Ready for Implementation
**Version:** 2.0 (Single Tier, Corrected Workflows)

---

## Executive Summary

Transform Seleen from a PM tool with intelligence features into an **intelligence layer** that sits on top of existing PM tools (MS Project, SmartSheet, Monday.com).

**Core Principle:** "CPMs input reality. Seleen interprets reality. Leadership acts on meaning."

**Key Architectural Decisions:**
1. **CPMs work ONLY in MS Project** - Never use web portal for tracker uploads
2. **Single-tier pricing** - All customers get all features (Enterprise tier only)
3. **Two portal views** - Account Management (admins) + Leadership Dashboard (everyone)
4. **Read-only intelligence** - Seleen never modifies MS Project or Excel files
5. **Account Admins configure trackers once** - CPMs just upload files

---

## Problem Statement

### Current State
- CPMs update reality in **two separate places**:
  1. MS Project timelines (task progress, dates, dependencies)
  2. Excel trackers (TMF completeness, Risk logs, Budget, Vendor management)
- These reality feeds are **fragmented** with no intelligence
- Leadership has no visibility into **what requires their attention**
- Timeline variance alone doesn't explain **why** things are slipping or **what** to do

### Target State
**Reality Feeds → Signal Normalization → Intelligence Synthesis → Leadership Views**

- CPMs continue working in MS Project + Excel (zero workflow changes)
- Seleen extracts data from both sources
- Intelligence engine correlates tracker signals with timeline impacts
- Escalation logic filters CPM noise → Director attention → VP escalation
- Leadership gets prescriptive insights, not just descriptive reports

---

## Complete User Workflows

### Workflow 1: One-Time Setup (Account Admin)

**Actor:** Account Admin
**Frequency:** Once during onboarding
**Location:** Web portal (app.seleen.io)

1. **Login to web portal** → Navigate to Account Management
2. **Go to Tracker Configuration** section
3. **Click "Add Tracker"** → Select "Risk Log"
4. **Upload sample Risk Log file** (Risk_Log_Sample.xlsx)
5. **System detects columns:**
   - ID, Risk Type, Description, Severity, Likelihood, Score, Mitigation Strategy, Responsible Person
6. **Map columns to Seleen schema:**
   ```
   ID                  → Risk #
   Risk Type           → Category
   Description         → Risk Detail
   Severity            → Impact
   Likelihood          → Probability
   Score               → Priority
   Mitigation Strategy → Mitigation Plan
   Responsible Person  → Owner
   ```
7. **Optional: Customize signal extraction rules**
   - Default: Priority ≥6 → Director escalation
   - Can adjust: Priority ≥7 → Director escalation (higher threshold)
8. **Click "Save Configuration"**
9. **Result:** Risk Log tracker configured for entire organization
10. **Repeat** for TMF Tracker, Budget Tracker, etc.

**Outcome:** All CPMs in organization can now upload trackers via MS Project add-in with automatic processing.

---

### Workflow 2: Daily CPM Operations (MS Project Only)

**Actor:** CPM
**Frequency:** Weekly (or as needed)
**Location:** MS Project with Seleen add-in

**Part A: Timeline Sync**
1. CPM works on timeline in MS Project as usual
2. Updates task progress, dates, dependencies
3. Clicks **"Sync Timeline"** button in Seleen ribbon
4. Background sync to Seleen API
5. Notification: "✅ Timeline synced"

**Part B: Tracker Upload**
1. CPM maintains Risk Log in Excel (as usual)
2. Updates risks, priorities, mitigation plans
3. Saves Excel file locally
4. In MS Project, clicks **"Upload Tracker"** button in Seleen ribbon
5. Dialog appears:
   ```
   Upload Tracker

   Select tracker type:
   • Risk Log
   • TMF Completeness Tracker
   • Budget Tracker

   [Browse for file...]

   C:\Users\Jane\Documents\Risk_Log_Jan2026.xlsx

   [Upload]
   ```
6. Clicks "Upload"
7. Background processing (2-5 seconds for <100 rows)
8. Notification appears:
   ```
   ✅ Upload complete!
   📊 23 risks processed
   ⚠️ 5 escalations generated
   🎯 Study health: 68 (Warning)

   [View Dashboard] [Close]
   ```
9. CPM continues working in MS Project
10. **CPM never opens web portal** (unless they want to view dashboard)

**Outcome:** Reality (timeline + tracker data) uploaded to Seleen with zero workflow changes for CPM.

---

### Workflow 3: Leadership Consumption (Web Portal)

**Actor:** Director, Executive, or CPM
**Frequency:** As needed (daily/weekly/monthly)
**Location:** Web portal (app.seleen.io)

1. **Login to web portal** → Navigate to Leadership Dashboard
2. **View portfolio overview:**
   ```
   Portfolio Overview

   Studies (12 total):
   🟢 Healthy (7)
   🟡 Warning (4)
   🔴 Critical (1)
   ```
3. **Click on study** (e.g., Study XYZ-123)
4. **View study details:**
   ```
   Study XYZ-123 | Health: 68 (Warning) | Updated: 5 min ago

   📍 Latest Signals (5):
   • Risk #13: Site activation slower (Priority 7) - 5 min ago
     Source: Risk Log uploaded by Jane Doe

   • TMF: 12 missing regulatory documents - 2 hours ago
     Source: TMF Tracker uploaded by Jane Doe

   🔗 Correlations (3):
   • Risk #13 → Site Activation milestone
     Type: Risk | Confidence: 85%
     Est. delay: 14 days | $344K impact
     Reasoning: "High priority site risk affects Site Activation
     milestone. Historical data shows similar risks cause 14-day delays."

   🚨 Escalations (3):
   • [DIRECTOR] Risk #13: Site activation at risk
     Recommended: Expedite site contracts, activate backup sites
     Status: Open | Created: 5 min ago

   • [DIRECTOR] TMF <75%: Regulatory resources needed
     Recommended: Allocate additional regulatory staff
     Status: Open | Created: 2 hours ago
   ```
5. **Click on escalation** to view details
6. **Add resolution notes** (what action was taken)
7. **Mark escalation as "Acknowledged" or "Resolved"**
8. **Filter/sort dashboard** by study, priority, signal type, etc.

**Outcome:** Leadership gets actionable intelligence with prescriptive recommendations.

---

## Architecture Components

### 1. Timeline Template System

**Purpose:** Replace task_ontology.yaml with database-driven template library

**5 Templates:**
1. **Study Startup** (224 tasks, 8 categories)
   - Study Award → FPI
   - Categories: Initiation, Legal/Finance, Meetings, Project Plans, Systems Setup, Drug Supply, Vendors, Training

2. **Study Implementation/Active Enrollment** (8 milestones + 2 recurring)
   - Milestones: FPI → FPD → FCR → LPI → LPD → LPLV → LSC → Follow-up
   - Recurring: IRB Continuing Review (annual), FDA Annual Report (annual if IND)

3. **Study Closeout** (4 subphases, 8-14 months)
   - Clinical DB Lock (6 weeks)
   - Laboratory DB Lock (14 weeks)
   - CSR Preparation (30 weeks)
   - Manuscript Submission (12 months)

4. **Site Activation** (60 checklist items)
   - Site selection → Site activated

5. **Site Closeout** (18 tasks, 7 categories)
   - Site complete → DB lock ready

**Database Schema:**

```sql
-- Timeline Templates Library
CREATE TABLE timeline_templates (
    template_id TEXT PRIMARY KEY,
    template_name TEXT NOT NULL,
    template_type TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0',
    description TEXT,
    total_task_count INTEGER,
    estimated_duration_days INTEGER,
    applicable_phases TEXT,  -- JSON array
    applicable_authorities TEXT,  -- JSON array
    org_id TEXT,  -- NULL = system template
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Template Tasks
CREATE TABLE template_tasks (
    task_id TEXT PRIMARY KEY,
    template_id TEXT NOT NULL,
    task_name TEXT NOT NULL,
    task_code TEXT,
    category TEXT NOT NULL,

    -- Duration with variance ranges
    typical_duration_days INTEGER NOT NULL,
    min_duration_days INTEGER,
    max_duration_days INTEGER,
    p25_duration_days INTEGER,
    p75_duration_days INTEGER,

    -- Task metadata
    is_milestone INTEGER DEFAULT 0,
    is_critical_path INTEGER DEFAULT 0,
    is_recurring INTEGER DEFAULT 0,
    recurrence_interval_days INTEGER,
    description TEXT,
    responsible_role TEXT,

    -- Hierarchy
    parent_task_id TEXT,
    sort_order INTEGER NOT NULL,
    outline_level INTEGER DEFAULT 1,

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Template Dependencies
CREATE TABLE template_dependencies (
    dependency_id TEXT PRIMARY KEY,
    template_id TEXT NOT NULL,
    predecessor_task_id TEXT NOT NULL,
    successor_task_id TEXT NOT NULL,
    dependency_type TEXT DEFAULT 'finish-to-start',
    lag_days INTEGER DEFAULT 0,
    is_hard_dependency INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);
```

---

### 2. Tracker System

**Purpose:** Define schemas for Excel trackers and store uploads

**Standard Trackers:**
1. **Risk Log** - Impact, Probability, Priority, Mitigation Plans
2. **TMF Completeness** - Regulatory artifacts, status, missing documents
3. **Budget Tracker** - Planned vs Actual, Variance tracking
4. **Vendor Management** - Deliverables, due dates, performance

**Database Schema:**

```sql
-- Tracker Definitions
CREATE TABLE tracker_definitions (
    tracker_def_id TEXT PRIMARY KEY,
    tracker_name TEXT NOT NULL,
    tracker_type TEXT NOT NULL,
    description TEXT,
    schema_definition TEXT NOT NULL,  -- JSON: Column mappings
    signal_extraction_rules TEXT,  -- JSON: Rules for extracting signals
    version TEXT NOT NULL DEFAULT '1.0',
    is_system_tracker INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Column Mappings (Account Admin Configuration)
CREATE TABLE tracker_column_mappings (
    mapping_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    tracker_type TEXT NOT NULL,
    column_mappings TEXT NOT NULL,  -- JSON: {"org_column": "seleen_field"}
    transformation_rules TEXT,  -- JSON: Custom logic
    created_by TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(org_id, tracker_type)
);

-- Tracker Uploads (CPM Uploads)
CREATE TABLE tracker_uploads (
    upload_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    tracker_def_id TEXT NOT NULL,
    uploaded_by TEXT,
    upload_timestamp TEXT DEFAULT (datetime('now')),
    original_filename TEXT,
    file_hash TEXT,  -- SHA256 for deduplication
    parse_status TEXT DEFAULT 'pending',
    rows_parsed INTEGER,
    signals_extracted INTEGER,
    parse_errors TEXT,  -- JSON array
    storage_url TEXT,
    version_number INTEGER DEFAULT 1,
    previous_upload_id TEXT
);
```

---

### 3. Signal System

**Purpose:** Normalize signals extracted from all trackers

**Signal Types:**
- `risk_high_priority` - Priority ≥6
- `risk_critical` - Priority 9
- `risk_no_mitigation` - High priority with no mitigation plan
- `risk_overdue` - Target date passed
- `risk_escalated` - Escalation notes populated
- `tmf_missing_document` - Status = "Missing Document"
- `tmf_overdue` - Pending Response >14 days
- `tmf_completeness_risk` - Completeness <75%
- `tmf_escalation` - Review Log escalation item
- `budget_variance` - Overspend >15%
- `vendor_delayed` - Deliverable overdue

**Database Schema:**

```sql
-- Signals (normalized across all trackers)
CREATE TABLE signals (
    signal_id TEXT PRIMARY KEY,
    upload_id TEXT NOT NULL,
    org_id TEXT NOT NULL,
    project_id TEXT NOT NULL,

    -- Signal classification
    signal_type TEXT NOT NULL,
    signal_category TEXT,  -- "Regulatory", "Clinical", "Site", "Safety"
    signal_source TEXT NOT NULL,  -- "risk_log", "tmf_tracker"

    -- Signal content
    signal_description TEXT NOT NULL,
    signal_detail TEXT,  -- JSON: Full structured data

    -- Severity
    priority INTEGER,  -- 1-9
    status TEXT DEFAULT 'open',  -- "open", "in_progress", "resolved"

    -- Temporal
    date_identified TEXT,
    target_date TEXT,
    actual_completion_date TEXT,

    -- Escalation
    escalation_notes TEXT,
    escalation_level TEXT,  -- NULL, "director", "vp"

    -- Ownership
    responsible_party TEXT,
    assigned_to TEXT,

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Signal State History (audit trail)
CREATE TABLE signal_state_history (
    history_id TEXT PRIMARY KEY,
    signal_id TEXT NOT NULL,
    state_change_type TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by TEXT,
    changed_at TEXT DEFAULT (datetime('now'))
);
```

---

### 4. Correlation System

**Purpose:** Link signals to timeline milestones

**Pre-configured Correlation Rules:**

```yaml
correlation_rules:
  - rule_id: "CORR_001"
    rule_name: "High Priority Risk → Site Activation"
    signal_type: "risk_high_priority"
    signal_category: "Site"
    signal_detail_pattern: ".*site activation.*|.*site contract.*"

    affected_milestones: ["Site Activation"]
    affected_milestone_codes: ["SITE_ACT"]

    correlation_type: "risk"
    confidence_score: 0.85
    impact_type: "delay"
    delay_estimation_logic: "multiplier:7.0"  # Priority × 7 days

    escalation_trigger: true
    escalation_level: "director"

    reasoning_template: "Risk #{signal.priority}: '{signal_description}' affects {milestone}. Estimated delay: {delay_days} days."

  - rule_id: "CORR_002"
    rule_name: "Enrollment Risk → LPI Milestone"
    signal_type: "risk_high_priority"
    signal_category: "Clinical"
    signal_detail_pattern: ".*enrollment.*|.*screen failure.*|.*drop.?out.*"

    affected_milestones: ["LPI", "Last Patient In"]
    affected_milestone_codes: ["LPI"]

    correlation_type: "risk"
    confidence_score: 0.90
    impact_type: "delay"

    escalation_trigger: true
    escalation_level: "director"

  - rule_id: "CORR_003"
    rule_name: "Site Closeout AE Resolution → Clinical DB Lock"
    signal_type: "site_closeout_blocker"
    signal_detail_pattern: "HS_CO_002"

    affected_milestones: ["Clinical DB Lock"]
    affected_milestone_codes: ["CDB_LOCK"]

    correlation_type: "blocker"  # HARD BLOCKER
    confidence_score: 1.0
    impact_type: "delay"
    delay_estimation_logic: "fixed:14"

    escalation_trigger: true
    escalation_level: "director"

  - rule_id: "CORR_004"
    rule_name: "TMF Completeness <75% → Regulatory Submission"
    signal_type: "tmf_completeness_risk"

    affected_milestones: ["IND Submission", "CTA Submission"]
    affected_milestone_codes: ["IND_SUB", "CTA_SUB"]

    correlation_type: "risk"
    confidence_score: 0.80
    impact_type: "delay"
    delay_estimation_logic: "fixed:30"

    escalation_trigger: true
    escalation_level: "director"

  - rule_id: "CORR_005"
    rule_name: "Safety/Toxicity Risk → FPD and DSMB"
    signal_type: "risk_high_priority"
    signal_category: "Safety"
    signal_detail_pattern: ".*toxicity.*|.*SAE.*|.*DSMB.*"

    affected_milestones: ["FPD", "First Patient Dosed", "DSMB Review"]
    affected_milestone_codes: ["FPD", "DSMB"]

    correlation_type: "risk"
    confidence_score: 0.95
    impact_type: "delay"
    delay_estimation_logic: "fixed:21"

    escalation_trigger: true
    escalation_level: "vp"  # Immediate VP escalation
```

**Database Schema:**

```sql
-- Signal-to-Timeline Correlations
CREATE TABLE signal_timeline_correlations (
    correlation_id TEXT PRIMARY KEY,
    signal_id TEXT NOT NULL,
    project_id TEXT NOT NULL,

    -- What timeline element is affected
    affected_milestone_name TEXT,
    affected_milestone_code TEXT,
    affected_task_ids TEXT,  -- JSON array

    -- Correlation strength
    correlation_type TEXT NOT NULL,  -- "blocker", "risk", "informational"
    confidence_score REAL,  -- 0.0-1.0

    -- Impact assessment
    impact_type TEXT,  -- "delay", "cost_increase", "resource_bottleneck"
    estimated_delay_days INTEGER,
    estimated_cost_impact REAL,

    -- Rule that triggered
    correlation_rule_id TEXT,
    correlation_reasoning TEXT,

    detected_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT
);
```

---

### 5. Escalation System

**Purpose:** Determine what requires Director vs VP attention

**Escalation Thresholds:**

```python
ESCALATION_THRESHOLDS = {
    'director': {
        'risk_priority': 6,  # Priority ≥6 → Director
        'tmf_completeness': 75,  # <75% → Director
        'milestone_delay_weeks': 2,  # >2 weeks → Director
        'correlation_type': ['risk', 'blocker'],
    },
    'vp': {
        'risk_priority': 9,  # Priority 9 → VP
        'critical_path_delay_weeks': 4,  # >4 weeks → VP
        'safety_risk': True,  # Any safety risk → VP
        'systemic_pattern': True,  # Systemic issues → VP
        'correlation_type': ['blocker'],
    }
}
```

**Database Schema:**

```sql
-- Escalation Rules
CREATE TABLE escalation_rules (
    rule_id TEXT PRIMARY KEY,
    rule_name TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    trigger_condition TEXT NOT NULL,  -- JSON
    escalation_level TEXT NOT NULL,  -- "cpm", "director", "vp"
    escalation_channel TEXT DEFAULT 'dashboard',
    notification_template TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Escalations (instances)
CREATE TABLE escalations (
    escalation_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    project_id TEXT NOT NULL,

    trigger_type TEXT NOT NULL,
    trigger_id TEXT NOT NULL,
    escalation_rule_id TEXT,

    escalation_level TEXT NOT NULL,
    escalation_reason TEXT NOT NULL,
    escalation_data TEXT,  -- JSON

    assigned_to TEXT,
    assigned_role TEXT,

    status TEXT DEFAULT 'open',
    priority INTEGER,

    intervention_recommended TEXT,
    intervention_taken TEXT,
    resolution_notes TEXT,

    created_at TEXT DEFAULT (datetime('now')),
    acknowledged_at TEXT,
    resolved_at TEXT
);
```

---

### 6. Study Health Score

**Purpose:** Calculate comprehensive study health (0-100)

**Calculation Weights:**

```python
WEIGHTS = {
    'timeline_variance': 0.25,
    'risk_exposure': 0.25,
    'tmf_completeness': 0.20,
    'enrollment_rate': 0.15,
    'budget_variance': 0.10,
    'vendor_performance': 0.05
}
```

**Health Status:**
- 75-100: 🟢 Healthy
- 50-74: 🟡 Warning
- 0-49: 🔴 Critical

**Database Schema:**

```sql
-- Study Health Snapshots (cached for performance)
CREATE TABLE study_health_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    project_id TEXT NOT NULL,

    overall_health_score REAL NOT NULL,
    health_status TEXT NOT NULL,

    -- Component scores
    timeline_score REAL,
    risk_score REAL,
    tmf_score REAL,
    enrollment_score REAL,
    budget_score REAL,
    vendor_score REAL,

    -- Top risks (JSON array)
    top_risks TEXT,

    -- Escalation counts
    active_escalations_count INTEGER DEFAULT 0,
    director_escalations_count INTEGER DEFAULT 0,
    vp_escalations_count INTEGER DEFAULT 0,

    -- Recommendations (JSON array)
    recommended_actions TEXT,

    snapshot_date TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
```

---

### 7. Dashboard System

**Two Portal Views:**

**1. Account Management View (Account Admins Only)**
- User & seat management
- Billing (FreshBooks integration)
- Tracker Configuration:
  - Upload sample tracker files
  - Configure column mappings
  - Customize signal extraction rules
  - Download standard tracker templates
- Organization settings

**2. Leadership Dashboard (All Users - No Role-Based Filtering)**
- All studies with health scores
- All signals across all trackers
- All correlations (signal → milestone impacts)
- All escalations (Director + VP level)
- Portfolio health summary
- Timeline variance analysis
- Recommended interventions
- Pattern detection (systemic issues)
- Financial impact summary

**Database Schema:**

```sql
-- Dashboard Views (pre-computed for performance)
CREATE TABLE dashboard_views (
    view_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    user_id TEXT,
    view_type TEXT NOT NULL,  -- "account_mgmt", "leadership_dashboard"
    view_data TEXT NOT NULL,  -- JSON
    generated_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT
);
```

---

### 8. Pattern Detection (Enterprise Feature)

**Purpose:** Detect systemic issues across multiple studies

**Pattern Types:**
- Systemic risks (same risk across multiple studies)
- Resource bottlenecks (shared resources causing delays)
- Timeline trends (consistent delays in specific phases)

**Database Schema:**

```sql
-- Patterns Table
CREATE TABLE patterns (
    pattern_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    pattern_type TEXT NOT NULL,
    pattern_name TEXT NOT NULL,
    pattern_description TEXT,

    scope TEXT NOT NULL,  -- "single_study", "portfolio", "organization"
    affected_project_ids TEXT,  -- JSON array

    severity TEXT NOT NULL,  -- "low", "medium", "high", "critical"
    confidence_score REAL,

    evidence_signals TEXT,  -- JSON array of signal_ids
    evidence_correlations TEXT,  -- JSON array

    recommended_interventions TEXT,  -- JSON array

    detected_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT,
    status TEXT DEFAULT 'active'
);
```

---

## Single-Tier Pricing

**All customers get all features (no tiers)**

**Enterprise Tier (Only Tier):**
- ✅ Timeline template library
- ✅ Template customization
- ✅ Variance detection
- ✅ Leadership Dashboard
- ✅ Tracker upload (all types)
- ✅ Signal extraction (configurable rules)
- ✅ Study health score
- ✅ Signal-to-timeline correlation
- ✅ Custom column mapping
- ✅ Custom signal extraction rules
- ✅ Pattern detection
- ✅ Intervention recommendations
- ✅ Escalation filtering
- ✅ Portfolio aggregation
- ✅ Systemic pattern detection
- ✅ Resource collision detection
- ✅ Portfolio forecasting
- ✅ Full API access
- ✅ SSO/SAML
- ✅ Custom tracker types

**Pricing Model:**
- Per-seat subscription
- All features included
- No upsells or feature gating
- Simple, transparent pricing

**Tier Enforcement:**
- `tier_enforcement.py` updated to always allow access
- All `check_tier()` calls return `True`
- All `check_feature_access()` calls return `True`
- `require_tier()` decorator logs but allows all access
- Backward compatible with existing code

---

## Data Flow

```
┌─────────────────────────────────────────┐
│      REALITY INPUT LAYER                │
│      (CPM Workflow - No Changes)        │
└─────────────────────────────────────────┘
                 ↓
    ┌────────────┬───────────┬──────────┐
    │            │           │          │
MS Project   TMF Tracker  Risk Log   Budget
(Timeline)    (Excel)     (Excel)    (Excel)
    │            │           │          │
    └────────────┴───────────┴──────────┘
                 ↓
┌─────────────────────────────────────────┐
│    SELEEN INTELLIGENCE LAYER            │
│    (Signal Normalization)               │
└─────────────────────────────────────────┘
                 ↓
    ┌────────────┬───────────┬──────────┐
    │            │           │          │
 Timeline    Signal      Signal      Signal
 Extractor  Extraction  Extraction  Extraction
            Engine      Engine      Engine
    │            │           │          │
    └────────────┴───────────┴──────────┘
                 ↓
           Signals (Normalized)
                 ↓
┌─────────────────────────────────────────┐
│    INTELLIGENCE SYNTHESIS               │
│    (Correlation, Escalation, Scoring)   │
└─────────────────────────────────────────┘
                 ↓
    ┌────────────┬───────────┬──────────┐
    │            │           │          │
Correlation  Pattern    Escalation  Health
Engine       Detection  Engine      Score
    │            │           │          │
    └────────────┴───────────┴──────────┘
                 ↓
┌─────────────────────────────────────────┐
│    LEADERSHIP CONSUMPTION LAYER         │
│    (Role-Based Dashboards)              │
└─────────────────────────────────────────┘
                 ↓
    ┌────────────┬───────────┬──────────┐
    │            │           │          │
    CPM        Director      VP
   Daily       Weekly      Monthly
  Dashboard   Dashboard   Dashboard
```

---

## Implementation Plan

### Phase 1: Foundation (Weeks 1-4)
- ✅ Database schema migration (007_intelligence_layer_expansion.sql)
- ⏳ Migration script: task_ontology.yaml → timeline_templates
- ⏳ Populate 5 timeline templates
- ⏳ Template retrieval API endpoints
- ⏳ Basic signal extraction engine (TMF, Risk Log)
- ⏳ Tracker definition schemas

### Phase 2: Correlation Engine (Weeks 5-8)
- Correlation rules engine
- Signal-to-timeline correlation logic
- Pattern detection (single-study)
- Study health score calculator
- Escalation logic engine

### Phase 3: Dashboards (Weeks 9-12)
- Unified Leadership Dashboard API + UI
- Study health snapshots (caching)
- Escalation notification system
- Account Management View API + UI
- Filter/sort capabilities

### Phase 4: Portfolio Intelligence (Weeks 13-16)
- Portfolio aggregation
- Portfolio health rollup
- Cross-study pattern detection
- Systemic issue detection
- Resource allocation recommendations

### Phase 5: Integrations & Polish (Weeks 17-20)
- MS Project add-in tracker upload UI
- Tracker upload workflow (file picker, notifications)
- Email/Slack/SMS notifications
- Dashboard export/reporting
- Column mapping UI polish

---

## API Endpoints

### Template Endpoints
```
GET    /api/v1/templates                          # List templates
GET    /api/v1/templates/{id}                     # Get template
GET    /api/v1/templates/{id}/tasks               # Get tasks
GET    /api/v1/templates/{id}/critical-path       # Calculate critical path
POST   /api/v1/templates/{id}/export              # Export to MS Project XML
POST   /api/v1/templates/{id}/customize           # Customize
```

### Tracker & Signal Endpoints
```
POST   /api/v1/trackers/upload                    # Upload Excel (from MS Project add-in)
POST   /api/v1/trackers/configure-mapping         # Configure column mapping (Account Admin)
GET    /api/v1/trackers/templates/{type}          # Download standard template
GET    /api/v1/signals                            # Get signals
POST   /api/v1/signals/{id}/resolve               # Mark resolved
GET    /api/v1/signals/correlations               # Get correlations
```

### Intelligence Endpoints
```
POST   /api/v1/intelligence/analyze               # Analyze timeline + trackers
GET    /api/v1/intelligence/health/{project_id}   # Get health score
POST   /api/v1/intelligence/correlate             # Correlate
GET    /api/v1/intelligence/patterns              # Patterns
```

### Dashboard Endpoints
```
GET    /api/v1/dashboards/leadership              # Unified leadership dashboard
GET    /api/v1/dashboards/portfolio/health        # Portfolio health
GET    /api/v1/dashboards/account-management      # Account management view
```

### Escalation Endpoints
```
GET    /api/v1/escalations                        # Get escalations
POST   /api/v1/escalations/{id}/acknowledge       # Acknowledge
POST   /api/v1/escalations/{id}/resolve           # Resolve
```

---

## Success Metrics

### Technical Metrics
- Signal extraction success rate >95%
- Correlation confidence scores (avg >0.75)
- Dashboard load times <2 seconds
- Real-time tracker processing <5s for <100 rows
- Background tracker processing <60s for 100-500 rows

### Business Metrics
- CPM time saved (target: 2 hours/week per CPM)
- Leadership attention precision (% of escalations resolved with intervention)
- Study delay prediction accuracy (±2 weeks)
- User adoption (% of studies with active tracker uploads)

---

## Key Design Principles

1. **CPM workflow preserved** (read-only, no additional burden)
2. **CPMs work ONLY in MS Project** (never use web portal for tracker uploads)
3. **Signal correlation transparent** (rule-based, explainable)
4. **Escalation precise** (right attention at right level)
5. **Single-tier pricing** (per-seat subscription, all features included)
6. **PM-tool agnostic** (easy expansion to SmartSheet, Monday.com)

---

## Migration from Existing Ontology

**Current State:**
- Single `task_ontology.yaml` with ~200+ task definitions
- 23 regulatory authorities with country-specific workflows

**Target State:**
- Template library with 5 templates in database
- Regulatory authority data preserved for multi-country calculator

**Migration Script:** `scripts/migrate_ontology_to_templates.py`

**Backward Compatibility:**
- Keep `task_ontology.yaml` for 2 release cycles
- Add deprecation warnings in API responses

---

## Critical Files

1. **`backend/database/migrations/007_intelligence_layer_expansion.sql`** - ✅ Created
2. **`backend/intelligence/tier_enforcement.py`** - ✅ Updated (single tier)
3. **`backend/config/task_ontology.yaml`** - Source data for migration
4. **`backend/api/intelligence.py`** - Intelligence API endpoints
5. **`desktop-addin/IlanaPM.AddIn/`** - MS Project add-in (C#)
6. **`frontend/src/`** - Web portal (Next.js)

---

**Status:** Ready for Phase 1 implementation
**Next Step:** Create migration script for task_ontology.yaml → timeline_templates database
