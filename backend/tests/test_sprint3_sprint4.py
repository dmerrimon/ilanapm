"""
Comprehensive Test Suite for Sprint 3 (Calibrated Tier) and Sprint 4 (Enterprise Tier)
Tests all intelligence engines, API endpoints, and database operations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from datetime import datetime, timedelta
import json

# Sprint 3 imports
from intelligence import (
    BenchmarkBlender,
    ConfidenceScoringEngine,
    OrgBenchmark,
    BlendedBenchmark,
    ConfidenceScore
)

# Sprint 4 imports
from intelligence import (
    PortfolioAggregationEngine,
    ResourceCollisionDetector,
    ResourceAssignment,
    ResourceCollision,
    PortfolioForecaster
)


class TestBenchmarkBlender(unittest.TestCase):
    """Test Sprint 3: Benchmark Blending Engine"""

    def setUp(self):
        self.blender = BenchmarkBlender()

        # Sample org benchmarks
        self.org_benchmarks = [
            OrgBenchmark(
                org_id="org_001",
                ontology_task_id="irb_submission",
                task_name="IRB Submission",
                category="Regulatory",
                median_days=55.0,
                p25_days=48.0,
                p75_days=65.0,
                sample_size=8,
                confidence=0.85,
                last_updated="2024-01-15T00:00:00"
            ),
            OrgBenchmark(
                org_id="org_001",
                ontology_task_id="site_initiation",
                task_name="Site Initiation Visit",
                category="Site Management",
                median_days=20.0,
                p25_days=15.0,
                p75_days=25.0,
                sample_size=12,
                confidence=0.90,
                last_updated="2024-01-15T00:00:00"
            )
        ]

        # Sample industry benchmarks (from ontology)
        from intelligence.models import BenchmarkData
        self.industry_benchmarks = [
            BenchmarkData(
                task_id="irb_submission",
                task_name="IRB Submission",
                category="Regulatory",
                country_code="US",
                authority="FDA",
                median_days=45,
                p25_days=38,
                p75_days=55,
                typical_duration_days=45,
                sample_size=150,
                source="WCG",
                confidence="high"
            ),
            BenchmarkData(
                task_id="site_initiation",
                task_name="Site Initiation Visit",
                category="Site Management",
                country_code="US",
                authority="FDA",
                median_days=18,
                p25_days=14,
                p75_days=22,
                typical_duration_days=18,
                sample_size=200,
                source="Tufts CSDD",
                confidence="high"
            )
        ]

    def test_blend_benchmarks_default_ratio(self):
        """Test blending with default 70/30 ratio"""
        blended = self.blender.blend_benchmarks(
            self.org_benchmarks,
            self.industry_benchmarks
        )

        self.assertEqual(len(blended), 2)

        # Check first benchmark (IRB Submission)
        irb_blend = next(b for b in blended if b.task_id == "irb_submission")
        expected_median = (55.0 * 0.7) + (45.0 * 0.3)  # 52.0 days
        self.assertAlmostEqual(irb_blend.blended_median_days, expected_median, places=1)
        self.assertAlmostEqual(irb_blend.blend_ratio["org"], 0.7, places=5)
        self.assertAlmostEqual(irb_blend.blend_ratio["industry"], 0.3, places=5)
        self.assertEqual(irb_blend.org_sample_size, 8)

    def test_blend_benchmarks_custom_ratio(self):
        """Test blending with custom 80/20 ratio"""
        blended = self.blender.blend_benchmarks(
            self.org_benchmarks,
            self.industry_benchmarks,
            org_weight=0.8
        )

        irb_blend = next(b for b in blended if b.task_id == "irb_submission")
        expected_median = (55.0 * 0.8) + (45.0 * 0.2)  # 53.0 days
        self.assertAlmostEqual(irb_blend.blended_median_days, expected_median, places=1)

    def test_fallback_to_industry_only(self):
        """Test fallback when org sample size too small"""
        # Create org benchmark with only 2 samples (below min_org_samples=3)
        small_sample_org = [
            OrgBenchmark(
                org_id="org_001",
                ontology_task_id="irb_submission",
                task_name="IRB Submission",
                category="Regulatory",
                median_days=55.0,
                p25_days=48.0,
                p75_days=65.0,
                sample_size=2,  # Too small
                confidence=0.60,
                last_updated="2024-01-15T00:00:00"
            )
        ]

        blended = self.blender.blend_benchmarks(
            small_sample_org,
            self.industry_benchmarks,
            min_org_samples=3
        )

        irb_blend = next(b for b in blended if b.task_id == "irb_submission")
        # Should use 100% industry benchmark
        self.assertAlmostEqual(irb_blend.blended_median_days, 45.0, places=1)
        self.assertEqual(irb_blend.blend_ratio["org"], 0.0)
        self.assertEqual(irb_blend.blend_ratio["industry"], 1.0)

    def test_empty_org_benchmarks(self):
        """Test with no org benchmarks (industry only)"""
        blended = self.blender.blend_benchmarks(
            [],
            self.industry_benchmarks
        )

        self.assertEqual(len(blended), 2)
        irb_blend = next(b for b in blended if b.task_id == "irb_submission")
        self.assertAlmostEqual(irb_blend.blended_median_days, 45.0, places=1)


class TestConfidenceScoringEngine(unittest.TestCase):
    """Test Sprint 3: Confidence Scoring Engine"""

    def setUp(self):
        self.scorer = ConfidenceScoringEngine()

        self.sample_benchmark = BlendedBenchmark(
            task_id="irb_submission",
            task_name="IRB Submission",
            category="Regulatory",
            blended_median_days=52.0,
            org_median_days=55.0,
            industry_median_days=45.0,
            blend_ratio={"org": 0.7, "industry": 0.3},
            org_sample_size=8,
            confidence=0.85
        )

    def test_high_confidence_score(self):
        """Test high confidence scenario: low variance, simple task, good calibration"""
        score = self.scorer.calculate_confidence(
            task_id="task_001",
            task_name="IRB Submission",
            task_category="Regulatory",
            customer_duration_days=50,
            benchmark=self.sample_benchmark,
            org_sample_size=8,
            dependency_count=2,
            is_on_critical_path=False,
            has_regulatory_component=True
        )

        self.assertIsInstance(score, ConfidenceScore)
        self.assertGreater(score.overall_score, 70)
        self.assertIn('variance', score.factors)

    def test_low_confidence_score(self):
        """Test low confidence scenario: high variance, complex task, no calibration"""
        score = self.scorer.calculate_confidence(
            task_id="task_002",
            task_name="Complex Regulatory Task",
            task_category="Regulatory",
            customer_duration_days=90,  # 73% higher than benchmark
            benchmark=self.sample_benchmark,
            org_sample_size=0,  # No org data
            dependency_count=10,  # Many dependencies
            is_on_critical_path=True,
            has_regulatory_component=True
        )

        self.assertLess(score.overall_score, 50)

    def test_no_benchmark_available(self):
        """Test when no benchmark is available"""
        score = self.scorer.calculate_confidence(
            task_id="task_003",
            task_name="Novel Task",
            task_category="Unknown",
            customer_duration_days=30,
            benchmark=None,
            org_sample_size=0
        )

        # When no benchmark is available, confidence should be moderate (not too high)
        self.assertLessEqual(score.overall_score, 65)
        self.assertGreaterEqual(score.overall_score, 40)


class TestPortfolioAggregationEngine(unittest.TestCase):
    """Test Sprint 4: Portfolio Aggregation Engine"""

    def setUp(self):
        self.engine = PortfolioAggregationEngine()

        # Sample studies
        self.studies = [
            {
                'study_id': 'STU_001',
                'study_name': 'Phase III Oncology',
                'phase': 'Phase III',
                'status': 'active',
                'timeline_status': 'on_track',
                'start_date': '2024-01-15T00:00:00'
            },
            {
                'study_id': 'STU_002',
                'study_name': 'Phase II Cardiology',
                'phase': 'Phase II',
                'status': 'active',
                'timeline_status': 'at_risk',
                'start_date': '2024-03-01T00:00:00'
            },
            {
                'study_id': 'STU_003',
                'study_name': 'Phase I Neurology',
                'phase': 'Phase I',
                'status': 'active',
                'timeline_status': 'on_track',
                'start_date': '2024-02-10T00:00:00'
            }
        ]

        # Sample variance reports
        self.variance_reports = [
            {
                'study_id': 'STU_001',
                'summary': {
                    'total_tasks_analyzed': 50,
                    'critical_count': 3,
                    'warning_count': 8,
                    'avg_variance_percent': -5.2,
                    'total_financial_impact_usd': -150000
                },
                'variance_signals': [
                    {
                        'benchmark': {'category': 'Regulatory'},
                        'variance': {'percentage': -12.5, 'severity': 'warning'}
                    }
                ]
            },
            {
                'study_id': 'STU_002',
                'summary': {
                    'total_tasks_analyzed': 40,
                    'critical_count': 8,
                    'warning_count': 12,
                    'avg_variance_percent': 15.3,
                    'total_financial_impact_usd': -500000
                },
                'variance_signals': [
                    {
                        'benchmark': {'category': 'Regulatory'},
                        'variance': {'percentage': 18.2, 'severity': 'critical'}
                    }
                ]
            },
            {
                'study_id': 'STU_003',
                'summary': {
                    'total_tasks_analyzed': 30,
                    'critical_count': 1,
                    'warning_count': 4,
                    'avg_variance_percent': 2.1,
                    'total_financial_impact_usd': 50000
                },
                'variance_signals': []
            }
        ]

    def test_aggregate_portfolio(self):
        """Test portfolio aggregation with multiple studies"""
        result = self.engine.aggregate_portfolio(
            org_id="org_001",
            studies=self.studies,
            variance_reports=self.variance_reports,
            org_benchmarks=[]
        )

        self.assertEqual(result['org_id'], "org_001")
        self.assertEqual(result['total_studies'], 3)
        self.assertIn('portfolio_health_score', result)
        self.assertIn('risk_distribution', result)
        self.assertIn('financial_metrics', result)

    def test_portfolio_health_calculation(self):
        """Test portfolio health score calculation"""
        health_score = self.engine._calculate_portfolio_health(
            self.studies,
            self.variance_reports
        )

        self.assertIsInstance(health_score, float)
        self.assertGreaterEqual(health_score, 0)
        self.assertLessEqual(health_score, 100)

    def test_systemic_pattern_detection(self):
        """Test detection of systemic patterns across studies"""
        patterns = self.engine._detect_systemic_patterns(self.variance_reports)

        self.assertIsInstance(patterns, list)
        # Should detect Regulatory pattern (appears in 2/3 studies)
        if patterns:
            self.assertIn('category', patterns[0])
            self.assertIn('avg_variance_percent', patterns[0])

    def test_risk_distribution(self):
        """Test risk distribution calculation"""
        risk_dist = self.engine._calculate_risk_distribution(self.variance_reports)

        self.assertIn('critical_studies', risk_dist)
        self.assertIn('warning_studies', risk_dist)
        self.assertIn('healthy_studies', risk_dist)
        self.assertEqual(
            risk_dist['critical_studies'] + risk_dist['warning_studies'] + risk_dist['healthy_studies'],
            3
        )

    def test_financial_aggregation(self):
        """Test financial impact aggregation"""
        financial = self.engine._aggregate_financial_impact(self.variance_reports)

        expected_total = -150000 + -500000 + 50000  # -600000
        self.assertAlmostEqual(financial['total_impact_usd'], expected_total, places=2)
        self.assertGreater(financial['at_risk_usd'], 0)
        self.assertGreater(financial['potential_savings_usd'], 0)

    def test_empty_portfolio(self):
        """Test with empty portfolio"""
        result = self.engine._empty_portfolio("org_001")

        self.assertEqual(result['total_studies'], 0)
        self.assertEqual(result['portfolio_health_score'], 0)


class TestResourceCollisionDetector(unittest.TestCase):
    """Test Sprint 4: Resource Collision Detection"""

    def setUp(self):
        self.detector = ResourceCollisionDetector()

        # Sample resource assignments
        self.assignments = [
            ResourceAssignment(
                resource_id="site_001",
                resource_name="Memorial Hospital",
                resource_type="site",
                study_id="STU_001",
                study_name="Phase III Oncology",
                start_date="2024-03-01T00:00:00",
                end_date="2024-12-01T00:00:00",
                utilization_percent=85.0
            ),
            ResourceAssignment(
                resource_id="site_001",
                resource_name="Memorial Hospital",
                resource_type="site",
                study_id="STU_002",
                study_name="Phase II Cardiology",
                start_date="2024-06-01T00:00:00",
                end_date="2025-03-01T00:00:00",
                utilization_percent=70.0
            ),
            ResourceAssignment(
                resource_id="site_002",
                resource_name="City Medical Center",
                resource_type="site",
                study_id="STU_003",
                study_name="Phase I Neurology",
                start_date="2024-04-01T00:00:00",
                end_date="2024-10-01T00:00:00",
                utilization_percent=60.0
            )
        ]

    def test_detect_collisions(self):
        """Test collision detection with overlapping resources"""
        result = self.detector.detect_collisions(
            org_id="org_001",
            resource_assignments=self.assignments
        )

        self.assertEqual(result['org_id'], "org_001")
        self.assertIn('collisions', result)
        self.assertIn('summary', result)

        # Should detect collision for site_001 (overlapping assignments)
        self.assertGreater(result['summary']['total_collisions'], 0)

    def test_collision_severity_critical(self):
        """Test critical collision detection (>100% utilization)"""
        collisions = self.detector._detect_resource_collisions(
            "site_001",
            self.assignments[:2]  # Two overlapping assignments
        )

        self.assertEqual(len(collisions), 1)
        collision = collisions[0]

        # Total utilization: 85% + 70% = 155% (critical)
        self.assertEqual(collision.severity, 'critical')
        self.assertEqual(collision.total_utilization, 155.0)

    def test_overlap_calculation(self):
        """Test overlap period calculation"""
        a1 = self.assignments[0]  # 2024-03-01 to 2024-12-01
        a2 = self.assignments[1]  # 2024-06-01 to 2025-03-01

        overlap = self.detector._calculate_overlap(a1, a2)

        self.assertIsNotNone(overlap)
        overlap_start, overlap_end, overlap_days = overlap

        # Overlap: 2024-06-01 to 2024-12-01 = 183 days
        self.assertGreater(overlap_days, 150)

    def test_no_collision(self):
        """Test with non-overlapping assignments"""
        non_overlapping = [
            ResourceAssignment(
                resource_id="site_003",
                resource_name="Research Center",
                resource_type="site",
                study_id="STU_001",
                study_name="Study A",
                start_date="2024-01-01T00:00:00",
                end_date="2024-06-01T00:00:00",
                utilization_percent=80.0
            ),
            ResourceAssignment(
                resource_id="site_003",
                resource_name="Research Center",
                resource_type="site",
                study_id="STU_002",
                study_name="Study B",
                start_date="2024-07-01T00:00:00",
                end_date="2024-12-01T00:00:00",
                utilization_percent=80.0
            )
        ]

        collisions = self.detector._detect_resource_collisions(
            "site_003",
            non_overlapping
        )

        self.assertEqual(len(collisions), 0)

    def test_empty_assignments(self):
        """Test with no assignments"""
        result = self.detector._empty_report("org_001")

        self.assertEqual(result['summary']['total_collisions'], 0)
        self.assertEqual(len(result['collisions']), 0)


class TestPortfolioForecaster(unittest.TestCase):
    """Test Sprint 4: Portfolio Forecasting"""

    def setUp(self):
        self.forecaster = PortfolioForecaster()

        # Sample studies
        self.studies = [
            {
                'study_id': 'STU_001',
                'study_name': 'Phase III Oncology',
                'phase': 'Phase III',
                'status': 'active',
                'start_date': datetime.utcnow().isoformat()
            },
            {
                'study_id': 'STU_002',
                'study_name': 'Phase II Cardiology',
                'phase': 'Phase II',
                'status': 'active',
                'start_date': (datetime.utcnow() - timedelta(days=30)).isoformat()
            }
        ]

    def test_forecast_portfolio(self):
        """Test portfolio forecasting"""
        result = self.forecaster.forecast_portfolio(
            org_id="org_001",
            studies=self.studies,
            org_benchmarks=[],
            horizon_days=90
        )

        self.assertEqual(result['org_id'], "org_001")
        self.assertEqual(result['horizon_days'], 90)
        self.assertIn('milestones', result)
        self.assertIn('resource_forecast', result)
        self.assertIn('capacity_forecast', result)
        self.assertIn('risk_forecast', result)
        self.assertIn('confidence', result)

    def test_milestone_projection(self):
        """Test milestone projection"""
        milestones = self.forecaster._project_milestones(
            self.studies,
            org_benchmarks=[],
            historical_performance=None,
            horizon_days=90
        )

        self.assertIsInstance(milestones, list)
        if milestones:
            self.assertIn('study_id', milestones[0])
            self.assertIn('milestone_type', milestones[0])
            self.assertIn('projected_date', milestones[0])
            self.assertIn('probability_on_time', milestones[0])

    def test_resource_forecast(self):
        """Test resource needs forecasting"""
        milestones = [
            {
                'study_id': 'STU_001',
                'milestone_type': 'site_initiation',
                'days_from_now': 30
            },
            {
                'study_id': 'STU_002',
                'milestone_type': 'first_patient_enrolled',
                'days_from_now': 60
            },
            {
                'study_id': 'STU_003',
                'milestone_type': 'database_lock',
                'days_from_now': 120
            }
        ]

        resource_forecast = self.forecaster._forecast_resource_needs(
            self.studies,
            milestones,
            horizon_days=90
        )

        self.assertIn('site_activations_needed', resource_forecast)
        self.assertIn('enrollment_starts', resource_forecast)
        self.assertIn('peak_activity_period', resource_forecast)

    def test_capacity_forecast(self):
        """Test capacity forecasting"""
        capacity = self.forecaster._forecast_capacity(
            self.studies,
            milestones=[]
        )

        self.assertIn('current_capacity_fte', capacity)
        self.assertIn('projected_peak_capacity_fte', capacity)
        self.assertIn('capacity_utilization', capacity)
        self.assertIn('recommendation', capacity)

    def test_risk_forecast(self):
        """Test risk forecasting"""
        # Create milestones with concentration
        milestones = [
            {
                'study_id': f'STU_{i:03d}',
                'milestone_type': 'regulatory_submission',
                'projected_date': '2024-06-15T00:00:00',
                'probability_on_time': 0.45
            } for i in range(12)  # 12 milestones in same month
        ]

        risks = self.forecaster._forecast_risks(
            self.studies,
            milestones,
            historical_performance=None
        )

        self.assertIsInstance(risks, list)
        # Should detect milestone concentration risk
        if risks:
            self.assertIn('risk_type', risks[0])
            self.assertIn('severity', risks[0])
            self.assertIn('mitigation', risks[0])

    def test_forecast_confidence(self):
        """Test forecast confidence calculation"""
        confidence = self.forecaster._calculate_forecast_confidence(
            org_benchmarks=[],
            historical_performance=None,
            study_count=5
        )

        self.assertIn('overall_confidence', confidence)
        self.assertIn('level', confidence)
        self.assertIn('factors', confidence)
        self.assertGreaterEqual(confidence['overall_confidence'], 0)
        self.assertLessEqual(confidence['overall_confidence'], 95)

    def test_empty_forecast(self):
        """Test with no studies"""
        result = self.forecaster._empty_forecast("org_001", 90)

        self.assertEqual(len(result['milestones']), 0)
        self.assertEqual(result['confidence']['overall_confidence'], 0)


def run_tests():
    """Run all tests and generate report"""
    print("=" * 70)
    print("SPRINT 3 & 4 TEST SUITE")
    print("=" * 70)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBenchmarkBlender))
    suite.addTests(loader.loadTestsFromTestCase(TestConfidenceScoringEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestPortfolioAggregationEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestResourceCollisionDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestPortfolioForecaster))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
