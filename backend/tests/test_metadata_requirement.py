"""
Test that study metadata is now required for intelligence validation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from fastapi.testclient import TestClient
from main import app

class TestMetadataRequirement(unittest.TestCase):
    """Test that study metadata is enforced"""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_validate_metadata_endpoint_exists(self):
        """Test that /validate-metadata endpoint exists"""
        response = self.client.post(
            "/api/v1/intelligence/validate-metadata",
            json={
                "phase": "Phase III",
                "therapeutic_area": "Oncology",
                "primary_country": "US"
            }
        )

        # Should return 200 or 401 (auth), not 404
        self.assertIn(response.status_code, [200, 401])

    def test_validate_metadata_with_valid_data(self):
        """Test metadata validation with valid study metadata"""
        response = self.client.post(
            "/api/v1/intelligence/validate-metadata",
            json={
                "phase": "Phase III",
                "therapeutic_area": "Oncology",
                "primary_country": "US",
                "study_name": "CART-01 Phase III Trial"
            }
        )

        # Should succeed (200) or require auth (401)
        self.assertIn(response.status_code, [200, 401])

        if response.status_code == 200:
            data = response.json()
            self.assertIn("is_valid", data)
            self.assertIn("coverage_percent", data)
            self.assertIn("benchmarks_available", data)

    def test_validate_metadata_missing_phase(self):
        """Test that missing phase is caught"""
        response = self.client.post(
            "/api/v1/intelligence/validate-metadata",
            json={
                "therapeutic_area": "Oncology",
                "primary_country": "US"
            }
        )

        # Should return 422 (validation error)
        self.assertEqual(response.status_code, 422)

    def test_validate_metadata_missing_therapeutic_area(self):
        """Test that missing therapeutic_area is caught"""
        response = self.client.post(
            "/api/v1/intelligence/validate-metadata",
            json={
                "phase": "Phase III",
                "primary_country": "US"
            }
        )

        # Should return 422 (validation error)
        self.assertEqual(response.status_code, 422)

    def test_validate_metadata_missing_country(self):
        """Test that missing primary_country is caught"""
        response = self.client.post(
            "/api/v1/intelligence/validate-metadata",
            json={
                "phase": "Phase III",
                "therapeutic_area": "Oncology"
            }
        )

        # Should return 422 (validation error)
        self.assertEqual(response.status_code, 422)

    def test_study_metadata_model_validation(self):
        """Test StudyMetadata model validation logic"""
        from intelligence import StudyMetadata

        # Valid metadata
        valid_metadata = StudyMetadata(
            phase="Phase III",
            therapeutic_area="Oncology",
            primary_country="US"
        )
        self.assertTrue(valid_metadata.validate_required_fields())

        # Missing phase
        invalid_metadata = StudyMetadata(
            phase="",
            therapeutic_area="Oncology",
            primary_country="US"
        )
        self.assertFalse(invalid_metadata.validate_required_fields())


def run_tests():
    """Run all metadata requirement tests"""
    print("\n" + "="*70)
    print("METADATA REQUIREMENT TEST SUITE")
    print("="*70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestMetadataRequirement))

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
    if result.testsRun > 0:
        print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_tests())
