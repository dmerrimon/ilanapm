-- PostgreSQL-compatible version
-- Migration 019: Clean TPL_001 Task Names
-- Created: 2026-02-15
-- Description: Remove multi-line text, bullets, and extra content from task_name field
--              for TPL_001 (Study Start-Up) template. This extracts only the first line
--              of each task name, leaving full content in the description field.
--
-- This migration is idempotent - safe to run multiple times
--
-- Problem: Task names contain multi-line text with bullet points that belong in notes
-- Solution: Extract first line only and clean up trailing special characters
-- Total updates: 33 tasks (out of 86 TPL_001 tasks)

-- ============================================================================
-- UPDATE TEMPLATE_TASKS - CLEAN TASK NAMES FOR TPL_001
-- ============================================================================

-- STARTUP_001: Internal Transition Meeting\n- Confirm date and PM prep tasks...
UPDATE template_tasks
SET task_name = 'Internal Transition Meeting',
    updated_at = NOW()
WHERE task_id = 'STARTUP_001'
  AND template_id = 'TPL_001';

-- STARTUP_002: Data Visualization Tool (DVT) with trailing dash
UPDATE template_tasks
SET task_name = 'Data Visualization Tool (DVT)',
    updated_at = NOW()
WHERE task_id = 'STARTUP_002'
  AND template_id = 'TPL_001';

-- STARTUP_003: US CT.gov\n▪ Registration
UPDATE template_tasks
SET task_name = 'US CT.gov',
    updated_at = NOW()
WHERE task_id = 'STARTUP_003'
  AND template_id = 'TPL_001';

-- STARTUP_006: Review study contract/budget for understanding on FTE allocation...
UPDATE template_tasks
SET task_name = 'Review study contract/budget for understanding on FTE allocation',
    updated_at = NOW()
WHERE task_id = 'STARTUP_006'
  AND template_id = 'TPL_001';

-- STARTUP_007: Financial tracking tools \n▪ Contract/budget tracking...
UPDATE template_tasks
SET task_name = 'Financial tracking tools',
    updated_at = NOW()
WHERE task_id = 'STARTUP_007'
  AND template_id = 'TPL_001';

-- STARTUP_008: Confidentiality Disclosure Agreement (CDA) for vendors...
UPDATE template_tasks
SET task_name = 'Confidentiality Disclosure Agreement (CDA) for vendors',
    updated_at = NOW()
WHERE task_id = 'STARTUP_008'
  AND template_id = 'TPL_001';

-- STARTUP_009: Site budget/contract \nSites Contract/Budget Template...
UPDATE template_tasks
SET task_name = 'Site budget/contract',
    updated_at = NOW()
WHERE task_id = 'STARTUP_009'
  AND template_id = 'TPL_001';

-- STARTUP_010: Invoice approvel:\n   -nvoice Review...
UPDATE template_tasks
SET task_name = 'Invoice approvel',
    updated_at = NOW()
WHERE task_id = 'STARTUP_010'
  AND template_id = 'TPL_001';

-- STARTUP_011: Financial Oversight (Revenue, Forcast, Billing)...
UPDATE template_tasks
SET task_name = 'Financial Oversight (Revenue, Forcast, Billing)',
    updated_at = NOW()
WHERE task_id = 'STARTUP_011'
  AND template_id = 'TPL_001';

-- STARTUP_012: Core Team Meetings (aka Internal  Team Meeting)...
UPDATE template_tasks
SET task_name = 'Core Team Meetings (aka Internal  Team Meeting)',
    updated_at = NOW()
WHERE task_id = 'STARTUP_012'
  AND template_id = 'TPL_001';

-- STARTUP_013: Project Team/Sponsor Meetings...
UPDATE template_tasks
SET task_name = 'Project Team/Sponsor Meetings',
    updated_at = NOW()
WHERE task_id = 'STARTUP_013'
  AND template_id = 'TPL_001';

-- STARTUP_014: Kick-Off Meeting (KOM)\n▪ Review budget for allocated resources...
UPDATE template_tasks
SET task_name = 'Kick-Off Meeting (KOM)',
    updated_at = NOW()
WHERE task_id = 'STARTUP_014'
  AND template_id = 'TPL_001';

-- STARTUP_015: Investigator Meeting, if scoped\n▪ Schedule after site selection
UPDATE template_tasks
SET task_name = 'Investigator Meeting, if scoped',
    updated_at = NOW()
WHERE task_id = 'STARTUP_015'
  AND template_id = 'TPL_001';

-- STARTUP_016: PM 1:1 Meetings\n▪Schedule with Sponsor Counterpart...
UPDATE template_tasks
SET task_name = 'PM 1:1 Meetings',
    updated_at = NOW()
WHERE task_id = 'STARTUP_016'
  AND template_id = 'TPL_001';

-- STARTUP_042: CTMS and eTMF setup...
UPDATE template_tasks
SET task_name = 'CTMS and eTMF setup',
    updated_at = NOW()
WHERE task_id = 'STARTUP_042'
  AND template_id = 'TPL_001';

-- STARTUP_044: Protocol/ICF development...
UPDATE template_tasks
SET task_name = 'Protocol/ICF development',
    updated_at = NOW()
WHERE task_id = 'STARTUP_044'
  AND template_id = 'TPL_001';

-- STARTUP_045: Project Dashboard...
UPDATE template_tasks
SET task_name = 'Project Dashboard',
    updated_at = NOW()
WHERE task_id = 'STARTUP_045'
  AND template_id = 'TPL_001';

-- STARTUP_046: Establish process/format for study reports to be shared/sent to sponsor...
UPDATE template_tasks
SET task_name = 'Establish process/format for study reports to be shared/sent to sponsor',
    updated_at = NOW()
WHERE task_id = 'STARTUP_046'
  AND template_id = 'TPL_001';

-- STARTUP_047: EDC Set up/ Account Access (with bullets on same line)
UPDATE template_tasks
SET task_name = 'EDC Set up/ Account Access',
    updated_at = NOW()
WHERE task_id = 'STARTUP_047'
  AND template_id = 'TPL_001';

-- STARTUP_048: IP contact information...
UPDATE template_tasks
SET task_name = 'IP contact information',
    updated_at = NOW()
WHERE task_id = 'STARTUP_048'
  AND template_id = 'TPL_001';

-- STARTUP_051: Labeling...
UPDATE template_tasks
SET task_name = 'Labeling',
    updated_at = NOW()
WHERE task_id = 'STARTUP_051'
  AND template_id = 'TPL_001';

-- STARTUP_052: International...
UPDATE template_tasks
SET task_name = 'International',
    updated_at = NOW()
WHERE task_id = 'STARTUP_052'
  AND template_id = 'TPL_001';

-- STARTUP_054: Service Providers...
UPDATE template_tasks
SET task_name = 'Service Providers',
    updated_at = NOW()
WHERE task_id = 'STARTUP_054'
  AND template_id = 'TPL_001';

-- STARTUP_055: Vendor identification...
UPDATE template_tasks
SET task_name = 'Vendor identification',
    updated_at = NOW()
WHERE task_id = 'STARTUP_055'
  AND template_id = 'TPL_001';

-- STARTUP_056: Vendor model, e.g....
UPDATE template_tasks
SET task_name = 'Vendor model, e.g.',
    updated_at = NOW()
WHERE task_id = 'STARTUP_056'
  AND template_id = 'TPL_001';

-- STARTUP_057: Vendor(s) setup...
UPDATE template_tasks
SET task_name = 'Vendor(s) setup',
    updated_at = NOW()
WHERE task_id = 'STARTUP_057'
  AND template_id = 'TPL_001';

-- STARTUP_058: Central IRB...
UPDATE template_tasks
SET task_name = 'Central IRB',
    updated_at = NOW()
WHERE task_id = 'STARTUP_058'
  AND template_id = 'TPL_001';

-- STARTUP_060: International: (with colon)
UPDATE template_tasks
SET task_name = 'International',
    updated_at = NOW()
WHERE task_id = 'STARTUP_060'
  AND template_id = 'TPL_001';

-- STARTUP_061: Onboarding...
UPDATE template_tasks
SET task_name = 'Onboarding',
    updated_at = NOW()
WHERE task_id = 'STARTUP_061'
  AND template_id = 'TPL_001';

-- STARTUP_071: Startup Tracking (Start-up is responsible)...
UPDATE template_tasks
SET task_name = 'Startup Tracking (Start-up is responsible)',
    updated_at = NOW()
WHERE task_id = 'STARTUP_071'
  AND template_id = 'TPL_001';

-- STARTUP_073: Country/site feasibility (Start-up is responsible)...
UPDATE template_tasks
SET task_name = 'Country/site feasibility (Start-up is responsible)',
    updated_at = NOW()
WHERE task_id = 'STARTUP_073'
  AND template_id = 'TPL_001';

-- STARTUP_076: Database build timelines sent to you?...
UPDATE template_tasks
SET task_name = 'Database build timelines sent to you?',
    updated_at = NOW()
WHERE task_id = 'STARTUP_076'
  AND template_id = 'TPL_001';

-- STARTUP_077: Program for patient profiles...
UPDATE template_tasks
SET task_name = 'Program for patient profiles',
    updated_at = NOW()
WHERE task_id = 'STARTUP_077'
  AND template_id = 'TPL_001';


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Show sample of cleaned task names
SELECT
    'Sample cleaned task names' as info,
    task_id,
    task_name,
    LENGTH(task_name) as name_length,
    CASE
        WHEN INSTR(task_name, CHAR(10)) > 0 THEN 'HAS NEWLINE'
        WHEN INSTR(task_name, '▪') > 0 THEN 'HAS BULLET'
        ELSE 'Clean'
    END as status
FROM template_tasks
WHERE template_id = 'TPL_001'
ORDER BY task_id
LIMIT 10;

-- Count tasks with newlines (should be 0 after migration)
SELECT
    'Tasks with newlines after migration' as check_type,
    COUNT(*) as count
FROM template_tasks
WHERE template_id = 'TPL_001'
  AND INSTR(task_name, CHAR(10)) > 0;

-- Count tasks with bullets (should be 0 after migration)
SELECT
    'Tasks with bullets after migration' as check_type,
    COUNT(*) as count
FROM template_tasks
WHERE template_id = 'TPL_001'
  AND (INSTR(task_name, '▪') > 0 OR INSTR(task_name, '•') > 0);

-- Show longest task names (for review)
SELECT
    'Longest task names (for review)' as info,
    task_id,
    task_name,
    LENGTH(task_name) as length
FROM template_tasks
WHERE template_id = 'TPL_001'
ORDER BY LENGTH(task_name) DESC
LIMIT 5;

-- Migration complete! Updated 33 task names for TPL_001
-- All task names now contain only the first line, with bullets and extra content removed
-- Full task details remain in the description field
