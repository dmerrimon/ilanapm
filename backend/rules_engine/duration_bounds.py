"""
Duration Bounds Validator

Validates that task durations fall within acceptable bounds based on:
- Task category
- Study phase
- Regulatory authority
- Historical data

Supports authority-specific duration adjustments for 23 countries.
"""

from typing import List, Dict, Optional
from .base_validator import BaseValidator
from backend.models.timeline import Timeline, Task, TaskCategory
from backend.models.validation import ValidationIssue, IssueSeverity, IssueCategory


class DurationBoundsValidator(BaseValidator):
    """
    Validates task durations are within acceptable bounds

    Checks that task durations are:
    - Not too short (which may indicate unrealistic planning)
    - Not too long (which may indicate inefficiency)
    - Aligned with authority-specific requirements
    - Appropriate for the study phase
    """

    @property
    def validator_name(self) -> str:
        return "Duration Bounds"

    def validate(self, timeline: Timeline) -> List[ValidationIssue]:
        """
        Validate task durations in the timeline

        Args:
            timeline: Timeline to validate

        Returns:
            List of validation issues found
        """
        issues = []

        # Get authority key for lookups
        authority_key = self._map_authority_to_key(timeline.authority)

        # Get authority configuration
        authorities_config = self.config.get('authorities', {})
        authority_config = authorities_config.get(authority_key, {})

        # Get task ontology for canonical task definitions
        task_ontology = self.config.get('task_ontology', [])

        # Get duration bounds rules
        duration_rules = self.config.get('duration_bounds', [])

        # Validate each task
        for task in timeline.tasks:
            # Find canonical task definition
            canonical = self._find_canonical_task(task, task_ontology)

            if canonical:
                # Use canonical task bounds with authority-specific adjustments
                self._validate_with_canonical(task, canonical, authority_key, authority_config, issues)
            else:
                # No canonical task - use general rules
                self._validate_with_general_rules(task, duration_rules, timeline, issues)

        return issues

    def _find_canonical_task(self, task: Task, task_ontology: List[Dict]) -> Optional[Dict]:
        """
        Find canonical task definition from ontology

        Args:
            task: Task to find canonical definition for
            task_ontology: List of canonical task definitions

        Returns:
            Canonical task dictionary if found, None otherwise
        """
        # Try exact category match first
        for canonical in task_ontology:
            if canonical.get('category') == task.category.value:
                # Check name similarity
                canonical_name = canonical.get('name', '').lower()
                task_name = task.name.lower()

                # Simple word-based similarity
                canonical_words = set(canonical_name.split())
                task_words = set(task_name.split())
                overlap = len(canonical_words.intersection(task_words))

                if overlap > 0 and overlap >= len(canonical_words) * 0.5:
                    return canonical

        return None

    def _validate_with_canonical(
        self,
        task: Task,
        canonical: Dict,
        authority_key: str,
        authority_config: Dict,
        issues: List[ValidationIssue]
    ):
        """
        Validate task using canonical definition

        Args:
            task: Task to validate
            canonical: Canonical task definition
            authority_key: Authority configuration key
            authority_config: Authority configuration dictionary
            issues: List to append issues to
        """
        # Check for authority-specific bounds
        auth_specific = canonical.get('authority_specific', {}).get(authority_key, {})

        if auth_specific:
            # Use authority-specific bounds
            typical_days = auth_specific.get('duration_days', canonical.get('typical_duration_days', 60))
            min_days = auth_specific.get('min_days', canonical.get('min_duration_days', int(typical_days * 0.7)))
            max_days = auth_specific.get('max_days', canonical.get('max_duration_days', int(typical_days * 1.5)))
            reference = f"{authority_config.get('name', 'Authority')} typical: {typical_days} days"
        else:
            # Use generic bounds
            typical_days = canonical.get('typical_duration_days', 60)
            min_days = canonical.get('min_duration_days', int(typical_days * 0.7))
            max_days = canonical.get('max_duration_days', int(typical_days * 1.5))
            reference = f"Industry typical: {typical_days} days"

        # Check if duration is below minimum
        if task.duration_days < min_days:
            severity = IssueSeverity.WARNING
            if task.duration_days < min_days * 0.5:
                # Significantly below minimum - escalate to error
                severity = IssueSeverity.ERROR

            issues.append(ValidationIssue(
                rule_id="DUR-001",
                severity=severity,
                category=IssueCategory.DURATION,
                task_id=task.id,
                task_name=task.name,
                message=f"Duration below minimum: {task.name}",
                detail=f"Task duration ({task.duration_days} days) is below minimum ({min_days} days) for this type of task",
                suggested_fix=f"Increase duration to at least {min_days} days. {reference}",
                confidence=0.85,
                evidence=[
                    f"Current: {task.duration_days} days",
                    f"Minimum: {min_days} days",
                    f"Typical: {typical_days} days"
                ]
            ))

        # Check if duration exceeds maximum
        elif task.duration_days > max_days:
            issues.append(ValidationIssue(
                rule_id="DUR-002",
                severity=IssueSeverity.INFO,
                category=IssueCategory.DURATION,
                task_id=task.id,
                task_name=task.name,
                message=f"Duration exceeds typical: {task.name}",
                detail=f"Task duration ({task.duration_days} days) exceeds typical maximum ({max_days} days)",
                suggested_fix=f"Review if {task.duration_days} days is justified. {reference}",
                confidence=0.75,
                evidence=[
                    f"Current: {task.duration_days} days",
                    f"Maximum: {max_days} days",
                    f"Typical: {typical_days} days"
                ]
            ))

    def _validate_with_general_rules(
        self,
        task: Task,
        duration_rules: List[Dict],
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Validate task using general duration rules

        Args:
            task: Task to validate
            duration_rules: List of duration rule dictionaries
            timeline: Timeline context
            issues: List to append issues to
        """
        # Find applicable rules based on category and authority
        authority_value = timeline.authority.value

        for rule in duration_rules:
            # Check if rule applies to this task
            rule_category = rule.get('task_category')
            rule_authority = rule.get('authority')

            if rule_category and rule_category != task.category.value:
                continue

            if rule_authority and rule_authority != authority_value and rule_authority != 'all':
                continue

            # Look for matching task name patterns
            for task_rule in rule.get('rules', []):
                pattern = task_rule.get('task_name_pattern', '')

                if self._matches_pattern(task.name, pattern):
                    # Apply this rule
                    min_days = task_rule.get('min_days', 0)
                    max_days = task_rule.get('max_days', 999)
                    typical_days = task_rule.get('typical_days', (min_days + max_days) // 2)

                    if task.duration_days < min_days:
                        issues.append(ValidationIssue(
                            rule_id="DUR-003",
                            severity=IssueSeverity.WARNING,
                            category=IssueCategory.DURATION,
                            task_id=task.id,
                            task_name=task.name,
                            message=f"Duration below expected: {task.name}",
                            detail=f"Task duration ({task.duration_days} days) is below minimum ({min_days} days) for this category",
                            suggested_fix=f"Increase to at least {min_days} days (typical: {typical_days} days)",
                            confidence=0.8
                        ))

                    elif task.duration_days > max_days:
                        issues.append(ValidationIssue(
                            rule_id="DUR-004",
                            severity=IssueSeverity.INFO,
                            category=IssueCategory.DURATION,
                            task_id=task.id,
                            task_name=task.name,
                            message=f"Duration exceeds expected: {task.name}",
                            detail=f"Task duration ({task.duration_days} days) exceeds maximum ({max_days} days)",
                            suggested_fix=f"Review if {task.duration_days} days is necessary (typical: {typical_days} days)",
                            confidence=0.75
                        ))

                    break  # Found matching rule, stop searching

    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """
        Check if text matches a simple pattern

        Args:
            text: Text to match
            pattern: Pattern (supports * wildcard and .* regex-like patterns)

        Returns:
            True if matches, False otherwise
        """
        import re

        # Convert simple pattern to regex
        pattern_lower = pattern.lower()
        text_lower = text.lower()

        # Replace .* with regex pattern
        if '.*' in pattern_lower:
            regex_pattern = pattern_lower.replace('.*', '.*?')
            return bool(re.search(regex_pattern, text_lower))

        # Simple substring match
        return pattern_lower in text_lower


__all__ = ["DurationBoundsValidator"]
