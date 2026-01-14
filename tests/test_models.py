"""
Tests for Pydantic data models
"""

import pytest
from datetime import date
from backend.models.timeline import (
    Timeline, Task, Dependency, StudyPhase, RegulatoryAuthority,
    TaskCategory, GatingStatus, DependencyType
)
from backend.models.validation import (
    ValidationResult, ValidationIssue, Recommendation,
    IssueSeverity, IssueCategory, ValidationStatus
)


class TestTaskModel:
    """Tests for Task model"""

    def test_task_creation_minimal(self):
        """Test creating a task with minimal required fields"""
        task = Task(
            id="T001",
            name="IND Submission",
            duration_days=60,
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA
        )

        assert task.id == "T001"
        assert task.name == "IND Submission"
        assert task.duration_days == 60
        assert task.category == TaskCategory.REGULATORY
        assert task.is_mandatory == False  # default
        assert task.checklist_completion_pct == 0  # default

    def test_task_creation_full(self):
        """Test creating a task with all fields"""
        task = Task(
            id="T002",
            name="Site Initiation Visit",
            duration_days=1,
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 1),
            category=TaskCategory.SITE,
            phase=StudyPhase.PHASE_III,
            authority=RegulatoryAuthority.EMA,
            therapeutic_area="Oncology",
            is_mandatory=True,
            gating_status=GatingStatus.READY,
            checklist_completion_pct=85,
            risk_score=25,
            ml_predicted_duration="1-2 days",
            ml_confidence_pct=90,
            notes="SIV for Site 001"
        )

        assert task.therapeutic_area == "Oncology"
        assert task.gating_status == GatingStatus.READY
        assert task.risk_score == 25
        assert task.ml_confidence_pct == 90

    def test_task_validation_duration_negative(self):
        """Test that negative duration fails validation"""
        with pytest.raises(ValueError):
            Task(
                id="T003",
                name="Invalid Task",
                duration_days=-5,  # Invalid
                category=TaskCategory.OPERATIONAL,
                phase=StudyPhase.PHASE_I,
                authority=RegulatoryAuthority.FDA
            )

    def test_task_validation_checklist_pct(self):
        """Test that checklist percentage is bounded 0-100"""
        with pytest.raises(ValueError):
            Task(
                id="T004",
                name="Invalid Checklist",
                duration_days=10,
                category=TaskCategory.OPERATIONAL,
                phase=StudyPhase.PHASE_I,
                authority=RegulatoryAuthority.FDA,
                checklist_completion_pct=150  # Invalid
            )


class TestDependencyModel:
    """Tests for Dependency model"""

    def test_dependency_creation(self):
        """Test creating a dependency"""
        dep = Dependency(
            predecessor_id="T001",
            successor_id="T002",
            type=DependencyType.FINISH_TO_START,
            lag_days=0
        )

        assert dep.predecessor_id == "T001"
        assert dep.successor_id == "T002"
        assert dep.type == DependencyType.FINISH_TO_START
        assert dep.lag_days == 0

    def test_dependency_with_lag(self):
        """Test dependency with lag time"""
        dep = Dependency(
            predecessor_id="T001",
            successor_id="T003",
            lag_days=30  # 30-day lag
        )

        assert dep.lag_days == 30

    def test_dependency_with_lead(self):
        """Test dependency with lead time (negative lag)"""
        dep = Dependency(
            predecessor_id="T001",
            successor_id="T004",
            lag_days=-14  # 14-day lead
        )

        assert dep.lag_days == -14


class TestTimelineModel:
    """Tests for Timeline model"""

    def test_timeline_creation_minimal(self):
        """Test creating a timeline with minimal data"""
        task1 = Task(
            id="T001",
            name="IND Submission",
            duration_days=60,
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA
        )

        timeline = Timeline(
            study_name="ABC-123 Phase II Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[task1]
        )

        assert timeline.study_name == "ABC-123 Phase II Study"
        assert timeline.phase == StudyPhase.PHASE_II
        assert len(timeline.tasks) == 1
        assert len(timeline.dependencies) == 0  # default

    def test_timeline_with_dependencies(self):
        """Test timeline with tasks and dependencies"""
        task1 = Task(
            id="T001",
            name="IND Submission",
            duration_days=60,
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA
        )

        task2 = Task(
            id="T002",
            name="IRB Approval",
            duration_days=45,
            category=TaskCategory.REGULATORY,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA
        )

        dep = Dependency(
            predecessor_id="T001",
            successor_id="T002",
            type=DependencyType.FINISH_TO_START
        )

        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[task1, task2],
            dependencies=[dep]
        )

        assert len(timeline.tasks) == 2
        assert len(timeline.dependencies) == 1
        assert timeline.dependencies[0].predecessor_id == "T001"


class TestValidationModels:
    """Tests for validation models"""

    def test_validation_issue_creation(self):
        """Test creating a validation issue"""
        issue = ValidationIssue(
            rule_id="REG-GATE-001",
            severity=IssueSeverity.ERROR,
            category=IssueCategory.REGULATORY,
            task_id="T001",
            task_name="IND Submission",
            message="Missing required regulatory gate",
            detail="FDA requires IND submission before enrollment",
            suggested_fix="Add IND Submission task before First Patient In",
            confidence=1.0
        )

        assert issue.rule_id == "REG-GATE-001"
        assert issue.severity == IssueSeverity.ERROR
        assert issue.category == IssueCategory.REGULATORY
        assert issue.confidence == 1.0

    def test_validation_result_passed(self):
        """Test validation result with no issues"""
        result = ValidationResult(
            status=ValidationStatus.PASSED,
            issues=[],
            total_tasks_analyzed=5
        )

        assert result.status == ValidationStatus.PASSED
        assert result.error_count == 0
        assert result.warning_count == 0
        assert len(result.issues) == 0

    def test_validation_result_with_issues(self):
        """Test validation result with errors and warnings"""
        issue1 = ValidationIssue(
            rule_id="DUR-001",
            severity=IssueSeverity.WARNING,
            category=IssueCategory.DURATION,
            message="Duration too short",
            detail="Task duration is below recommended minimum",
            suggested_fix="Increase duration"
        )

        issue2 = ValidationIssue(
            rule_id="DEP-001",
            severity=IssueSeverity.ERROR,
            category=IssueCategory.DEPENDENCIES,
            message="Circular dependency",
            detail="Tasks have circular dependency",
            suggested_fix="Remove one dependency"
        )

        result = ValidationResult(
            status=ValidationStatus.FAILED,
            issues=[issue1, issue2],
            error_count=1,
            warning_count=1,
            total_tasks_analyzed=10
        )

        assert result.status == ValidationStatus.FAILED
        assert result.error_count == 1
        assert result.warning_count == 1
        assert len(result.issues) == 2

    def test_recommendation_creation(self):
        """Test creating a recommendation"""
        rec = Recommendation(
            recommendation_id="PAR-001",
            type="parallelization",
            task_ids=["T005", "T006"],
            title="Parallelize site contracts",
            description="These tasks can run in parallel",
            benefit="Save 30 days on critical path",
            impact_days=30,
            confidence=0.9
        )

        assert rec.recommendation_id == "PAR-001"
        assert rec.type == "parallelization"
        assert len(rec.task_ids) == 2
        assert rec.impact_days == 30


class TestEnums:
    """Tests for enum types"""

    def test_study_phase_enum(self):
        """Test StudyPhase enum"""
        assert StudyPhase.PHASE_I.value == "Phase I"
        assert StudyPhase.PHASE_II.value == "Phase II"
        assert StudyPhase.PHASE_III.value == "Phase III"

    def test_regulatory_authority_enum(self):
        """Test RegulatoryAuthority enum"""
        assert RegulatoryAuthority.FDA.value == "FDA"
        assert RegulatoryAuthority.EMA.value == "EMA"
        assert RegulatoryAuthority.MHRA.value == "MHRA"

    def test_task_category_enum(self):
        """Test TaskCategory enum"""
        assert TaskCategory.REGULATORY.value == "Regulatory"
        assert TaskCategory.OPERATIONAL.value == "Operational"
        assert TaskCategory.SITE.value == "Site"

    def test_issue_severity_enum(self):
        """Test IssueSeverity enum"""
        assert IssueSeverity.ERROR.value == "error"
        assert IssueSeverity.WARNING.value == "warning"
        assert IssueSeverity.INFO.value == "info"


class TestModelSerialization:
    """Tests for JSON serialization"""

    def test_timeline_to_json(self):
        """Test that timeline can be serialized to JSON"""
        task = Task(
            id="T001",
            name="Test Task",
            duration_days=30,
            category=TaskCategory.OPERATIONAL,
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA
        )

        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[task]
        )

        # Test model_dump (Pydantic v2)
        json_data = timeline.model_dump()
        assert json_data["study_name"] == "Test Study"
        assert json_data["phase"] == "Phase II"
        assert len(json_data["tasks"]) == 1

    def test_timeline_from_json(self):
        """Test that timeline can be deserialized from JSON"""
        json_data = {
            "study_name": "Test Study",
            "phase": "Phase II",
            "authority": "FDA",
            "tasks": [
                {
                    "id": "T001",
                    "name": "Test Task",
                    "duration_days": 30,
                    "category": "Operational",
                    "phase": "Phase II",
                    "authority": "FDA"
                }
            ]
        }

        timeline = Timeline(**json_data)
        assert timeline.study_name == "Test Study"
        assert len(timeline.tasks) == 1
        assert timeline.tasks[0].name == "Test Task"
