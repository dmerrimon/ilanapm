-- Migration 009: Single Tier Model
-- Created: 2026-02-12
-- Description: Simplify to single-tier pricing - all customers get all features

-- ============================================================================
-- Documentation: Tier Model Change
-- ============================================================================

-- Old model (3 tiers):
-- - Core: Basic features
-- - Calibrated: Advanced features
-- - Enterprise: Portfolio features

-- Old model (2 tiers):
-- - Calibrated: Base tier with all intelligence features
-- - Enterprise: Portfolio features + API + SSO

-- New model (1 tier):
-- - Enterprise: All features included, per-seat pricing
-- - No feature gating
-- - Simple, transparent pricing

-- ============================================================================
-- Implementation Notes
-- ============================================================================

-- Database schema:
-- - organizations.tier still exists (kept for backward compatibility)
-- - All tier values ('enterprise', 'calibrated', 'professional') treated equally
-- - tier_enforcement.py updated to always allow access

-- Application layer:
-- - check_tier() always returns True
-- - check_feature_access() always returns True
-- - require_tier() decorator logs but allows all access
-- - TIER_FEATURES maps all tiers to ALL_FEATURES

-- Backward compatibility:
-- - Existing tier values in database unchanged
-- - API endpoints with @require_tier decorators still work
-- - No breaking changes to existing code

-- ============================================================================
-- No Schema Changes Required
-- ============================================================================

-- All changes handled in application layer (tier_enforcement.py)
-- Database schema remains unchanged for backward compatibility

-- ============================================================================
-- Migration Complete
-- ============================================================================
