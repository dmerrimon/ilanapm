"""
Database Operations Testing for Sprint 3 (Calibrated Tier) and Sprint 4 (Enterprise Tier)
Tests CRUD operations on all intelligence-related database tables
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
import sqlite3
from datetime import datetime
import json
import uuid

class TestDatabaseSchema(unittest.TestCase):
    """Test database schema and table structure"""

    @classmethod
    def setUpClass(cls):
        """Set up database connection"""
        cls.db_path = "database/feedback.db"
        cls.conn = sqlite3.connect(cls.db_path)
        cls.cursor = cls.conn.cursor()

    @classmethod
    def tearDownClass(cls):
        """Close database connection"""
        cls.conn.close()

    def test_org_benchmarks_table_exists(self):
        """Test that org_benchmarks table exists"""
        self.cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='org_benchmarks'
        """)
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "org_benchmarks table should exist")

    def test_calibration_results_table_exists(self):
        """Test that calibration_results table exists"""
        self.cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='calibration_results'
        """)
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "calibration_results table should exist")

    def test_org_benchmarks_schema(self):
        """Test org_benchmarks table schema"""
        self.cursor.execute("PRAGMA table_info(org_benchmarks)")
        columns = {row[1]: row[2] for row in self.cursor.fetchall()}

        expected_columns = {
            'benchmark_id': 'INTEGER',
            'org_id': 'TEXT',
            'ontology_task_id': 'TEXT',
            'task_name': 'TEXT',
            'category': 'TEXT',
            'median_days': 'REAL',
            'p25_days': 'REAL',
            'p75_days': 'REAL',
            'sample_size': 'INTEGER',
            'confidence': 'REAL',
            'last_updated': 'TEXT'
        }

        for col_name, col_type in expected_columns.items():
            self.assertIn(col_name, columns, f"Column {col_name} should exist")

    def test_calibration_results_schema(self):
        """Test calibration_results table schema"""
        self.cursor.execute("PRAGMA table_info(calibration_results)")
        columns = {row[1]: row[2] for row in self.cursor.fetchall()}

        expected_columns = {
            'calibration_id': 'TEXT',
            'org_id': 'TEXT',
            'project_name': 'TEXT',
            'tasks_extracted': 'INTEGER',
            'tasks_normalized': 'INTEGER',
            'benchmarks_generated': 'INTEGER',
            'patterns_detected': 'TEXT',
            'quality_metrics': 'TEXT',
            'created_at': 'TIMESTAMP'
        }

        for col_name in expected_columns.keys():
            self.assertIn(col_name, columns, f"Column {col_name} should exist")


class TestOrgBenchmarksCRUD(unittest.TestCase):
    """Test CRUD operations on org_benchmarks table"""

    @classmethod
    def setUpClass(cls):
        """Set up database connection"""
        cls.db_path = "database/feedback.db"
        cls.conn = sqlite3.connect(cls.db_path)
        cls.cursor = cls.conn.cursor()
        cls.test_org_id = f"test_org_{uuid.uuid4().hex[:8]}"

    @classmethod
    def tearDownClass(cls):
        """Clean up test data and close connection"""
        cls.cursor.execute("DELETE FROM org_benchmarks WHERE org_id LIKE 'test_org_%'")
        cls.conn.commit()
        cls.conn.close()

    def test_01_insert_org_benchmark(self):
        """Test INSERT operation on org_benchmarks"""
        self.cursor.execute("""
            INSERT INTO org_benchmarks (
                org_id, ontology_task_id, task_name, category,
                median_days, p25_days, p75_days,
                sample_size, confidence, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.test_org_id,
            "protocol_development",
            "Protocol Development",
            "Planning",
            15.5,
            12.0,
            18.0,
            10,
            0.85,
            datetime.now().isoformat()
        ))
        self.conn.commit()

        # Verify insert
        self.cursor.execute("""
            SELECT COUNT(*) FROM org_benchmarks WHERE org_id = ?
        """, (self.test_org_id,))
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 1, "Should have 1 org benchmark")

    def test_02_read_org_benchmark(self):
        """Test SELECT operation on org_benchmarks"""
        self.cursor.execute("""
            SELECT org_id, ontology_task_id, median_days, sample_size, confidence
            FROM org_benchmarks WHERE org_id = ?
        """, (self.test_org_id,))

        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "Should find org benchmark")
        self.assertEqual(result[0], self.test_org_id)
        self.assertEqual(result[1], "protocol_development")
        self.assertAlmostEqual(result[2], 15.5, places=1)
        self.assertEqual(result[3], 10)
        self.assertAlmostEqual(result[4], 0.85, places=2)

    def test_03_update_org_benchmark(self):
        """Test UPDATE operation on org_benchmarks"""
        self.cursor.execute("""
            UPDATE org_benchmarks
            SET median_days = ?, confidence = ?, last_updated = ?
            WHERE org_id = ? AND ontology_task_id = ?
        """, (20.0, 0.90, datetime.now().isoformat(), self.test_org_id, "protocol_development"))
        self.conn.commit()

        # Verify update
        self.cursor.execute("""
            SELECT median_days, confidence FROM org_benchmarks
            WHERE org_id = ? AND ontology_task_id = ?
        """, (self.test_org_id, "protocol_development"))

        result = self.cursor.fetchone()
        self.assertAlmostEqual(result[0], 20.0, places=1)
        self.assertAlmostEqual(result[1], 0.90, places=2)

    def test_04_bulk_insert_org_benchmarks(self):
        """Test bulk INSERT of multiple org benchmarks"""
        benchmarks = [
            (self.test_org_id, "irb_submission", "IRB Submission", "Regulatory", 45.0, 38.0, 52.0, 8, 0.80),
            (self.test_org_id, "site_initiation", "Site Initiation", "Site Management", 20.0, 15.0, 25.0, 12, 0.88),
            (self.test_org_id, "enrollment_planning", "Enrollment Planning", "Study Operations", 10.0, 8.0, 12.0, 15, 0.92)
        ]

        for bench in benchmarks:
            self.cursor.execute("""
                INSERT INTO org_benchmarks (
                    org_id, ontology_task_id, task_name, category,
                    median_days, p25_days, p75_days,
                    sample_size, confidence, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, bench + (datetime.now().isoformat(),))

        self.conn.commit()

        # Verify bulk insert
        self.cursor.execute("""
            SELECT COUNT(*) FROM org_benchmarks WHERE org_id = ?
        """, (self.test_org_id,))
        count = self.cursor.fetchone()[0]
        self.assertGreaterEqual(count, 3, "Should have at least 3 benchmarks after bulk insert")

    def test_05_query_with_filters(self):
        """Test SELECT with WHERE clauses and filters"""
        # Query high-confidence benchmarks
        self.cursor.execute("""
            SELECT ontology_task_id, confidence
            FROM org_benchmarks
            WHERE org_id = ? AND confidence >= 0.85
            ORDER BY confidence DESC
        """, (self.test_org_id,))

        results = self.cursor.fetchall()
        self.assertGreater(len(results), 0, "Should find high-confidence benchmarks")

        # Verify all results meet confidence threshold
        for result in results:
            self.assertGreaterEqual(result[1], 0.85)

    def test_06_delete_org_benchmark(self):
        """Test DELETE operation on org_benchmarks"""
        initial_count_result = self.cursor.execute("""
            SELECT COUNT(*) FROM org_benchmarks WHERE org_id = ?
        """, (self.test_org_id,))
        initial_count = initial_count_result.fetchone()[0]

        # Delete one benchmark
        self.cursor.execute("""
            DELETE FROM org_benchmarks
            WHERE org_id = ? AND ontology_task_id = ?
        """, (self.test_org_id, "enrollment_planning"))
        self.conn.commit()

        # Verify deletion
        final_count_result = self.cursor.execute("""
            SELECT COUNT(*) FROM org_benchmarks WHERE org_id = ?
        """, (self.test_org_id,))
        final_count = final_count_result.fetchone()[0]

        self.assertEqual(final_count, initial_count - 1, "Should have one fewer benchmark")


class TestCalibrationResultsCRUD(unittest.TestCase):
    """Test CRUD operations on calibration_results table"""

    @classmethod
    def setUpClass(cls):
        """Set up database connection"""
        cls.db_path = "database/feedback.db"
        cls.conn = sqlite3.connect(cls.db_path)
        cls.cursor = cls.conn.cursor()
        cls.test_org_id = f"test_org_{uuid.uuid4().hex[:8]}"
        cls.test_calibration_id = str(uuid.uuid4())

    @classmethod
    def tearDownClass(cls):
        """Clean up test data and close connection"""
        cls.cursor.execute("DELETE FROM calibration_results WHERE org_id LIKE 'test_org_%'")
        cls.conn.commit()
        cls.conn.close()

    def test_01_insert_calibration_result(self):
        """Test INSERT operation on calibration_results"""
        patterns = json.dumps([
            {"pattern_type": "duration_consistency", "category": "Regulatory", "confidence": 0.85}
        ])

        quality_metrics = json.dumps({
            "match_rate": 0.92,
            "outlier_count": 2,
            "data_completeness": 0.95
        })

        self.cursor.execute("""
            INSERT INTO calibration_results (
                calibration_id, org_id, project_name, tasks_extracted,
                tasks_normalized, benchmarks_generated, patterns_detected,
                quality_metrics, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.test_calibration_id,
            self.test_org_id,
            "Phase III Oncology Study",
            150,
            145,
            42,
            patterns,
            quality_metrics,
            datetime.now().isoformat()
        ))
        self.conn.commit()

        # Verify insert
        self.cursor.execute("""
            SELECT COUNT(*) FROM calibration_results WHERE calibration_id = ?
        """, (self.test_calibration_id,))
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 1, "Should have 1 calibration result")

    def test_02_read_calibration_result(self):
        """Test SELECT operation on calibration_results"""
        self.cursor.execute("""
            SELECT org_id, project_name, tasks_extracted, benchmarks_generated
            FROM calibration_results WHERE calibration_id = ?
        """, (self.test_calibration_id,))

        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "Should find calibration result")
        self.assertEqual(result[0], self.test_org_id)
        self.assertEqual(result[1], "Phase III Oncology Study")
        self.assertEqual(result[2], 150)
        self.assertEqual(result[3], 42)

    def test_03_read_json_fields(self):
        """Test reading and parsing JSON fields"""
        self.cursor.execute("""
            SELECT patterns_detected, quality_metrics
            FROM calibration_results WHERE calibration_id = ?
        """, (self.test_calibration_id,))

        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "Should find calibration result")

        # Parse JSON fields
        patterns = json.loads(result[0])
        quality_metrics = json.loads(result[1])

        self.assertIsInstance(patterns, list)
        self.assertGreater(len(patterns), 0)
        self.assertIn("pattern_type", patterns[0])

        self.assertIsInstance(quality_metrics, dict)
        self.assertIn("match_rate", quality_metrics)
        self.assertAlmostEqual(quality_metrics["match_rate"], 0.92, places=2)

    def test_04_update_calibration_result(self):
        """Test UPDATE operation on calibration_results"""
        self.cursor.execute("""
            UPDATE calibration_results
            SET benchmarks_generated = ?
            WHERE calibration_id = ?
        """, (45, self.test_calibration_id))
        self.conn.commit()

        # Verify update
        self.cursor.execute("""
            SELECT benchmarks_generated FROM calibration_results
            WHERE calibration_id = ?
        """, (self.test_calibration_id,))

        result = self.cursor.fetchone()
        self.assertEqual(result[0], 45)

    def test_05_query_by_org(self):
        """Test querying all calibration results for an organization"""
        # Insert additional calibration results
        for i in range(3):
            cal_id = str(uuid.uuid4())
            self.cursor.execute("""
                INSERT INTO calibration_results (
                    calibration_id, org_id, project_name, tasks_extracted,
                    tasks_normalized, benchmarks_generated, patterns_detected,
                    quality_metrics, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cal_id,
                self.test_org_id,
                f"Study {i+1}",
                100 + i*10,
                95 + i*10,
                30 + i*5,
                "[]",
                "{}",
                datetime.now().isoformat()
            ))
        self.conn.commit()

        # Query all results for org
        self.cursor.execute("""
            SELECT COUNT(*) FROM calibration_results WHERE org_id = ?
        """, (self.test_org_id,))
        count = self.cursor.fetchone()[0]

        self.assertGreaterEqual(count, 4, "Should have at least 4 calibration results")

    def test_06_delete_calibration_result(self):
        """Test DELETE operation on calibration_results"""
        self.cursor.execute("""
            DELETE FROM calibration_results
            WHERE calibration_id = ?
        """, (self.test_calibration_id,))
        self.conn.commit()

        # Verify deletion
        self.cursor.execute("""
            SELECT COUNT(*) FROM calibration_results WHERE calibration_id = ?
        """, (self.test_calibration_id,))
        count = self.cursor.fetchone()[0]

        self.assertEqual(count, 0, "Should have 0 calibration results after deletion")


class TestDatabaseConstraints(unittest.TestCase):
    """Test database constraints and data integrity"""

    @classmethod
    def setUpClass(cls):
        """Set up database connection"""
        cls.db_path = "database/feedback.db"
        cls.conn = sqlite3.connect(cls.db_path)
        cls.cursor = cls.conn.cursor()
        cls.test_org_id = f"test_org_{uuid.uuid4().hex[:8]}"

    @classmethod
    def tearDownClass(cls):
        """Clean up test data and close connection"""
        cls.cursor.execute("DELETE FROM org_benchmarks WHERE org_id LIKE 'test_org_%'")
        cls.conn.commit()
        cls.conn.close()

    def test_unique_constraint_org_benchmarks(self):
        """Test UNIQUE constraint on (org_id, ontology_task_id)"""
        # Insert first benchmark
        self.cursor.execute("""
            INSERT INTO org_benchmarks (
                org_id, ontology_task_id, task_name, category,
                median_days, p25_days, p75_days,
                sample_size, confidence, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.test_org_id,
            "unique_test_task",
            "Unique Test Task",
            "Test Category",
            15.0,
            12.0,
            18.0,
            5,
            0.75,
            datetime.now().isoformat()
        ))
        self.conn.commit()

        # Try to insert duplicate (should fail or be handled)
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("""
                INSERT INTO org_benchmarks (
                    org_id, ontology_task_id, task_name, category,
                    median_days, p25_days, p75_days,
                    sample_size, confidence, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.test_org_id,
                "unique_test_task",
                "Different Name",
                "Different Category",
                20.0,
                15.0,
                25.0,
                8,
                0.85,
                datetime.now().isoformat()
            ))
            self.conn.commit()

    def test_not_null_constraints(self):
        """Test NOT NULL constraints on required fields"""
        # Try to insert with NULL required fields
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("""
                INSERT INTO org_benchmarks (
                    org_id, ontology_task_id, median_days
                ) VALUES (?, ?, ?)
            """, (self.test_org_id, "null_test_task", None))
            self.conn.commit()


def run_tests():
    """Run all database operation tests"""
    print("\n" + "="*70)
    print("DATABASE OPERATIONS TEST SUITE")
    print("="*70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseSchema))
    suite.addTests(loader.loadTestsFromTestCase(TestOrgBenchmarksCRUD))
    suite.addTests(loader.loadTestsFromTestCase(TestCalibrationResultsCRUD))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseConstraints))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())
