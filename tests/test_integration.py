"""
Integration Tests for Ilana PM

Tests complete workflows across multiple modules including:
- Full timeline validation with all validators
- Graph analytics integration
- ML advisory services
- API endpoint integration
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.timeline import (
    Timeline, Task, Dependency,
    StudyPhase, RegulatoryAuthority, TaskCategory
)

client = TestClient(app)


class TestAPIIntegration:
    """Test API endpoints with real workflows"""

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Ilana PM Intelligence API"
        assert data["version"] == "0.1.0"

    def test_validate_endpoint_with_valid_timeline(self):
        """Test validation endpoint with valid timeline"""
        timeline_data = {
            "study_name": "Test Study",
            "phase": "Phase II",
            "authority": "FDA",
            "therapeutic_area": "Oncology",
            "tasks": [
                {
                    "id": "T1",
                    "name": "IND/CTA Submission",
                    "duration_days": 60,
                    "category": "Regulatory",
                    "phase": "Phase II",
                    "authority": "FDA",
                    "is_mandatory": True,
                    "checklist_completion_pct": 100
                },
                {
                    "id": "T2",
                    "name": "IRB Approval",
                    "duration_days": 45,
                    "category": "Regulatory",
                    "phase": "Phase II",
                    "authority": "FDA",
                    "is_mandatory": True,
                    "checklist_completion_pct": 90
                }
            ],
            "dependencies": [
                {"predecessor_id": "T1", "successor_id": "T2", "type": "finish-to-start", "lag_days": 0}
            ]
        }

        response = client.post("/api/v1/validate", json=timeline_data)
        assert response.status_code == 200

        result = response.json()
        assert "status" in result
        assert "issues" in result
        assert "error_count" in result
        assert "warning_count" in result
        assert "info_count" in result
        assert "total_tasks_analyzed" in result
        assert result["total_tasks_analyzed"] == 2

    def test_validate_endpoint_with_errors(self):
        """Test validation endpoint detects errors"""
        timeline_data = {
            "study_name": "Test Study",
            "phase": "Phase II",
            "authority": "FDA",
            "tasks": [
                {
                    "id": "T1",
                    "name": "Task 1",
                    "duration_days": 10,
                    "category": "Operational",
                    "phase": "Phase II",
                    "authority": "FDA"
                },
                {
                    "id": "T2",
                    "name": "Task 2",
                    "duration_days": 20,
                    "category": "Operational",
                    "phase": "Phase II",
                    "authority": "FDA"
                }
            ],
            "dependencies": [
                {"predecessor_id": "T1", "successor_id": "T2"},
                {"predecessor_id": "T2", "successor_id": "T1"}  # Circular dependency!
            ]
        }

        response = client.post("/api/v1/validate", json=timeline_data)
        assert response.status_code == 200

        result = response.json()
        assert result["status"] == "failed"
        assert result["error_count"] > 0

    def test_config_authorities_endpoint(self):
        """Test configuration authorities endpoint"""
        response = client.get("/api/v1/config/authorities")
        assert response.status_code == 200

        authorities = response.json()
        assert isinstance(authorities, list)
        assert len(authorities) > 0

        # Should have FDA, EMA, MHRA
        authority_codes = [a["code"] for a in authorities]
        assert "FDA" in authority_codes
        assert "EMA" in authority_codes
        assert "MHRA" in authority_codes

    def test_config_task_ontology_endpoint(self):
        """Test task ontology endpoint"""
        response = client.get("/api/v1/config/tasks")
        assert response.status_code == 200

        tasks = response.json()
        assert isinstance(tasks, list)
        assert len(tasks) > 0

    def test_config_checklists_endpoint(self):
        """Test checklists configuration endpoint"""
        response = client.get("/api/v1/config/checklists")
        assert response.status_code == 200

        checklists = response.json()
        assert isinstance(checklists, dict)

        # Should have STARTUP checklist
        assert "STARTUP" in checklists

    def test_analytics_critical_path_endpoint(self):
        """Test critical path analytics endpoint"""
        timeline_data = {
            "study_name": "Test Study",
            "phase": "Phase II",
            "authority": "FDA",
            "tasks": [
                {
                    "id": "T1",
                    "name": "Task 1",
                    "duration_days": 30,
                    "category": "Regulatory",
                    "phase": "Phase II",
                    "authority": "FDA"
                },
                {
                    "id": "T2",
                    "name": "Task 2",
                    "duration_days": 45,
                    "category": "Operational",
                    "phase": "Phase II",
                    "authority": "FDA"
                },
                {
                    "id": "T3",
                    "name": "Task 3",
                    "duration_days": 20,
                    "category": "Site",
                    "phase": "Phase II",
                    "authority": "FDA"
                }
            ],
            "dependencies": [
                {"predecessor_id": "T1", "successor_id": "T2"},
                {"predecessor_id": "T2", "successor_id": "T3"}
            ]
        }

        response = client.post("/api/v1/analytics/critical-path", json=timeline_data)
        assert response.status_code == 200

        data = response.json()
        assert "critical_path" in data
        assert "total_duration_days" in data
        assert data["total_duration_days"] == 95  # 30 + 45 + 20

    def test_analytics_slack_endpoint(self):
        """Test slack analysis endpoint"""
        timeline_data = {
            "study_name": "Test Study",
            "phase": "Phase II",
            "authority": "FDA",
            "tasks": [
                {
                    "id": "T1",
                    "name": "Task 1",
                    "duration_days": 30,
                    "category": "Regulatory",
                    "phase": "Phase II",
                    "authority": "FDA"
                },
                {
                    "id": "T2",
                    "name": "Task 2",
                    "duration_days": 45,
                    "category": "Operational",
                    "phase": "Phase II",
                    "authority": "FDA"
                }
            ],
            "dependencies": [
                {"predecessor_id": "T1", "successor_id": "T2"}
            ]
        }

        response = client.post("/api/v1/analytics/slack", json=timeline_data)
        assert response.status_code == 200

        data = response.json()
        assert "slack_by_task" in data
        assert len(data["slack_by_task"]) == 2

        # T1 and T2 should be on critical path (slack = 0)
        for task_slack in data["slack_by_task"]:
            assert task_slack["slack_days"] == 0
            assert task_slack["on_critical_path"] is True

    def test_analytics_parallelization_endpoint(self):
        """Test parallelization opportunities endpoint"""
        timeline_data = {
            "study_name": "Test Study",
            "phase": "Phase II",
            "authority": "FDA",
            "tasks": [
                {
                    "id": "T1",
                    "name": "Task 1",
                    "duration_days": 30,
                    "category": "Regulatory",
                    "phase": "Phase II",
                    "authority": "FDA"
                },
                {
                    "id": "T2",
                    "name": "Task 2",
                    "duration_days": 45,
                    "category": "Site",
                    "phase": "Phase II",
                    "authority": "FDA"
                },
                {
                    "id": "T3",
                    "name": "Task 3",
                    "duration_days": 20,
                    "category": "Site",
                    "phase": "Phase II",
                    "authority": "FDA"
                }
            ],
            "dependencies": [
                {"predecessor_id": "T1", "successor_id": "T3"}
            ]
        }

        response = client.post("/api/v1/analytics/parallelization", json=timeline_data)
        assert response.status_code == 200

        data = response.json()
        assert "opportunities" in data
        # T2 and T3 could potentially run in parallel (both Site, no dependency)

    def test_analytics_summary_endpoint(self):
        """Test analytics summary endpoint"""
        timeline_data = {
            "study_name": "Test Study",
            "phase": "Phase II",
            "authority": "FDA",
            "tasks": [
                {
                    "id": "T1",
                    "name": "Task 1",
                    "duration_days": 30,
                    "category": "Regulatory",
                    "phase": "Phase II",
                    "authority": "FDA"
                }
            ],
            "dependencies": []
        }

        response = client.post("/api/v1/analytics/summary", json=timeline_data)
        assert response.status_code == 200

        data = response.json()
        assert "critical_path" in data
        assert "slack_analysis" in data
        assert "parallelization" in data

    def test_advisory_duration_endpoint(self):
        """Test duration prediction endpoint"""
        task_data = {
            "id": "T1",
            "name": "IND/CTA Submission",
            "duration_days": 45,
            "category": "Regulatory",
            "phase": "Phase II",
            "authority": "FDA",
            "is_mandatory": True,
            "checklist_completion_pct": 100
        }

        response = client.post("/api/v1/advisory/duration", json=task_data)
        assert response.status_code == 200

        data = response.json()
        assert "predicted_duration_days" in data
        assert "confidence_interval" in data
        assert "confidence_score" in data
        assert "explanation" in data

    def test_advisory_risk_endpoint(self):
        """Test risk scoring endpoint"""
        task_data = {
            "id": "T1",
            "name": "IND/CTA Submission",
            "duration_days": 20,  # Very aggressive!
            "category": "Regulatory",
            "phase": "Phase II",
            "authority": "FDA",
            "is_mandatory": True,
            "checklist_completion_pct": 30  # Incomplete!
        }

        response = client.post("/api/v1/advisory/risk", json=task_data)
        assert response.status_code == 200

        data = response.json()
        assert "risk_score" in data
        assert "risk_level" in data
        assert "risk_factors" in data
        assert "mitigation_suggestions" in data

        # Should be high risk
        assert data["risk_score"] > 50
        assert data["risk_level"] in ["high", "critical"]

    def test_advisory_timeline_endpoint(self):
        """Test comprehensive timeline advisory endpoint"""
        timeline_data = {
            "study_name": "Test Study",
            "phase": "Phase II",
            "authority": "FDA",
            "therapeutic_area": "Oncology",
            "tasks": [
                {
                    "id": "T1",
                    "name": "IND/CTA Submission",
                    "duration_days": 45,
                    "category": "Regulatory",
                    "phase": "Phase II",
                    "authority": "FDA",
                    "is_mandatory": True,
                    "checklist_completion_pct": 50
                },
                {
                    "id": "T2",
                    "name": "IRB Approval",
                    "duration_days": 40,
                    "category": "Regulatory",
                    "phase": "Phase II",
                    "authority": "FDA",
                    "is_mandatory": True,
                    "checklist_completion_pct": 80
                }
            ],
            "dependencies": [
                {"predecessor_id": "T1", "successor_id": "T2"}
            ]
        }

        response = client.post("/api/v1/advisory/timeline", json=timeline_data)
        assert response.status_code == 200

        data = response.json()
        assert "study_name" in data
        assert "duration_predictions" in data
        assert "risk_analysis" in data
        assert "summary_statistics" in data
        assert "recommendations" in data

        # Should have predictions for both tasks
        assert len(data["duration_predictions"]["predictions"]) == 2


class TestFullWorkflow:
    """Test complete end-to-end workflows"""

    def test_complete_validation_workflow(self):
        """Test complete validation workflow with all components"""
        # Create a comprehensive timeline
        timeline_data = {
            "study_name": "Phase II Oncology Study",
            "phase": "Phase II",
            "authority": "FDA",
            "therapeutic_area": "Oncology",
            "tasks": [
                {
                    "id": "REG-1",
                    "name": "IND/CTA Submission",
                    "duration_days": 60,
                    "category": "Regulatory",
                    "phase": "Phase II",
                    "authority": "FDA",
                    "is_mandatory": True,
                    "checklist_completion_pct": 100
                },
                {
                    "id": "REG-2",
                    "name": "IRB Approval",
                    "duration_days": 45,
                    "category": "Regulatory",
                    "phase": "Phase II",
                    "authority": "FDA",
                    "is_mandatory": True,
                    "checklist_completion_pct": 90
                },
                {
                    "id": "SITE-1",
                    "name": "Site Identification",
                    "duration_days": 90,
                    "category": "Site",
                    "phase": "Phase II",
                    "authority": "FDA",
                    "checklist_completion_pct": 70
                },
                {
                    "id": "SITE-2",
                    "name": "Site Initiation Visit",
                    "duration_days": 30,
                    "category": "Site",
                    "phase": "Phase II",
                    "authority": "FDA",
                    "checklist_completion_pct": 60
                },
                {
                    "id": "OPS-1",
                    "name": "First Patient In",
                    "duration_days": 1,
                    "category": "Operational",
                    "phase": "Phase II",
                    "authority": "FDA",
                    "is_mandatory": True,
                    "checklist_completion_pct": 100
                }
            ],
            "dependencies": [
                {"predecessor_id": "REG-1", "successor_id": "REG-2"},
                {"predecessor_id": "REG-2", "successor_id": "SITE-1"},
                {"predecessor_id": "SITE-1", "successor_id": "SITE-2"},
                {"predecessor_id": "SITE-2", "successor_id": "OPS-1"}
            ]
        }

        # Step 1: Validate timeline
        validation_response = client.post("/api/v1/validate", json=timeline_data)
        assert validation_response.status_code == 200
        validation_result = validation_response.json()

        # Step 2: Get critical path
        critical_path_response = client.post("/api/v1/analytics/critical-path", json=timeline_data)
        assert critical_path_response.status_code == 200
        critical_path_result = critical_path_response.json()
        assert critical_path_result["total_duration_days"] == 226  # Sum of all tasks

        # Step 3: Get risk analysis
        advisory_response = client.post("/api/v1/advisory/timeline", json=timeline_data)
        assert advisory_response.status_code == 200
        advisory_result = advisory_response.json()

        # Step 4: Get analytics summary
        summary_response = client.post("/api/v1/analytics/summary", json=timeline_data)
        assert summary_response.status_code == 200
        summary_result = summary_response.json()

        # Verify all components worked together
        assert validation_result["total_tasks_analyzed"] == 5
        assert len(critical_path_result["critical_path"]) == 5
        assert len(advisory_result["duration_predictions"]["predictions"]) == 5
        assert len(advisory_result["risk_analysis"]["risk_scores"]) == 5


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_validate_empty_timeline(self):
        """Test validation with empty task list"""
        timeline_data = {
            "study_name": "Empty Study",
            "phase": "Phase II",
            "authority": "FDA",
            "tasks": [],
            "dependencies": []
        }

        response = client.post("/api/v1/validate", json=timeline_data)
        assert response.status_code == 200

        result = response.json()
        assert result["total_tasks_analyzed"] == 0

    def test_validate_invalid_dependency(self):
        """Test validation with invalid dependency reference"""
        timeline_data = {
            "study_name": "Test Study",
            "phase": "Phase II",
            "authority": "FDA",
            "tasks": [
                {
                    "id": "T1",
                    "name": "Task 1",
                    "duration_days": 30,
                    "category": "Operational",
                    "phase": "Phase II",
                    "authority": "FDA"
                }
            ],
            "dependencies": [
                {"predecessor_id": "T1", "successor_id": "T999"}  # Invalid reference
            ]
        }

        response = client.post("/api/v1/validate", json=timeline_data)
        assert response.status_code == 200

        result = response.json()
        # Should have error for invalid dependency
        assert result["error_count"] > 0

    def test_invalid_json(self):
        """Test API with malformed JSON"""
        response = client.post(
            "/api/v1/validate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422  # Unprocessable Entity

    def test_missing_required_fields(self):
        """Test API with missing required fields"""
        timeline_data = {
            "study_name": "Test Study"
            # Missing phase, authority, tasks, dependencies
        }

        response = client.post("/api/v1/validate", json=timeline_data)
        assert response.status_code == 422  # Validation error


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
