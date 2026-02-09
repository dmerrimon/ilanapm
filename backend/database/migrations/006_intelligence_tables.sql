-- Migration 006: Intelligence Layer Tables
-- Created: 2026-02-08
-- Description: Add tables for intelligence layer configuration and task normalization

-- ============================================================================
-- 1. Update organizations table with intelligence_config
-- ============================================================================

ALTER TABLE organizations
ADD COLUMN intelligence_config TEXT DEFAULT '{
  "variance_thresholds": {"warning_percent": 15.0, "critical_percent": 30.0},
  "financial_rate_per_month_usd": 733000.0,
  "benchmark_source": "industry_only"
}';

-- Update tier constraint to include 'core'
-- Note: SQLite doesn't support ALTER COLUMN, so we need to recreate the table if constraint exists
-- For now, we'll just add a check for new rows

-- ============================================================================
-- 2. Task Mappings Table (Org-Specific Task Name Normalization)
-- ============================================================================

CREATE TABLE IF NOT EXISTS task_mappings (
    mapping_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    customer_task_name TEXT NOT NULL,
    ontology_task_id TEXT NOT NULL,
    ontology_task_name TEXT NOT NULL,
    confidence REAL DEFAULT 0.0,
    confirmed_by_user INTEGER DEFAULT 0,  -- SQLite uses INTEGER for boolean
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(org_id, customer_task_name),
    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_task_mappings_org ON task_mappings(org_id);
CREATE INDEX IF NOT EXISTS idx_task_mappings_confirmed ON task_mappings(confirmed_by_user);
CREATE INDEX IF NOT EXISTS idx_task_mappings_confidence ON task_mappings(confidence);

-- ============================================================================
-- 3. Project Profiles Table (Metadata Management)
-- ============================================================================

CREATE TABLE IF NOT EXISTS project_profiles (
    profile_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    project_name TEXT NOT NULL,
    study_id TEXT,
    therapeutic_area TEXT,
    phase TEXT,
    primary_country TEXT,
    additional_countries TEXT,  -- JSON array as TEXT (SQLite doesn't have array type)
    metadata TEXT,  -- JSON object as TEXT
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_project_profiles_org ON project_profiles(org_id);
CREATE INDEX IF NOT EXISTS idx_project_profiles_study ON project_profiles(study_id);
CREATE INDEX IF NOT EXISTS idx_project_profiles_name ON project_profiles(project_name);

-- ============================================================================
-- 4. Intelligence Usage Tracking (for analytics)
-- ============================================================================

CREATE TABLE IF NOT EXISTS intelligence_usage (
    usage_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL,
    user_id TEXT,
    feature TEXT NOT NULL,  -- 'variance_detection', 'task_normalization', etc.
    timestamp TEXT DEFAULT (datetime('now')),
    execution_time_ms INTEGER,
    tasks_analyzed INTEGER,
    variances_detected INTEGER,
    success INTEGER DEFAULT 1,  -- Boolean: 1 = success, 0 = failure
    error_message TEXT,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_intelligence_usage_org ON intelligence_usage(org_id);
CREATE INDEX IF NOT EXISTS idx_intelligence_usage_feature ON intelligence_usage(feature);
CREATE INDEX IF NOT EXISTS idx_intelligence_usage_timestamp ON intelligence_usage(timestamp);

-- ============================================================================
-- 5. Insert Default Project Profile for Testing
-- ============================================================================

-- Note: This is optional, for testing purposes only
-- Uncomment if you want a default profile for development

-- INSERT INTO project_profiles (
--     profile_id,
--     org_id,
--     project_name,
--     study_id,
--     therapeutic_area,
--     phase,
--     primary_country,
--     metadata
-- ) VALUES (
--     'prof_test_001',
--     'demo_org_id',  -- Replace with actual org_id
--     'Demo Clinical Study',
--     'STUDY-001',
--     'Oncology',
--     'Phase III',
--     'US',
--     '{"sponsor": "Demo Pharma", "indication": "Breast Cancer"}'
-- );

-- ============================================================================
-- Migration Complete
-- ============================================================================
