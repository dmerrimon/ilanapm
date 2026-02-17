-- Migration 011: Correlation Rules
-- Created: 2026-02-13
-- Description: Add correlation_rules table for signal-to-timeline correlation logic

-- ============================================================================
-- Correlation Rules Table
-- ============================================================================

-- Defines rules for correlating signals (from trackers) to timeline milestones
-- Example: High priority site risk → Site Activation milestone delay

CREATE TABLE IF NOT EXISTS correlation_rules (
    rule_id TEXT PRIMARY KEY,
    rule_name TEXT NOT NULL,

    -- What signals trigger this rule
    signal_type TEXT NOT NULL,  -- "risk_high_priority", "tmf_completeness_risk"
    signal_category TEXT,  -- Optional: "Site", "Clinical", "Safety"
    signal_detail_pattern TEXT,  -- JSON: keyword matching, task codes, etc.

    -- What timeline elements are affected
    affected_milestones TEXT NOT NULL,  -- JSON array: ["Site Activation", "LPI"]
    affected_milestone_codes TEXT NOT NULL,  -- JSON array: ["SITE_ACT", "LPI"]

    -- Correlation characteristics
    correlation_type TEXT NOT NULL,  -- "blocker", "risk", "informational"
    confidence_score REAL NOT NULL DEFAULT 0.5,  -- 0.0 to 1.0
    impact_type TEXT,  -- "delay", "cost_increase", "resource_bottleneck"

    -- Delay estimation
    delay_estimation_logic TEXT,  -- JSON: formula for calculating delay

    -- Escalation
    escalation_trigger BOOLEAN DEFAULT FALSE,
    escalation_level TEXT,  -- "director", "vp"

    -- Reasoning
    reasoning_template TEXT,  -- Template for human-readable explanation

    -- Metadata
    created_at TEXT DEFAULT (NOW()),
    updated_at TEXT DEFAULT (NOW()),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_correlation_rules_signal_type
    ON correlation_rules(signal_type);

CREATE INDEX IF NOT EXISTS idx_correlation_rules_signal_category
    ON correlation_rules(signal_category);

CREATE INDEX IF NOT EXISTS idx_correlation_rules_correlation_type
    ON correlation_rules(correlation_type);

CREATE INDEX IF NOT EXISTS idx_correlation_rules_escalation
    ON correlation_rules(escalation_level);

-- ============================================================================
-- Documentation
-- ============================================================================

-- Correlation Rule Structure:
--
-- Each rule defines:
-- 1. What signals it matches (signal_type + category + detail patterns)
-- 2. What timeline milestones are affected
-- 3. Correlation strength (confidence_score)
-- 4. Impact estimation (delay days, cost)
-- 5. Whether escalation is triggered
--
-- Example Rule:
-- {
--   "rule_name": "High Priority Risk → Site Activation",
--   "signal_type": "risk_high_priority",
--   "signal_category": "Site",
--   "signal_detail_pattern": {
--     "pattern_type": "keyword_match",
--     "keywords": ["site activation", "site contract"]
--   },
--   "affected_milestones": ["Site Activation"],
--   "affected_milestone_codes": ["SITE_ACT"],
--   "correlation_type": "risk",
--   "confidence_score": 0.85,
--   "impact_type": "delay",
--   "delay_estimation_logic": {
--     "type": "multiplier",
--     "formula": "priority * 7"
--   },
--   "escalation_trigger": true,
--   "escalation_level": "director",
--   "reasoning_template": "Risk #{priority}: '{signal_description}' affects {milestone}. Estimated delay: {delay_days} days."
-- }

-- ============================================================================
-- Migration Complete
-- ============================================================================
