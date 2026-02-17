-- Migration 014: Portfolio Intelligence
-- Created: 2026-02-13
-- Description: Add tables for cross-study patterns and systemic issues

-- ============================================================================
-- Cross-Study Patterns Table
-- ============================================================================

-- Stores patterns detected across multiple studies
CREATE TABLE IF NOT EXISTS cross_study_patterns (
    pattern_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id),
    pattern_type TEXT NOT NULL,  -- 'resource_collision', 'systemic_issue', 'common_risk', 'timeline_correlation'
    pattern_name TEXT NOT NULL,
    pattern_description TEXT NOT NULL,
    severity TEXT NOT NULL,  -- 'low', 'medium', 'high', 'critical'

    -- Affected studies
    affected_studies TEXT NOT NULL,  -- JSON array of project_ids
    affected_study_count INTEGER NOT NULL,

    -- Evidence
    evidence TEXT,  -- JSON with pattern-specific evidence
    confidence_score REAL DEFAULT 0.0,  -- 0.0 to 1.0

    -- Impact
    portfolio_impact TEXT,
    recommended_action TEXT,

    -- Metadata
    detected_at TEXT DEFAULT (NOW()),
    resolved_at TEXT,
    resolution_notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_cross_study_patterns_org
    ON cross_study_patterns(org_id);

CREATE INDEX IF NOT EXISTS idx_cross_study_patterns_type
    ON cross_study_patterns(pattern_type);

CREATE INDEX IF NOT EXISTS idx_cross_study_patterns_severity
    ON cross_study_patterns(severity);

CREATE INDEX IF NOT EXISTS idx_cross_study_patterns_detected
    ON cross_study_patterns(detected_at);

-- ============================================================================
-- Systemic Issues Table
-- ============================================================================

-- Stores systemic issues affecting portfolio
CREATE TABLE IF NOT EXISTS systemic_issues (
    issue_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id),
    issue_type TEXT NOT NULL,  -- 'vendor_performance', 'site_activation_delays', 'enrollment_challenges', 'regulatory_delays'
    issue_name TEXT NOT NULL,
    issue_description TEXT NOT NULL,
    severity TEXT NOT NULL,  -- 'low', 'medium', 'high', 'critical'

    -- Affected studies
    affected_studies TEXT NOT NULL,  -- JSON array of project_ids
    affected_study_count INTEGER NOT NULL,

    -- Root cause analysis
    root_cause TEXT,
    contributing_factors TEXT,  -- JSON array

    -- Impact
    portfolio_impact_description TEXT,
    estimated_delay_days INTEGER DEFAULT 0,
    estimated_cost_impact REAL DEFAULT 0.0,

    -- Recommendations
    recommended_intervention TEXT,
    responsible_party TEXT,  -- 'director', 'vp', 'executive'

    -- Metadata
    detected_at TEXT DEFAULT (NOW()),
    resolved_at TEXT,
    resolution_notes TEXT,
    intervention_taken TEXT
);

CREATE INDEX IF NOT EXISTS idx_systemic_issues_org
    ON systemic_issues(org_id);

CREATE INDEX IF NOT EXISTS idx_systemic_issues_type
    ON systemic_issues(issue_type);

CREATE INDEX IF NOT EXISTS idx_systemic_issues_severity
    ON systemic_issues(severity);

CREATE INDEX IF NOT EXISTS idx_systemic_issues_detected
    ON systemic_issues(detected_at);

CREATE INDEX IF NOT EXISTS idx_systemic_issues_responsible
    ON systemic_issues(responsible_party);

-- ============================================================================
-- Portfolio Health Snapshots Table
-- ============================================================================

-- Caches portfolio-wide health metrics for performance
CREATE TABLE IF NOT EXISTS portfolio_health_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id),

    -- Overall metrics
    total_studies INTEGER NOT NULL,
    average_health_score REAL NOT NULL,
    median_health_score REAL NOT NULL,

    -- Health distribution
    healthy_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,

    -- Trends
    improving_count INTEGER DEFAULT 0,
    declining_count INTEGER DEFAULT 0,
    stable_count INTEGER DEFAULT 0,

    -- Escalations
    total_escalations INTEGER DEFAULT 0,
    director_escalations INTEGER DEFAULT 0,
    vp_escalations INTEGER DEFAULT 0,

    -- Signals
    total_active_signals INTEGER DEFAULT 0,
    total_high_priority_risks INTEGER DEFAULT 0,

    -- Financial impact
    estimated_total_delay_days INTEGER DEFAULT 0,
    estimated_total_cost_impact REAL DEFAULT 0.0,

    -- Studies needing attention (JSON arrays)
    studies_needing_immediate_attention TEXT,
    studies_at_risk TEXT,

    -- Metadata
    snapshot_date DATE NOT NULL,
    created_at TEXT DEFAULT (NOW()),

    -- One snapshot per org per day
    UNIQUE(org_id, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_portfolio_health_org
    ON portfolio_health_snapshots(org_id);

CREATE INDEX IF NOT EXISTS idx_portfolio_health_date
    ON portfolio_health_snapshots(snapshot_date);

-- ============================================================================
-- Resource Allocation Table
-- ============================================================================

-- Stores resource allocation analysis (future enhancement)
CREATE TABLE IF NOT EXISTS resource_allocations (
    allocation_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id),
    resource_id TEXT,
    resource_name TEXT,
    resource_type TEXT,  -- 'personnel', 'equipment', 'facility'

    -- Allocation details
    allocated_studies TEXT,  -- JSON array of project_ids
    allocation_percentage REAL,  -- 0-100
    utilization_rate REAL,  -- 0-100

    -- Conflicts
    has_collision BOOLEAN DEFAULT FALSE,
    is_overallocated BOOLEAN DEFAULT FALSE,

    -- Recommendations
    reallocation_recommended BOOLEAN DEFAULT FALSE,
    recommendation_notes TEXT,

    -- Metadata
    analysis_date DATE NOT NULL,
    created_at TEXT DEFAULT (NOW())
);

CREATE INDEX IF NOT EXISTS idx_resource_allocations_org
    ON resource_allocations(org_id);

CREATE INDEX IF NOT EXISTS idx_resource_allocations_resource
    ON resource_allocations(resource_id);

CREATE INDEX IF NOT EXISTS idx_resource_allocations_date
    ON resource_allocations(analysis_date);

-- ============================================================================
-- Documentation
-- ============================================================================

-- Cross-Study Patterns:
-- - Detects patterns across multiple studies (common risks, timeline delays, resource conflicts)
-- - Generated by portfolio_service.detect_cross_study_patterns()
-- - Used in Leadership Dashboard portfolio view

-- Systemic Issues:
-- - Detects systemic issues (vendor problems, site activation delays, enrollment challenges)
-- - Generated by portfolio_service.detect_systemic_issues()
-- - Triggers VP-level escalations

-- Portfolio Health Snapshots:
-- - Cached portfolio-wide metrics for performance
-- - Generated daily or on-demand
-- - Used for portfolio summary views

-- Resource Allocations:
-- - Tracks resource allocation across studies
-- - Identifies conflicts and overallocation
-- - Future enhancement for Phase 5

-- ============================================================================
-- Migration Complete
-- ============================================================================
