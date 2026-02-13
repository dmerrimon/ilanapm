"""
Phase 4 Implementation Testing

Comprehensive test suite for Phase 4: Portfolio Intelligence

Tests:
1. Database schema (migration 014)
2. Portfolio service functionality
3. Cross-study pattern detection
4. Systemic issue detection
5. Portfolio API endpoints
6. End-to-end workflows

Usage:
    python3 scripts/test_phase4_implementation.py
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class Phase4TestSuite:
    """Test suite for Phase 4 implementation"""

    def __init__(self):
        self.db_path = backend_dir / "database" / "feedback.db"
        self.conn = None
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def setup(self):
        """Setup test environment"""
        print(f"\n{BLUE}{'=' * 80}{RESET}")
        print(f"{BLUE}PHASE 4 IMPLEMENTATION TESTING{RESET}")
        print(f"{BLUE}{'=' * 80}{RESET}\n")

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        # Create test data
        self._create_test_data()

    def teardown(self):
        """Cleanup test environment"""
        # Clean up test data
        self._cleanup_test_data()

        if self.conn:
            self.conn.close()

        print(f"\n{BLUE}{'=' * 80}{RESET}")
        print(f"{BLUE}TEST RESULTS{RESET}")
        print(f"{BLUE}{'=' * 80}{RESET}\n")

        print(f"Total Tests: {self.tests_passed + self.tests_failed}")
        print(f"{GREEN}Passed: {self.tests_passed} ✅{RESET}")
        print(f"{RED}Failed: {self.tests_failed} ❌{RESET}")

        pass_rate = (self.tests_passed / (self.tests_passed + self.tests_failed) * 100) if (self.tests_passed + self.tests_failed) > 0 else 0
        print(f"Pass Rate: {pass_rate:.1f}%\n")

        if self.tests_failed == 0:
            print(f"{GREEN}🎉 ALL TESTS PASSED! Phase 4 implementation is complete.{RESET}")
        else:
            print(f"{RED}❌ Some tests failed. Please review the errors above.{RESET}")

        print(f"{BLUE}{'=' * 80}{RESET}\n")

    def run_test(self, test_name: str, test_func):
        """Run a single test"""
        try:
            result = test_func()
            if result:
                self.tests_passed += 1
                print(f"{GREEN}✓{RESET} {test_name}")
                self.test_results.append({"test": test_name, "status": "passed"})
                return True
            else:
                self.tests_failed += 1
                print(f"{RED}✗{RESET} {test_name}")
                self.test_results.append({"test": test_name, "status": "failed"})
                return False
        except Exception as e:
            self.tests_failed += 1
            print(f"{RED}✗{RESET} {test_name}: {str(e)}")
            self.test_results.append({"test": test_name, "status": "failed", "error": str(e)})
            return False

    def _create_test_data(self):
        """Create test data for portfolio intelligence tests"""
        cursor = self.conn.cursor()

        # Create test org
        cursor.execute("""
            INSERT OR IGNORE INTO organizations (org_id, org_name, tier)
            VALUES ('test_portfolio_org', 'Test Portfolio Org', 'enterprise')
        """)

        # Create 3 test projects with health snapshots
        for i in range(1, 4):
            project_id = f"test_portfolio_project_{i}"

            # Create health snapshot
            cursor.execute("""
                INSERT INTO study_health_snapshots (
                    snapshot_id, org_id, project_id,
                    overall_health_score, health_status,
                    timeline_score, risk_score, tmf_score,
                    active_escalations_count,
                    snapshot_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))
            """, (
                str(uuid.uuid4()),
                'test_portfolio_org',
                project_id,
                65.0 + i * 5,  # Varying health scores
                'warning' if i <= 2 else 'healthy',
                70.0,
                60.0,
                75.0,
                i
            ))

            # Create signals (Site risks for pattern detection)
            for j in range(2):
                cursor.execute("""
                    INSERT INTO signals (
                        signal_id, upload_id, org_id, project_id,
                        signal_type, signal_category, signal_source,
                        signal_description, signal_detail,
                        priority, status, date_identified
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))
                """, (
                    str(uuid.uuid4()),
                    str(uuid.uuid4()),
                    'test_portfolio_org',
                    project_id,
                    'risk_high_priority',
                    'Site',
                    'risk_log',
                    f'Site activation issue in project {i}',
                    json.dumps({}),
                    7,
                    'open'
                ))

        self.conn.commit()

    def _cleanup_test_data(self):
        """Clean up test data"""
        cursor = self.conn.cursor()

        cursor.execute("DELETE FROM signals WHERE org_id = 'test_portfolio_org'")
        cursor.execute("DELETE FROM study_health_snapshots WHERE org_id = 'test_portfolio_org'")
        cursor.execute("DELETE FROM cross_study_patterns WHERE org_id = 'test_portfolio_org'")
        cursor.execute("DELETE FROM systemic_issues WHERE org_id = 'test_portfolio_org'")
        cursor.execute("DELETE FROM portfolio_health_snapshots WHERE org_id = 'test_portfolio_org'")

        self.conn.commit()

    # ========================================================================
    # Database Schema Tests
    # ========================================================================

    def test_migration_014_applied(self):
        """Test that migration 014 was applied"""
        cursor = self.conn.cursor()

        tables = [
            'cross_study_patterns',
            'systemic_issues',
            'portfolio_health_snapshots',
            'resource_allocations'
        ]

        for table in tables:
            cursor.execute(f"""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='{table}'
            """)
            if not cursor.fetchone():
                print(f"      Missing table: {table}")
                return False

        return True

    def test_cross_study_patterns_schema(self):
        """Test cross_study_patterns table schema"""
        cursor = self.conn.cursor()

        cursor.execute("PRAGMA table_info(cross_study_patterns)")
        columns = {row['name'] for row in cursor.fetchall()}

        required_columns = {
            'pattern_id', 'org_id', 'pattern_type', 'pattern_name',
            'pattern_description', 'severity', 'affected_studies',
            'affected_study_count', 'evidence', 'confidence_score',
            'portfolio_impact', 'recommended_action', 'detected_at'
        }

        return required_columns.issubset(columns)

    def test_systemic_issues_schema(self):
        """Test systemic_issues table schema"""
        cursor = self.conn.cursor()

        cursor.execute("PRAGMA table_info(systemic_issues)")
        columns = {row['name'] for row in cursor.fetchall()}

        required_columns = {
            'issue_id', 'org_id', 'issue_type', 'issue_name',
            'issue_description', 'severity', 'affected_studies',
            'root_cause', 'recommended_intervention', 'responsible_party'
        }

        return required_columns.issubset(columns)

    def test_portfolio_health_snapshots_schema(self):
        """Test portfolio_health_snapshots table schema"""
        cursor = self.conn.cursor()

        cursor.execute("PRAGMA table_info(portfolio_health_snapshots)")
        columns = {row['name'] for row in cursor.fetchall()}

        required_columns = {
            'snapshot_id', 'org_id', 'total_studies',
            'average_health_score', 'median_health_score',
            'healthy_count', 'warning_count', 'critical_count',
            'total_escalations', 'snapshot_date'
        }

        return required_columns.issubset(columns)

    # ========================================================================
    # Module Import Tests
    # ========================================================================

    def test_portfolio_service_import(self):
        """Test that portfolio_service module imports successfully"""
        try:
            from intelligence.portfolio_service import PortfolioService, PortfolioHealth, CrossStudyPattern, SystemicIssue
            return True
        except ImportError as e:
            print(f"      Import error: {e}")
            return False

    # ========================================================================
    # Portfolio Service Functional Tests
    # ========================================================================

    def test_portfolio_service_initialization(self):
        """Test PortfolioService can be initialized"""
        try:
            from intelligence.portfolio_service import PortfolioService

            service = PortfolioService(self.conn)
            return service is not None
        except Exception as e:
            print(f"      Error: {e}")
            return False

    def test_get_portfolio_health(self):
        """Test getting portfolio health"""
        try:
            from intelligence.portfolio_service import PortfolioService

            service = PortfolioService(self.conn)

            portfolio_health = service.get_portfolio_health('test_portfolio_org')

            # Verify basic metrics
            if portfolio_health.total_studies != 3:
                print(f"      Expected 3 studies, got {portfolio_health.total_studies}")
                return False

            if portfolio_health.average_health_score <= 0:
                print(f"      Invalid average health score: {portfolio_health.average_health_score}")
                return False

            # Should have health distribution
            total_distribution = (
                portfolio_health.healthy_count +
                portfolio_health.warning_count +
                portfolio_health.critical_count
            )

            if total_distribution != 3:
                print(f"      Health distribution doesn't match total studies")
                return False

            return True

        except Exception as e:
            print(f"      Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_detect_cross_study_patterns(self):
        """Test detecting cross-study patterns"""
        try:
            from intelligence.portfolio_service import PortfolioService

            service = PortfolioService(self.conn)

            patterns = service.detect_cross_study_patterns('test_portfolio_org')

            # Should detect at least one pattern (common Site risks)
            if len(patterns) < 1:
                print(f"      Expected at least 1 pattern, got {len(patterns)}")
                return False

            # Verify pattern structure
            pattern = patterns[0]
            if not pattern.pattern_id:
                print(f"      Pattern missing pattern_id")
                return False

            if not pattern.affected_studies:
                print(f"      Pattern has no affected_studies")
                return False

            return True

        except Exception as e:
            print(f"      Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_detect_systemic_issues(self):
        """Test detecting systemic issues"""
        try:
            from intelligence.portfolio_service import PortfolioService

            service = PortfolioService(self.conn)

            issues = service.detect_systemic_issues('test_portfolio_org')

            # Should detect at least one systemic issue (site activation)
            if len(issues) < 1:
                print(f"      Expected at least 1 systemic issue, got {len(issues)}")
                return False

            # Verify issue structure
            issue = issues[0]
            if not issue.issue_id:
                print(f"      Issue missing issue_id")
                return False

            if not issue.affected_studies:
                print(f"      Issue has no affected_studies")
                return False

            if issue.affected_study_count < 2:
                print(f"      Systemic issue should affect ≥2 studies, got {issue.affected_study_count}")
                return False

            return True

        except Exception as e:
            print(f"      Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_store_cross_study_patterns(self):
        """Test storing cross-study patterns in database"""
        try:
            from intelligence.portfolio_service import PortfolioService, store_cross_study_patterns

            service = PortfolioService(self.conn)

            patterns = service.detect_cross_study_patterns('test_portfolio_org')

            # Store patterns
            store_cross_study_patterns(self.conn, patterns, 'test_portfolio_org')

            # Verify they were stored
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM cross_study_patterns
                WHERE org_id = 'test_portfolio_org'
            """)

            count = cursor.fetchone()['count']

            if count != len(patterns):
                print(f"      Expected {len(patterns)} patterns stored, got {count}")
                return False

            return True

        except Exception as e:
            print(f"      Error: {e}")
            return False

    def test_store_systemic_issues(self):
        """Test storing systemic issues in database"""
        try:
            from intelligence.portfolio_service import PortfolioService, store_systemic_issues

            service = PortfolioService(self.conn)

            issues = service.detect_systemic_issues('test_portfolio_org')

            # Store issues
            store_systemic_issues(self.conn, issues, 'test_portfolio_org')

            # Verify they were stored
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM systemic_issues
                WHERE org_id = 'test_portfolio_org'
            """)

            count = cursor.fetchone()['count']

            if count != len(issues):
                print(f"      Expected {len(issues)} issues stored, got {count}")
                return False

            return True

        except Exception as e:
            print(f"      Error: {e}")
            return False

    # ========================================================================
    # API Endpoint Tests
    # ========================================================================

    def test_portfolio_endpoints_added(self):
        """Test that portfolio endpoints were added to dashboard API"""
        try:
            from api.dashboard import router

            route_paths = [route.path for route in router.routes]

            required_endpoints = [
                '/dashboard/portfolio/health',
                '/dashboard/portfolio/patterns',
                '/dashboard/portfolio/systemic-issues',
                '/dashboard/portfolio/refresh'
            ]

            for endpoint in required_endpoints:
                if endpoint not in route_paths:
                    print(f"      Missing endpoint: {endpoint}")
                    return False

            return True

        except Exception as e:
            print(f"      Error: {e}")
            return False

    # ========================================================================
    # Integration Tests
    # ========================================================================

    def test_end_to_end_portfolio_analysis(self):
        """Test complete portfolio analysis workflow"""
        try:
            from intelligence.portfolio_service import PortfolioService, store_cross_study_patterns, store_systemic_issues

            service = PortfolioService(self.conn)

            # 1. Get portfolio health
            portfolio_health = service.get_portfolio_health('test_portfolio_org')
            if not portfolio_health:
                print("      Failed to get portfolio health")
                return False

            # 2. Detect patterns
            patterns = service.detect_cross_study_patterns('test_portfolio_org')
            if len(patterns) == 0:
                print("      No patterns detected")
                return False

            # 3. Store patterns
            store_cross_study_patterns(self.conn, patterns, 'test_portfolio_org')

            # 4. Detect systemic issues
            issues = service.detect_systemic_issues('test_portfolio_org')
            if len(issues) == 0:
                print("      No systemic issues detected")
                return False

            # 5. Store issues
            store_systemic_issues(self.conn, issues, 'test_portfolio_org')

            # 6. Store portfolio health snapshot
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO portfolio_health_snapshots (
                    snapshot_id, org_id, total_studies,
                    average_health_score, median_health_score,
                    healthy_count, warning_count, critical_count,
                    snapshot_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, date('now'))
            """, (
                str(uuid.uuid4()),
                'test_portfolio_org',
                portfolio_health.total_studies,
                portfolio_health.average_health_score,
                portfolio_health.median_health_score,
                portfolio_health.healthy_count,
                portfolio_health.warning_count,
                portfolio_health.critical_count
            ))
            self.conn.commit()

            # 7. Verify all data was stored
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM portfolio_health_snapshots
                WHERE org_id = 'test_portfolio_org'
            """)
            if cursor.fetchone()['count'] == 0:
                print("      Portfolio health snapshot not stored")
                return False

            return True

        except Exception as e:
            print(f"      Error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """Run all tests"""
        self.setup()

        print(f"{YELLOW}Database Schema Tests{RESET}")
        print("-" * 80)
        self.run_test("Migration 014 applied (portfolio intelligence tables)", self.test_migration_014_applied)
        self.run_test("cross_study_patterns table schema", self.test_cross_study_patterns_schema)
        self.run_test("systemic_issues table schema", self.test_systemic_issues_schema)
        self.run_test("portfolio_health_snapshots table schema", self.test_portfolio_health_snapshots_schema)

        print(f"\n{YELLOW}Module Import Tests{RESET}")
        print("-" * 80)
        self.run_test("portfolio_service module imports", self.test_portfolio_service_import)

        print(f"\n{YELLOW}Portfolio Service Tests{RESET}")
        print("-" * 80)
        self.run_test("PortfolioService initialization", self.test_portfolio_service_initialization)
        self.run_test("Get portfolio health", self.test_get_portfolio_health)
        self.run_test("Detect cross-study patterns", self.test_detect_cross_study_patterns)
        self.run_test("Detect systemic issues", self.test_detect_systemic_issues)
        self.run_test("Store cross-study patterns", self.test_store_cross_study_patterns)
        self.run_test("Store systemic issues", self.test_store_systemic_issues)

        print(f"\n{YELLOW}API Endpoint Tests{RESET}")
        print("-" * 80)
        self.run_test("Portfolio endpoints added to dashboard API", self.test_portfolio_endpoints_added)

        print(f"\n{YELLOW}Integration Tests{RESET}")
        print("-" * 80)
        self.run_test("End-to-end portfolio analysis workflow", self.test_end_to_end_portfolio_analysis)

        self.teardown()

        return self.tests_failed == 0


def main():
    """Main entry point"""
    test_suite = Phase4TestSuite()
    success = test_suite.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
