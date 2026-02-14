#!/usr/bin/env python3
"""
Update Timeline Templates from User-Provided Data

This script:
1. Parses Study Start-Up Guidance Document.csv (86 tasks)
2. Parses Site_Activation_Checklist.csv (60 items)
3. Parses Study Implementation milestones (from plain text)
4. Parses Site Closeout activities (from plain text)
5. Parses Study Closeout timeline (from plain text)
6. Updates backend database with 6 templates

Templates:
- TPL_001: Study Start-Up (86 tasks)
- TPL_002: Study Implementation/Active Enrollment (8 milestones + 2 recurring)
- TPL_003: Study Closeout (23 tasks across 4 phases)
- TPL_004: Site Activation (60 checklist items)
- TPL_005: Site Closeout (checklist categories)
- TPL_006: Full Study Timeline (combination of TPL_001 + TPL_002 + TPL_003)
"""

import sqlite3
import csv
import re
from pathlib import Path
from datetime import datetime

# Database path
DB_PATH = Path(__file__).parent.parent / "database" / "feedback.db"

# CSV paths
STARTUP_CSV = Path("/Users/donmerriman/Projects/Seleen (formaly ilana-pm)/assets/Study Timeline/Study Start-Up Guidance Document.csv")
SITE_ACTIVATION_CSV = Path("/Users/donmerriman/Projects/Seleen (formaly ilana-pm)/assets/Study Timeline/Site_Activation_Checklist.csv")


def clear_existing_templates(conn):
    """Delete existing templates and tasks"""
    print("Clearing existing templates...")
    cursor = conn.cursor()

    # Delete template dependencies first
    cursor.execute("DELETE FROM template_dependencies")

    # Delete template tasks
    cursor.execute("DELETE FROM template_tasks")

    # Delete templates
    cursor.execute("DELETE FROM timeline_templates WHERE org_id IS NULL")

    conn.commit()
    print("✓ Existing templates cleared")


def parse_startup_csv():
    """Parse Study Start-Up Guidance Document.csv"""
    print("\nParsing Study Start-Up tasks...")

    tasks = []
    current_category = None

    with open(STARTUP_CSV, 'r', encoding='utf-8-sig') as f:
        # Skip first 2 rows (empty + title), read headers from row 3
        next(f)  # Skip row 1
        next(f)  # Skip row 2

        reader = csv.DictReader(f)

        for row in reader:
            # Get values
            category = row.get('Category', '').strip()
            task_name = row.get('Task', '').strip()
            predecessor = row.get('Predecessor', '').strip()
            date_due = row.get('Date\nDue Per SOP', '').strip()

            # Skip if no task name
            if not task_name:
                continue

            # Use last known category if current row has no category
            if category and category != 'blank':
                current_category = category

            # Use current_category or default to 'General'
            final_category = current_category if current_category else 'General'

            # Map date due to typical duration
            duration_days = map_due_date_to_duration(date_due)

            tasks.append({
                'category': final_category,
                'task_name': task_name,
                'predecessor': predecessor,
                'duration_days': duration_days,
                'notes': row.get('Comments', '').strip()
            })

    print(f"✓ Parsed {len(tasks)} Study Start-Up tasks")
    return tasks


def map_due_date_to_duration(date_due):
    """Map 'Date Due Per SOP' to typical duration in days"""
    if not date_due or date_due == 'N/A':
        return 1

    # Common patterns
    if 'Study Award' in date_due:
        return 1
    elif 'KOM' in date_due:
        return 30  # Typically 1 month after award
    elif 'FPI' in date_due or 'First' in date_due:
        return 90  # Typically 3 months
    elif 'SIV' in date_due:
        return 60
    elif 'Database' in date_due:
        return 45
    elif 'Prior to' in date_due:
        return 7  # Week before
    elif 'Month' in date_due or 'Monthly' in date_due:
        return 30
    else:
        return 14  # Default 2 weeks


def parse_site_activation_csv():
    """Parse Site_Activation_Checklist.csv"""
    print("\nParsing Site Activation checklist...")

    items = []
    current_category = None

    with open(SITE_ACTIVATION_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)

        # Skip first 4 rows (title, site, headers, empty)
        for _ in range(4):
            next(reader, None)

        for row in reader:
            if not row or len(row) == 0:
                continue

            item_text = row[0].strip() if row[0] else ''

            # Skip empty rows
            if not item_text:
                continue

            # Check if this is a category header
            # Categories usually have trailing spaces or are in specific patterns
            is_category = (
                row[0].endswith('  ') or  # Has trailing spaces (like "Documents, Training and Funding  ")
                item_text in ['Data Management', 'Pharmacy', 'Laboratory',
                             'Approvals', 'To confirm with sites (may not be required for activation)',
                             'To be discussed with CPM']
            )

            if is_category:
                current_category = item_text
                continue

            # Regular checklist item
            if current_category and item_text:
                # Skip sub-items like "a. ", "b. "
                if not re.match(r'^[a-z]\.\s+', item_text):
                    items.append({
                        'category': current_category,
                        'item': item_text,
                        'notes': row[3].strip() if len(row) > 3 and row[3] else ''
                    })

    print(f"✓ Parsed {len(items)} Site Activation items")
    return items


def create_study_implementation_milestones():
    """Create Study Implementation milestones from plain text"""
    print("\nCreating Study Implementation milestones...")

    milestones = [
        {
            'code': 'FPI',
            'name': 'First Person In (FPI)',
            'description': 'First participant enrolled in the study',
            'is_milestone': True
        },
        {
            'code': 'FPD',
            'name': 'First Person Dosed (FPD)',
            'description': 'First participant receives study intervention/drug',
            'is_milestone': True
        },
        {
            'code': 'FCR',
            'name': 'First Cohort Review (FCR)',
            'description': 'Review of first cohort data before proceeding (if applicable)',
            'is_milestone': True
        },
        {
            'code': 'LPI',
            'name': 'Last Patient In (LPI)',
            'description': 'Last participant enrolled in the study',
            'is_milestone': True
        },
        {
            'code': 'LPD',
            'name': 'Last Person Dosed (LPD)',
            'description': 'Last participant receives final dose of study intervention',
            'is_milestone': True
        },
        {
            'code': 'LPLV',
            'name': 'Last Participant Last Visit (LPLV)',
            'description': 'Last participant completes final study visit',
            'is_milestone': True
        },
        {
            'code': 'LSC',
            'name': 'Last Specimen Collection',
            'description': 'Final biological specimen collected from last participant',
            'is_milestone': True
        },
        {
            'code': 'FOLLOW_UP',
            'name': 'Follow Up',
            'description': 'Post-study follow-up period',
            'is_milestone': True
        },
        {
            'code': 'IRB_REVIEW',
            'name': 'IRB Continuing Review',
            'description': 'Ongoing throughout study conduct',
            'is_milestone': False,
            'is_recurring': True,
            'recurrence_interval_days': 365
        },
        {
            'code': 'FDA_ANNUAL',
            'name': 'FDA Annual Report',
            'description': 'Submit 60 days within anniversary date the IND went into effect (if sponsor of IND)',
            'is_milestone': False,
            'is_recurring': True,
            'recurrence_interval_days': 365
        }
    ]

    print(f"✓ Created {len(milestones)} Study Implementation milestones")
    return milestones


def create_site_closeout_tasks():
    """Create Site Closeout tasks from plain text"""
    print("\nCreating Site Closeout tasks...")

    tasks = [
        # Regulatory
        {'category': 'Regulatory', 'task': 'Determine IRB close-out reporting requirements', 'duration_days': 3},
        {'category': 'Regulatory', 'task': 'Submit final IRB report to PS', 'duration_days': 2},
        {'category': 'Regulatory', 'task': 'Complete regulatory binder with all essential documents', 'duration_days': 5},
        {'category': 'Regulatory', 'task': 'Report all protocol deviations, unblinding, and SAEs to DMID', 'duration_days': 3},
        {'category': 'Regulatory', 'task': 'Provide final study personnel log to FHI360', 'duration_days': 1},

        # Human Subjects
        {'category': 'Human Subjects', 'task': 'Verify all consent forms on file', 'duration_days': 2},
        {'category': 'Human Subjects', 'task': 'Confirm post-study specimen storage consent list', 'duration_days': 2},
        {'category': 'Human Subjects', 'task': 'Contact participants with ongoing AEs', 'duration_days': 14},
        {'category': 'Human Subjects', 'task': 'Resolve all AE queries', 'duration_days': 7},

        # Study Product
        {'category': 'Study Product', 'task': 'Dispose of remaining study product with monitor present', 'duration_days': 1},

        # Close-out Monitoring
        {'category': 'Close-out Monitoring', 'task': 'Facilitate site close-out visit', 'duration_days': 1},
        {'category': 'Close-out Monitoring', 'task': 'Resolve all monitoring issues', 'duration_days': 7},
        {'category': 'Close-out Monitoring', 'task': 'Download and save all participant data', 'duration_days': 1},

        # Data Management
        {'category': 'Data Management', 'task': 'Complete all paper and electronic CRFs', 'duration_days': 3},
        {'category': 'Data Management', 'task': 'Resolve all outstanding queries', 'duration_days': 7},

        # Laboratory Specimens
        {'category': 'Laboratory Specimens', 'task': 'Verify all specimens sent to labs', 'duration_days': 2},
        {'category': 'Laboratory Specimens', 'task': 'Confirm specimen retention/disposal per consent', 'duration_days': 3},

        # Record Retention
        {'category': 'Record Retention', 'task': 'Plan long-term storage per protocol', 'duration_days': 2},
        {'category': 'Record Retention', 'task': 'Obtain authorization from COU and DMID', 'duration_days': 5}
    ]

    print(f"✓ Created {len(tasks)} Site Closeout tasks")
    return tasks


def create_study_closeout_tasks():
    """Create Study Closeout tasks from plain text (detailed timeline)"""
    print("\nCreating Study Closeout tasks...")

    tasks = [
        # Clinical Database Lock
        {'code': 'CDB_001', 'category': 'Data Management', 'task': 'Clinical data entry completed', 'duration_days': 4,
         'description': '4 days after last subject, last visit'},
        {'code': 'CDB_002', 'category': 'Data Management', 'task': 'Data cleaning and querying', 'duration_days': 14,
         'description': '2 weeks after data entry completion', 'predecessors': ['CDB_001']},
        {'code': 'CDB_003', 'category': 'Safety', 'task': 'Serious Adverse Event reconciliation', 'duration_days': 21,
         'description': '3 weeks after data entry completion', 'predecessors': ['CDB_001']},
        {'code': 'CDB_004', 'category': 'Monitoring', 'task': 'Final monitoring visit', 'duration_days': 35,
         'description': '5 weeks after last subject, last visit', 'predecessors': ['CDB_002', 'CDB_003']},
        {'code': 'CDB_005', 'category': 'Data Management', 'task': 'Resolution of all data management and monitoring queries', 'duration_days': 1,
         'description': '1 day after final monitoring visit', 'predecessors': ['CDB_004']},
        {'code': 'CDB_006', 'category': 'Data Management', 'task': 'Clinical database lock', 'duration_days': 1,
         'description': '1 day after resolution of all queries', 'predecessors': ['CDB_005'], 'is_milestone': True},

        # Laboratory Database Lock
        {'code': 'LDB_001', 'category': 'Laboratory', 'task': 'Assay completion and transfer of laboratory data', 'duration_days': 84,
         'description': '12 weeks after last specimen collection'},
        {'code': 'LDB_002', 'category': 'Laboratory', 'task': 'QC of laboratory data and distribution of queries', 'duration_days': 4,
         'description': '4 days after receipt of laboratory data', 'predecessors': ['LDB_001']},
        {'code': 'LDB_003', 'category': 'Laboratory', 'task': 'Resolution of laboratory queries', 'duration_days': 7,
         'description': '1 week after distribution of queries', 'predecessors': ['LDB_002']},
        {'code': 'LDB_004', 'category': 'Laboratory', 'task': 'Laboratory database lock', 'duration_days': 1,
         'description': '1 day after resolution of lab queries', 'predecessors': ['LDB_003'], 'is_milestone': True},

        # CSR Preparation
        {'code': 'CSR_001', 'category': 'Regulatory', 'task': 'Preparation of draft Interim CSR', 'duration_days': 84,
         'description': '12 weeks after clinical AND laboratory database lock', 'predecessors': ['CDB_006', 'LDB_004']},
        {'code': 'CSR_002', 'category': 'Safety', 'task': 'PVG provides SAE narratives', 'duration_days': 30,
         'description': '30 days after clinical database lock', 'predecessors': ['CDB_006']},
        {'code': 'CSR_003', 'category': 'Regulatory', 'task': 'Distribute draft Interim CSR to PI for review', 'duration_days': 1,
         'description': '1 day after draft CSR complete', 'predecessors': ['CSR_001']},
        {'code': 'CSR_004', 'category': 'Regulatory', 'task': 'PI reviews and completes designated sections of CSR', 'duration_days': 35,
         'description': '4-6 weeks after distribution of draft CSR', 'predecessors': ['CSR_003']},
        {'code': 'CSR_005', 'category': 'Regulatory', 'task': 'Incorporate PI text, address comments, format CSR', 'duration_days': 7,
         'description': '1 week after receiving draft CSR from PI', 'predecessors': ['CSR_004']},
        {'code': 'CSR_006', 'category': 'Regulatory', 'task': 'Distribute draft CSR to DMID and PI for review', 'duration_days': 1,
         'description': '1 day after draft CSR complete', 'predecessors': ['CSR_005']},
        {'code': 'CSR_007', 'category': 'Regulatory', 'task': 'DMID reviews draft CSR and provides comments', 'duration_days': 28,
         'description': '4 weeks after distribution to DMID', 'predecessors': ['CSR_006']},
        {'code': 'CSR_008', 'category': 'Regulatory', 'task': 'Incorporate DMID comments and prepare final draft CSR', 'duration_days': 7,
         'description': '1 week after receipt of DMID comments', 'predecessors': ['CSR_007']},
        {'code': 'CSR_009', 'category': 'Regulatory', 'task': 'Receive DMID and PI approval to finalize CSR', 'duration_days': 3,
         'description': '3 days after final draft distributed', 'predecessors': ['CSR_008']},
        {'code': 'CSR_010', 'category': 'Regulatory', 'task': 'Prepare approved CSR per regulatory requirements', 'duration_days': 3,
         'description': '3 days after approval to finalize', 'predecessors': ['CSR_009']},
        {'code': 'CSR_011', 'category': 'Regulatory', 'task': 'Lead PI signs signature page and returns', 'duration_days': 3,
         'description': '3 days after notification of approved CSR', 'predecessors': ['CSR_010']},
        {'code': 'CSR_012', 'category': 'Regulatory', 'task': 'Distribute approved CSR to CROMS portals', 'duration_days': 1,
         'description': '1 day after receipt of PI signature', 'predecessors': ['CSR_011']},
        {'code': 'CSR_013', 'category': 'Regulatory', 'task': 'RAS submits final, signed CSR to FDA', 'duration_days': 17,
         'description': '2-3 weeks after signature page posted', 'predecessors': ['CSR_012'], 'is_milestone': True}
    ]

    print(f"✓ Created {len(tasks)} Study Closeout tasks")
    return tasks


def insert_templates(conn):
    """Insert template definitions"""
    print("\nInserting template definitions...")

    cursor = conn.cursor()

    # Parse all tasks first to count them
    startup_tasks = parse_startup_csv()
    site_activation_items = parse_site_activation_csv()
    implementation_milestones = create_study_implementation_milestones()
    site_closeout_tasks = create_site_closeout_tasks()
    study_closeout_tasks = create_study_closeout_tasks()

    templates = [
        {
            'template_id': 'TPL_001',
            'template_name': 'Study Start-Up',
            'template_type': 'study_startup',
            'version': '1.0',
            'description': 'Study startup activities from Study Award to FPI',
            'total_task_count': len(startup_tasks),
            'estimated_duration_days': 180  # ~6 months
        },
        {
            'template_id': 'TPL_002',
            'template_name': 'Study Implementation/Active Enrollment',
            'template_type': 'implementation',
            'version': '1.0',
            'description': 'Study conduct milestones (FPI → LPLV) with recurring activities',
            'total_task_count': len(implementation_milestones),
            'estimated_duration_days': 730  # Variable, typically 2 years
        },
        {
            'template_id': 'TPL_003',
            'template_name': 'Study Closeout',
            'template_type': 'closeout',
            'version': '1.0',
            'description': 'Study closeout from LPLV to FDA CSR submission',
            'total_task_count': len(study_closeout_tasks),
            'estimated_duration_days': 300  # ~10 months
        },
        {
            'template_id': 'TPL_004',
            'template_name': 'Site Activation',
            'template_type': 'site_activation',
            'version': '1.0',
            'description': 'Site activation checklist from site selection to site activated',
            'total_task_count': len(site_activation_items),
            'estimated_duration_days': 90  # ~3 months
        },
        {
            'template_id': 'TPL_005',
            'template_name': 'Site Closeout',
            'template_type': 'site_closeout',
            'version': '1.0',
            'description': 'Site closeout activities by category',
            'total_task_count': len(site_closeout_tasks),
            'estimated_duration_days': 30  # ~1 month
        },
        {
            'template_id': 'TPL_006',
            'template_name': 'Full Study Timeline',
            'template_type': 'full_study',
            'version': '1.0',
            'description': 'Complete study timeline: Startup + Implementation + Closeout',
            'total_task_count': len(startup_tasks) + len(implementation_milestones) + len(study_closeout_tasks),
            'estimated_duration_days': 1260  # ~3.5 years total
        }
    ]

    for template in templates:
        cursor.execute("""
            INSERT INTO timeline_templates (
                template_id, template_name, template_type, version,
                description, total_task_count, estimated_duration_days, org_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
        """, (
            template['template_id'],
            template['template_name'],
            template['template_type'],
            template['version'],
            template['description'],
            template['total_task_count'],
            template['estimated_duration_days']
        ))

    conn.commit()
    print(f"✓ Inserted {len(templates)} template definitions")

    return {
        'startup_tasks': startup_tasks,
        'site_activation_items': site_activation_items,
        'implementation_milestones': implementation_milestones,
        'site_closeout_tasks': site_closeout_tasks,
        'study_closeout_tasks': study_closeout_tasks
    }


def insert_template_tasks(conn, all_tasks):
    """Insert all template tasks"""
    print("\nInserting template tasks...")

    cursor = conn.cursor()
    task_count = 0

    # TPL_001: Study Start-Up
    for idx, task in enumerate(all_tasks['startup_tasks'], 1):
        cursor.execute("""
            INSERT INTO template_tasks (
                task_id, template_id, task_name, category,
                typical_duration_days, sort_order, notes,
                is_milestone, is_critical_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"STARTUP_{idx:03d}",
            'TPL_001',
            task['task_name'],
            task['category'],
            task['duration_days'],
            idx,
            task.get('notes', ''),
            0,
            0
        ))
        task_count += 1

    # TPL_002: Study Implementation
    for idx, milestone in enumerate(all_tasks['implementation_milestones'], 1):
        cursor.execute("""
            INSERT INTO template_tasks (
                task_id, template_id, task_name, task_code, category,
                typical_duration_days, sort_order, description,
                is_milestone, is_recurring, recurrence_interval_days
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"IMPL_{idx:03d}",
            'TPL_002',
            milestone['name'],
            milestone['code'],
            'Study Conduct',
            1,  # Milestones are single day
            idx,
            milestone['description'],
            1 if milestone['is_milestone'] else 0,
            1 if milestone.get('is_recurring', False) else 0,
            milestone.get('recurrence_interval_days')
        ))
        task_count += 1

    # TPL_003: Study Closeout
    for idx, task in enumerate(all_tasks['study_closeout_tasks'], 1):
        cursor.execute("""
            INSERT INTO template_tasks (
                task_id, template_id, task_name, task_code, category,
                typical_duration_days, sort_order, description,
                is_milestone
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.get('code', f"CLOSEOUT_{idx:03d}"),
            'TPL_003',
            task['task'],
            task.get('code'),
            task['category'],
            task['duration_days'],
            idx,
            task.get('description', ''),
            1 if task.get('is_milestone', False) else 0
        ))
        task_count += 1

    # TPL_004: Site Activation
    for idx, item in enumerate(all_tasks['site_activation_items'], 1):
        cursor.execute("""
            INSERT INTO template_tasks (
                task_id, template_id, task_name, category,
                typical_duration_days, sort_order, notes,
                is_milestone
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"SITEACT_{idx:03d}",
            'TPL_004',
            item['item'],
            item['category'],
            3,  # Checklist items ~3 days each
            idx,
            item.get('notes', ''),
            0
        ))
        task_count += 1

    # TPL_005: Site Closeout
    for idx, task in enumerate(all_tasks['site_closeout_tasks'], 1):
        cursor.execute("""
            INSERT INTO template_tasks (
                task_id, template_id, task_name, category,
                typical_duration_days, sort_order,
                is_milestone
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            f"SITECLOSE_{idx:03d}",
            'TPL_005',
            task['task'],
            task['category'],
            task['duration_days'],
            idx,
            0
        ))
        task_count += 1

    # TPL_006: Full Study Timeline (reference to other templates)
    # Add references to TPL_001, TPL_002, TPL_003 tasks
    combined_idx = 1

    # Add all startup tasks
    for task in all_tasks['startup_tasks']:
        cursor.execute("""
            INSERT INTO template_tasks (
                task_id, template_id, task_name, category,
                typical_duration_days, sort_order, notes,
                is_milestone
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"FULL_{combined_idx:03d}",
            'TPL_006',
            task['task_name'],
            task['category'],
            task['duration_days'],
            combined_idx,
            task.get('notes', ''),
            0
        ))
        combined_idx += 1
        task_count += 1

    # Add all implementation milestones
    for milestone in all_tasks['implementation_milestones']:
        cursor.execute("""
            INSERT INTO template_tasks (
                task_id, template_id, task_name, task_code, category,
                typical_duration_days, sort_order, description,
                is_milestone, is_recurring, recurrence_interval_days
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"FULL_{combined_idx:03d}",
            'TPL_006',
            milestone['name'],
            milestone['code'],
            'Study Conduct',
            1,
            combined_idx,
            milestone['description'],
            1 if milestone['is_milestone'] else 0,
            1 if milestone.get('is_recurring', False) else 0,
            milestone.get('recurrence_interval_days')
        ))
        combined_idx += 1
        task_count += 1

    # Add all closeout tasks
    for task in all_tasks['study_closeout_tasks']:
        cursor.execute("""
            INSERT INTO template_tasks (
                task_id, template_id, task_name, task_code, category,
                typical_duration_days, sort_order, description,
                is_milestone
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"FULL_{combined_idx:03d}",
            'TPL_006',
            task['task'],
            task.get('code'),
            task['category'],
            task['duration_days'],
            combined_idx,
            task.get('description', ''),
            1 if task.get('is_milestone', False) else 0
        ))
        combined_idx += 1
        task_count += 1

    conn.commit()
    print(f"✓ Inserted {task_count} template tasks")


def insert_template_dependencies(conn, all_tasks):
    """Insert template task dependencies (predecessors)"""
    print("\nInserting template dependencies...")

    cursor = conn.cursor()
    dep_count = 0

    # Study Start-Up dependencies
    # First, create a mapping of task names to task IDs and milestone keywords
    task_name_to_id = {}
    milestone_keywords = {}

    for idx, task in enumerate(all_tasks['startup_tasks'], 1):
        task_id = f"SS_{idx:03d}"
        task_name_to_id[task['task_name']] = task_id

        # Map milestone keywords from task names
        task_name_lower = task['task_name'].lower()

        # Common milestone mappings
        if 'internal transition meeting' in task_name_lower:
            milestone_keywords['Internal Transition Meeting'] = task_id
            milestone_keywords['Transition Meeting'] = task_id
        if 'kick' in task_name_lower and 'off' in task_name_lower:
            milestone_keywords['KOM'] = task_id
            milestone_keywords['Kick-off Meeting'] = task_id
        if 'study award' in task_name_lower:
            milestone_keywords['Study Award'] = task_id
        if 'final protocol' in task_name_lower or (task_name_lower.startswith('protocol') and 'final' in task_name_lower):
            milestone_keywords['Final Protocol'] = task_id
        if 'budget' in task_name_lower and ('final' in task_name_lower or 'contract' in task_name_lower):
            milestone_keywords['Final Study Budget & Contract'] = task_id
            milestone_keywords['Study Budget and Contract Finalized'] = task_id
            milestone_keywords['Final Budget/Contract'] = task_id
        if 'database' in task_name_lower and 'build' in task_name_lower:
            milestone_keywords['Database Build'] = task_id
        if 'contract' in task_name_lower and ('execution' in task_name_lower or 'final' in task_name_lower):
            milestone_keywords['Full Execution of contract'] = task_id
            milestone_keywords['Contract Final'] = task_id

    # Insert Study Start-Up dependencies
    for idx, task in enumerate(all_tasks['startup_tasks'], 1):
        task_id = f"SS_{idx:03d}"
        predecessor = task.get('predecessor', '').strip()

        if predecessor and predecessor not in ['None', 'N/A', '']:
            # Handle comma-separated multiple predecessors
            pred_parts = [p.strip() for p in predecessor.split(',')]

            for pred_part in pred_parts:
                if not pred_part:
                    continue

                pred_task_id = None

                # Try milestone keywords first
                if pred_part in milestone_keywords:
                    pred_task_id = milestone_keywords[pred_part]
                # Then exact task name match
                elif pred_part in task_name_to_id:
                    pred_task_id = task_name_to_id[pred_part]
                else:
                    # Fuzzy match - check if any milestone keyword is in the predecessor
                    for keyword, tid in milestone_keywords.items():
                        if keyword.lower() in pred_part.lower():
                            pred_task_id = tid
                            break

                if pred_task_id and pred_task_id != task_id:  # Don't create self-dependencies
                    try:
                        cursor.execute("""
                            INSERT INTO template_dependencies (
                                dependency_id, template_id, predecessor_task_id, successor_task_id,
                                dependency_type, lag_days, is_hard_dependency
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            f"DEP_TPL001_{task_id}_{pred_task_id}_{dep_count}",
                            'TPL_001',
                            pred_task_id,
                            task_id,
                            'finish-to-start',
                            0,
                            0  # Not hard dependency for Study Start-Up (more flexible)
                        ))
                        dep_count += 1
                    except sqlite3.IntegrityError:
                        # Skip duplicate dependencies
                        pass

    # Study Closeout has explicit predecessors
    for task in all_tasks['study_closeout_tasks']:
        if 'predecessors' in task and task['predecessors']:
            for pred_code in task['predecessors']:
                cursor.execute("""
                    INSERT INTO template_dependencies (
                        dependency_id, template_id, predecessor_task_id, successor_task_id,
                        dependency_type, lag_days, is_hard_dependency
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"DEP_TPL003_{task['code']}_{pred_code}",
                    'TPL_003',
                    pred_code,
                    task['code'],
                    'finish-to-start',
                    0,
                    1
                ))
                dep_count += 1

    conn.commit()
    print(f"✓ Inserted {dep_count} template dependencies")


def main():
    """Main execution"""
    print("="*80)
    print("UPDATING TIMELINE TEMPLATES FROM USER DATA")
    print("="*80)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        # Clear existing templates
        clear_existing_templates(conn)

        # Insert new templates and get tasks
        all_tasks = insert_templates(conn)

        # Insert template tasks
        insert_template_tasks(conn, all_tasks)

        # Insert dependencies
        insert_template_dependencies(conn, all_tasks)

        print("\n" + "="*80)
        print("✅ TEMPLATE UPDATE COMPLETE")
        print("="*80)

        # Verify
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM timeline_templates WHERE org_id IS NULL")
        template_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM template_tasks")
        task_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM template_dependencies")
        dep_count = cursor.fetchone()[0]

        print(f"\nFinal counts:")
        print(f"  Templates: {template_count}")
        print(f"  Tasks: {task_count}")
        print(f"  Dependencies: {dep_count}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    main()
