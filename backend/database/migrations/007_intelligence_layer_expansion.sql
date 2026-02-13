-- Migration 007: Intelligence Layer Expansion
-- Created: 2026-02-12
-- Description: Complete intelligence layer for signal extraction, correlation, and escalation
-- Based on approved plan: Transform Seleen into intelligence layer sitting on top of PM tools

-- ============================================================================
-- 1. TIMELINE TEMPLATES SYSTEM
-- Replaces task_ontology.yaml with database-driven template library
-- ============================================================================

-- Timeline Templates Library
CREATE TABLE IF NOT EXISTS timeline_templates (
    template_id TEXT PRIMARY KEY,
    template_name TEXT NOT NULL,  -- "Study Startup", "Site Activation", etc.
    template_type TEXT NOT NULL,  -- "study_startup", "implementation", "closeout", "site_activation", "site_closeout"
    version TEXT NOT NULL DEFAULT '1.0',
    description TEXT,
    total_task_count INTEGER,
    estimated_duration_days INTEGER,
    applicable_phases TEXT,  -- JSON array: ["Phase I", "Phase II", "Phase III"]
    applicable_authorities TEXT,  -- JSON array: ["FDA", "EMA", "PPB"]
    org_id TEXT,  -- NULL = system template, non-NULL = custom org template
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_timeline_templates_type ON timeline_templates(template_type);
CREATE INDEX IF NOT EXISTS idx_timeline_templates_org ON timeline_templates(org_id);

-- Template Tasks (master definitions)
CREATE TABLE IF NOT EXISTS template_tasks (
    task_id TEXT PRIMARY KEY,
    template_id TEXT NOT NULL,
    task_name TEXT NOT NULL,
    task_code TEXT,  -- "SS_INI_001", "SITE_ACT_001"
    category TEXT NOT NULL,  -- "Initiation", "Regulatory", "Data Management"

    -- Duration with variance ranges
    typical_duration_days INTEGER NOT NULL,
    min_duration_days INTEGER,
    max_duration_days INTEGER,
    p25_duration_days INTEGER,
    p75_duration_days INTEGER,

    -- Task metadata
    is_milestone INTEGER DEFAULT 0,  -- Boolean: 1 = milestone, 0 = task
    is_critical_path INTEGER DEFAULT 0,  -- Boolean
    is_recurring INTEGER DEFAULT 0,  -- Boolean (for annual IRB reviews, etc.)
    recurrence_interval_days INTEGER,  -- For recurring tasks
    description TEXT,
    responsible_role TEXT,  -- "CPM", "Regulatory Manager", "Site Coordinator"
    notes TEXT,

    -- Hierarchy
    parent_task_id TEXT,
    sort_order INTEGER NOT NULL,
    outline_level INTEGER DEFAULT 1,  -- 1 = top level, 2 = subtask, etc.

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (template_id) REFERENCES timeline_templates(template_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_task_id) REFERENCES template_tasks(task_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_template_tasks_template ON template_tasks(template_id);
CREATE INDEX IF NOT EXISTS idx_template_tasks_category ON template_tasks(category);
CREATE INDEX IF NOT EXISTS idx_template_tasks_parent ON template_tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_template_tasks_milestone ON template_tasks(is_milestone);
CREATE INDEX IF NOT EXISTS idx_template_tasks_code ON template_tasks(task_code);

-- Template Dependencies
CREATE TABLE IF NOT EXISTS template_dependencies (
    dependency_id TEXT PRIMARY KEY,
    template_id TEXT NOT NULL,
    predecessor_task_id TEXT NOT NULL,
    successor_task_id TEXT NOT NULL,
    dependency_type TEXT DEFAULT 'finish-to-start',  -- "finish-to-start", "start-to-start", "finish-to-finish"
    lag_days INTEGER DEFAULT 0,
    is_hard_dependency INTEGER DEFAULT 1,  -- Boolean: 1 = hard blocker, 0 = soft

    created_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (template_id) REFERENCES timeline_templates(template_id) ON DELETE CASCADE,
    FOREIGN KEY (predecessor_task_id) REFERENCES template_tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (successor_task_id) REFERENCES template_tasks(task_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_template_dependencies_template ON template_dependencies(template_id);
CREATE INDEX IF NOT EXISTS idx_template_dependencies_predecessor ON template_dependencies(predecessor_task_id);
CREATE INDEX IF NOT EXISTS idx_template_dependencies_successor ON template_dependencies(successor_task_id);

-- ============================================================================
-- 2. TRACKER SYSTEM
-- Defines schemas for Excel trackers (TMF, Risk Log, Budget, Vendor, etc.)
-- ============================================================================

-- Tracker Definitions (what trackers exist)
CREATE TABLE IF NOT EXISTS tracker_definitions (
    tracker_def_id TEXT PRIMARY KEY,
    tracker_name TEXT NOT NULL,  -- "TMF Completeness", "Risk Log"
    tracker_type TEXT NOT NULL,  -- "tmf", "risk", "budget", "vendor", "resource"
    description TEXT,
    schema_definition TEXT NOT NULL,  -- JSON: Column mappings, data types, validation rules
    signal_extraction_rules TEXT,  -- JSON: Rules for extracting signals from this tracker
    version TEXT NOT NULL DEFAULT '1.0',
    is_system_tracker INTEGER DEFAULT 1,  -- Boolean: 1 = built-in, 0 = custom
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tracker_definitions_type ON tracker_definitions(tracker_type);

-- Tracker Uploads (CPM uploads Excel files)
CREATE TABLE IF NOT EXISTS tracker_uploads (
    upload_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    project_id TEXT NOT NULL,  -- Links to project_profiles.profile_id or MS Project file ID
    tracker_def_id TEXT NOT NULL,

    uploaded_by TEXT,
    upload_timestamp TEXT DEFAULT (datetime('now')),
    original_filename TEXT,
    file_hash TEXT,  -- SHA256 for deduplication

    parse_status TEXT DEFAULT 'pending',  -- "pending", "parsing", "completed", "failed"
    rows_parsed INTEGER,
    signals_extracted INTEGER,
    parse_errors TEXT,  -- JSON array of error messages

    storage_url TEXT,  -- S3/Azure Blob URL
    version_number INTEGER DEFAULT 1,
    previous_upload_id TEXT,  -- For versioning/history

    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE,
    FOREIGN KEY (tracker_def_id) REFERENCES tracker_definitions(tracker_def_id),
    FOREIGN KEY (previous_upload_id) REFERENCES tracker_uploads(upload_id) ON DELETE SET NULL,
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_tracker_uploads_org ON tracker_uploads(org_id);
CREATE INDEX IF NOT EXISTS idx_tracker_uploads_project ON tracker_uploads(project_id);
CREATE INDEX IF NOT EXISTS idx_tracker_uploads_tracker ON tracker_uploads(tracker_def_id);
CREATE INDEX IF NOT EXISTS idx_tracker_uploads_timestamp ON tracker_uploads(upload_timestamp);
CREATE INDEX IF NOT EXISTS idx_tracker_uploads_status ON tracker_uploads(parse_status);

-- ============================================================================
-- 3. SIGNAL SYSTEM
-- Normalized signals extracted from all trackers
-- ============================================================================

-- Signals (normalized across all trackers)
CREATE TABLE IF NOT EXISTS signals (
    signal_id TEXT PRIMARY KEY,
    upload_id TEXT NOT NULL,
    org_id TEXT NOT NULL,
    project_id TEXT NOT NULL,

    -- Signal classification
    signal_type TEXT NOT NULL,  -- "risk_high_priority", "tmf_missing_document", "tmf_overdue", etc.
    signal_category TEXT,  -- "Regulatory", "Clinical", "Site", "Safety", "General"
    signal_source TEXT NOT NULL,  -- "risk_log", "tmf_tracker", "budget_tracker"

    -- Signal content
    signal_description TEXT NOT NULL,
    signal_detail TEXT,  -- JSON: Full structured data from tracker row

    -- Severity
    priority INTEGER,  -- 1-9 (for Risk Log: Impact × Probability)
    status TEXT DEFAULT 'open',  -- "open", "in_progress", "resolved", "closed"

    -- Temporal
    date_identified TEXT,
    target_date TEXT,
    actual_completion_date TEXT,

    -- Escalation
    escalation_notes TEXT,
    escalation_level TEXT,  -- NULL, "director", "vp"

    -- Ownership
    responsible_party TEXT,
    assigned_to TEXT,  -- user_id

    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (upload_id) REFERENCES tracker_uploads(upload_id) ON DELETE CASCADE,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_signals_org ON signals(org_id);
CREATE INDEX IF NOT EXISTS idx_signals_project ON signals(project_id);
CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(signal_type);
CREATE INDEX IF NOT EXISTS idx_signals_category ON signals(signal_category);
CREATE INDEX IF NOT EXISTS idx_signals_priority ON signals(priority);
CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status);
CREATE INDEX IF NOT EXISTS idx_signals_escalation ON signals(escalation_level);

-- Signal State History (audit trail)
CREATE TABLE IF NOT EXISTS signal_state_history (
    history_id TEXT PRIMARY KEY,
    signal_id TEXT NOT NULL,
    state_change_type TEXT NOT NULL,  -- "status_change", "priority_change", "assignment_change", "escalation"
    old_value TEXT,
    new_value TEXT,
    changed_by TEXT,  -- user_id
    changed_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (signal_id) REFERENCES signals(signal_id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_signal_history_signal ON signal_state_history(signal_id);
CREATE INDEX IF NOT EXISTS idx_signal_history_timestamp ON signal_state_history(changed_at);

-- ============================================================================
-- 4. CORRELATION SYSTEM
-- Links signals to timeline milestones
-- ============================================================================

-- Signal-to-Timeline Correlations
CREATE TABLE IF NOT EXISTS signal_timeline_correlations (
    correlation_id TEXT PRIMARY KEY,
    signal_id TEXT NOT NULL,
    project_id TEXT NOT NULL,

    -- What timeline element is affected
    affected_milestone_name TEXT,  -- "Site Activation", "Clinical DB Lock", "FPI"
    affected_milestone_code TEXT,  -- "SITE_ACT", "CDB_LOCK", "FPI"
    affected_task_ids TEXT,  -- JSON array of task IDs from MS Project

    -- Correlation strength
    correlation_type TEXT NOT NULL,  -- "blocker", "risk", "informational"
    confidence_score REAL,  -- 0.0-1.0

    -- Impact assessment
    impact_type TEXT,  -- "delay", "cost_increase", "resource_bottleneck"
    estimated_delay_days INTEGER,
    estimated_cost_impact REAL,

    -- Rule that triggered
    correlation_rule_id TEXT,
    correlation_reasoning TEXT,  -- Human-readable explanation

    detected_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT,

    FOREIGN KEY (signal_id) REFERENCES signals(signal_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_correlations_signal ON signal_timeline_correlations(signal_id);
CREATE INDEX IF NOT EXISTS idx_correlations_project ON signal_timeline_correlations(project_id);
CREATE INDEX IF NOT EXISTS idx_correlations_milestone ON signal_timeline_correlations(affected_milestone_code);
CREATE INDEX IF NOT EXISTS idx_correlations_type ON signal_timeline_correlations(correlation_type);

-- ============================================================================
-- 5. ESCALATION SYSTEM
-- Determines what requires Director vs. VP attention
-- ============================================================================

-- Escalation Rules
CREATE TABLE IF NOT EXISTS escalation_rules (
    rule_id TEXT PRIMARY KEY,
    rule_name TEXT NOT NULL,
    trigger_type TEXT NOT NULL,  -- "signal_priority", "correlation_type", "pattern", "milestone_delay"
    trigger_condition TEXT NOT NULL,  -- JSON: Condition logic
    escalation_level TEXT NOT NULL,  -- "cpm", "director", "vp"
    escalation_channel TEXT DEFAULT 'dashboard',  -- "dashboard", "email", "slack", "sms"
    notification_template TEXT,
    is_active INTEGER DEFAULT 1,  -- Boolean
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_escalation_rules_level ON escalation_rules(escalation_level);
CREATE INDEX IF NOT EXISTS idx_escalation_rules_active ON escalation_rules(is_active);

-- Escalations (instances)
CREATE TABLE IF NOT EXISTS escalations (
    escalation_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    project_id TEXT NOT NULL,

    trigger_type TEXT NOT NULL,  -- "signal", "correlation", "pattern", "milestone_delay"
    trigger_id TEXT NOT NULL,  -- signal_id, correlation_id, etc.
    escalation_rule_id TEXT,

    escalation_level TEXT NOT NULL,  -- "director", "vp"
    escalation_reason TEXT NOT NULL,
    escalation_data TEXT,  -- JSON: Full context data

    assigned_to TEXT,  -- user_id
    assigned_role TEXT,  -- "director", "vp"

    status TEXT DEFAULT 'open',  -- "open", "acknowledged", "in_progress", "resolved", "closed"
    priority INTEGER,  -- 1-9

    intervention_recommended TEXT,  -- Prescriptive recommendations
    intervention_taken TEXT,  -- What was actually done
    resolution_notes TEXT,

    created_at TEXT DEFAULT (datetime('now')),
    acknowledged_at TEXT,
    resolved_at TEXT,

    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE,
    FOREIGN KEY (escalation_rule_id) REFERENCES escalation_rules(rule_id),
    FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_escalations_org ON escalations(org_id);
CREATE INDEX IF NOT EXISTS idx_escalations_project ON escalations(project_id);
CREATE INDEX IF NOT EXISTS idx_escalations_level ON escalations(escalation_level);
CREATE INDEX IF NOT EXISTS idx_escalations_status ON escalations(status);
CREATE INDEX IF NOT EXISTS idx_escalations_priority ON escalations(priority);
CREATE INDEX IF NOT EXISTS idx_escalations_created ON escalations(created_at);

-- ============================================================================
-- 6. STUDY HEALTH & DASHBOARD SYSTEM
-- Pre-computed views for leadership dashboards
-- ============================================================================

-- Study Health Snapshots (cached for performance)
CREATE TABLE IF NOT EXISTS study_health_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    project_id TEXT NOT NULL,

    overall_health_score REAL NOT NULL,  -- 0-100
    health_status TEXT NOT NULL,  -- "healthy", "warning", "critical"

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
    created_at TEXT DEFAULT (datetime('now')),

    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_health_snapshots_org ON study_health_snapshots(org_id);
CREATE INDEX IF NOT EXISTS idx_health_snapshots_project ON study_health_snapshots(project_id);
CREATE INDEX IF NOT EXISTS idx_health_snapshots_date ON study_health_snapshots(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_health_snapshots_status ON study_health_snapshots(health_status);

-- Dashboard Views (pre-computed)
CREATE TABLE IF NOT EXISTS dashboard_views (
    view_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    user_id TEXT,
    view_type TEXT NOT NULL,  -- "cpm_daily", "director_weekly", "vp_monthly", "portfolio_summary"
    view_data TEXT NOT NULL,  -- JSON: Full dashboard data
    generated_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT,

    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_dashboard_views_org ON dashboard_views(org_id);
CREATE INDEX IF NOT EXISTS idx_dashboard_views_user ON dashboard_views(user_id);
CREATE INDEX IF NOT EXISTS idx_dashboard_views_type ON dashboard_views(view_type);
CREATE INDEX IF NOT EXISTS idx_dashboard_views_expires ON dashboard_views(expires_at);

-- ============================================================================
-- 7. PATTERN DETECTION SYSTEM (Enterprise Tier)
-- Cross-study systemic issue detection
-- ============================================================================

-- Patterns Table
CREATE TABLE IF NOT EXISTS patterns (
    pattern_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    pattern_type TEXT NOT NULL,  -- "systemic_risk", "resource_bottleneck", "timeline_trend"
    pattern_name TEXT NOT NULL,
    pattern_description TEXT,

    -- Scope
    scope TEXT NOT NULL,  -- "single_study", "portfolio", "organization"
    affected_project_ids TEXT,  -- JSON array

    -- Severity
    severity TEXT NOT NULL,  -- "low", "medium", "high", "critical"
    confidence_score REAL,  -- 0.0-1.0

    -- Evidence
    evidence_signals TEXT,  -- JSON array of signal_ids
    evidence_correlations TEXT,  -- JSON array of correlation_ids

    -- Recommendations
    recommended_interventions TEXT,  -- JSON array

    detected_at TEXT DEFAULT (datetime('now')),
    resolved_at TEXT,
    status TEXT DEFAULT 'active',  -- "active", "acknowledged", "mitigated", "resolved"

    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_patterns_org ON patterns(org_id);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_patterns_severity ON patterns(severity);
CREATE INDEX IF NOT EXISTS idx_patterns_status ON patterns(status);

-- ============================================================================
-- 8. Update tier constraint to include 'core' and 'calibrated'
-- ============================================================================

-- Note: SQLite doesn't support ALTER COLUMN with CHECK constraints
-- The tier check will be enforced at application level
-- New tiers: 'core', 'calibrated' (was 'professional'), 'enterprise'

-- ============================================================================
-- Migration Complete
-- ============================================================================
