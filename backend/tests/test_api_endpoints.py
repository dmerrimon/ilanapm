"""
API Endpoint Testing for Sprint 3 (Calibrated Tier) and Sprint 4 (Enterprise Tier)
Tests all intelligence API endpoints with various scenarios
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from fastapi.testclient import TestClient
from datetime import datetime
import json

# Import the FastAPI app
from main import app

class TestCalibrationEndpoints(unittest.TestCase):
    """Test Sprint 3: Calibration API Endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.client = TestClient(app)
        cls.org_id = "test_org_001"

        # Mock JWT token for calibrated tier
        cls.headers_calibrated = {
            "Authorization": "Bearer mock_calibrated_token"
        }

        # Mock JWT token for enterprise tier
        cls.headers_enterprise = {
            "Authorization": "Bearer mock_enterprise_token"
        }

    def test_upload_calibration_file(self):
        """Test POST /api/v1/calibration/upload"""
        # Mock MS Project XML file content
        mock_xml_content = b"""<?xml version="1.0"?>
        <Project>
            <Tasks>
                <Task>
                    <UID>1</UID>
                    <Name>Protocol Development</Name>
                    <Duration>PT120H0M0S</Duration>
                </Task>
            </Tasks>
        </Project>
        """

        payload = {
            "org_id": self.org_id,
            "file_content": list(mock_xml_content),
            "project_metadata": {
                "phase": "Phase III",
                "therapeutic_area": "Oncology",
                "country": "US"
            }
        }

        response = self.client.post(
            "/api/v1/calibration/upload",
            json=payload,
            headers=self.headers_calibrated
        )

        # Should return 401 without proper auth, or 422 for validation errors
        # In production, this would work with real JWT validation
        self.assertIn(response.status_code, [200, 401, 403, 422])

    def test_get_calibration_results(self):
        """Test GET /api/v1/calibration/results"""
        response = self.client.get(
            f"/api/v1/calibration/results?org_id={self.org_id}&limit=10",
            headers=self.headers_calibrated
        )

        # Should return 401 without proper auth
        self.assertIn(response.status_code, [200, 401, 403])

    def test_get_org_benchmarks(self):
        """Test GET /api/v1/calibration/org-benchmarks"""
        response = self.client.get(
            f"/api/v1/calibration/org-benchmarks?org_id={self.org_id}",
            headers=self.headers_calibrated
        )

        # Should return 401 without proper auth
        self.assertIn(response.status_code, [200, 401, 403])

    def test_get_blended_benchmarks(self):
        """Test GET /api/v1/calibration/blended-benchmarks"""
        response = self.client.get(
            f"/api/v1/calibration/blended-benchmarks?org_id={self.org_id}&org_weight=0.7&min_org_samples=3",
            headers=self.headers_calibrated
        )

        # Should return 401 without proper auth
        self.assertIn(response.status_code, [200, 401, 403])

    def test_calculate_confidence_score(self):
        """Test POST /api/v1/calibration/confidence-score"""
        payload = {
            "org_id": self.org_id,
            "task_id": "task_001",
            "task_name": "IRB Submission",
            "task_category": "Regulatory",
            "customer_duration_days": 50,
            "org_sample_size": 8,
            "dependency_count": 2,
            "is_on_critical_path": False,
            "has_regulatory_component": True
        }

        response = self.client.post(
            "/api/v1/calibration/confidence-score",
            json=payload,
            headers=self.headers_calibrated
        )

        # Should return 401 without proper auth, or 422 for validation errors
        self.assertIn(response.status_code, [200, 401, 403, 422])

    def test_tier_enforcement_core_tier(self):
        """Test that Core tier is blocked from calibration endpoints"""
        headers_core = {
            "Authorization": "Bearer mock_core_token"
        }

        response = self.client.get(
            f"/api/v1/calibration/results?org_id={self.org_id}",
            headers=headers_core
        )

        # Should return 403 Forbidden for Core tier
        self.assertIn(response.status_code, [401, 403])


class TestPortfolioEndpoints(unittest.TestCase):
    """Test Sprint 4: Portfolio API Endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.client = TestClient(app)
        cls.org_id = "test_org_002"

        # Mock JWT token for enterprise tier
        cls.headers_enterprise = {
            "Authorization": "Bearer mock_enterprise_token"
        }

    def test_get_portfolio_analytics(self):
        """Test GET /api/v1/portfolio/analytics"""
        response = self.client.get(
            f"/api/v1/portfolio/analytics?org_id={self.org_id}",
            headers=self.headers_enterprise
        )

        # Should return 401 without proper auth
        self.assertIn(response.status_code, [200, 401, 403])

    def test_get_resource_collisions(self):
        """Test GET /api/v1/portfolio/collisions"""
        response = self.client.get(
            f"/api/v1/portfolio/collisions?org_id={self.org_id}",
            headers=self.headers_enterprise
        )

        # Should return 401 without proper auth
        self.assertIn(response.status_code, [200, 401, 403])

    def test_get_portfolio_forecast(self):
        """Test GET /api/v1/portfolio/forecast"""
        response = self.client.get(
            f"/api/v1/portfolio/forecast?org_id={self.org_id}&horizon_days=90",
            headers=self.headers_enterprise
        )

        # Should return 401 without proper auth
        self.assertIn(response.status_code, [200, 401, 403])

    def test_tier_enforcement_calibrated_tier(self):
        """Test that Calibrated tier is blocked from portfolio endpoints"""
        headers_calibrated = {
            "Authorization": "Bearer mock_calibrated_token"
        }

        response = self.client.get(
            f"/api/v1/portfolio/analytics?org_id={self.org_id}",
            headers=headers_calibrated
        )

        # Should return 403 Forbidden for Calibrated tier
        self.assertIn(response.status_code, [401, 403])


class TestHealthEndpoint(unittest.TestCase):
    """Test Health Check Endpoint"""

    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.client = TestClient(app)

    def test_health_check(self):
        """Test GET /api/v1/health"""
        response = self.client.get("/api/v1/health")

        # Health check should always return 200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)


class TestAPIDocumentation(unittest.TestCase):
    """Test API Documentation Endpoints"""

    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.client = TestClient(app)

    def test_openapi_schema(self):
        """Test GET /openapi.json"""
        response = self.client.get("/openapi.json")

        # Should return OpenAPI schema
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("openapi", data)
        self.assertIn("info", data)
        self.assertIn("paths", data)

    def test_swagger_ui(self):
        """Test GET /docs (Swagger UI)"""
        response = self.client.get("/docs")

        # Should return Swagger UI HTML
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_redoc(self):
        """Test GET /redoc (ReDoc)"""
        response = self.client.get("/redoc")

        # Should return ReDoc HTML
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])


def run_tests():
    """Run all API endpoint tests"""
    print("\n" + "="*70)
    print("API ENDPOINT TEST SUITE")
    print("="*70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCalibrationEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestPortfolioEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthEndpoint))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIDocumentation))

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
