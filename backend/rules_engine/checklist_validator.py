"""
Checklist Completeness Validator

Validates that timelines include appropriate checklist tasks and that
checklist completion percentages are appropriate for the task status.
"""

from typing import List, Dict, Optional
from .base_validator import BaseValidator
from backend.models.timeline import Timeline, Task, TaskCategory
from backend.models.validation import ValidationIssue, IssueSeverity, IssueCategory


class ChecklistCompletenessValidator(BaseValidator):
    """
    Validates checklist coverage and completion

    Checks that:
    - Required checklists are represented in the timeline
    - Checklist tasks have appropriate completion percentages
    - Mandatory checklist items are tracked
    - Checklists are associated with correct study phases
    """

    @property
    def validator_name(self) -> str:
        return "Checklist Completeness"

    def validate(self, timeline: Timeline) -> List[ValidationIssue]:
        """
        Validate checklist coverage and completion

        Args:
            timeline: Timeline to validate

        Returns:
            List of validation issues found
        """
        issues = []

        # Get checklists from configuration
        checklists = self.config.get('checklists', {})

        # Validate each defined checklist
        for checklist_id, checklist_data in checklists.items():
            self._validate_checklist(
                checklist_id,
                checklist_data,
                timeline,
                issues
            )

        # Validate checklist completion percentages
        self._validate_completion_percentages(timeline, issues)

        return issues

    def _validate_checklist(
        self,
        checklist_id: str,
        checklist_data: Dict,
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Validate a specific checklist

        Args:
            checklist_id: Checklist identifier (e.g., "STARTUP", "SIV")
            checklist_data: Checklist configuration
            timeline: Timeline being validated
            issues: List to append issues to
        """
        checklist_name = checklist_data.get('name', checklist_id)

        # Find tasks associated with this checklist
        checklist_tasks = self._find_checklist_tasks(
            checklist_id,
            checklist_name,
            timeline
        )

        # Check if checklist should be present for this timeline
        is_required = self._is_checklist_required(
            checklist_id,
            checklist_data,
            timeline
        )

        if is_required and not checklist_tasks:
            # Checklist is missing but required
            issues.append(ValidationIssue(
                rule_id="CHECK-001",
                severity=IssueSeverity.WARNING,
                category=IssueCategory.CHECKLISTS,
                message=f"Missing required checklist: {checklist_name}",
                detail=f"Timeline should include tasks for {checklist_name}. {checklist_data.get('description', '')}",
                suggested_fix=f"Add task(s) for {checklist_name} with appropriate checklist items tracked",
                confidence=0.8,
                evidence=[
                    f"Study phase: {timeline.phase.value}",
                    f"Authority: {timeline.authority.value}",
                    f"Required checklist items: {len(checklist_data.get('items', []))}"
                ]
            ))
        elif checklist_tasks:
            # Checklist exists - validate completion
            self._validate_checklist_tasks(
                checklist_id,
                checklist_name,
                checklist_data,
                checklist_tasks,
                issues
            )

    def _find_checklist_tasks(
        self,
        checklist_id: str,
        checklist_name: str,
        timeline: Timeline
    ) -> List[Task]:
        """
        Find tasks associated with a checklist

        Args:
            checklist_id: Checklist identifier
            checklist_name: Checklist display name
            timeline: Timeline to search

        Returns:
            List of tasks associated with this checklist
        """
        checklist_tasks = []

        # Search by checklist ID in task name (case-insensitive)
        checklist_id_lower = checklist_id.lower()
        checklist_name_lower = checklist_name.lower()

        for task in timeline.tasks:
            task_name_lower = task.name.lower()

            # Check if task name contains checklist identifier or name
            if (checklist_id_lower in task_name_lower or
                any(word in task_name_lower for word in checklist_name_lower.split())):
                checklist_tasks.append(task)

        return checklist_tasks

    def _is_checklist_required(
        self,
        checklist_id: str,
        checklist_data: Dict,
        timeline: Timeline
    ) -> bool:
        """
        Determine if checklist is required for this timeline

        Args:
            checklist_id: Checklist identifier
            checklist_data: Checklist configuration
            timeline: Timeline being validated

        Returns:
            True if checklist is required, False otherwise
        """
        # STARTUP checklist is always required
        if checklist_id == "STARTUP":
            return True

        # SIV (Site Initiation Visit) required if timeline has site tasks
        if checklist_id == "SIV":
            has_site_tasks = any(
                task.category == TaskCategory.SITE
                for task in timeline.tasks
            )
            return has_site_tasks

        # CLOSEOUT required if timeline has closeout tasks
        if checklist_id == "CLOSEOUT":
            has_closeout_tasks = any(
                task.category == TaskCategory.CLOSEOUT
                for task in timeline.tasks
            )
            return has_closeout_tasks

        # Check if checklist has phase requirements
        if 'required_for_phases' in checklist_data:
            return timeline.phase.value in checklist_data['required_for_phases']

        return False

    def _validate_checklist_tasks(
        self,
        checklist_id: str,
        checklist_name: str,
        checklist_data: Dict,
        checklist_tasks: List[Task],
        issues: List[ValidationIssue]
    ):
        """
        Validate tasks associated with a checklist

        Args:
            checklist_id: Checklist identifier
            checklist_name: Checklist display name
            checklist_data: Checklist configuration
            checklist_tasks: Tasks associated with checklist
            issues: List to append issues to
        """
        checklist_items = checklist_data.get('items', [])
        mandatory_count = sum(
            1 for item in checklist_items
            if item.get('mandatory', False)
        )

        for task in checklist_tasks:
            # Check completion percentage
            if task.checklist_completion_pct < 100:
                # Determine severity based on completion level
                if task.checklist_completion_pct < 50:
                    severity = IssueSeverity.WARNING
                else:
                    severity = IssueSeverity.INFO

                issues.append(ValidationIssue(
                    rule_id="CHECK-002",
                    severity=severity,
                    category=IssueCategory.CHECKLISTS,
                    task_id=task.id,
                    task_name=task.name,
                    message=f"Checklist incomplete: {task.name}",
                    detail=f"Checklist completion: {task.checklist_completion_pct}%. {checklist_name} has {len(checklist_items)} items ({mandatory_count} mandatory).",
                    suggested_fix="Complete all mandatory checklist items before task execution",
                    confidence=0.85,
                    evidence=[
                        f"Current completion: {task.checklist_completion_pct}%",
                        f"Total checklist items: {len(checklist_items)}",
                        f"Mandatory items: {mandatory_count}"
                    ]
                ))

            # Warn if checklist is 0% complete
            if task.checklist_completion_pct == 0:
                issues.append(ValidationIssue(
                    rule_id="CHECK-003",
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.CHECKLISTS,
                    task_id=task.id,
                    task_name=task.name,
                    message=f"Checklist not started: {task.name}",
                    detail=f"No checklist items completed for {checklist_name}. Consider starting checklist preparation early.",
                    suggested_fix=f"Begin completing {checklist_name} items: {', '.join([item.get('task', '') for item in checklist_items[:3]])}...",
                    confidence=0.7
                ))

    def _validate_completion_percentages(
        self,
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Validate that completion percentages are reasonable

        Args:
            timeline: Timeline being validated
            issues: List to append issues to
        """
        for task in timeline.tasks:
            # Check for invalid percentages
            if task.checklist_completion_pct < 0 or task.checklist_completion_pct > 100:
                issues.append(ValidationIssue(
                    rule_id="CHECK-004",
                    severity=IssueSeverity.ERROR,
                    category=IssueCategory.CHECKLISTS,
                    task_id=task.id,
                    task_name=task.name,
                    message=f"Invalid checklist completion: {task.checklist_completion_pct}%",
                    detail=f"Completion percentage must be between 0-100%. Current value: {task.checklist_completion_pct}%",
                    suggested_fix="Set completion percentage to a value between 0 and 100",
                    confidence=1.0
                ))

            # Warn if critical tasks have low checklist completion
            if task.is_mandatory and task.checklist_completion_pct < 80:
                issues.append(ValidationIssue(
                    rule_id="CHECK-005",
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.CHECKLISTS,
                    task_id=task.id,
                    task_name=task.name,
                    message=f"Mandatory task with incomplete checklist: {task.name}",
                    detail=f"Mandatory task has only {task.checklist_completion_pct}% checklist completion. Ensure all required items are addressed.",
                    suggested_fix="Complete checklist items to at least 80% before task execution",
                    confidence=0.8,
                    evidence=[
                        f"Task is mandatory: {task.is_mandatory}",
                        f"Current completion: {task.checklist_completion_pct}%"
                    ]
                ))


__all__ = ["ChecklistCompletenessValidator"]
