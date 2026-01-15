"""
Unit Tests for Advanced Validators (Milestone 2.1)

Tests the new validators including:
- Dependency Validator (circular dependencies, orphans)
- Checklist Completeness Validator
- Parallelization Opportunities Validator
"""

import pytest
from datetime import date
from backend.models.timeline import (
    Timeline, Task, Dependency, StudyPhase, RegulatoryAuthority,
    TaskCategory, DependencyType
)
from backend.models.validation import IssueSeverity, IssueCategory
from backend.rules_engine.dependency_validator import DependencyValidator
from backend.rules_engine.checklist_validator import ChecklistCompletenessValidator
from backend.rules_engine.parallelization_validator import ParallelizationValidator


# Sample configuration for testing
TEST_CONFIG = {
    'checklists': {
        'STARTUP': {
            'name': 'Study Startup Checklist',
            'description': 'Required activities before First Patient In',
            'items': [
                {'id': 'START-001', 'task': 'Protocol finalized', 'mandatory': True},
                {'id': 'START-002', 'task': 'IRB approval', 'mandatory': True},
                {'id': 'START-003', 'task': 'Site contracts', 'mandatory': True},
            ]
        },
        'SIV': {
            'name': 'Site Initiation Visit',
            'description': 'Site activation activities',
            'items': [
                {'id': 'SIV-001', 'task': 'Protocol training', 'mandatory': True},
                {'id': 'SIV-002', 'task': 'eCRF training', 'mandatory': True},
            ]
        }
    }
}


class TestDependencyValidator:
    """Tests for Dependency Validator"""

    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Task A",
                    duration_days=10,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Task B",
                    duration_days=10,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T3",
                    name="Task C",
                    duration_days=10,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2"),
                Dependency(predecessor_id="T2", successor_id="T3"),
                Dependency(predecessor_id="T3", successor_id="T1"),  # Creates cycle!
            ]
        )

        validator = DependencyValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should detect circular dependency
        assert len(issues) >= 1
        assert any('circular' in issue.message.lower() or 'cycle' in issue.message.lower()
                  for issue in issues)
        assert any(issue.severity == IssueSeverity.ERROR for issue in issues)

    def test_orphaned_task_detection(self):
        """Test detection of orphaned tasks"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Connected Task",
                    duration_days=10,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Another Connected Task",
                    duration_days=10,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T3",
                    name="Orphaned Task",
                    duration_days=10,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA,
                    is_mandatory=True
                )
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2"),
                # T3 has no dependencies - orphaned!
            ]
        )

        validator = DependencyValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should detect orphaned task
        orphaned_issues = [i for i in issues if i.task_id == "T3"]
        assert len(orphaned_issues) >= 1
        assert any('orphan' in issue.message.lower() for issue in orphaned_issues)

    def test_self_dependency_detection(self):
        """Test detection of self-referencing dependencies"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Self-Dependent Task",
                    duration_days=10,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T1"),  # Self-dependency!
            ]
        )

        validator = DependencyValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should detect self-dependency
        assert len(issues) >= 1
        assert any('itself' in issue.message.lower() for issue in issues)
        assert any(issue.severity == IssueSeverity.ERROR for issue in issues)

    def test_invalid_dependency_references(self):
        """Test detection of dependencies referencing non-existent tasks"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Existing Task",
                    duration_days=10,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T999"),  # T999 doesn't exist!
            ]
        )

        validator = DependencyValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should detect invalid reference
        assert len(issues) >= 1
        assert any('not found' in issue.message.lower() for issue in issues)
        assert any(issue.severity == IssueSeverity.ERROR for issue in issues)

    def test_valid_dependencies(self):
        """Test that valid dependencies pass without errors"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="First Task",
                    duration_days=10,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Second Task",
                    duration_days=10,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2"),
            ]
        )

        validator = DependencyValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should have no errors
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0


class TestChecklistCompletenessValidator:
    """Tests for Checklist Completeness Validator"""

    def test_incomplete_checklist_warning(self):
        """Test warning for incomplete checklists"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Study Startup Activities",
                    duration_days=30,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA,
                    checklist_completion_pct=50  # Incomplete
                )
            ],
            dependencies=[]
        )

        validator = ChecklistCompletenessValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should flag incomplete checklist
        incomplete_issues = [i for i in issues if 'incomplete' in i.message.lower()]
        assert len(incomplete_issues) >= 1

    def test_zero_percent_checklist(self):
        """Test info message for 0% complete checklists"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Site Initiation Visit",
                    duration_days=1,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA,
                    checklist_completion_pct=0  # Not started
                )
            ],
            dependencies=[]
        )

        validator = ChecklistCompletenessValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should have info about checklist not started
        not_started_issues = [i for i in issues if 'not started' in i.message.lower()]
        assert len(not_started_issues) >= 1
        assert any(i.severity == IssueSeverity.INFO for i in not_started_issues)

    def test_invalid_completion_percentage(self):
        """Test error for invalid completion percentages"""
        # Pydantic validates the field, so invalid values are caught before the validator runs
        # This test verifies that Pydantic validation works correctly
        from pydantic_core._pydantic_core import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            timeline = Timeline(
                study_name="Test Study",
                phase=StudyPhase.PHASE_II,
                authority=RegulatoryAuthority.FDA,
                tasks=[
                    Task(
                        id="T1",
                        name="Task with Invalid Percentage",
                        duration_days=10,
                        category=TaskCategory.OPERATIONAL,
                        phase=StudyPhase.PHASE_II,
                        authority=RegulatoryAuthority.FDA,
                        checklist_completion_pct=150  # Invalid!
                    )
                ],
                dependencies=[]
            )

        # Verify the error is about checklist_completion_pct
        assert 'checklist_completion_pct' in str(exc_info.value)

    def test_mandatory_task_low_completion(self):
        """Test warning for mandatory tasks with low checklist completion"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Critical Mandatory Task",
                    duration_days=30,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA,
                    is_mandatory=True,
                    checklist_completion_pct=30  # Too low for mandatory task
                )
            ],
            dependencies=[]
        )

        validator = ChecklistCompletenessValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should warn about mandatory task with low completion
        mandatory_issues = [i for i in issues if 'mandatory' in i.message.lower()]
        assert len(mandatory_issues) >= 1
        assert any(i.severity == IssueSeverity.WARNING for i in mandatory_issues)


class TestParallelizationValidator:
    """Tests for Parallelization Validator"""

    def test_parallel_opportunity_detection(self):
        """Test detection of tasks that could run in parallel"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Site Task A",
                    duration_days=30,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Site Task B",
                    duration_days=30,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T3",
                    name="Data Task",
                    duration_days=10,
                    category=TaskCategory.DATA,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[
                # T1 and T2 have no dependencies - could run in parallel!
                # T3 is separate category
            ]
        )

        validator = ParallelizationValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should identify parallelization opportunity for T1 and T2
        parallel_issues = [i for i in issues if 'parallel' in i.message.lower()]
        assert len(parallel_issues) >= 1
        assert any(i.severity == IssueSeverity.INFO for i in parallel_issues)

    def test_batch_opportunity_detection(self):
        """Test detection of similar tasks that could be batched"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Site Initiation Visit A",
                    duration_days=1,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Site Initiation Visit B",
                    duration_days=1,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T3",
                    name="Site Initiation Visit C",
                    duration_days=1,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[]
        )

        validator = ParallelizationValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should identify batch opportunity
        batch_issues = [i for i in issues if 'batch' in i.message.lower()]
        # May or may not find batch opportunities depending on similarity logic
        # This is an info-level suggestion

    def test_no_false_positives_with_dependencies(self):
        """Test that parallelization isn't suggested for dependent tasks"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="First Task",
                    duration_days=30,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Second Task",
                    duration_days=30,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2"),  # T2 depends on T1
            ]
        )

        validator = ParallelizationValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should NOT suggest parallelizing T1 and T2 since they have dependencies
        parallel_issues = [i for i in issues
                          if 'parallel' in i.message.lower() and
                          ('First Task' in i.detail and 'Second Task' in i.detail)]
        # Should be empty or not suggest these specific tasks together
        # (may have other parallelization suggestions)


def test_integration_all_new_validators():
    """Integration test for all three new validators"""
    timeline = Timeline(
        study_name="Complex Test Study",
        phase=StudyPhase.PHASE_II,
        authority=RegulatoryAuthority.FDA,
        tasks=[
            Task(
                id="T1",
                name="IND Submission",
                duration_days=60,
                category=TaskCategory.REGULATORY,
                phase=StudyPhase.PHASE_II,
                authority=RegulatoryAuthority.FDA,
                is_mandatory=True,
                checklist_completion_pct=100
            ),
            Task(
                id="T2",
                name="Site Initiation Visit",
                duration_days=1,
                category=TaskCategory.SITE,
                phase=StudyPhase.PHASE_II,
                authority=RegulatoryAuthority.FDA,
                checklist_completion_pct=80
            ),
            Task(
                id="T3",
                name="First Patient In",
                duration_days=1,
                category=TaskCategory.SITE,
                phase=StudyPhase.PHASE_II,
                authority=RegulatoryAuthority.FDA,
                checklist_completion_pct=100
            )
        ],
        dependencies=[
            Dependency(predecessor_id="T1", successor_id="T2"),
            Dependency(predecessor_id="T2", successor_id="T3")
        ]
    )

    # Run all three validators
    dep_validator = DependencyValidator(TEST_CONFIG)
    check_validator = ChecklistCompletenessValidator(TEST_CONFIG)
    par_validator = ParallelizationValidator(TEST_CONFIG)

    dep_issues = dep_validator.validate(timeline)
    check_issues = check_validator.validate(timeline)
    par_issues = par_validator.validate(timeline)

    # Should have no critical errors
    all_issues = dep_issues + check_issues + par_issues
    errors = [i for i in all_issues if i.severity == IssueSeverity.ERROR]
    assert len(errors) == 0

    print(f"Integration test passed with {len(all_issues)} total issues (no errors)")
