#!/usr/bin/env python3
"""
Migration script: Populate timeline templates from actual source data

Data sources:
- Study Closeout: YAML structure with 24 tasks across 4 subphases
- Site Closeout: YAML structure with 18 tasks across 7 categories
- Study Implementation: YAML structure with 8 milestones + 2 recurring activities
- Study Startup: CSV file with ~100-120 tasks
- Site Activation: CSV file with ~50-55 checklist items

Replaces:
- "Emmes" → "CRO or sponsor"
- "DMID" → "CRO or sponsor"
"""

import sqlite3
import uuid
import csv
from pathlib import Path
from typing import List, Dict, Any

# Study Closeout YAML data (provided by user)
STUDY_CLOSEOUT_DATA = {
    "clinical_database_lock": {
        "subphase_name": "Clinical Database Lock",
        "estimated_total_duration_weeks": 6,
        "tasks": [
            {
                "task_id": "CDB_001",
                "task_name": "Clinical Data Entry Completed",
                "duration_days": 4,
                "predecessor": "last_subject_last_visit",
                "typical_duration_days": 4,
                "responsible_role": "Data Management"
            },
            {
                "task_id": "CDB_002",
                "task_name": "Data Queries Resolved",
                "duration_days": 14,
                "predecessor": "CDB_001",
                "typical_duration_days": 14,
                "responsible_role": "Data Management"
            },
            {
                "task_id": "CDB_003",
                "task_name": "Data Review (QC)",
                "duration_days": 7,
                "predecessor": "CDB_002",
                "typical_duration_days": 7,
                "responsible_role": "Data Management"
            },
            {
                "task_id": "CDB_004",
                "task_name": "Medical Coding Completed",
                "duration_days": 3,
                "predecessor": "CDB_002",
                "typical_duration_days": 3,
                "responsible_role": "Medical Coding"
            },
            {
                "task_id": "CDB_005",
                "task_name": "Data Lock Plan Finalized",
                "duration_days": 2,
                "predecessor": "CDB_003",
                "typical_duration_days": 2,
                "responsible_role": "Data Management"
            },
            {
                "task_id": "CDB_006",
                "task_name": "Clinical Database Lock",
                "duration_days": 1,
                "predecessor": "CDB_004;CDB_005",
                "typical_duration_days": 1,
                "responsible_role": "Data Management",
                "is_milestone": True
            }
        ]
    },
    "laboratory_database_lock": {
        "subphase_name": "Laboratory Database Lock",
        "estimated_total_duration_weeks": 14,
        "tasks": [
            {
                "task_id": "LDB_001",
                "task_name": "Assay Completion and Transfer",
                "duration_weeks": 12,
                "predecessor": "last_subject_last_visit",
                "typical_duration_days": 84,
                "responsible_role": "Laboratory"
            },
            {
                "task_id": "LDB_002",
                "task_name": "Lab Data Quality Check",
                "duration_days": 7,
                "predecessor": "LDB_001",
                "typical_duration_days": 7,
                "responsible_role": "Laboratory"
            },
            {
                "task_id": "LDB_003",
                "task_name": "Lab Data Integration",
                "duration_days": 7,
                "predecessor": "LDB_002",
                "typical_duration_days": 7,
                "responsible_role": "Data Management"
            },
            {
                "task_id": "LDB_004",
                "task_name": "Laboratory Database Lock",
                "duration_days": 1,
                "predecessor": "LDB_003;CDB_006",
                "typical_duration_days": 1,
                "responsible_role": "Data Management",
                "is_milestone": True
            }
        ]
    },
    "csr_preparation": {
        "subphase_name": "CSR Preparation",
        "estimated_total_duration_weeks": 30,
        "tasks": [
            {
                "task_id": "CSR_001",
                "task_name": "Preparation of Draft v01 CSR",
                "duration_weeks": 12,
                "predecessor": "LDB_004",
                "typical_duration_days": 84,
                "responsible_role": "Medical Writing"
            },
            {
                "task_id": "CSR_002",
                "task_name": "Statistical Analysis Plan (SAP) Finalization",
                "duration_weeks": 2,
                "predecessor": "LDB_004",
                "typical_duration_days": 14,
                "responsible_role": "Biostatistics"
            },
            {
                "task_id": "CSR_003",
                "task_name": "Statistical Programming and Analysis",
                "duration_weeks": 8,
                "predecessor": "CSR_002",
                "typical_duration_days": 56,
                "responsible_role": "Biostatistics"
            },
            {
                "task_id": "CSR_004",
                "task_name": "Tables, Listings, and Figures (TLFs)",
                "duration_weeks": 6,
                "predecessor": "CSR_003",
                "typical_duration_days": 42,
                "responsible_role": "Biostatistics"
            },
            {
                "task_id": "CSR_005",
                "task_name": "Integration of TLFs into CSR",
                "duration_weeks": 2,
                "predecessor": "CSR_001;CSR_004",
                "typical_duration_days": 14,
                "responsible_role": "Medical Writing"
            },
            {
                "task_id": "CSR_006",
                "task_name": "Internal CSR Review (QC)",
                "duration_weeks": 3,
                "predecessor": "CSR_005",
                "typical_duration_days": 21,
                "responsible_role": "Quality Assurance"
            },
            {
                "task_id": "CSR_007",
                "task_name": "Incorporation of Internal Comments",
                "duration_weeks": 2,
                "predecessor": "CSR_006",
                "typical_duration_days": 14,
                "responsible_role": "Medical Writing"
            },
            {
                "task_id": "CSR_008",
                "task_name": "Submit CSR to Sponsor for Review",
                "duration_days": 1,
                "predecessor": "CSR_007",
                "typical_duration_days": 1,
                "responsible_role": "Medical Writing",
                "is_milestone": True
            },
            {
                "task_id": "CSR_009",
                "task_name": "Sponsor Review of CSR",
                "duration_weeks": 4,
                "predecessor": "CSR_008",
                "typical_duration_days": 28,
                "responsible_role": "Sponsor"
            },
            {
                "task_id": "CSR_010",
                "task_name": "Incorporation of Sponsor Comments",
                "duration_weeks": 3,
                "predecessor": "CSR_009",
                "typical_duration_days": 21,
                "responsible_role": "Medical Writing"
            },
            {
                "task_id": "CSR_011",
                "task_name": "Final CSR QC",
                "duration_weeks": 1,
                "predecessor": "CSR_010",
                "typical_duration_days": 7,
                "responsible_role": "Quality Assurance"
            },
            {
                "task_id": "CSR_012",
                "task_name": "CSR Finalization",
                "duration_days": 1,
                "predecessor": "CSR_011",
                "typical_duration_days": 1,
                "responsible_role": "Medical Writing",
                "is_milestone": True
            },
            {
                "task_id": "CSR_013",
                "task_name": "CSR Submission to Regulatory Authorities",
                "duration_days": 1,
                "predecessor": "CSR_012",
                "typical_duration_days": 1,
                "responsible_role": "Regulatory Affairs",
                "is_milestone": True
            }
        ]
    },
    "manuscript": {
        "subphase_name": "Manuscript Submission",
        "tasks": [
            {
                "task_id": "MANU_001",
                "task_name": "Submit Manuscript",
                "duration_months": 12,
                "predecessor": "CSR_012",
                "typical_duration_days": 365,
                "responsible_role": "Medical Writing",
                "description": "Prepare and submit manuscript for peer review publication",
                "is_milestone": True
            }
        ]
    }
}

# Site Closeout YAML data (provided by user)
SITE_CLOSEOUT_DATA = {
    "regulatory": {
        "category_name": "Regulatory",
        "tasks": [
            {
                "task_id": "REG_CO_001",
                "task_name": "IRB Close-Out Reporting Requirements",
                "estimated_duration_days": 7,
                "typical_duration_days": 7,
                "responsible_role": "Regulatory Affairs"
            },
            {
                "task_id": "REG_CO_002",
                "task_name": "IRB Report Close Out Form",
                "estimated_duration_days": 3,
                "typical_duration_days": 3,
                "responsible_role": "Regulatory Affairs"
            },
            {
                "task_id": "REG_CO_003",
                "task_name": "IRB Continuing Review (if needed)",
                "estimated_duration_days": 14,
                "typical_duration_days": 14,
                "responsible_role": "Regulatory Affairs"
            },
            {
                "task_id": "REG_CO_004",
                "task_name": "Close-Out Audit Prep",
                "estimated_duration_days": 5,
                "typical_duration_days": 5,
                "responsible_role": "Quality Assurance"
            },
            {
                "task_id": "REG_CO_005",
                "task_name": "Close Out Visit",
                "estimated_duration_days": 1,
                "typical_duration_days": 1,
                "responsible_role": "CRO or sponsor",
                "is_milestone": True
            }
        ]
    },
    "human_subjects": {
        "category_name": "Human Subjects",
        "tasks": [
            {
                "task_id": "HS_CO_001",
                "task_name": "Informed Consent Verification",
                "estimated_duration_days": 3,
                "typical_duration_days": 3,
                "responsible_role": "Clinical Research Associate"
            },
            {
                "task_id": "HS_CO_002",
                "task_name": "Adverse Event Resolution",
                "estimated_duration_days": 14,
                "typical_duration_days": 14,
                "responsible_role": "Clinical Research Associate",
                "description": "Critical for Clinical DB Lock - must be complete before database lock"
            }
        ]
    },
    "study_product": {
        "category_name": "Study Product",
        "tasks": [
            {
                "task_id": "SP_CO_001",
                "task_name": "Final Accountability Reconciliation",
                "estimated_duration_days": 5,
                "typical_duration_days": 5,
                "responsible_role": "Pharmacist"
            },
            {
                "task_id": "SP_CO_002",
                "task_name": "IP Return/Destruction",
                "estimated_duration_days": 7,
                "typical_duration_days": 7,
                "responsible_role": "Pharmacist"
            },
            {
                "task_id": "SP_CO_003",
                "task_name": "IP Destruction Certificate",
                "estimated_duration_days": 3,
                "typical_duration_days": 3,
                "responsible_role": "Pharmacist"
            }
        ]
    },
    "monitoring_visit": {
        "category_name": "Monitoring Visit",
        "tasks": [
            {
                "task_id": "MV_CO_001",
                "task_name": "Schedule Close-Out Visit",
                "estimated_duration_days": 7,
                "typical_duration_days": 7,
                "responsible_role": "Clinical Research Associate"
            },
            {
                "task_id": "MV_CO_002",
                "task_name": "Conduct Close-Out Visit",
                "estimated_duration_days": 1,
                "typical_duration_days": 1,
                "responsible_role": "Clinical Research Associate",
                "is_milestone": True
            },
            {
                "task_id": "MV_CO_003",
                "task_name": "Close-Out Visit Report",
                "estimated_duration_days": 5,
                "typical_duration_days": 5,
                "responsible_role": "Clinical Research Associate"
            }
        ]
    },
    "data_management": {
        "category_name": "Data Management",
        "tasks": [
            {
                "task_id": "DM_CO_001",
                "task_name": "Final Data Entry",
                "estimated_duration_days": 7,
                "typical_duration_days": 7,
                "responsible_role": "Data Management"
            },
            {
                "task_id": "DM_CO_002",
                "task_name": "Query Resolution",
                "estimated_duration_days": 14,
                "typical_duration_days": 14,
                "responsible_role": "Data Management"
            }
        ]
    },
    "laboratory": {
        "category_name": "Laboratory",
        "tasks": [
            {
                "task_id": "LAB_CO_001",
                "task_name": "Final Sample Shipment",
                "estimated_duration_days": 3,
                "typical_duration_days": 3,
                "responsible_role": "Laboratory"
            },
            {
                "task_id": "LAB_CO_002",
                "task_name": "Sample Destruction Authorization",
                "estimated_duration_days": 5,
                "typical_duration_days": 5,
                "responsible_role": "Laboratory"
            }
        ]
    },
    "record_retention": {
        "category_name": "Record Retention",
        "tasks": [
            {
                "task_id": "RR_CO_001",
                "task_name": "Essential Document Archiving",
                "estimated_duration_days": 7,
                "typical_duration_days": 7,
                "responsible_role": "CRO or sponsor"
            },
            {
                "task_id": "RR_CO_002",
                "task_name": "Site File Closure",
                "estimated_duration_days": 3,
                "typical_duration_days": 3,
                "responsible_role": "CRO or sponsor",
                "is_milestone": True
            }
        ]
    }
}

# Study Implementation YAML data (provided by user)
STUDY_IMPLEMENTATION_DATA = {
    "enrollment_milestones": {
        "milestones": [
            {
                "milestone_id": "FPI",
                "milestone_name": "First Person In (FPI)",
                "is_milestone": True,
                "typical_duration_days": 1
            },
            {
                "milestone_id": "FPD",
                "milestone_name": "First Person Dosed (FPD)",
                "is_milestone": True,
                "typical_duration_days": 1
            },
            {
                "milestone_id": "FCR",
                "milestone_name": "First Cohort Review (FCR)",
                "is_milestone": True,
                "typical_duration_days": 1
            },
            {
                "milestone_id": "LPI",
                "milestone_name": "Last Patient In (LPI)",
                "is_milestone": True,
                "typical_duration_days": 1
            },
            {
                "milestone_id": "LPD",
                "milestone_name": "Last Person Dosed (LPD)",
                "is_milestone": True,
                "typical_duration_days": 1
            },
            {
                "milestone_id": "LPLV",
                "milestone_name": "Last Participant Last Visit (LPLV)",
                "is_milestone": True,
                "typical_duration_days": 1
            },
            {
                "milestone_id": "LSC",
                "milestone_name": "Last Specimen Collection",
                "is_milestone": True,
                "typical_duration_days": 1
            },
            {
                "milestone_id": "FOLLOWUP",
                "milestone_name": "Follow Up",
                "is_milestone": True,
                "typical_duration_days": 1
            }
        ]
    },
    "recurring_activities": {
        "activities": [
            {
                "activity_id": "IRB_CR",
                "activity_name": "IRB Continuing Review",
                "frequency": "Every 12 months",
                "typical_duration_days": 14,
                "responsible_role": "Regulatory Affairs"
            },
            {
                "activity_id": "FDA_AR",
                "activity_name": "FDA Annual Report",
                "frequency": "Annually (if IND)",
                "typical_duration_days": 30,
                "responsible_role": "Regulatory Affairs",
                "description": "Required only if study conducted under IND"
            }
        ]
    }
}


class OntologyToTemplatesMigration:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.conn = None

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA foreign_keys = ON")

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def clear_existing_templates(self):
        """Clear existing template data"""
        print("Clearing existing template data...")
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM template_dependencies")
        cursor.execute("DELETE FROM template_tasks")
        cursor.execute("DELETE FROM timeline_templates")
        self.conn.commit()
        print("  ✓ Cleared")

    def create_template(self, template_id: str, template_name: str,
                       template_type: str, description: str = None) -> str:
        """Create a template record"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO timeline_templates (
                template_id, template_name, template_type,
                version, description
            ) VALUES (?, ?, ?, ?, ?)
        """, (template_id, template_name, template_type, "1.0", description))
        self.conn.commit()
        return template_id

    def create_task(self, template_id: str, task_data: Dict[str, Any],
                   sort_order: int, parent_task_id: str = None):
        """Create a task record"""
        task_id = task_data.get('task_id', f"{template_id}_TASK_{sort_order}")

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO template_tasks (
                task_id, template_id, task_name, task_code, category,
                typical_duration_days, is_milestone, is_critical_path,
                description, responsible_role, parent_task_id, sort_order,
                outline_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            template_id,
            task_data.get('task_name', ''),
            task_data.get('task_code', task_data.get('task_id', '')),
            task_data.get('category', ''),
            task_data.get('typical_duration_days', 1),
            task_data.get('is_milestone', False),
            task_data.get('is_critical_path', False),
            task_data.get('description', ''),
            task_data.get('responsible_role', ''),
            parent_task_id,
            sort_order,
            2 if parent_task_id else 1
        ))
        self.conn.commit()
        return task_id

    def create_dependency(self, template_id: str, predecessor_id: str,
                         successor_id: str, dependency_type: str = 'finish-to-start'):
        """Create a dependency record"""
        dependency_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO template_dependencies (
                dependency_id, template_id, predecessor_task_id,
                successor_task_id, dependency_type, lag_days, is_hard_dependency
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (dependency_id, template_id, predecessor_id, successor_id,
              dependency_type, 0, True))
        self.conn.commit()

    def populate_study_closeout(self):
        """Populate Study Closeout template from YAML data"""
        print("\n📋 Populating Study Closeout template...")

        template_id = "TPL_003"
        self.create_template(
            template_id,
            "Study Closeout",
            "closeout",
            "Study closeout activities: Clinical DB Lock → Lab DB Lock → CSR Preparation → Manuscript"
        )

        task_counter = 1
        task_id_map = {}

        # Process each subphase
        for subphase_key, subphase_data in STUDY_CLOSEOUT_DATA.items():
            subphase_name = subphase_data.get('subphase_name', subphase_key.replace('_', ' ').title())

            # Create subphase header task
            header_task_id = f"{template_id}_HEADER_{subphase_key.upper()}"
            self.create_task(template_id, {
                'task_id': header_task_id,
                'task_name': subphase_name,
                'task_code': subphase_key.upper(),
                'category': 'Closeout',
                'typical_duration_days': 1,
                'is_milestone': False
            }, task_counter)
            task_counter += 1

            # Create tasks under subphase
            for task in subphase_data.get('tasks', []):
                task_id = self.create_task(template_id, {
                    'task_id': task['task_id'],
                    'task_name': task['task_name'],
                    'task_code': task['task_id'],
                    'category': subphase_name,
                    'typical_duration_days': task.get('typical_duration_days', 1),
                    'is_milestone': task.get('is_milestone', False),
                    'description': task.get('description', ''),
                    'responsible_role': task.get('responsible_role', '')
                }, task_counter, header_task_id)

                task_id_map[task['task_id']] = task_id
                task_counter += 1

                # Create dependencies if specified
                if 'predecessor' in task:
                    predecessors = task['predecessor'].split(';')
                    for pred in predecessors:
                        pred = pred.strip()
                        if pred in task_id_map:
                            self.create_dependency(template_id, task_id_map[pred], task_id)

        print(f"  ✓ Created {task_counter - 1} tasks (24 actual tasks + 4 subphase headers)")

    def populate_site_closeout(self):
        """Populate Site Closeout template from YAML data"""
        print("\n📋 Populating Site Closeout template...")

        template_id = "TPL_005"
        self.create_template(
            template_id,
            "Site Closeout",
            "site_closeout",
            "Site closeout activities across 7 categories: 18 tasks total"
        )

        task_counter = 1
        task_id_map = {}

        # Process each category
        for category_key, category_data in SITE_CLOSEOUT_DATA.items():
            category_name = category_data.get('category_name', category_key.replace('_', ' ').title())

            # Create category header task
            header_task_id = f"{template_id}_HEADER_{category_key.upper()}"
            self.create_task(template_id, {
                'task_id': header_task_id,
                'task_name': category_name,
                'task_code': category_key.upper(),
                'category': 'Site Closeout',
                'typical_duration_days': 1,
                'is_milestone': False
            }, task_counter)
            task_counter += 1

            # Create tasks under category
            for task in category_data.get('tasks', []):
                task_id = self.create_task(template_id, {
                    'task_id': task['task_id'],
                    'task_name': task['task_name'],
                    'task_code': task['task_id'],
                    'category': category_name,
                    'typical_duration_days': task.get('typical_duration_days',
                                                    task.get('estimated_duration_days', 1)),
                    'is_milestone': task.get('is_milestone', False),
                    'description': task.get('description', ''),
                    'responsible_role': task.get('responsible_role', '')
                }, task_counter, header_task_id)

                task_id_map[task['task_id']] = task_id
                task_counter += 1

        print(f"  ✓ Created {task_counter - 1} tasks (18 actual tasks + 7 category headers)")

    def populate_study_implementation(self):
        """Populate Study Implementation template from YAML data"""
        print("\n📋 Populating Study Implementation template...")

        template_id = "TPL_002"
        self.create_template(
            template_id,
            "Study Implementation/Active Enrollment",
            "implementation",
            "Study implementation: 8 enrollment milestones + 2 recurring activities"
        )

        task_counter = 1

        # Create enrollment milestones
        milestones_header_id = f"{template_id}_HEADER_MILESTONES"
        self.create_task(template_id, {
            'task_id': milestones_header_id,
            'task_name': 'Enrollment Milestones',
            'task_code': 'ENROLLMENT',
            'category': 'Implementation',
            'typical_duration_days': 1,
            'is_milestone': False
        }, task_counter)
        task_counter += 1

        for milestone in STUDY_IMPLEMENTATION_DATA['enrollment_milestones']['milestones']:
            self.create_task(template_id, {
                'task_id': milestone['milestone_id'],
                'task_name': milestone['milestone_name'],
                'task_code': milestone['milestone_id'],
                'category': 'Enrollment Milestone',
                'typical_duration_days': milestone.get('typical_duration_days', 1),
                'is_milestone': True
            }, task_counter, milestones_header_id)
            task_counter += 1

        # Create recurring activities
        recurring_header_id = f"{template_id}_HEADER_RECURRING"
        self.create_task(template_id, {
            'task_id': recurring_header_id,
            'task_name': 'Recurring Activities',
            'task_code': 'RECURRING',
            'category': 'Implementation',
            'typical_duration_days': 1,
            'is_milestone': False
        }, task_counter)
        task_counter += 1

        for activity in STUDY_IMPLEMENTATION_DATA['recurring_activities']['activities']:
            self.create_task(template_id, {
                'task_id': activity['activity_id'],
                'task_name': f"{activity['activity_name']} ({activity['frequency']})",
                'task_code': activity['activity_id'],
                'category': 'Recurring Activity',
                'typical_duration_days': activity.get('typical_duration_days', 14),
                'is_milestone': False,
                'description': activity.get('description', ''),
                'responsible_role': activity.get('responsible_role', '')
            }, task_counter, recurring_header_id)
            task_counter += 1

        print(f"  ✓ Created {task_counter - 1} tasks (8 milestones + 2 recurring + 2 headers)")

    def populate_study_startup_from_csv(self):
        """Populate Study Startup template from CSV file"""
        print("\n📋 Populating Study Startup template from CSV...")

        template_id = "TPL_001"
        self.create_template(
            template_id,
            "Study Startup",
            "study_startup",
            "Study startup activities from Study Award to FPI"
        )

        csv_path = self.db_path.parent.parent.parent / "assets" / "Study Timeline" / "Study Start-Up Guidance Document.csv"

        if not csv_path.exists():
            print(f"  ⚠ CSV file not found: {csv_path}")
            return

        task_counter = 1
        current_category = None
        category_header_id = None
        task_id_map = {}
        task_dependencies = []  # Store dependencies to create after all tasks

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            # Skip first 2 rows (empty row + title row)
            next(f)  # Skip row 1
            next(f)  # Skip row 2

            reader = csv.DictReader(f)

            for row in reader:
                # Skip empty rows
                if not row.get('Task', '').strip():
                    continue

                category = row.get('Category', '').strip()
                task_name = row.get('Task', '').strip()
                predecessor = row.get('Predecessor', '').strip()

                # Replace "DMID" with "CRO or sponsor"
                task_name = task_name.replace('DMID', 'CRO or sponsor')

                # Skip if no task name
                if not task_name:
                    continue

                # Create category header if new category
                if category and category != current_category:
                    current_category = category
                    category_header_id = f"{template_id}_HEADER_{category.upper().replace(' ', '_')}"
                    self.create_task(template_id, {
                        'task_id': category_header_id,
                        'task_name': category,
                        'task_code': category.upper().replace(' ', '_'),
                        'category': 'Study Startup',
                        'typical_duration_days': 1,
                        'is_milestone': False
                    }, task_counter)
                    task_counter += 1

                # Create task
                task_id = f"SS_{task_counter:03d}"
                self.create_task(template_id, {
                    'task_id': task_id,
                    'task_name': task_name,
                    'task_code': task_id,
                    'category': current_category or 'Study Startup',
                    'typical_duration_days': 7,  # Default duration
                    'is_milestone': False,
                    'responsible_role': row.get('Resource(s) Needed (trial type)', '').strip()
                }, task_counter, category_header_id)

                task_id_map[task_name] = task_id

                # Store dependency info for later processing
                if predecessor:
                    task_dependencies.append({
                        'task_name': task_name,
                        'task_id': task_id,
                        'predecessor': predecessor
                    })

                task_counter += 1

        print(f"  ✓ Created {task_counter - 1} tasks from CSV")

        # Create dependencies
        dependencies_created = 0
        for dep in task_dependencies:
            # Predecessor might be a milestone name like "Study Award", "KOM", "FPI", etc.
            # Try to find matching task by name
            predecessor_name = dep['predecessor']

            # Try exact match first
            if predecessor_name in task_id_map:
                self.create_dependency(template_id, task_id_map[predecessor_name], dep['task_id'])
                dependencies_created += 1
            # Try partial match (case-insensitive)
            else:
                found = False
                for task_name, pred_task_id in task_id_map.items():
                    if predecessor_name.lower() in task_name.lower():
                        self.create_dependency(template_id, pred_task_id, dep['task_id'])
                        dependencies_created += 1
                        found = True
                        break

                # If no match found, it might be a milestone from another template (like "Study Award")
                # which is external to this template - skip for now

        if dependencies_created > 0:
            print(f"  ✓ Created {dependencies_created} dependencies")

    def populate_site_activation_from_csv(self):
        """Populate Site Activation template from CSV file"""
        print("\n📋 Populating Site Activation template from CSV...")

        template_id = "TPL_004"
        self.create_template(
            template_id,
            "Site Activation",
            "site_activation",
            "Site activation checklist from site selection to site activated"
        )

        csv_path = self.db_path.parent.parent.parent / "assets" / "Study Timeline" / "Site_Activation_Checklist.csv"

        if not csv_path.exists():
            print(f"  ⚠ CSV file not found: {csv_path}")
            return

        task_counter = 1
        current_category = None
        category_header_id = None

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)

            for row in reader:
                # Skip header rows
                if not row or len(row) < 1:
                    continue

                item = row[0].strip()

                # Skip empty or header rows
                if not item or item in ['Site Activation Checklist', 'Site:', 'Item', '(Y/N or N/A)']:
                    continue

                # Replace "Emmes" with "CRO or sponsor"
                item = item.replace('Emmes', 'CRO or sponsor')
                item = item.replace('DMID', 'CRO or sponsor')

                # Check if this is a category header (usually ends with multiple spaces or is short)
                is_category = len(item) < 50 and not item.endswith('.')

                if is_category:
                    # Create category header
                    current_category = item
                    category_header_id = f"{template_id}_HEADER_{item.upper().replace(' ', '_')[:20]}"
                    self.create_task(template_id, {
                        'task_id': category_header_id,
                        'task_name': item,
                        'task_code': category_header_id,
                        'category': 'Site Activation',
                        'typical_duration_days': 1,
                        'is_milestone': False
                    }, task_counter)
                    task_counter += 1
                else:
                    # Create task item
                    task_id = f"SA_{task_counter:03d}"
                    self.create_task(template_id, {
                        'task_id': task_id,
                        'task_name': item,
                        'task_code': task_id,
                        'category': current_category or 'Site Activation',
                        'typical_duration_days': 3,  # Default duration
                        'is_milestone': False
                    }, task_counter, category_header_id)
                    task_counter += 1

        print(f"  ✓ Created {task_counter - 1} tasks from CSV")

    def update_template_task_counts(self):
        """Update template records with actual task counts"""
        print("\n📊 Updating template task counts...")

        cursor = self.conn.cursor()
        templates = cursor.execute("SELECT template_id FROM timeline_templates").fetchall()

        for (template_id,) in templates:
            # Count non-header tasks (outline_level = 2)
            count = cursor.execute("""
                SELECT COUNT(*)
                FROM template_tasks
                WHERE template_id = ? AND outline_level = 2
            """, (template_id,)).fetchone()[0]

            cursor.execute("""
                UPDATE timeline_templates
                SET total_task_count = ?
                WHERE template_id = ?
            """, (count, template_id))

        self.conn.commit()
        print("  ✓ Updated task counts")

    def run(self):
        """Execute the full migration"""
        print("=" * 80)
        print("TIMELINE TEMPLATES MIGRATION")
        print("=" * 80)

        self.connect()

        try:
            self.clear_existing_templates()
            self.populate_study_closeout()
            self.populate_site_closeout()
            self.populate_study_implementation()
            self.populate_study_startup_from_csv()
            self.populate_site_activation_from_csv()
            self.update_template_task_counts()

            print("\n" + "=" * 80)
            print("✅ MIGRATION COMPLETE")
            print("=" * 80)

            # Print summary
            cursor = self.conn.cursor()
            templates = cursor.execute("""
                SELECT template_name, total_task_count
                FROM timeline_templates
                ORDER BY template_id
            """).fetchall()

            print("\nTemplate Summary:")
            print("-" * 80)
            for name, count in templates:
                print(f"  {name}: {count} tasks")
            print("-" * 80)

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.close()


if __name__ == "__main__":
    db_path = Path(__file__).parent.parent / "database" / "feedback.db"

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        exit(1)

    migration = OntologyToTemplatesMigration(str(db_path))
    migration.run()
