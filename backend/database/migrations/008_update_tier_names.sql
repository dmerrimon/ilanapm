-- Migration 008: Update Tier Names
-- Created: 2026-02-12
-- Description: Remove "core" tier, rename "professional" to "calibrated"

-- ============================================================================
-- Update tier constraint in organizations table
-- ============================================================================

-- Note: SQLite doesn't support ALTER COLUMN with CHECK constraints
-- The tier names are now: 'calibrated', 'enterprise'
-- 'professional' remains as backward-compatible alias (handled in application layer)

-- No schema changes needed - tier_enforcement.py handles the mapping:
-- "professional" → "calibrated" (level 1)
-- "calibrated" → "calibrated" (level 1)
-- "enterprise" → "enterprise" (level 2)

-- ============================================================================
-- Update existing license_keys table tier constraint
-- ============================================================================

-- Note: license_keys table also has tier constraint
-- Same approach: handled in application layer, no schema change needed

-- ============================================================================
-- Documentation Update
-- ============================================================================

-- Tier structure (as of 2026-02-12):
-- - Calibrated (base tier): All intelligence features, single-study focus
-- - Enterprise (premium tier): Portfolio features, cross-study analytics, API, SSO

-- Backward compatibility:
-- - "professional" in database → treated as "calibrated" by tier_enforcement.py
-- - Future: migrate all "professional" values to "calibrated" in data migration

-- ============================================================================
-- Migration Complete
-- ============================================================================
