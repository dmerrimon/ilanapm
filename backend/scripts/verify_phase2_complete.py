#!/usr/bin/env python3
"""
Comprehensive Phase 2 Verification

Verifies that ALL claimed work is actually complete:
- All files exist
- All code compiles
- All database tables exist
- All data is populated
- All integrations work
- No bugs or errors
"""

import sqlite3
import json
import sys
import os
from pathlib import Path
from datetime import datetime, date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))


class Phase2Verifier:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "database" / "feedback.db"
        self.backend_path = Path(__file__).parent.parent
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.issues = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_failed = 0

    def log_issue(self, category: str, message: str):
        """Log a critical issue"""
        self.issues.append(f"❌ {category}: {message}")
        print(f"❌ ISSUE - {category}: {message}")
        self.checks_failed += 1

    def log_warning(self, category: str, message: str):
        """Log a warning"""
        self.warnings.append(f"⚠️  {category}: {message}")
        print(f"⚠️  WARNING - {category}: {message}")

    def log_pass(self, category: str, message: str):
        """Log a passed check"""
        print(f"✅ PASS - {category}: {message}")
        self.checks_passed += 1

    def print_section(self, title: str):
        print("\n" + "=" * 80)
        print(title)
        print("=" * 80)

    # ========================================================================
    # FILE EXISTENCE CHECKS
    # ========================================================================

    def verify_files_exist(self):
        """Verify all claimed files actually exist"""
        self.print_section("FILE EXISTENCE: Verify All Claimed Files")

        required_files = {
            'intelligence/correlation_engine.py': 'Correlation Engine',
            'intelligence/pattern_detection.py': 'Pattern Detection',
            'intelligence/health_score.py': 'Health Score Calculator',
            'intelligence/escalation_engine.py': 'Escalation Engine',
            'scripts/populate_correlation_rules.py': 'Correlation Rules Population Script',
            'scripts/test_phase2_implementation.py': 'Phase 2 Test Suite',
            'database/migrations/011_correlation_rules.sql': 'Migration 011',
            'PHASE2_COMPLETION_REPORT.md': 'Phase 2 Completion Report'
        }

        for file_path, description in required_files.items():
            full_path = self.backend_path / file_path
            if full_path.exists():
                # Check file size
                size = full_path.stat().st_size
                if size > 0:
                    self.log_pass("File Exists", f"{description}: {file_path} ({size} bytes)")
                else:
                    self.log_issue("Empty File", f"{description}: {file_path} is empty")
            else:
                self.log_issue("Missing File", f"{description}: {file_path} NOT FOUND")

    # ========================================================================
    # CODE COMPILATION CHECKS
    # ========================================================================

    def verify_code_compiles(self):
        """Verify all Python files compile without syntax errors"""
        self.print_section("CODE COMPILATION: Verify No Syntax Errors")

        python_files = [
            'intelligence/correlation_engine.py',
            'intelligence/pattern_detection.py',
            'intelligence/health_score.py',
            'intelligence/escalation_engine.py',
            'scripts/populate_correlation_rules.py',
            'scripts/test_phase2_implementation.py'
        ]

        for file_path in python_files:
            full_path = self.backend_path / file_path
            if not full_path.exists():
                self.log_issue("Compilation", f"{file_path} does not exist")
                continue

            try:
                with open(full_path, 'r') as f:
                    code = f.read()
                compile(code, str(full_path), 'exec')
                self.log_pass("Compilation", f"{file_path} compiles successfully")
            except SyntaxError as e:
                self.log_issue("Syntax Error", f"{file_path}: Line {e.lineno}: {e.msg}")
            except Exception as e:
                self.log_issue("Compilation", f"{file_path}: {str(e)}")

    # ========================================================================
    # IMPORTS CHECK
    # ========================================================================

    def verify_imports_work(self):
        """Verify all modules can be imported"""
        self.print_section("IMPORTS: Verify All Modules Import Successfully")

        modules_to_import = [
            ('intelligence.correlation_engine', 'CorrelationEngine'),
            ('intelligence.pattern_detection', 'PatternDetector'),
            ('intelligence.health_score', 'HealthScoreCalculator'),
            ('intelligence.escalation_engine', 'EscalationEngine')
        ]

        for module_name, class_name in modules_to_import:
            try:
                module = __import__(module_name, fromlist=[class_name])
                cls = getattr(module, class_name)
                self.log_pass("Import", f"Successfully imported {class_name} from {module_name}")
            except ImportError as e:
                self.log_issue("Import Error", f"Cannot import {class_name} from {module_name}: {e}")
            except AttributeError as e:
                self.log_issue("Class Not Found", f"{class_name} not found in {module_name}: {e}")
            except Exception as e:
                self.log_issue("Import", f"Error importing {module_name}: {e}")

    # ========================================================================
    # DATABASE CHECKS
    # ========================================================================

    def verify_database_tables(self):
        """Verify correlation_rules table exists"""
        self.print_section("DATABASE: Verify Tables and Schema")

        cursor = self.conn.cursor()

        # Check correlation_rules table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='correlation_rules'
        """)
        if cursor.fetchone():
            self.log_pass("Database", "correlation_rules table exists")

            # Check schema
            cursor.execute("PRAGMA table_info(correlation_rules)")
            columns = {row['name'] for row in cursor.fetchall()}

            required_columns = {
                'rule_id', 'rule_name', 'signal_type', 'signal_category',
                'signal_detail_pattern', 'affected_milestones', 'affected_milestone_codes',
                'correlation_type', 'confidence_score', 'impact_type',
                'delay_estimation_logic', 'escalation_trigger', 'escalation_level',
                'reasoning_template', 'is_active'
            }

            missing_columns = required_columns - columns
            if missing_columns:
                self.log_issue("Schema", f"correlation_rules missing columns: {missing_columns}")
            else:
                self.log_pass("Schema", "correlation_rules has all required columns")

        else:
            self.log_issue("Database", "correlation_rules table NOT FOUND")

        # Check indexes
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND tbl_name='correlation_rules'
        """)
        indexes = [row['name'] for row in cursor.fetchall()]

        expected_indexes = [
            'idx_correlation_rules_signal_type',
            'idx_correlation_rules_signal_category',
            'idx_correlation_rules_correlation_type',
            'idx_correlation_rules_escalation'
        ]

        for idx in expected_indexes:
            if idx in indexes:
                self.log_pass("Indexes", f"Index {idx} exists")
            else:
                self.log_warning("Indexes", f"Index {idx} missing (performance impact)")

    def verify_correlation_rules_populated(self):
        """Verify correlation rules are actually in database"""
        self.print_section("DATA POPULATION: Verify Correlation Rules")

        cursor = self.conn.cursor()

        # Count total rules
        cursor.execute("SELECT COUNT(*) as count FROM correlation_rules WHERE is_active = 1")
        count = cursor.fetchone()['count']

        if count >= 6:
            self.log_pass("Data Population", f"Found {count} active correlation rules (expected ≥6)")
        else:
            self.log_issue("Data Population", f"Only {count} rules found (expected ≥6)")

        # Verify specific rules
        expected_rules = [
            ('risk_high_priority', 'Site', 'director', 'High Priority Risk → Site Activation'),
            ('risk_high_priority', 'Clinical', 'director', 'Enrollment Risk'),
            ('site_closeout_blocker', None, 'director', 'Site Closeout'),
            ('tmf_completeness_risk', None, 'director', 'TMF Completeness'),
            ('risk_high_priority', 'Safety', 'vp', 'Safety/Toxicity'),
            ('budget_overrun', None, 'director', 'Budget Overrun')
        ]

        for signal_type, category, esc_level, name_fragment in expected_rules:
            if category:
                cursor.execute("""
                    SELECT rule_id, rule_name FROM correlation_rules
                    WHERE signal_type = ? AND signal_category = ? AND escalation_level = ? AND is_active = 1
                """, (signal_type, category, esc_level))
            else:
                cursor.execute("""
                    SELECT rule_id, rule_name FROM correlation_rules
                    WHERE signal_type = ? AND escalation_level = ? AND is_active = 1
                """, (signal_type, esc_level))

            rule = cursor.fetchone()
            if rule:
                self.log_pass("Rule Exists", f"{rule['rule_name']}")
            else:
                self.log_issue("Missing Rule", f"Rule for {signal_type} ({category or 'any'}) → {esc_level} not found")

        # Verify VP escalation exists
        cursor.execute("""
            SELECT COUNT(*) as count FROM correlation_rules
            WHERE escalation_level = 'vp' AND is_active = 1
        """)
        vp_count = cursor.fetchone()['count']
        if vp_count > 0:
            self.log_pass("VP Rules", f"Found {vp_count} VP escalation rule(s)")
        else:
            self.log_issue("VP Rules", "No VP escalation rules found")

        # Verify blocker type exists
        cursor.execute("""
            SELECT COUNT(*) as count FROM correlation_rules
            WHERE correlation_type = 'blocker' AND is_active = 1
        """)
        blocker_count = cursor.fetchone()['count']
        if blocker_count > 0:
            self.log_pass("Blocker Rules", f"Found {blocker_count} blocker correlation rule(s)")
        else:
            self.log_issue("Blocker Rules", "No blocker correlation rules found")

    # ========================================================================
    # FUNCTIONAL TESTS
    # ========================================================================

    def verify_correlation_engine_works(self):
        """Verify correlation engine actually works"""
        self.print_section("FUNCTIONAL TEST: Correlation Engine")

        try:
            from intelligence.correlation_engine import CorrelationEngine

            engine = CorrelationEngine(self.conn)

            # Create test signal (with keywords that match the rule)
            test_signal = {
                'signal_id': 'verify_test_001',
                'signal_type': 'risk_high_priority',
                'signal_category': 'Site',
                'signal_description': 'Site activation slower than anticipated',
                'signal_detail': json.dumps({'risk_number': 1}),
                'priority': 7,
                'status': 'open'
            }

            # Create test timeline
            test_timeline = {
                'milestones': [
                    {
                        'milestone_name': 'Site Activation',
                        'milestone_code': 'SITE_ACT',
                        'task_id': 'verify_task_001',
                        'planned_date': '2026-06-15',
                        'is_critical_path': True
                    }
                ]
            }

            # Test: Find matching rules
            matching_rules = engine._find_matching_rules(test_signal)
            if len(matching_rules) > 0:
                self.log_pass("Correlation Engine", f"Finds matching rules ({len(matching_rules)} found)")
            else:
                self.log_issue("Correlation Engine", "Cannot find matching rules for test signal")

            # Test: Find milestones
            if matching_rules:
                milestones = engine._find_milestones_in_timeline(test_timeline, matching_rules[0])
                if len(milestones) > 0:
                    self.log_pass("Correlation Engine", f"Finds affected milestones ({len(milestones)} found)")
                else:
                    self.log_issue("Correlation Engine", "Cannot find affected milestones")

            # Test: Calculate delay
            if matching_rules:
                delay = engine._estimate_delay(test_signal, matching_rules[0])
                if delay > 0:
                    self.log_pass("Correlation Engine", f"Calculates delay ({delay} days)")
                else:
                    self.log_warning("Correlation Engine", "Delay calculation returned 0")

            # Test: Full correlation
            correlations = engine.correlate_signals([test_signal], test_timeline, 'verify_project')
            if len(correlations) > 0:
                self.log_pass("Correlation Engine", f"Creates correlations ({len(correlations)} created)")

                # Check correlation has required fields
                corr = correlations[0]
                if corr.correlation_reasoning and len(corr.correlation_reasoning) > 0:
                    self.log_pass("Correlation Engine", "Generates reasoning")
                else:
                    self.log_issue("Correlation Engine", "Reasoning is empty")

            else:
                self.log_issue("Correlation Engine", "Failed to create correlations")

        except Exception as e:
            self.log_issue("Correlation Engine", f"Runtime error: {str(e)}")

    def verify_pattern_detection_works(self):
        """Verify pattern detection actually works"""
        self.print_section("FUNCTIONAL TEST: Pattern Detection")

        try:
            from intelligence.pattern_detection import PatternDetector

            detector = PatternDetector(self.conn)

            # Test: Signal clustering
            test_signals = [
                {'signal_id': 'p1', 'signal_category': 'Site', 'priority': 7, 'status': 'open', 'signal_type': 'risk_high_priority', 'signal_description': 'Test', 'signal_detail': '{}'},
                {'signal_id': 'p2', 'signal_category': 'Site', 'priority': 6, 'status': 'open', 'signal_type': 'risk_high_priority', 'signal_description': 'Test', 'signal_detail': '{}'},
                {'signal_id': 'p3', 'signal_category': 'Site', 'priority': 8, 'status': 'open', 'signal_type': 'risk_high_priority', 'signal_description': 'Test', 'signal_detail': '{}'},
            ]

            patterns = detector._detect_signal_clustering(test_signals)
            if len(patterns) > 0:
                self.log_pass("Pattern Detection", f"Detects signal clustering ({len(patterns)} patterns)")
            else:
                self.log_warning("Pattern Detection", "No clustering detected (may be threshold issue)")

            # Test: Overdue signals
            test_signals_overdue = [
                {'signal_id': 'o1', 'status': 'open', 'target_date': (date.today() - timedelta(days=30)).isoformat(), 'signal_type': 'risk_high_priority', 'signal_description': 'Test', 'signal_detail': '{}', 'priority': 6},
                {'signal_id': 'o2', 'status': 'open', 'target_date': (date.today() - timedelta(days=15)).isoformat(), 'signal_type': 'risk_high_priority', 'signal_description': 'Test', 'signal_detail': '{}', 'priority': 6},
            ]

            patterns_overdue = detector._detect_overdue_signals(test_signals_overdue)
            if len(patterns_overdue) > 0:
                self.log_pass("Pattern Detection", f"Detects overdue signals ({len(patterns_overdue)} patterns)")
            else:
                self.log_issue("Pattern Detection", "Cannot detect overdue signals")

        except Exception as e:
            self.log_issue("Pattern Detection", f"Runtime error: {str(e)}")

    def verify_health_score_works(self):
        """Verify health score calculator actually works"""
        self.print_section("FUNCTIONAL TEST: Health Score Calculator")

        try:
            from intelligence.health_score import HealthScoreCalculator

            calculator = HealthScoreCalculator(self.conn)

            # Test with high risk signals
            test_signals = [
                {'signal_id': 'h1', 'signal_type': 'risk_high_priority', 'priority': 9, 'status': 'open', 'signal_detail': '{}', 'signal_category': 'Clinical', 'signal_description': 'Test'},
                {'signal_id': 'h2', 'signal_type': 'risk_high_priority', 'priority': 7, 'status': 'open', 'signal_detail': '{}', 'signal_category': 'Site', 'signal_description': 'Test'},
            ]

            health_score = calculator.calculate_health_score(
                'verify_project',
                test_signals,
                [],
                None
            )

            # Check overall score
            if 0 <= health_score.overall_score <= 100:
                self.log_pass("Health Score", f"Calculates overall score: {health_score.overall_score}")
            else:
                self.log_issue("Health Score", f"Overall score out of range: {health_score.overall_score}")

            # Check health status
            if health_score.health_status in ['healthy', 'warning', 'critical']:
                self.log_pass("Health Score", f"Determines health status: {health_score.health_status}")
            else:
                self.log_issue("Health Score", f"Invalid health status: {health_score.health_status}")

            # Check component scores
            if health_score.risk_score is not None:
                self.log_pass("Health Score", f"Calculates risk score: {health_score.risk_score}")
            else:
                self.log_issue("Health Score", "Risk score is None")

            # Check recommendations
            if len(health_score.recommended_actions) > 0:
                self.log_pass("Health Score", f"Generates {len(health_score.recommended_actions)} recommendation(s)")
            else:
                self.log_warning("Health Score", "No recommendations generated")

        except Exception as e:
            self.log_issue("Health Score", f"Runtime error: {str(e)}")

    def verify_escalation_engine_works(self):
        """Verify escalation engine actually works"""
        self.print_section("FUNCTIONAL TEST: Escalation Engine")

        try:
            from intelligence.escalation_engine import EscalationEngine

            engine = EscalationEngine(self.conn)

            # Test Director escalation
            test_signal_director = {
                'signal_id': 'e_dir',
                'signal_type': 'risk_high_priority',
                'signal_category': 'Site',
                'signal_description': 'Director test',
                'signal_detail': '{}',
                'priority': 7,
                'status': 'open'
            }

            director_check = engine._check_director_escalation(test_signal_director, [], {})
            if director_check:
                self.log_pass("Escalation Engine", "Detects Director escalation (Priority ≥6)")
            else:
                self.log_issue("Escalation Engine", "Failed to detect Director escalation for Priority 7")

            # Test VP escalation
            test_signal_vp = {
                'signal_id': 'e_vp',
                'signal_type': 'risk_critical',
                'signal_category': 'Clinical',
                'signal_description': 'VP test',
                'signal_detail': '{}',
                'priority': 9,
                'status': 'open'
            }

            vp_check = engine._check_vp_escalation(test_signal_vp, [], [], {})
            if vp_check:
                self.log_pass("Escalation Engine", "Detects VP escalation (Priority = 9)")
            else:
                self.log_issue("Escalation Engine", "Failed to detect VP escalation for Priority 9")

            # Test Safety VP escalation
            test_signal_safety = {
                'signal_id': 'e_safety',
                'signal_type': 'risk_high_priority',
                'signal_category': 'Safety',
                'signal_description': 'Safety test',
                'signal_detail': '{}',
                'priority': 7,
                'status': 'open'
            }

            safety_check = engine._check_vp_escalation(test_signal_safety, [], [], {})
            if safety_check:
                self.log_pass("Escalation Engine", "Detects VP escalation for Safety risks")
            else:
                self.log_issue("Escalation Engine", "Failed to detect VP escalation for Safety")

            # Test full escalation evaluation
            escalations = engine.evaluate_escalations(
                'verify_org',
                'verify_project',
                [test_signal_director, test_signal_vp, test_signal_safety],
                [],
                [],
                {}
            )

            if len(escalations) > 0:
                self.log_pass("Escalation Engine", f"Creates escalations ({len(escalations)} created)")

                # Check escalation levels
                director_count = sum(1 for e in escalations if e.escalation_level == 'director')
                vp_count = sum(1 for e in escalations if e.escalation_level == 'vp')

                if director_count > 0 and vp_count > 0:
                    self.log_pass("Escalation Engine", f"Assigns correct levels (Director: {director_count}, VP: {vp_count})")
                else:
                    self.log_warning("Escalation Engine", f"Unexpected level distribution (Director: {director_count}, VP: {vp_count})")

                # Check interventions
                has_interventions = all(len(e.intervention_recommended) > 0 for e in escalations)
                if has_interventions:
                    self.log_pass("Escalation Engine", "All escalations have interventions")
                else:
                    self.log_issue("Escalation Engine", "Some escalations missing interventions")

            else:
                self.log_issue("Escalation Engine", "Failed to create escalations")

        except Exception as e:
            self.log_issue("Escalation Engine", f"Runtime error: {str(e)}")

    # ========================================================================
    # RUN TEST SUITE
    # ========================================================================

    def verify_test_suite_passes(self):
        """Verify the test suite actually passes"""
        self.print_section("TEST SUITE: Run Phase 2 Tests")

        test_script = self.backend_path / "scripts" / "test_phase2_implementation.py"

        if not test_script.exists():
            self.log_issue("Test Suite", "test_phase2_implementation.py not found")
            return

        try:
            # Import and run the test suite
            import subprocess
            result = subprocess.run(
                ['python3', str(test_script)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.backend_path)
            )

            if result.returncode == 0:
                self.log_pass("Test Suite", "Phase 2 test suite passes (exit code 0)")

                # Check output for pass confirmation
                if "ALL TESTS PASSED" in result.stdout:
                    self.log_pass("Test Suite", "All tests confirmed passed")
                if "Pass Rate: 100.0%" in result.stdout:
                    self.log_pass("Test Suite", "100% pass rate confirmed")
            else:
                self.log_issue("Test Suite", f"Test suite failed (exit code {result.returncode})")
                print("\nTest output:")
                print(result.stdout[-1000:])  # Last 1000 chars

        except subprocess.TimeoutExpired:
            self.log_issue("Test Suite", "Test suite timed out after 60 seconds")
        except Exception as e:
            self.log_issue("Test Suite", f"Error running test suite: {str(e)}")

    # ========================================================================
    # SUMMARY
    # ========================================================================

    def print_summary(self):
        """Print verification summary"""
        self.print_section("VERIFICATION SUMMARY")

        total = self.checks_passed + self.checks_failed
        pass_rate = (self.checks_passed / total * 100) if total > 0 else 0

        print(f"\n📊 Checks Passed: {self.checks_passed}")
        print(f"❌ Checks Failed: {self.checks_failed}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"Pass Rate: {pass_rate:.1f}%")

        if self.checks_failed > 0:
            print("\n❌ CRITICAL ISSUES FOUND:")
            for issue in self.issues:
                print(f"  {issue}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.checks_failed == 0 and len(self.warnings) == 0:
            print("\n🎉 PERFECT! All verification checks passed.")
            print("Phase 2 implementation is verified and production-ready.")
        elif self.checks_failed == 0:
            print("\n✅ VERIFIED! All critical checks passed.")
            print(f"Review {len(self.warnings)} warning(s) above.")
        else:
            print("\n❌ VERIFICATION FAILED!")
            print("Critical issues must be fixed before deployment.")

        print("=" * 80)

        return self.checks_failed == 0

    def run_all_verifications(self):
        """Run all verification checks"""
        print("\n" + "=" * 80)
        print("PHASE 2 COMPREHENSIVE VERIFICATION")
        print("Verifying ALL claimed work is actually complete")
        print("=" * 80)

        self.verify_files_exist()
        self.verify_code_compiles()
        self.verify_imports_work()
        self.verify_database_tables()
        self.verify_correlation_rules_populated()
        self.verify_correlation_engine_works()
        self.verify_pattern_detection_works()
        self.verify_health_score_works()
        self.verify_escalation_engine_works()
        self.verify_test_suite_passes()

        success = self.print_summary()

        self.conn.close()

        return success


if __name__ == "__main__":
    verifier = Phase2Verifier()
    success = verifier.run_all_verifications()
    sys.exit(0 if success else 1)
