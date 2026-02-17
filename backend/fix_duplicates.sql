-- Fix duplicate tracker definitions
-- Keeps only the first entry for each tracker_def_id

-- Show current state
SELECT 'Current tracker definitions:' as info;
SELECT tracker_def_id, tracker_name, COUNT(*) as count
FROM tracker_definitions
GROUP BY tracker_def_id, tracker_name
ORDER BY tracker_name;

-- Delete duplicates (PostgreSQL-specific using ctid)
DELETE FROM tracker_definitions
WHERE ctid NOT IN (
    SELECT MIN(ctid)
    FROM tracker_definitions
    GROUP BY tracker_def_id
);

-- Show final state
SELECT 'After cleanup:' as info;
SELECT tracker_def_id, tracker_name, created_at
FROM tracker_definitions
ORDER BY tracker_name;

SELECT 'Total unique trackers:' as info, COUNT(*) as count
FROM tracker_definitions;
