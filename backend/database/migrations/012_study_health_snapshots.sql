-- Migration 012: Study Health Snapshots
-- Created: 2026-02-13
-- Description: Add study_health_snapshots table for dashboard caching

-- ============================================================================
-- Study Health Snapshots Table
-- ============================================================================

-- Caches calculated health scores for performance
-- Leadership Dashboard queries this table instead of recalculating every time

CREATE TABLE IF NOT EXISTS study_health_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id),
    project_id TEXT NOT NULL,

    -- Overall health
    overall_health_score REAL NOT NULL,  -- 0.0 to 100.0
    health_status TEXT NOT NULL,  -- 'healthy', 'warning', 'critical'

    -- Component scores
    timeline_score REAL,
    risk_score REAL,
    tmf_score REAL,
    enrollment_score REAL,
    budget_score REAL,
    vendor_score REAL,

    -- Top risks (JSON array)
    top_risks TEXT,  -- JSON array of top 5 risks

    -- Escalation counts
    active_escalations_count INTEGER DEFAULT 0,
    director_escalations_count INTEGER DEFAULT 0,
    vp_escalations_count INTEGER DEFAULT 0,

    -- Recommended actions (JSON array)
    recommended_actions TEXT,  -- JSON array of action strings

    -- Snapshot metadata
    snapshot_date DATE NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),

    -- One snapshot per project per day
    UNIQUE(org_id, project_id, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_health_snapshots_org
    ON study_health_snapshots(org_id);

CREATE INDEX IF NOT EXISTS idx_health_snapshots_project
    ON study_health_snapshots(project_id);

CREATE INDEX IF NOT EXISTS idx_health_snapshots_date
    ON study_health_snapshots(snapshot_date);

CREATE INDEX IF NOT EXISTS idx_health_snapshots_status
    ON study_health_snapshots(health_status);

CREATE INDEX IF NOT EXISTS idx_health_snapshots_score
    ON study_health_snapshots(overall_health_score);

-- ============================================================================
-- Dashboard Views Table (for caching complex queries)
-- ============================================================================

CREATE TABLE IF NOT EXISTS dashboard_views (
    view_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id),
    user_id TEXT REFERENCES users(user_id),
    view_type TEXT NOT NULL,  -- 'leadership_dashboard', 'portfolio_summary'
    view_data TEXT NOT NULL,  -- JSON with complete dashboard data
    generated_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT,  -- Cache expiration timestamp

    -- Filter/sort preferences (for user-specific views)
    filter_criteria TEXT,  -- JSON
    sort_criteria TEXT  -- JSON
);

CREATE INDEX IF NOT EXISTS idx_dashboard_views_org
    ON dashboard_views(org_id);

CREATE INDEX IF NOT EXISTS idx_dashboard_views_user
    ON dashboard_views(user_id);

CREATE INDEX IF NOT EXISTS idx_dashboard_views_type
    ON dashboard_views(view_type);

CREATE INDEX IF NOT EXISTS idx_dashboard_views_expires
    ON dashboard_views(expires_at);

-- ============================================================================
-- Documentation
-- ============================================================================

-- Health Snapshots Usage:
-- 1. Calculate health score (expensive operation)
-- 2. Store snapshot in study_health_snapshots
-- 3. Dashboard queries snapshot (fast)
-- 4. Recalculate daily or on-demand (tracker upload)
--
-- Dashboard Views Usage:
-- 1. User requests Leadership Dashboard
-- 2. Check if cached view exists and not expired
-- 3. If cached: return cached data (instant)
-- 4. If not cached: generate view, cache it, return
-- 5. Cache expires after configurable time (e.g., 15 minutes)

-- ============================================================================
-- Migration Complete
-- ============================================================================
