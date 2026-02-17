#!/usr/bin/env python3
"""
Fix duplicate tracker definitions in production database
Keeps only the first entry for each tracker_def_id
"""
from database.connection import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()

    # Check for duplicates
    print("Checking for duplicate trackers...")
    cursor.execute("""
        SELECT tracker_def_id, tracker_name, COUNT(*) as count
        FROM tracker_definitions
        GROUP BY tracker_def_id, tracker_name
        ORDER BY tracker_name
    """)

    trackers = cursor.fetchall()
    print(f"\nFound {len(trackers)} tracker entries:")
    for tracker in trackers:
        print(f"  {tracker['tracker_name']} ({tracker['tracker_def_id']}): {tracker['count']} entries")

    # Delete duplicates, keeping only the first entry for each tracker_def_id
    print("\nDeleting duplicates...")

    # For PostgreSQL, we need to use a subquery with CTID (row identifier)
    cursor.execute("""
        DELETE FROM tracker_definitions
        WHERE ctid NOT IN (
            SELECT MIN(ctid)
            FROM tracker_definitions
            GROUP BY tracker_def_id
        )
    """)

    deleted_count = cursor.rowcount
    print(f"✅ Deleted {deleted_count} duplicate entries")

    conn.commit()

    # Verify final state
    cursor.execute("SELECT tracker_def_id, tracker_name FROM tracker_definitions ORDER BY tracker_name")
    final = cursor.fetchall()

    print(f"\n✅ Final state: {len(final)} unique trackers")
    for t in final:
        print(f"  - {t['tracker_name']} ({t['tracker_def_id']})")
