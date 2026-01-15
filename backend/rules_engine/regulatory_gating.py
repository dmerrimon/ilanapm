"""
Regulatory Gating Validator

Validates that timeline includes required regulatory gates/milestones
based on the regulatory authority and that these gates are properly sequenced.

Supports 23 global regulatory authorities.
"""

from typing import List, Dict
from .base_validator import BaseValidator
from backend.models.timeline import Timeline, Task
from backend.models.validation import ValidationIssue, IssueSeverity, IssueCategory


class RegulatoryGatingValidator(BaseValidator):
    """
    Validates regulatory gates are present and properly sequenced

    Checks that timelines include:
    - Required regulatory submissions (IND, CTA, etc.)
    - Ethics committee approvals
    - Authority-specific gates
    - Proper sequencing of regulatory milestones
    """

    @property
    def validator_name(self) -> str:
        return "Regulatory Gating"

    def validate(self, timeline: Timeline) -> List[ValidationIssue]:
        """
        Validate regulatory gates for the timeline

        Args:
            timeline: Timeline to validate

        Returns:
            List of validation issues found
        """
        issues = []

        # Map authority to configuration key
        authority_key = self._map_authority_to_key(timeline.authority)

        # Get authority-specific configuration
        authorities_config = self.config.get('authorities', {})
        authority_config = authorities_config.get(authority_key, {})

        if not authority_config:
            # Authority not in configuration - warn but don't fail
            issues.append(ValidationIssue(
                rule_id="REG-GATE-000",
                severity=IssueSeverity.WARNING,
                category=IssueCategory.REGULATORY,
                message=f"Unknown regulatory authority: {timeline.authority.value}",
                detail=f"Authority '{authority_key}' not found in configuration database. Cannot validate gates.",
                suggested_fix="Use a supported authority or add configuration for this authority",
                confidence=1.0
            ))
            return issues

        # Get required regulatory gates
        gates = authority_config.get('regulatory_gates', [])

        # Validate each required gate
        for gate in gates:
            if gate.get('blocking', False):
                # This gate is mandatory - check if it exists
                self._validate_gate_exists(timeline, gate, authority_config, issues)

        # Validate gate sequencing
        self._validate_gate_sequencing(timeline, gates, issues)

        return issues

    def _validate_gate_exists(
        self,
        timeline: Timeline,
        gate: Dict,
        authority_config: Dict,
        issues: List[ValidationIssue]
    ):
        """
        Validate that a required gate exists in the timeline

        Args:
            timeline: Timeline to check
            gate: Gate configuration dictionary
            authority_config: Authority configuration
            issues: List to append issues to
        """
        gate_name = gate.get('name', '')
        gate_task = self._find_task_by_name(timeline, gate_name, fuzzy=True)

        if not gate_task:
            # Gate is missing - create error
            typical_duration = gate.get('typical_duration_days', 60)
            suggested_fix = self._generate_gate_fix(gate, authority_config)

            issues.append(ValidationIssue(
                rule_id="REG-GATE-001",
                severity=IssueSeverity.ERROR,
                category=IssueCategory.REGULATORY,
                message=f"Missing required gate: {gate_name}",
                detail=f"{authority_config.get('name', 'Authority')} requires '{gate_name}' before study initiation. {gate.get('description', '')}",
                suggested_fix=suggested_fix,
                confidence=1.0,
                regulatory_reference=gate.get('description', ''),
                evidence=[
                    f"Typical duration: {typical_duration} days",
                    f"Required documents: {', '.join(gate.get('required_documents', [])[:3])}"
                ]
            ))
        else:
            # Gate exists - validate its duration
            self._validate_gate_duration(gate_task, gate, authority_config, issues)

    def _validate_gate_duration(
        self,
        task: Task,
        gate: Dict,
        authority_config: Dict,
        issues: List[ValidationIssue]
    ):
        """
        Validate that a gate task has reasonable duration

        Args:
            task: Task representing the gate
            gate: Gate configuration
            authority_config: Authority configuration
            issues: List to append issues to
        """
        typical_duration = gate.get('typical_duration_days', 60)
        min_duration = gate.get('min_duration_days', int(typical_duration * 0.5))

        if task.duration_days < min_duration:
            # Duration is too short
            issues.append(ValidationIssue(
                rule_id="REG-GATE-002",
                severity=IssueSeverity.WARNING,
                category=IssueCategory.REGULATORY,
                task_id=task.id,
                task_name=task.name,
                message=f"Gate duration too short: {task.name}",
                detail=f"Task duration ({task.duration_days} days) is significantly below typical ({typical_duration} days) for {authority_config.get('name', 'this authority')}",
                suggested_fix=f"Increase duration to at least {typical_duration} days to allow adequate review time",
                confidence=0.9,
                evidence=[
                    f"Minimum expected: {min_duration} days",
                    f"Typical for {authority_config.get('country', 'this country')}: {typical_duration} days"
                ]
            ))

    def _validate_gate_sequencing(
        self,
        timeline: Timeline,
        gates: List[Dict],
        issues: List[ValidationIssue]
    ):
        """
        Validate that gates are properly sequenced

        Args:
            timeline: Timeline to validate
            gates: List of gate configurations
            issues: List to append issues to
        """
        # Build a map of gate names to tasks
        gate_tasks = {}
        for gate in gates:
            gate_name = gate.get('name', '')
            task = self._find_task_by_name(timeline, gate_name, fuzzy=True)
            if task:
                gate_tasks[gate_name] = task

        # Check common sequencing requirements
        # Example: Ethics approval should come after regulatory submission

        for i, gate in enumerate(gates):
            if i > 0:  # Not the first gate
                current_gate_name = gate.get('name', '')
                prev_gate_name = gates[i-1].get('name', '')

                current_task = gate_tasks.get(current_gate_name)
                prev_task = gate_tasks.get(prev_gate_name)

                if current_task and prev_task:
                    # Check if there's a dependency
                    has_dep = self._has_dependency(timeline, prev_task.id, current_task.id)

                    if not has_dep:
                        # No dependency - suggest adding one
                        issues.append(ValidationIssue(
                            rule_id="REG-GATE-003",
                            severity=IssueSeverity.INFO,
                            category=IssueCategory.REGULATORY,
                            task_id=current_task.id,
                            task_name=current_task.name,
                            message=f"Consider adding dependency: {prev_gate_name} → {current_gate_name}",
                            detail=f"Typically '{prev_gate_name}' completes before '{current_gate_name}' begins",
                            suggested_fix=f"Add finish-to-start dependency from '{prev_task.name}' to '{current_task.name}'",
                            confidence=0.7
                        ))

    def _generate_gate_fix(self, gate: Dict, authority_config: Dict) -> str:
        """
        Generate a context-aware fix suggestion for missing gate

        Args:
            gate: Gate configuration
            authority_config: Authority configuration

        Returns:
            String with suggested fix
        """
        gate_name = gate.get('name', 'Gate')
        typical_duration = gate.get('typical_duration_days', 60)
        docs = gate.get('required_documents', [])[:2]

        fix = f"Add '{gate_name}' task with {typical_duration} days duration. "

        if docs:
            fix += f"Ensure you have: {', '.join(docs)}. "

        # Add fee information if available
        if 'fees' in gate:
            fees = gate['fees']
            if isinstance(fees, dict):
                fee_items = []
                for key, value in fees.items():
                    if 'local' in key.lower():
                        fee_items.append(f"${value:,} USD (local)")
                    elif 'foreign' in key.lower():
                        fee_items.append(f"${value:,} USD (foreign)")
                    elif 'application' in key.lower():
                        fee_items.append(f"${value:,} USD")

                if fee_items:
                    fix += f"Budget: {' or '.join(fee_items[:2])}."

        return fix


__all__ = ["RegulatoryGatingValidator"]
