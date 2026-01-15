"""
Operational Sequences Validator

Validates logical task prerequisites and operational dependencies.
Ensures that tasks follow proper operational sequences (e.g., site contracts
must be executed before site initiation visits).
"""

from typing import List, Dict
from .base_validator import BaseValidator
from backend.models.timeline import Timeline, Task
from backend.models.validation import ValidationIssue, IssueSeverity, IssueCategory


class OperationalSequencesValidator(BaseValidator):
    """
    Validates operational task sequencing and prerequisites

    Checks that:
    - Tasks have logical prerequisites (e.g., approval before enrollment)
    - Dependencies reflect operational reality
    - Critical sequences are properly defined
    """

    @property
    def validator_name(self) -> str:
        return "Operational Sequences"

    def validate(self, timeline: Timeline) -> List[ValidationIssue]:
        """
        Validate operational sequences in the timeline

        Args:
            timeline: Timeline to validate

        Returns:
            List of validation issues found
        """
        issues = []

        # Get operational sequences from configuration
        sequences = self.config.get('operational_sequences', [])

        # Validate each sequence
        for sequence in sequences:
            # Check if this sequence applies to the timeline
            if self._sequence_applies(sequence, timeline):
                self._validate_sequence(sequence, timeline, issues)

        return issues

    def _sequence_applies(self, sequence: Dict, timeline: Timeline) -> bool:
        """
        Check if a sequence applies to this timeline

        Args:
            sequence: Sequence configuration
            timeline: Timeline to check

        Returns:
            True if sequence applies, False otherwise
        """
        # Check if sequence has authority restrictions
        if 'authority' in sequence:
            seq_authority = sequence['authority']
            timeline_authority = timeline.authority.value

            if seq_authority != timeline_authority and seq_authority != 'all':
                return False

        # Check if sequence has phase restrictions
        if 'phase' in sequence:
            seq_phase = sequence['phase']
            timeline_phase = timeline.phase.value

            if seq_phase != timeline_phase and seq_phase != 'all':
                return False

        return True

    def _validate_sequence(
        self,
        sequence: Dict,
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Validate a single operational sequence

        Args:
            sequence: Sequence configuration
            timeline: Timeline to validate
            issues: List to append issues to
        """
        sequence_name = sequence.get('name', 'Sequence')
        criticality = sequence.get('criticality', 'medium')

        # Get rules for this sequence
        rules = sequence.get('rules', [])

        for rule in rules:
            self._validate_sequence_rule(rule, sequence_name, criticality, timeline, issues)

    def _validate_sequence_rule(
        self,
        rule: Dict,
        sequence_name: str,
        criticality: str,
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Validate a single sequence rule

        Args:
            rule: Rule configuration
            sequence_name: Name of parent sequence
            criticality: Criticality level (critical, high, medium, low)
            timeline: Timeline to validate
            issues: List to append issues to
        """
        predecessor_name = rule.get('predecessor', '')
        successor_name = rule.get('successor', '')
        rationale = rule.get('rationale', 'Operational dependency')
        optional = rule.get('optional', False)

        # Find the tasks
        predecessor_task = self._find_task_by_name(timeline, predecessor_name, fuzzy=True)
        successor_task = self._find_task_by_name(timeline, successor_name, fuzzy=True)

        # Determine severity based on criticality and whether rule is optional
        if criticality == 'critical' and not optional:
            severity = IssueSeverity.ERROR
        elif criticality == 'high' or (criticality == 'critical' and optional):
            severity = IssueSeverity.WARNING
        else:
            severity = IssueSeverity.INFO

        if predecessor_task and successor_task:
            # Both tasks exist - check if dependency exists
            has_dependency = self._has_dependency(timeline, predecessor_task.id, successor_task.id)

            if not has_dependency and not optional:
                issues.append(ValidationIssue(
                    rule_id="SEQ-001",
                    severity=severity,
                    category=IssueCategory.OPERATIONAL,
                    task_id=successor_task.id,
                    task_name=successor_task.name,
                    message=f"Missing logical dependency: {predecessor_name} → {successor_name}",
                    detail=f"Sequence '{sequence_name}': {rationale}",
                    suggested_fix=f"Add finish-to-start dependency from '{predecessor_task.name}' to '{successor_task.name}'",
                    confidence=0.8,
                    evidence=[f"Part of {sequence_name}"]
                ))

            # Check lag time if dependency exists
            elif has_dependency:
                lag_days = rule.get('lag_days', 0)
                if lag_days > 0:
                    # Check if actual lag matches recommended lag
                    actual_lag = self._get_dependency_lag(timeline, predecessor_task.id, successor_task.id)
                    if actual_lag is not None and actual_lag < lag_days:
                        issues.append(ValidationIssue(
                            rule_id="SEQ-002",
                            severity=IssueSeverity.INFO,
                            category=IssueCategory.OPERATIONAL,
                            task_id=successor_task.id,
                            task_name=successor_task.name,
                            message=f"Dependency lag may be insufficient: {predecessor_name} → {successor_name}",
                            detail=f"Actual lag ({actual_lag} days) is less than recommended ({lag_days} days). {rationale}",
                            suggested_fix=f"Consider increasing lag to {lag_days} days",
                            confidence=0.6
                        ))

        elif successor_task and not predecessor_task and not optional:
            # Successor exists but prerequisite is missing
            issues.append(ValidationIssue(
                rule_id="SEQ-003",
                severity=severity,
                category=IssueCategory.OPERATIONAL,
                task_id=successor_task.id,
                task_name=successor_task.name,
                message=f"Missing prerequisite task: {predecessor_name}",
                detail=f"Task '{successor_name}' requires '{predecessor_name}' to be completed first. {rationale}",
                suggested_fix=f"Add '{predecessor_name}' task before '{successor_name}'",
                confidence=0.9,
                evidence=[f"Part of {sequence_name}"]
            ))

        elif predecessor_task and not successor_task and not optional:
            # Predecessor exists but successor is missing
            # This might be okay (not all sequences must be complete)
            # Only flag if criticality is high
            if criticality in ['critical', 'high']:
                issues.append(ValidationIssue(
                    rule_id="SEQ-004",
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.OPERATIONAL,
                    task_id=predecessor_task.id,
                    task_name=predecessor_task.name,
                    message=f"Incomplete sequence: missing {successor_name}",
                    detail=f"Found '{predecessor_name}' but '{successor_name}' is missing. {rationale}",
                    suggested_fix=f"Add '{successor_name}' task after '{predecessor_name}'",
                    confidence=0.6,
                    evidence=[f"Part of {sequence_name}"]
                ))

    def _get_dependency_lag(self, timeline: Timeline, predecessor_id: str, successor_id: str) -> int:
        """
        Get the lag time for a specific dependency

        Args:
            timeline: Timeline to search
            predecessor_id: Predecessor task ID
            successor_id: Successor task ID

        Returns:
            Lag time in days, or None if dependency not found
        """
        for dep in timeline.dependencies:
            if dep.predecessor_id == predecessor_id and dep.successor_id == successor_id:
                return dep.lag_days
        return None


__all__ = ["OperationalSequencesValidator"]
