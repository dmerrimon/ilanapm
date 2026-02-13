#!/usr/bin/env python3
"""
Test Phase 2 Implementation

Validates:
1. Correlation rules populated
2. Correlation engine functionality
3. Pattern detection
4. Health score calculation
5. Escalation logic

Run: python scripts/test_phase2_implementation.py
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from intelligence.correlation_engine import CorrelationEngine, SignalTimelineCorrelation
from intelligence.pattern_detection import PatternDetector
from intelligence.health_score import HealthScoreCalculator
from intelligence.escalation_engine import EscalationEngine


class Phase2Tester:
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "database" / "feedback.db"
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.passed = 0
        self.failed = 0

    def print_section(self, title: str):
        print("\n" + "=" * 80)
        print(title)
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

    # ========================================================================
    # CORRELATION RULES TESTS
    # ========================================================================

    def test_correlation_rules(self):
        """Test that correlation rules are populated"""
        self.print_section("TEST 1: CORRELATION RULES")

        cursor = self.conn.cursor()

        # Check rules exist
        cursor.execute("SELECT COUNT(*) as count FROM correlation_rules WHERE is_active = 1")
        rule_count = cursor.fetchone()['count']
        self.print_test("Correlation rules populated", rule_count >= 6,
                       f"Found {rule_count} active rules (expected ≥6)")

        # Check rule types
        cursor.execute("""
            SELECT rule_name, signal_type, correlation_type, escalation_level
            FROM correlation_rules
            WHERE is_active = 1
            ORDER BY rule_name
        """)

        rules = cursor.fetchall()
        print("\n  Loaded rules:")
        for rule in rules:
            print(f"    • {rule['rule_name']}: {rule['signal_type']} → {rule['correlation_type']} ({rule['escalation_level']})")

        # Check for VP escalation rule (Safety)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM correlation_rules
            WHERE escalation_level = 'vp' AND is_active = 1
        """)
        vp_rules = cursor.fetchone()['count']
        self.print_test("VP escalation rules exist", vp_rules >= 1,
                       f"Found {vp_rules} VP-level rules")

        # Check for blocker rules
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM correlation_rules
            WHERE correlation_type = 'blocker' AND is_active = 1
        """)
        blocker_rules = cursor.fetchone()['count']
        self.print_test("Blocker correlation rules exist", blocker_rules >= 1,
                       f"Found {blocker_rules} blocker rules")

    # ========================================================================
    # CORRELATION ENGINE TESTS
    # ========================================================================

    def test_correlation_engine(self):
        """Test correlation engine functionality"""
        self.print_section("TEST 2: CORRELATION ENGINE")

        engine = CorrelationEngine(self.conn)

        # Test signal: Site risk
        test_signal = {
            'signal_id': 'test_sig_001',
            'signal_type': 'risk_high_priority',
            'signal_category': 'Site',
            'signal_description': 'Site activation slower than anticipated',
            'signal_detail': json.dumps({'risk_number': 13}),
            'priority': 7,
            'status': 'open'
        }

        # Test timeline
        test_timeline = {
            'milestones': [
                {
                    'milestone_name': 'Site Activation',
                    'milestone_code': 'SITE_ACT',
                    'task_id': 'task_123',
                    'planned_date': '2026-06-15',
                    'is_critical_path': True
                },
                {
                    'milestone_name': 'LPI',
                    'milestone_code': 'LPI',
                    'task_id': 'task_456',
                    'planned_date': '2026-09-01',
                    'is_critical_path': True
                }
            ]
        }

        try:
            # Test: Find matching rules
            matching_rules = engine._find_matching_rules(test_signal)
            self.print_test("Finds matching correlation rules", len(matching_rules) > 0,
                           f"Found {len(matching_rules)} matching rules for site risk")

            # Test: Find milestones
            if matching_rules:
                rule = matching_rules[0]
                matching_milestones = engine._find_milestones_in_timeline(test_timeline, rule)
                self.print_test("Finds affected milestones", len(matching_milestones) > 0,
                               f"Found {len(matching_milestones)} affected milestones")

            # Test: Estimate delay
            if matching_rules:
                delay = engine._estimate_delay(test_signal, matching_rules[0])
                self.print_test("Calculates delay estimate", delay > 0,
                               f"Estimated delay: {delay} days")

            # Test: Full correlation
            correlations = engine.correlate_signals([test_signal], test_timeline, 'test_project')
            self.print_test("Creates full correlations", len(correlations) > 0,
                           f"Created {len(correlations)} correlation(s)")

            if correlations:
                corr = correlations[0]
                self.print_test("Correlation has reasoning", len(corr.correlation_reasoning) > 0,
                               f"Reasoning: {corr.correlation_reasoning[:80]}...")

        except Exception as e:
            self.print_test("Correlation engine runs without errors", False, str(e))

    # ========================================================================
    # PATTERN DETECTION TESTS
    # ========================================================================

    def test_pattern_detection(self):
        """Test pattern detection functionality"""
        self.print_section("TEST 3: PATTERN DETECTION")

        detector = PatternDetector(self.conn)

        # Test: Signal clustering
        test_signals_clustering = [
            {'signal_id': 's1', 'signal_category': 'Site', 'priority': 7, 'status': 'open'},
            {'signal_id': 's2', 'signal_category': 'Site', 'priority': 6, 'status': 'open'},
            {'signal_id': 's3', 'signal_category': 'Site', 'priority': 8, 'status': 'open'},
        ]

        patterns = detector._detect_signal_clustering(test_signals_clustering)
        self.print_test("Detects signal clustering", len(patterns) > 0,
                       f"Detected {len(patterns)} clustering pattern(s)")

        # Test: Escalating severity
        test_signals_escalating = [
            {'signal_id': 's1', 'priority': 4, 'date_identified': (date.today() - timedelta(days=30)).isoformat()},
            {'signal_id': 's2', 'priority': 5, 'date_identified': (date.today() - timedelta(days=20)).isoformat()},
            {'signal_id': 's3', 'priority': 3, 'date_identified': (date.today() - timedelta(days=25)).isoformat()},
            {'signal_id': 's4', 'priority': 7, 'date_identified': (date.today() - timedelta(days=3)).isoformat()},
            {'signal_id': 's5', 'priority': 8, 'date_identified': (date.today() - timedelta(days=1)).isoformat()},
            {'signal_id': 's6', 'priority': 9, 'date_identified': date.today().isoformat()},
        ]

        patterns = detector._detect_escalating_severity(test_signals_escalating)
        self.print_test("Detects escalating severity", len(patterns) > 0,
                       f"Detected {len(patterns)} escalation pattern(s)")

        # Test: No mitigation
        test_signals_no_mitigation = [
            {
                'signal_id': 's1',
                'priority': 7,
                'status': 'open',
                'signal_detail': json.dumps({'mitigation_plan': ''})
            },
            {
                'signal_id': 's2',
                'priority': 8,
                'status': 'open',
                'signal_detail': json.dumps({})
            },
        ]

        patterns = detector._detect_no_mitigation(test_signals_no_mitigation)
        self.print_test("Detects missing mitigation plans", len(patterns) > 0,
                       f"Detected {len(patterns)} no-mitigation pattern(s)")

        # Test: Overdue signals
        test_signals_overdue = [
            {
                'signal_id': 's1',
                'status': 'open',
                'target_date': (date.today() - timedelta(days=30)).isoformat()
            },
            {
                'signal_id': 's2',
                'status': 'open',
                'target_date': (date.today() - timedelta(days=15)).isoformat()
            },
        ]

        patterns = detector._detect_overdue_signals(test_signals_overdue)
        self.print_test("Detects overdue signals", len(patterns) > 0,
                       f"Detected {len(patterns)} overdue pattern(s)")

    # ========================================================================
    # HEALTH SCORE TESTS
    # ========================================================================

    def test_health_score_calculator(self):
        """Test health score calculation"""
        self.print_section("TEST 4: HEALTH SCORE CALCULATOR")

        calculator = HealthScoreCalculator(self.conn)

        # Test: High risk scenario
        test_signals_high_risk = [
            {'signal_id': 's1', 'signal_type': 'risk_high_priority', 'priority': 9, 'status': 'open', 'signal_detail': json.dumps({})},
            {'signal_id': 's2', 'signal_type': 'risk_high_priority', 'priority': 7, 'status': 'open', 'signal_detail': json.dumps({})},
            {'signal_id': 's3', 'signal_type': 'risk_high_priority', 'priority': 6, 'status': 'open', 'signal_detail': json.dumps({})},
        ]

        health_score = calculator.calculate_health_score(
            'test_project',
            test_signals_high_risk,
            [],
            None
        )

        self.print_test("Calculates overall health score", health_score.overall_score >= 0 and health_score.overall_score <= 100,
                       f"Overall score: {health_score.overall_score}")

        self.print_test("Determines health status", health_score.health_status in ['healthy', 'warning', 'critical'],
                       f"Status: {health_score.health_status}")

        self.print_test("Risk score reflects high risk signals", health_score.risk_score < 80,
                       f"Risk score: {health_score.risk_score} (should be lower with 3 high-priority risks)")

        self.print_test("Generates recommendations", len(health_score.recommended_actions) > 0,
                       f"Generated {len(health_score.recommended_actions)} recommendation(s)")

        # Test: Healthy scenario
        test_signals_healthy = [
            {'signal_id': 's1', 'signal_type': 'risk_high_priority', 'priority': 3, 'status': 'open', 'signal_detail': json.dumps({})},
        ]

        health_score_healthy = calculator.calculate_health_score(
            'test_project',
            test_signals_healthy,
            [],
            None
        )

        self.print_test("Healthy scenario has high score", health_score_healthy.overall_score > health_score.overall_score,
                       f"Healthy: {health_score_healthy.overall_score} > Risky: {health_score.overall_score}")

        # Test: Component scores
        self.print_test("Calculates timeline score", health_score.timeline_score >= 0,
                       f"Timeline score: {health_score.timeline_score}")

        self.print_test("Calculates risk score", health_score.risk_score >= 0,
                       f"Risk score: {health_score.risk_score}")

        self.print_test("Calculates TMF score", health_score.tmf_score >= 0,
                       f"TMF score: {health_score.tmf_score}")

    # ========================================================================
    # ESCALATION ENGINE TESTS
    # ========================================================================

    def test_escalation_engine(self):
        """Test escalation logic"""
        self.print_section("TEST 5: ESCALATION ENGINE")

        engine = EscalationEngine(self.conn)

        # Test: High priority risk → Director escalation
        test_signal_director = {
            'signal_id': 's_dir',
            'signal_type': 'risk_high_priority',
            'signal_category': 'Site',
            'signal_description': 'Site risk requiring director attention',
            'signal_detail': json.dumps({}),
            'priority': 7,
            'status': 'open'
        }

        director_escalation = engine._check_director_escalation(test_signal_director, [], {})
        self.print_test("Detects Director escalation (Priority ≥6)", director_escalation,
                       "Priority 7 risk triggers Director escalation")

        # Test: Critical priority risk → VP escalation
        test_signal_vp = {
            'signal_id': 's_vp',
            'signal_type': 'risk_critical',
            'signal_category': 'Clinical',
            'signal_description': 'Critical risk requiring VP attention',
            'signal_detail': json.dumps({}),
            'priority': 9,
            'status': 'open'
        }

        vp_escalation = engine._check_vp_escalation(test_signal_vp, [], [], {})
        self.print_test("Detects VP escalation (Priority = 9)", vp_escalation,
                       "Priority 9 risk triggers VP escalation")

        # Test: Safety risk → VP escalation
        test_signal_safety = {
            'signal_id': 's_safety',
            'signal_type': 'risk_high_priority',
            'signal_category': 'Safety',
            'signal_description': 'Safety risk',
            'signal_detail': json.dumps({}),
            'priority': 7,
            'status': 'open'
        }

        vp_escalation_safety = engine._check_vp_escalation(test_signal_safety, [], [], {})
        self.print_test("Detects VP escalation for Safety risks", vp_escalation_safety,
                       "Safety risks with Priority ≥6 trigger VP escalation")

        # Test: Full escalation evaluation
        test_signals_escalation = [test_signal_director, test_signal_vp, test_signal_safety]
        escalations = engine.evaluate_escalations(
            'test_org',
            'test_project',
            test_signals_escalation,
            [],
            [],
            {}
        )

        self.print_test("Creates escalation objects", len(escalations) > 0,
                       f"Created {len(escalations)} escalations from {len(test_signals_escalation)} signals")

        # Count escalation levels
        director_count = sum(1 for e in escalations if e.escalation_level == 'director')
        vp_count = sum(1 for e in escalations if e.escalation_level == 'vp')

        self.print_test("Escalations assigned to correct levels",
                       director_count > 0 and vp_count > 0,
                       f"Director: {director_count}, VP: {vp_count}")

        # Test: Escalation has intervention
        if escalations:
            has_intervention = all(len(e.intervention_recommended) > 0 for e in escalations)
            self.print_test("Escalations include interventions", has_intervention,
                           "All escalations have recommended interventions")

    # ========================================================================
    # SUMMARY
    # ========================================================================

    def print_summary(self):
        """Print test summary"""
        self.print_section("TEST SUMMARY")

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")

        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! Phase 2 implementation is complete.")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed. Review errors above.")

        print("=" * 80)

    def run_all_tests(self):
        """Run all Phase 2 tests"""
        print("\n" + "=" * 80)
        print("PHASE 2 IMPLEMENTATION TESTING")
        print("=" * 80)

        self.test_correlation_rules()
        self.test_correlation_engine()
        self.test_pattern_detection()
        self.test_health_score_calculator()
        self.test_escalation_engine()
        self.print_summary()

        self.conn.close()

        return self.failed == 0


if __name__ == "__main__":
    tester = Phase2Tester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
