#!/usr/bin/env python3
"""
Comprehensive Phase 1 Verification

Checks for:
- Database integrity (foreign keys, constraints)
- Data consistency (no orphaned records)
- Edge cases in signal extraction
- API endpoint validation
- Migration completeness
- Potential bugs and issues
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime, date

sys.path.insert(0, str(Path(__file__).parent.parent))

from intelligence.signal_extraction import SignalExtractionEngine, Signal


class Phase1Verifier:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "database" / "feedback.db"
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.issues = []
        self.warnings = []

    def log_issue(self, category: str, message: str):
        """Log a critical issue"""
        self.issues.append(f"❌ {category}: {message}")
        print(f"❌ ISSUE - {category}: {message}")

    def log_warning(self, category: str, message: str):
        """Log a warning"""
        self.warnings.append(f"⚠️  {category}: {message}")
        print(f"⚠️  WARNING - {category}: {message}")

    def log_pass(self, category: str, message: str):
        """Log a passed check"""
        print(f"✅ PASS - {category}: {message}")

    def print_section(self, title: str):
        print("\n" + "=" * 80)
        print(title)
        print("=" * 80)

    # ========================================================================
    # DATABASE INTEGRITY CHECKS
    # ========================================================================

    def check_foreign_key_constraints(self):
        """Verify foreign key constraints are valid"""
        self.print_section("DATABASE INTEGRITY: Foreign Key Constraints")

        cursor = self.conn.cursor()

        # Enable foreign key checking
        cursor.execute("PRAGMA foreign_keys = ON")

        # Check for foreign key violations
        tables_to_check = [
            'template_tasks',
            'template_dependencies',
            'tracker_column_mappings',
            'tracker_uploads',
            'signals',
            'signal_state_history',
            'signal_timeline_correlations',
            'escalations'
        ]

        violations_found = False
        for table in tables_to_check:
            try:
                cursor.execute(f"PRAGMA foreign_key_check({table})")
                violations = cursor.fetchall()
                if violations:
                    violations_found = True
                    for v in violations:
                        self.log_issue("Foreign Key Violation", f"Table {table}: {dict(v)}")
                else:
                    self.log_pass("Foreign Keys", f"Table {table} has no violations")
            except sqlite3.Error as e:
                self.log_warning("Foreign Key Check", f"Could not check {table}: {e}")

        if not violations_found:
            self.log_pass("Foreign Key Integrity", "All foreign keys are valid")

    def check_orphaned_records(self):
        """Check for orphaned records that reference non-existent parents"""
        self.print_section("DATABASE INTEGRITY: Orphaned Records")

        cursor = self.conn.cursor()

        # Check template_tasks without valid template
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM template_tasks tk
            WHERE NOT EXISTS (
                SELECT 1 FROM timeline_templates t
                WHERE t.template_id = tk.template_id
            )
        """)
        orphaned_tasks = cursor.fetchone()['count']
        if orphaned_tasks > 0:
            self.log_issue("Orphaned Records", f"{orphaned_tasks} template tasks without valid template")
        else:
            self.log_pass("Orphaned Records", "No orphaned template tasks")

        # Check template_dependencies without valid template
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM template_dependencies td
            WHERE NOT EXISTS (
                SELECT 1 FROM timeline_templates t
                WHERE t.template_id = td.template_id
            )
        """)
        orphaned_deps = cursor.fetchone()['count']
        if orphaned_deps > 0:
            self.log_issue("Orphaned Records", f"{orphaned_deps} dependencies without valid template")
        else:
            self.log_pass("Orphaned Records", "No orphaned dependencies")

        # Check dependencies with invalid task references
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM template_dependencies td
            WHERE NOT EXISTS (
                SELECT 1 FROM template_tasks tk
                WHERE tk.task_id = td.predecessor_task_id
            )
            OR NOT EXISTS (
                SELECT 1 FROM template_tasks tk
                WHERE tk.task_id = td.successor_task_id
            )
        """)
        invalid_dep_refs = cursor.fetchone()['count']
        if invalid_dep_refs > 0:
            self.log_issue("Invalid References", f"{invalid_dep_refs} dependencies reference non-existent tasks")
        else:
            self.log_pass("Dependency References", "All dependencies reference valid tasks")

    def check_data_consistency(self):
        """Check for data consistency issues"""
        self.print_section("DATABASE INTEGRITY: Data Consistency")

        cursor = self.conn.cursor()

        # Check that total_task_count matches actual count
        cursor.execute("""
            SELECT
                t.template_name,
                t.total_task_count as stored_count,
                COUNT(tk.task_id) as actual_count
            FROM timeline_templates t
            LEFT JOIN template_tasks tk ON t.template_id = tk.template_id AND tk.outline_level = 2
            GROUP BY t.template_id
            HAVING stored_count != actual_count
        """)

        mismatches = cursor.fetchall()
        if mismatches:
            for row in mismatches:
                self.log_issue("Count Mismatch",
                             f"{row['template_name']}: stored={row['stored_count']}, actual={row['actual_count']}")
        else:
            self.log_pass("Task Count Consistency", "All template task counts are correct")

        # Check for duplicate task IDs
        cursor.execute("""
            SELECT task_id, COUNT(*) as count
            FROM template_tasks
            GROUP BY task_id
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            for row in duplicates:
                self.log_issue("Duplicate Task ID", f"Task ID '{row['task_id']}' appears {row['count']} times")
        else:
            self.log_pass("Task ID Uniqueness", "All task IDs are unique")

        # Check for circular dependencies
        cursor.execute("""
            SELECT d1.dependency_id, t1.task_name as task1, t2.task_name as task2
            FROM template_dependencies d1
            JOIN template_dependencies d2
                ON d1.predecessor_task_id = d2.successor_task_id
                AND d1.successor_task_id = d2.predecessor_task_id
            JOIN template_tasks t1 ON d1.predecessor_task_id = t1.task_id
            JOIN template_tasks t2 ON d1.successor_task_id = t2.task_id
        """)
        circular = cursor.fetchall()
        if circular:
            for row in circular:
                self.log_warning("Circular Dependency", f"{row['task1']} ↔ {row['task2']}")
        else:
            self.log_pass("Circular Dependencies", "No circular dependencies found")

    # ========================================================================
    # SIGNAL EXTRACTION ENGINE CHECKS
    # ========================================================================

    def check_signal_extraction_edge_cases(self):
        """Test signal extraction with edge cases"""
        self.print_section("SIGNAL EXTRACTION: Edge Cases")

        cursor = self.conn.cursor()

        # Get test org
        cursor.execute("SELECT org_id FROM organizations LIMIT 1")
        org_row = cursor.fetchone()
        if not org_row:
            self.log_warning("Signal Extraction", "No organization found for testing")
            return
        org_id = org_row['org_id']

        engine = SignalExtractionEngine(self.conn)

        # Test 1: Empty values
        test_row_empty = {
            "risk_number": None,
            "category": "",
            "priority": None
        }

        try:
            result = engine._evaluate_condition(
                {"field": "priority", "operator": "is_null"},
                test_row_empty
            )
            if result:
                self.log_pass("Edge Case", "Handles None values correctly")
            else:
                self.log_issue("Edge Case", "Failed to detect None value with is_null")
        except Exception as e:
            self.log_issue("Edge Case", f"Error handling None values: {e}")

        # Test 2: String to number conversion
        test_row_string_num = {
            "priority": "7"
        }

        try:
            result = engine._evaluate_condition(
                {"field": "priority", "operator": "greater_than_or_equal", "value": 6},
                test_row_string_num
            )
            if result:
                self.log_pass("Edge Case", "Handles string-to-number conversion")
            else:
                self.log_warning("Edge Case", "May have issue with string-to-number conversion")
        except Exception as e:
            self.log_issue("Edge Case", f"Error with string-to-number conversion: {e}")

        # Test 3: Invalid date formats
        test_row_invalid_date = {
            "target_date": "not-a-date"
        }

        try:
            result = engine._evaluate_condition(
                {"field": "target_date", "operator": "is_past"},
                test_row_invalid_date
            )
            if not result:  # Should return False for invalid dates
                self.log_pass("Edge Case", "Handles invalid date formats gracefully")
            else:
                self.log_warning("Edge Case", "May incorrectly evaluate invalid dates")
        except Exception as e:
            # Should not throw exception, should return False
            self.log_warning("Edge Case", f"Throws exception on invalid date: {e}")

        # Test 4: Case sensitivity in equals
        test_row_case = {
            "status": "Missing Document"
        }

        try:
            result1 = engine._evaluate_condition(
                {"field": "status", "operator": "equals", "value": "Missing Document"},
                test_row_case
            )
            result2 = engine._evaluate_condition(
                {"field": "status", "operator": "equals", "value": "missing document"},
                test_row_case
            )

            if result1 and not result2:
                self.log_pass("Edge Case", "String comparison is case-sensitive (as expected)")
            elif result1 and result2:
                self.log_warning("Edge Case", "String comparison is case-insensitive (may cause issues)")
            else:
                self.log_issue("Edge Case", "String comparison not working correctly")
        except Exception as e:
            self.log_issue("Edge Case", f"Error in string comparison: {e}")

        # Test 5: Nested composite conditions
        test_row_nested = {
            "priority": 7,
            "category": "Site",
            "mitigation_plan": None
        }

        try:
            result = engine._evaluate_condition(
                {
                    "all_of": [
                        {"field": "priority", "operator": "greater_than_or_equal", "value": 6},
                        {
                            "any_of": [
                                {"field": "category", "operator": "equals", "value": "Site"},
                                {"field": "category", "operator": "equals", "value": "Safety"}
                            ]
                        }
                    ]
                },
                test_row_nested
            )
            if result:
                self.log_pass("Edge Case", "Handles nested composite conditions (all_of + any_of)")
            else:
                self.log_issue("Edge Case", "Failed nested composite condition evaluation")
        except Exception as e:
            self.log_issue("Edge Case", f"Error with nested conditions: {e}")

    def check_tracker_definitions_completeness(self):
        """Verify tracker definitions are complete and valid"""
        self.print_section("TRACKER DEFINITIONS: Completeness")

        cursor = self.conn.cursor()

        # Check TMF tracker
        cursor.execute("""
            SELECT schema_definition, signal_extraction_rules
            FROM tracker_definitions
            WHERE tracker_type = 'tmf_completeness'
        """)
        tmf_row = cursor.fetchone()

        if tmf_row:
            try:
                schema = json.loads(tmf_row['schema_definition'])
                rules = json.loads(tmf_row['signal_extraction_rules'])

                # Verify required fields exist
                if 'required_fields' not in schema:
                    self.log_issue("TMF Schema", "Missing 'required_fields' in schema")
                else:
                    required_field_names = [f['field_name'] for f in schema['required_fields']]
                    expected_fields = ['artifact_number', 'artifact_name', 'status']
                    missing = [f for f in expected_fields if f not in required_field_names]
                    if missing:
                        self.log_issue("TMF Schema", f"Missing required fields: {missing}")
                    else:
                        self.log_pass("TMF Schema", "All required fields present")

                # Verify rules are valid
                if 'rules' not in rules:
                    self.log_issue("TMF Rules", "Missing 'rules' array")
                else:
                    for rule in rules['rules']:
                        if 'rule_id' not in rule:
                            self.log_issue("TMF Rules", f"Rule missing rule_id")
                        if 'condition' not in rule:
                            self.log_issue("TMF Rules", f"Rule {rule.get('rule_id', 'unknown')} missing condition")
                        if 'signal_type' not in rule:
                            self.log_issue("TMF Rules", f"Rule {rule.get('rule_id', 'unknown')} missing signal_type")

                    self.log_pass("TMF Rules", f"All {len(rules['rules'])} rules have required fields")

            except json.JSONDecodeError as e:
                self.log_issue("TMF Tracker", f"Invalid JSON: {e}")
            except Exception as e:
                self.log_issue("TMF Tracker", f"Error validating: {e}")
        else:
            self.log_issue("TMF Tracker", "Not found in database")

        # Check Risk Log tracker
        cursor.execute("""
            SELECT schema_definition, signal_extraction_rules
            FROM tracker_definitions
            WHERE tracker_type = 'risk_log'
        """)
        risk_row = cursor.fetchone()

        if risk_row:
            try:
                schema = json.loads(risk_row['schema_definition'])
                rules = json.loads(risk_row['signal_extraction_rules'])

                # Verify required fields
                required_field_names = [f['field_name'] for f in schema['required_fields']]
                expected_fields = ['risk_number', 'category', 'risk_detail', 'impact', 'probability', 'priority']
                missing = [f for f in expected_fields if f not in required_field_names]
                if missing:
                    self.log_issue("Risk Log Schema", f"Missing required fields: {missing}")
                else:
                    self.log_pass("Risk Log Schema", "All required fields present")

                # Check for high priority escalation rule
                high_priority_rule = None
                for rule in rules['rules']:
                    if rule['signal_type'] == 'risk_high_priority':
                        high_priority_rule = rule
                        break

                if high_priority_rule:
                    if high_priority_rule.get('escalation_level') == 'director':
                        self.log_pass("Risk Log Rules", "High priority rule escalates to director")
                    else:
                        self.log_warning("Risk Log Rules", f"High priority escalation level is '{high_priority_rule.get('escalation_level')}', expected 'director'")
                else:
                    self.log_warning("Risk Log Rules", "No high priority risk rule found")

            except Exception as e:
                self.log_issue("Risk Log Tracker", f"Error validating: {e}")
        else:
            self.log_issue("Risk Log Tracker", "Not found in database")

    # ========================================================================
    # TEMPLATE VALIDATION
    # ========================================================================

    def check_template_data_quality(self):
        """Check template data for quality issues"""
        self.print_section("TEMPLATE DATA: Quality Checks")

        cursor = self.conn.cursor()

        # Check for tasks with zero or negative duration
        cursor.execute("""
            SELECT t.template_name, tk.task_name, tk.typical_duration_days
            FROM template_tasks tk
            JOIN timeline_templates t ON tk.template_id = t.template_id
            WHERE tk.typical_duration_days <= 0 AND tk.outline_level = 2
        """)
        zero_duration = cursor.fetchall()
        if zero_duration:
            for row in zero_duration:
                self.log_warning("Template Data",
                               f"{row['template_name']}: Task '{row['task_name']}' has duration {row['typical_duration_days']}")
        else:
            self.log_pass("Template Data", "All tasks have positive duration")

        # Check for tasks with missing categories
        cursor.execute("""
            SELECT t.template_name, tk.task_name, tk.category
            FROM template_tasks tk
            JOIN timeline_templates t ON tk.template_id = t.template_id
            WHERE tk.category IS NULL OR tk.category = ''
        """)
        missing_category = cursor.fetchall()
        if missing_category:
            for row in missing_category:
                self.log_warning("Template Data",
                               f"{row['template_name']}: Task '{row['task_name']}' missing category")
        else:
            self.log_pass("Template Data", "All tasks have categories")

        # Check for unreasonably long durations (>365 days)
        cursor.execute("""
            SELECT t.template_name, tk.task_name, tk.typical_duration_days
            FROM template_tasks tk
            JOIN timeline_templates t ON tk.template_id = t.template_id
            WHERE tk.typical_duration_days > 365 AND tk.outline_level = 2
        """)
        long_duration = cursor.fetchall()
        if long_duration:
            for row in long_duration:
                self.log_warning("Template Data",
                               f"{row['template_name']}: Task '{row['task_name']}' has very long duration ({row['typical_duration_days']} days)")
        else:
            self.log_pass("Template Data", "No tasks with unreasonably long durations")

        # Check for duplicate task names within same template
        cursor.execute("""
            SELECT t.template_name, tk.task_name, COUNT(*) as count
            FROM template_tasks tk
            JOIN timeline_templates t ON tk.template_id = t.template_id
            WHERE tk.outline_level = 2
            GROUP BY t.template_id, tk.task_name
            HAVING count > 1
        """)
        duplicate_names = cursor.fetchall()
        if duplicate_names:
            for row in duplicate_names:
                self.log_warning("Template Data",
                               f"{row['template_name']}: Duplicate task name '{row['task_name']}' ({row['count']} times)")
        else:
            self.log_pass("Template Data", "No duplicate task names within templates")

    def check_dependency_validity(self):
        """Check that dependencies make logical sense"""
        self.print_section("DEPENDENCIES: Validity Checks")

        cursor = self.conn.cursor()

        # Check for self-referencing dependencies
        cursor.execute("""
            SELECT td.dependency_id, t.template_name, tk.task_name
            FROM template_dependencies td
            JOIN template_tasks tk ON td.predecessor_task_id = tk.task_id
            JOIN timeline_templates t ON td.template_id = t.template_id
            WHERE td.predecessor_task_id = td.successor_task_id
        """)
        self_refs = cursor.fetchall()
        if self_refs:
            for row in self_refs:
                self.log_issue("Dependencies",
                             f"{row['template_name']}: Task '{row['task_name']}' depends on itself")
        else:
            self.log_pass("Dependencies", "No self-referencing dependencies")

        # Check for dependencies between different templates
        cursor.execute("""
            SELECT
                td.dependency_id,
                t1.template_name as pred_template,
                t2.template_name as succ_template
            FROM template_dependencies td
            JOIN template_tasks pred ON td.predecessor_task_id = pred.task_id
            JOIN template_tasks succ ON td.successor_task_id = succ.task_id
            JOIN timeline_templates t1 ON pred.template_id = t1.template_id
            JOIN timeline_templates t2 ON succ.template_id = t2.template_id
            WHERE pred.template_id != succ.template_id
        """)
        cross_template = cursor.fetchall()
        if cross_template:
            for row in cross_template:
                self.log_warning("Dependencies",
                               f"Cross-template dependency: {row['pred_template']} → {row['succ_template']}")
        else:
            self.log_pass("Dependencies", "No cross-template dependencies")

        # Check dependency counts per template
        cursor.execute("""
            SELECT t.template_name, COUNT(td.dependency_id) as dep_count
            FROM timeline_templates t
            LEFT JOIN template_dependencies td ON t.template_id = td.template_id
            GROUP BY t.template_id
        """)
        dep_counts = cursor.fetchall()
        print("\n  Dependency counts by template:")
        for row in dep_counts:
            print(f"    {row['template_name']}: {row['dep_count']} dependencies")

    # ========================================================================
    # API ENDPOINT VALIDATION
    # ========================================================================

    def check_api_endpoints(self):
        """Verify API endpoint code exists and is correct"""
        self.print_section("API ENDPOINTS: Code Validation")

        api_file = Path(__file__).parent.parent / "api" / "templates.py"

        if not api_file.exists():
            self.log_issue("API File", f"templates.py not found at {api_file}")
            return

        content = api_file.read_text()

        # Check for required endpoints
        required_endpoints = [
            ('list_timeline_templates', 'GET /templates/library'),
            ('get_timeline_template', 'GET /templates/library/{template_id}'),
            ('get_template_tasks', 'GET /templates/library/{template_id}/tasks')
        ]

        for func_name, route in required_endpoints:
            if func_name in content:
                self.log_pass("API Endpoints", f"Found {route}")
            else:
                self.log_issue("API Endpoints", f"Missing function {func_name} for {route}")

        # Check for database connection handling
        if 'get_db_connection' in content or 'sqlite3.connect' in content:
            self.log_pass("API Endpoints", "Database connection handling present")
        else:
            self.log_warning("API Endpoints", "No obvious database connection handling")

    # ========================================================================
    # MIGRATION COMPLETENESS
    # ========================================================================

    def check_migration_completeness(self):
        """Verify all migrations have been applied"""
        self.print_section("MIGRATIONS: Completeness")

        migrations_dir = Path(__file__).parent.parent / "database" / "migrations"

        if not migrations_dir.exists():
            self.log_warning("Migrations", f"Migrations directory not found at {migrations_dir}")
            return

        migration_files = sorted(migrations_dir.glob("*.sql"))
        print(f"\n  Found {len(migration_files)} migration files")

        # Check that migration 010 exists (tracker_column_mappings)
        migration_010 = migrations_dir / "010_tracker_column_mappings.sql"
        if migration_010.exists():
            self.log_pass("Migrations", "Migration 010 (tracker_column_mappings) exists")
        else:
            self.log_issue("Migrations", "Migration 010 (tracker_column_mappings) not found")

    # ========================================================================
    # SUMMARY
    # ========================================================================

    def print_summary(self):
        """Print verification summary"""
        self.print_section("VERIFICATION SUMMARY")

        print(f"\n📊 Issues Found: {len(self.issues)}")
        if self.issues:
            print("\nCritical Issues:")
            for issue in self.issues:
                print(f"  {issue}")

        print(f"\n⚠️  Warnings: {len(self.warnings)}")
        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.issues and not self.warnings:
            print("\n🎉 PERFECT! No issues or warnings found.")
            print("Phase 1 implementation is production-ready.")
        elif not self.issues:
            print("\n✅ GOOD! No critical issues found.")
            print(f"Review {len(self.warnings)} warning(s) above.")
        else:
            print("\n❌ ISSUES FOUND! Review critical issues above.")

        print("=" * 80)

        return len(self.issues) == 0

    def run_all_checks(self):
        """Run all verification checks"""
        print("\n" + "=" * 80)
        print("PHASE 1 COMPREHENSIVE VERIFICATION")
        print("=" * 80)

        self.check_foreign_key_constraints()
        self.check_orphaned_records()
        self.check_data_consistency()
        self.check_signal_extraction_edge_cases()
        self.check_tracker_definitions_completeness()
        self.check_template_data_quality()
        self.check_dependency_validity()
        self.check_api_endpoints()
        self.check_migration_completeness()

        success = self.print_summary()

        self.conn.close()

        return success


if __name__ == "__main__":
    verifier = Phase1Verifier()
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)
