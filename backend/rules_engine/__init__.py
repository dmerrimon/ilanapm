"""
Rules Engine for Clinical Trial Timeline Validation

Provides a framework for validating clinical trial timelines against
regulatory requirements, operational best practices, and historical data.
"""

from typing import List, Dict
from backend.models.timeline import Timeline
from backend.models.validation import ValidationIssue, ValidationResult, ValidationStatus


class RulesEngine:
    """Main rules engine orchestrating all validators"""

    def __init__(self, config: Dict):
        """
        Initialize rules engine with configuration

        Args:
            config: Dictionary containing YAML configuration data
        """
        self.config = config
        self.validators = []

        # Import and register validators
        self._register_validators()

    def _register_validators(self):
        """Register all available validators"""
        from .regulatory_gating import RegulatoryGatingValidator
        from .duration_bounds import DurationBoundsValidator
        from .operational_sequences import OperationalSequencesValidator
        from .dependency_validator import DependencyValidator
        from .checklist_validator import ChecklistCompletenessValidator
        from .parallelization_validator import ParallelizationValidator

        self.validators = [
            RegulatoryGatingValidator(self.config),
            DurationBoundsValidator(self.config),
            OperationalSequencesValidator(self.config),
            DependencyValidator(self.config),
            ChecklistCompletenessValidator(self.config),
            ParallelizationValidator(self.config),
        ]

    def validate_timeline(self, timeline: Timeline) -> ValidationResult:
        """
        Run all validators on a timeline and return aggregated results

        Args:
            timeline: Timeline object to validate

        Returns:
            ValidationResult with all issues found
        """
        all_issues = []
        validators_run = []

        # Run each validator
        for validator in self.validators:
            try:
                issues = validator.validate(timeline)
                all_issues.extend(issues)
                validators_run.append(validator.validator_name)
            except Exception as e:
                # Log validation error but continue
                print(f"Warning: Validator {validator.validator_name} failed: {e}")

        # Count issues by severity
        error_count = sum(1 for i in all_issues if i.severity == "error")
        warning_count = sum(1 for i in all_issues if i.severity == "warning")
        info_count = sum(1 for i in all_issues if i.severity == "info")

        # Determine overall status
        if error_count > 0:
            status = ValidationStatus.FAILED
        elif warning_count > 0:
            status = ValidationStatus.WARNINGS
        else:
            status = ValidationStatus.PASSED

        # Sort issues by severity (errors first, then warnings, then info)
        severity_order = {"error": 0, "warning": 1, "info": 2}
        all_issues.sort(key=lambda x: severity_order.get(x.severity.value, 999))

        return ValidationResult(
            status=status,
            issues=all_issues,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            total_tasks_analyzed=len(timeline.tasks),
            validators_run=validators_run
        )


__all__ = ["RulesEngine"]
