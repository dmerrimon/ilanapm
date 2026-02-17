-- Migration 010: Tracker Column Mappings
-- Created: 2026-02-12
-- Description: Add tracker_column_mappings table for Account Admin configuration

-- ============================================================================
-- Tracker Column Mappings Table
-- ============================================================================

-- Account Admins configure org-specific column mappings in web portal (one-time setup)
-- CPMs then upload trackers via MS Project add-in, and backend uses saved mappings

CREATE TABLE IF NOT EXISTS tracker_column_mappings (
    mapping_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id),
    tracker_type TEXT NOT NULL,  -- "risk_log", "tmf_completeness", "budget", "vendor"

    -- Column mappings stored as JSON
    -- Example: {"org_column": "seleen_field", "ID": "risk_number", "Risk Type": "category"}
    column_mappings TEXT NOT NULL,  -- JSON

    -- Optional transformation rules for special cases
    transformation_rules TEXT,  -- JSON

    created_by TEXT REFERENCES users(user_id),
    created_at TEXT DEFAULT (NOW()),
    updated_at TEXT DEFAULT (NOW()),

    UNIQUE(org_id, tracker_type)
);

CREATE INDEX IF NOT EXISTS idx_column_mappings_org ON tracker_column_mappings(org_id);
CREATE INDEX IF NOT EXISTS idx_column_mappings_type ON tracker_column_mappings(tracker_type);

-- ============================================================================
-- Documentation
-- ============================================================================

-- Workflow:
-- 1. Account Admin logs into app.seleen.io → Account Management View
-- 2. Navigate to Tracker Configuration
-- 3. Upload sample tracker file (e.g., Risk_Log_Sample.xlsx)
-- 4. Web UI shows column mapping interface
-- 5. Account Admin maps org columns to Seleen schema
-- 6. Save mapping to this table
-- 7. All future CPM uploads via MS Project add-in use this saved mapping

-- Example saved mapping:
-- {
--   "column_mappings": {
--     "ID": "risk_number",
--     "Risk Type": "category",
--     "Description": "risk_detail",
--     "Severity": "impact",
--     "Likelihood": "probability",
--     "Score": "priority",
--     "Mitigation Plan": "mitigation_plan",
--     "Owner": "owner",
--     "Target Date": "target_date",
--     "Status": "status",
--     "Escalation Notes": "escalation_notes"
--   }
-- }

-- ============================================================================
-- Migration Complete
-- ============================================================================
