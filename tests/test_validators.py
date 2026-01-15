"""
Unit Tests for Timeline Validators

Tests the rules engine validators including:
- Regulatory Gating Validator
- Duration Bounds Validator
- Operational Sequences Validator
"""

import pytest
from datetime import date
from backend.models.timeline import (
    Timeline, Task, Dependency, StudyPhase, RegulatoryAuthority,
    TaskCategory, GatingStatus, DependencyType
)
from backend.models.validation import IssueSeverity, IssueCategory
from backend.rules_engine.regulatory_gating import RegulatoryGatingValidator
from backend.rules_engine.duration_bounds import DurationBoundsValidator
from backend.rules_engine.operational_sequences import OperationalSequencesValidator


# Sample configuration for testing
TEST_CONFIG = {
    'authorities': {
        'MCAZ_ZW': {
            'name': 'Medicines Control Authority of Zimbabwe',
            'country': 'Zimbabwe',
            'regulatory_gates': [
                {
                    'gate_id': 'MCAZ_ZW-CTA',
                    'name': 'Clinical Trial Authorization',
                    'typical_duration_days': 60,
                    'min_duration_days': 30,
                    'description': 'MCAZ review and authorization',
                    'blocking': True,
                    'required_documents': ['Protocol', 'IB', 'ICF']
                },
                {
                    'gate_id': 'MCAZ_ZW-ETHICS',
                    'name': 'MRCZ Ethical Approval',
                    'typical_duration_days': 45,
                    'blocking': True
                }
            ]
        },
        'FDA': {
            'name': 'U.S. Food and Drug Administration',
            'regulatory_gates': [
                {
                    'gate_id': 'FDA-IND',
                    'name': 'IND Submission',
                    'typical_duration_days': 60,
                    'min_duration_days': 30,
                    'blocking': True
                }
            ]
        }
    },
    'task_ontology': [
        {
            'id': 'REG-001',
            'name': 'IND Submission',
            'category': 'Regulatory',
            'typical_duration_days': 60,
            'min_duration_days': 30,
            'max_duration_days': 90
        },
        {
            'id': 'SITE-001',
            'name': 'Site Initiation Visit',
            'category': 'Site',
            'typical_duration_days': 1,
            'min_duration_days': 1,
            'max_duration_days': 2
        }
    ],
    'operational_sequences': [
        {
            'name': 'Regulatory Gating Sequence',
            'criticality': 'critical',
            'rules': [
                {
                    'predecessor': 'IND Submission',
                    'successor': 'First Patient In',
                    'rationale': 'Cannot enroll without regulatory approval',
                    'optional': False
                }
            ]
        }
    ],
    'duration_bounds': []
}


class TestRegulatoryGatingValidator:
    """Tests for Regulatory Gating Validator"""

    def test_missing_regulatory_gate_zimbabwe(self):
        """Test detection of missing MCAZ gate"""
        timeline = Timeline(
            study_name="Zimbabwe Phase II Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.MCAZ_ZW,
            tasks=[
                Task(
                    id="T1",
                    name="First Patient In",
                    duration_days=1,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.MCAZ_ZW
                )
            ],
            dependencies=[]
        )

        validator = RegulatoryGatingValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should flag missing MCAZ CTA and MRCZ Ethics gates
        assert len(issues) >= 2
        assert any('Clinical Trial Authorization' in issue.message or 'Authorization' in issue.message for issue in issues)
        assert any(issue.severity == IssueSeverity.ERROR for issue in issues)

    def test_gate_exists_with_valid_duration(self):
        """Test that existing gate with valid duration passes"""
        timeline = Timeline(
            study_name="Zimbabwe Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.MCAZ_ZW,
            tasks=[
                Task(
                    id="T1",
                    name="Clinical Trial Authorization",
                    duration_days=60,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.MCAZ_ZW
                ),
                Task(
                    id="T2",
                    name="MRCZ Ethical Approval",
                    duration_days=45,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.MCAZ_ZW
                )
            ],
            dependencies=[]
        )

        validator = RegulatoryGatingValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should have no errors (may have info about sequencing)
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0

    def test_gate_duration_too_short(self):
        """Test detection of unrealistically short gate duration"""
        timeline = Timeline(
            study_name="Zimbabwe Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.MCAZ_ZW,
            tasks=[
                Task(
                    id="T1",
                    name="Clinical Trial Authorization",
                    duration_days=10,  # Too short!
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.MCAZ_ZW
                ),
                Task(
                    id="T2",
                    name="MRCZ Ethics",
                    duration_days=45,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.MCAZ_ZW
                )
            ],
            dependencies=[]
        )

        validator = RegulatoryGatingValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should warn about short duration
        warnings = [i for i in issues if i.severity == IssueSeverity.WARNING and 'short' in i.message.lower()]
        assert len(warnings) >= 1

    def test_unknown_authority_warning(self):
        """Test that unknown authority generates warning"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.PMDA,  # Not in TEST_CONFIG
            tasks=[],
            dependencies=[]
        )

        validator = RegulatoryGatingValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should warn about unknown authority
        assert len(issues) == 1
        assert issues[0].severity == IssueSeverity.WARNING
        assert 'Unknown' in issues[0].message or 'unknown' in issues[0].message


class TestDurationBoundsValidator:
    """Tests for Duration Bounds Validator"""

    def test_duration_below_minimum(self):
        """Test detection of duration below minimum"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="IND Submission",
                    duration_days=15,  # Below 30-day minimum
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[]
        )

        validator = DurationBoundsValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should flag duration as too short
        assert len(issues) >= 1
        assert any('below' in i.message.lower() or 'short' in i.message.lower() for i in issues)
        assert any(i.task_id == "T1" for i in issues)

    def test_duration_above_maximum(self):
        """Test detection of duration above maximum"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="IND Submission",
                    duration_days=120,  # Above 90-day maximum
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[]
        )

        validator = DurationBoundsValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should flag duration as too long (info level)
        assert len(issues) >= 1
        assert any('exceed' in i.message.lower() or 'long' in i.message.lower() for i in issues)

    def test_valid_duration_no_issues(self):
        """Test that valid durations pass without issues"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="IND Submission",
                    duration_days=60,  # Valid
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Site Initiation Visit",
                    duration_days=1,  # Valid
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[]
        )

        validator = DurationBoundsValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should have no critical issues
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0


class TestOperationalSequencesValidator:
    """Tests for Operational Sequences Validator"""

    def test_missing_prerequisite_task(self):
        """Test detection of missing prerequisite"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="First Patient In",
                    duration_days=1,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
                # Missing IND Submission!
            ],
            dependencies=[]
        )

        validator = OperationalSequencesValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should flag missing IND Submission
        assert len(issues) >= 1
        assert any('IND' in issue.message or 'prerequisite' in issue.message.lower() for issue in issues)

    def test_missing_dependency_between_existing_tasks(self):
        """Test detection of missing dependency"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="IND Submission",
                    duration_days=60,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="First Patient In",
                    duration_days=1,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[]  # No dependency defined!
        )

        validator = OperationalSequencesValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should suggest adding dependency
        assert len(issues) >= 1
        assert any('dependency' in issue.message.lower() for issue in issues)

    def test_valid_sequence_with_dependency(self):
        """Test that properly sequenced tasks pass"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="IND Submission",
                    duration_days=60,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="First Patient In",
                    duration_days=1,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                )
            ],
            dependencies=[
                Dependency(
                    predecessor_id="T1",
                    successor_id="T2",
                    type=DependencyType.FINISH_TO_START
                )
            ]
        )

        validator = OperationalSequencesValidator(TEST_CONFIG)
        issues = validator.validate(timeline)

        # Should have no critical errors
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0


def test_integration_all_validators():
    """Integration test running all validators together"""
    timeline = Timeline(
        study_name="Zimbabwe Phase II Study",
        phase=StudyPhase.PHASE_II,
        authority=RegulatoryAuthority.MCAZ_ZW,
        tasks=[
            Task(
                id="T1",
                name="Clinical Trial Authorization",
                duration_days=60,
                category=TaskCategory.REGULATORY,
                phase=StudyPhase.PHASE_II,
                authority=RegulatoryAuthority.MCAZ_ZW
            ),
            Task(
                id="T2",
                name="MRCZ Ethical Approval",
                duration_days=45,
                category=TaskCategory.REGULATORY,
                phase=StudyPhase.PHASE_II,
                authority=RegulatoryAuthority.MCAZ_ZW
            ),
            Task(
                id="T3",
                name="IND Submission",
                duration_days=60,
                category=TaskCategory.REGULATORY,
                phase=StudyPhase.PHASE_II,
                authority=RegulatoryAuthority.MCAZ_ZW
            ),
            Task(
                id="T4",
                name="First Patient In",
                duration_days=1,
                category=TaskCategory.SITE,
                phase=StudyPhase.PHASE_II,
                authority=RegulatoryAuthority.MCAZ_ZW
            )
        ],
        dependencies=[
            Dependency(predecessor_id="T1", successor_id="T2"),
            Dependency(predecessor_id="T2", successor_id="T3"),
            Dependency(predecessor_id="T3", successor_id="T4")
        ]
    )

    # Run all validators
    reg_validator = RegulatoryGatingValidator(TEST_CONFIG)
    dur_validator = DurationBoundsValidator(TEST_CONFIG)
    seq_validator = OperationalSequencesValidator(TEST_CONFIG)

    reg_issues = reg_validator.validate(timeline)
    dur_issues = dur_validator.validate(timeline)
    seq_issues = seq_validator.validate(timeline)

    all_issues = reg_issues + dur_issues + seq_issues

    # Should have no critical errors
    errors = [i for i in all_issues if i.severity == IssueSeverity.ERROR]
    assert len(errors) == 0

    print(f"Integration test passed with {len(all_issues)} total issues (no errors)")
