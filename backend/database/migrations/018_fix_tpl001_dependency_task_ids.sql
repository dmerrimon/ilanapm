-- PostgreSQL-compatible version
-- Migration: Fix TPL_001 dependency task IDs
-- Description: Updates template_dependencies predecessor_task_id and successor_task_id
--              from SS_XXX format to STARTUP_XXX format for TPL_001 template
-- Author: Migration Script
-- Date: 2026-02-15

-- This migration fixes the mismatch between task IDs in template_tasks (STARTUP_XXX)
-- and the dependency references in template_dependencies (SS_XXX) for the Study Start-Up template

-- Update predecessor_task_id from SS_XXX to STARTUP_XXX
UPDATE template_dependencies
SET
    predecessor_task_id = 'STARTUP_' || substr(predecessor_task_id, 4)
WHERE
    template_id = 'TPL_001'
    AND predecessor_task_id LIKE 'SS_%';

-- Update successor_task_id from SS_XXX to STARTUP_XXX
UPDATE template_dependencies
SET
    successor_task_id = 'STARTUP_' || substr(successor_task_id, 4)
WHERE
    template_id = 'TPL_001'
    AND successor_task_id LIKE 'SS_%';

-- Verify the updates by counting remaining SS_ references
-- (This is informational only, the result will show 0 if successful)
SELECT
    'Remaining SS_ references in predecessor_task_id' as check_type,
    COUNT(*) as count
FROM template_dependencies
WHERE template_id = 'TPL_001'
    AND predecessor_task_id LIKE 'SS_%'
UNION ALL
SELECT
    'Remaining SS_ references in successor_task_id' as check_type,
    COUNT(*) as count
FROM template_dependencies
WHERE template_id = 'TPL_001'
    AND successor_task_id LIKE 'SS_%';

-- Show sample of updated dependencies
SELECT
    'Sample updated dependencies' as info,
    dependency_id,
    predecessor_task_id,
    successor_task_id,
    dependency_type
FROM template_dependencies
WHERE template_id = 'TPL_001'
LIMIT 10;
