-- Migration 016: Remove TPL_006 (Full Study Timeline)
-- Created: 2026-02-14
-- Reason: TPL_006 is redundant with TPL_001 + TPL_002 + TPL_003
-- Users can achieve same result by selecting all three study-level templates
-- This reduces maintenance burden and eliminates duplicate data

-- ============================================================================
-- DELETE TPL_006 DATA
-- ============================================================================

-- Remove dependencies for TPL_006
DELETE FROM template_dependencies WHERE template_id = 'TPL_006';

-- Remove tasks for TPL_006 (119 tasks with IDs FULL_001 to FULL_119)
DELETE FROM template_tasks WHERE template_id = 'TPL_006';

-- Remove template definition
DELETE FROM timeline_templates WHERE template_id = 'TPL_006';

-- ============================================================================
-- VERIFICATION QUERY (optional - run manually to verify)
-- ============================================================================
-- SELECT COUNT(*) FROM timeline_templates;  -- Should be 5 (TPL_001 to TPL_005)
-- SELECT COUNT(*) FROM template_tasks;       -- Should be 172 (86+10+23+34+19)
-- SELECT COUNT(*) FROM template_dependencies; -- Should be 75
