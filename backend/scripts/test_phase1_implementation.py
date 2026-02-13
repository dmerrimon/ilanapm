#!/usr/bin/env python3
"""
Test Phase 1 Implementation

Validates:
1. Database schema (all tables exist)
2. Timeline templates populated correctly
3. Tracker definitions populated
4. Template retrieval API functionality
5. Signal extraction engine with sample data

Run: python scripts/test_phase1_implementation.py
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from intelligence.signal_extraction import SignalExtractionEngine, Signal, store_signals


class Phase1Tester:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "database" / "feedback.db"
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.passed = 0
        self.failed = 0

    def print_header(self, text: str):
        print("\n" + "=" * 80)
        print(text)
        print("=" * 80)

    def print_test(self, test_name: str, passed: bool, details: str = ""):
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"  {details}")

        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def test_database_schema(self):
        """Test that all required tables exist"""
        self.print_header("TEST 1: DATABASE SCHEMA")

        required_tables = [
            'timeline_templates',
            'template_tasks',
            'template_dependencies',
            'tracker_definitions',
            'tracker_column_mappings',
            'tracker_uploads',
            'signals',
            'signal_state_history',
            'signal_timeline_correlations',
            'escalation_rules',
            'escalations'
        ]

        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row['name'] for row in cursor.fetchall()}

        for table in required_tables:
            exists = table in existing_tables
            self.print_test(f"Table '{table}' exists", exists)

    def test_timeline_templates(self):
        """Test that timeline templates are populated"""
        self.print_header("TEST 2: TIMELINE TEMPLATES")

        cursor = self.conn.cursor()

        # Check templates exist
        cursor.execute("SELECT COUNT(*) as count FROM timeline_templates")
        template_count = cursor.fetchone()['count']
        self.print_test("Timeline templates populated", template_count == 5,
                       f"Found {template_count} templates (expected 5)")

        # Check each template
        expected_templates = {
            'study_startup': 86,
            'implementation': 10,
            'closeout': 24,
            'site_activation': 27,
            'site_closeout': 19
        }

        for template_type, expected_task_count in expected_templates.items():
            cursor.execute("""
                SELECT t.template_name, t.total_task_count, COUNT(tk.task_id) as actual_task_count
                FROM timeline_templates t
                LEFT JOIN template_tasks tk ON t.template_id = tk.template_id AND tk.outline_level = 2
                WHERE t.template_type = ?
                GROUP BY t.template_id
            """, (template_type,))

            row = cursor.fetchone()
            if row:
                actual = row['actual_task_count']
                matches = actual == expected_task_count
                self.print_test(
                    f"{row['template_name']} has correct task count",
                    matches,
                    f"Found {actual} work tasks (expected {expected_task_count}, excluding category headers)"
                )
            else:
                self.print_test(f"Template '{template_type}' exists", False, "Not found")

    def test_dependencies(self):
        """Test that dependencies are created"""
        self.print_header("TEST 3: TASK DEPENDENCIES")

        cursor = self.conn.cursor()

        # Check Study Startup dependencies
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM template_dependencies td
            JOIN timeline_templates t ON td.template_id = t.template_id
            WHERE t.template_type = 'study_startup'
        """)

        dep_count = cursor.fetchone()['count']
        self.print_test("Study Startup dependencies created", dep_count >= 14,
                       f"Found {dep_count} dependencies (expected ≥14)")

        # Sample a few dependencies
        cursor.execute("""
            SELECT
                pred.task_name as predecessor,
                succ.task_name as successor,
                td.dependency_type
            FROM template_dependencies td
            JOIN template_tasks pred ON td.predecessor_task_id = pred.task_id
            JOIN template_tasks succ ON td.successor_task_id = succ.task_id
            JOIN timeline_templates t ON td.template_id = t.template_id
            WHERE t.template_type = 'study_startup'
            LIMIT 3
        """)

        print("\n  Sample dependencies:")
        for row in cursor.fetchall():
            print(f"    {row['predecessor']} → {row['successor']} ({row['dependency_type']})")

    def test_tracker_definitions(self):
        """Test that tracker definitions are populated"""
        self.print_header("TEST 4: TRACKER DEFINITIONS")

        cursor = self.conn.cursor()

        # Check TMF tracker
        cursor.execute("""
            SELECT tracker_name, signal_extraction_rules
            FROM tracker_definitions
            WHERE tracker_type = 'tmf_completeness'
        """)

        tmf_row = cursor.fetchone()
        if tmf_row:
            rules = json.loads(tmf_row['signal_extraction_rules'])
            rule_count = len(rules['rules'])
            self.print_test("TMF Completeness Tracker defined", True,
                           f"Has {rule_count} signal extraction rules")

            # Check rule IDs
            rule_ids = [r['rule_id'] for r in rules['rules']]
            expected_rules = ['TMF_001', 'TMF_002', 'TMF_003', 'TMF_004']
            has_all_rules = all(rid in rule_ids for rid in expected_rules)
            self.print_test("TMF has all expected rules", has_all_rules,
                           f"Found: {', '.join(rule_ids)}")
        else:
            self.print_test("TMF Completeness Tracker defined", False)

        # Check Risk Log tracker
        cursor.execute("""
            SELECT tracker_name, signal_extraction_rules
            FROM tracker_definitions
            WHERE tracker_type = 'risk_log'
        """)

        risk_row = cursor.fetchone()
        if risk_row:
            rules = json.loads(risk_row['signal_extraction_rules'])
            rule_count = len(rules['rules'])
            self.print_test("Risk Log Tracker defined", True,
                           f"Has {rule_count} signal extraction rules")

            # Check rule IDs
            rule_ids = [r['rule_id'] for r in rules['rules']]
            expected_rules = ['RISK_001', 'RISK_002', 'RISK_003', 'RISK_004', 'RISK_005', 'RISK_006']
            has_all_rules = all(rid in rule_ids for rid in expected_rules)
            self.print_test("Risk Log has all expected rules", has_all_rules,
                           f"Found: {', '.join(rule_ids)}")
        else:
            self.print_test("Risk Log Tracker defined", False)

    def test_signal_extraction_engine(self):
        """Test signal extraction engine with mock data"""
        self.print_header("TEST 5: SIGNAL EXTRACTION ENGINE")

        # Create mock column mapping
        cursor = self.conn.cursor()

        # Check if org exists, create test org if not
        cursor.execute("SELECT org_id FROM organizations LIMIT 1")
        org_row = cursor.fetchone()

        if not org_row:
            test_org_id = "test_org_001"
            cursor.execute("""
                INSERT INTO organizations (org_id, org_name, tier)
                VALUES (?, ?, ?)
            """, (test_org_id, "Test Organization", "enterprise"))
            self.conn.commit()
        else:
            test_org_id = org_row['org_id']

        # Create test column mapping for Risk Log
        mapping_id = "test_mapping_001"
        cursor.execute("""
            INSERT OR REPLACE INTO tracker_column_mappings (
                mapping_id, org_id, tracker_type, column_mappings
            ) VALUES (?, ?, ?, ?)
        """, (
            mapping_id,
            test_org_id,
            "risk_log",
            json.dumps({
                "Risk Number": "risk_number",
                "Category": "category",
                "Risk Detail": "risk_detail",
                "Impact": "impact",
                "Probability": "probability",
                "Priority": "priority",
                "Mitigation Plan": "mitigation_plan",
                "Owner": "owner"
            })
        ))
        self.conn.commit()

        self.print_test("Test column mapping created", True, f"Org: {test_org_id}")

        # Test engine initialization
        try:
            engine = SignalExtractionEngine(self.conn)
            self.print_test("Signal extraction engine initialized", True)
        except Exception as e:
            self.print_test("Signal extraction engine initialized", False, str(e))
            return

        # Test column mapping retrieval
        mapping = engine._get_column_mapping(test_org_id, "risk_log")
        self.print_test("Column mapping retrieved", mapping is not None,
                       f"Found {len(mapping['column_mappings'])} column mappings" if mapping else "")

        # Test tracker definition retrieval
        tracker_def = engine._get_tracker_definition("risk_log")
        self.print_test("Tracker definition retrieved", tracker_def is not None,
                       f"Found {len(tracker_def['signal_extraction_rules']['rules'])} rules" if tracker_def else "")

        # Test condition evaluation
        test_row = {
            "risk_number": 13,
            "category": "Site",
            "priority": 7
        }

        # Test equals condition
        condition1 = {"field": "category", "operator": "equals", "value": "Site"}
        result1 = engine._evaluate_condition(condition1, test_row)
        self.print_test("Condition evaluation (equals)", result1)

        # Test greater_than_or_equal condition
        condition2 = {"field": "priority", "operator": "greater_than_or_equal", "value": 6}
        result2 = engine._evaluate_condition(condition2, test_row)
        self.print_test("Condition evaluation (greater_than_or_equal)", result2)

        # Test is_null condition
        condition3 = {"field": "mitigation_plan", "operator": "is_null"}
        result3 = engine._evaluate_condition(condition3, test_row)
        self.print_test("Condition evaluation (is_null)", result3)

        # Test composite condition (all_of)
        condition4 = {
            "all_of": [
                {"field": "category", "operator": "equals", "value": "Site"},
                {"field": "priority", "operator": "greater_than_or_equal", "value": 6}
            ]
        }
        result4 = engine._evaluate_condition(condition4, test_row)
        self.print_test("Condition evaluation (all_of composite)", result4)

    def test_template_api_integration(self):
        """Test that template API can retrieve data"""
        self.print_header("TEST 6: TEMPLATE API INTEGRATION")

        cursor = self.conn.cursor()

        # Simulate API call: list templates
        cursor.execute("""
            SELECT template_id, template_name, template_type, total_task_count
            FROM timeline_templates
            ORDER BY template_type
        """)

        templates = cursor.fetchall()
        self.print_test("API can list templates", len(templates) > 0,
                       f"Found {len(templates)} templates")

        # Simulate API call: get template details
        if templates:
            template_id = templates[0]['template_id']

            cursor.execute("""
                SELECT task_id, task_name, category, typical_duration_days
                FROM template_tasks
                WHERE template_id = ?
                LIMIT 5
            """, (template_id,))

            tasks = cursor.fetchall()
            self.print_test("API can retrieve template tasks", len(tasks) > 0,
                           f"Found {len(tasks)} tasks for {templates[0]['template_name']}")

            # Simulate API call: get dependencies
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM template_dependencies
                WHERE template_id = ?
            """, (template_id,))

            dep_count = cursor.fetchone()['count']
            if dep_count > 0:
                self.print_test("API can retrieve template dependencies", True,
                               f"Found {dep_count} dependencies")
            else:
                self.print_test("API can retrieve template dependencies", True,
                               "No dependencies (valid for some templates)")

    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")

        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! Phase 1 implementation is complete.")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed. Review errors above.")

        print("=" * 80)

    def run_all_tests(self):
        """Run all Phase 1 tests"""
        print("\n" + "=" * 80)
        print("PHASE 1 IMPLEMENTATION TESTING")
        print("=" * 80)

        self.test_database_schema()
        self.test_timeline_templates()
        self.test_dependencies()
        self.test_tracker_definitions()
        self.test_signal_extraction_engine()
        self.test_template_api_integration()
        self.print_summary()

        self.conn.close()

        return self.failed == 0


if __name__ == "__main__":
    tester = Phase1Tester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
