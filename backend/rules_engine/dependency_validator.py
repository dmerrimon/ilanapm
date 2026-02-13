"""
Dependency Validator

Validates dependencies for cycles, logical consistency, and completeness.
Uses NetworkX for graph analysis to detect circular dependencies and
orphaned tasks.
"""

from typing import List, Dict, Set
import networkx as nx
from .base_validator import BaseValidator
from models.timeline import Timeline, Task
from models.validation import ValidationIssue, IssueSeverity, IssueCategory


class DependencyValidator(BaseValidator):
    """
    Validates dependencies for cycles and logical consistency

    Checks that:
    - No circular dependencies exist
    - Dependencies are logically valid
    - Critical tasks have appropriate predecessors
    - No orphaned tasks (except regulatory start tasks)
    """

    @property
    def validator_name(self) -> str:
        return "Dependency Validation"

    def validate(self, timeline: Timeline) -> List[ValidationIssue]:
        """
        Validate dependencies in the timeline

        Args:
            timeline: Timeline to validate

        Returns:
            List of validation issues found
        """
        issues = []

        # Build dependency graph
        graph = self._build_dependency_graph(timeline)

        # Check for circular dependencies
        self._check_circular_dependencies(graph, timeline, issues)

        # Check for orphaned tasks
        self._check_orphaned_tasks(graph, timeline, issues)

        # Check for missing critical dependencies
        self._check_critical_dependencies(graph, timeline, issues)

        # Check for invalid dependency types
        self._check_dependency_validity(timeline, issues)

        return issues

    def _build_dependency_graph(self, timeline: Timeline) -> nx.DiGraph:
        """
        Build NetworkX directed graph from timeline dependencies

        Args:
            timeline: Timeline to build graph from

        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()

        # Add tasks as nodes
        for task in timeline.tasks:
            G.add_node(
                task.id,
                name=task.name,
                category=task.category.value,
                is_mandatory=task.is_mandatory
            )

        # Add dependencies as edges
        for dep in timeline.dependencies:
            G.add_edge(
                dep.predecessor_id,
                dep.successor_id,
                type=dep.type,
                lag_days=dep.lag_days
            )

        return G

    def _check_circular_dependencies(
        self,
        graph: nx.DiGraph,
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Check for circular dependencies using NetworkX cycle detection

        Args:
            graph: Dependency graph
            timeline: Timeline being validated
            issues: List to append issues to
        """
        try:
            # Find all simple cycles
            cycles = list(nx.simple_cycles(graph))

            if cycles:
                for cycle in cycles:
                    # Get task names for the cycle
                    task_names = [
                        self._get_task_name_by_id(timeline, task_id)
                        for task_id in cycle
                    ]

                    # Create cycle description
                    cycle_path = " → ".join(task_names) + f" → {task_names[0]}"

                    issues.append(ValidationIssue(
                        rule_id="DEP-001",
                        severity=IssueSeverity.ERROR,
                        category=IssueCategory.DEPENDENCIES,
                        task_id=cycle[0],
                        task_name=task_names[0],
                        message="Circular dependency detected",
                        detail=f"Cycle found: {cycle_path}. This creates an impossible schedule where tasks depend on each other in a loop.",
                        suggested_fix="Remove one dependency from the cycle to break the loop. Review which dependency is least critical.",
                        confidence=1.0,
                        evidence=[
                            f"Cycle length: {len(cycle)} tasks",
                            f"Involved tasks: {', '.join(task_names)}"
                        ]
                    ))

        except Exception as e:
            issues.append(ValidationIssue(
                rule_id="DEP-002",
                severity=IssueSeverity.WARNING,
                category=IssueCategory.DEPENDENCIES,
                message="Dependency graph analysis error",
                detail=f"Failed to analyze dependency graph: {str(e)}",
                suggested_fix="Review dependency definitions for inconsistencies",
                confidence=0.8
            ))

    def _check_orphaned_tasks(
        self,
        graph: nx.DiGraph,
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Check for orphaned tasks (no dependencies)

        Args:
            graph: Dependency graph
            timeline: Timeline being validated
            issues: List to append issues to
        """
        for task in timeline.tasks:
            # Check if task has any dependencies (in or out)
            has_predecessors = graph.in_degree(task.id) > 0
            has_successors = graph.out_degree(task.id) > 0

            if not has_predecessors and not has_successors:
                # Task is completely isolated
                # Only flag if it's not a regulatory start task
                if task.category.value != "Regulatory" or task.is_mandatory:
                    issues.append(ValidationIssue(
                        rule_id="DEP-003",
                        severity=IssueSeverity.INFO,
                        category=IssueCategory.DEPENDENCIES,
                        task_id=task.id,
                        task_name=task.name,
                        message=f"Orphaned task: {task.name}",
                        detail="Task has no dependencies (no predecessors or successors). Consider linking to appropriate tasks.",
                        suggested_fix="Add dependencies to integrate this task into the timeline flow",
                        confidence=0.7,
                        evidence=[
                            f"Category: {task.category.value}",
                            f"Duration: {task.duration_days} days"
                        ]
                    ))

    def _check_critical_dependencies(
        self,
        graph: nx.DiGraph,
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Check that critical tasks have appropriate dependencies

        Args:
            graph: Dependency graph
            timeline: Timeline being validated
            issues: List to append issues to
        """
        # Specific task-to-predecessor requirements
        required_predecessors = {
            "Site Identification & Feasibility": {
                "required": ["Confidentiality Agreement", "CDA", "Confidentiality"],
                "detail": "Site feasibility work requires an executed confidentiality agreement (CDA) before site visits and data sharing can occur.",
                "fix": "Add 'Confidentiality Agreement' task as predecessor"
            },
            "Site Initiation Visit": {
                "required": ["Site Contract", "Site Agreement"],
                "detail": "Site initiation visits require executed site contracts before site activation activities can begin.",
                "fix": "Add 'Site Contract' or 'Site Agreement' task as predecessor"
            }
        }

        # Build task name lookup
        task_by_id = {task.id: task for task in timeline.tasks}
        task_names = {task.id: task.name for task in timeline.tasks}

        for task in timeline.tasks:
            # Check specific task requirements
            for required_task_name, requirement in required_predecessors.items():
                if required_task_name.lower() in task.name.lower():
                    # Get predecessors
                    predecessors = list(graph.predecessors(task.id))
                    predecessor_names = [task_names.get(pred_id, "") for pred_id in predecessors]

                    # Check if any required predecessor exists
                    has_required_pred = any(
                        any(req.lower() in pred_name.lower() for req in requirement["required"])
                        for pred_name in predecessor_names
                    )

                    if not has_required_pred:
                        issues.append(ValidationIssue(
                            rule_id="DEP-004",
                            severity=IssueSeverity.WARNING,
                            category=IssueCategory.DEPENDENCIES,
                            task_id=task.id,
                            task_name=task.name,
                            message=f"Critical task missing required predecessor: {task.name}",
                            detail=requirement["detail"],
                            suggested_fix=requirement["fix"],
                            confidence=0.85,
                            evidence=[
                                f"Task: {task.name}",
                                f"Required predecessor: {' or '.join(requirement['required'])}",
                                f"Current predecessors: {', '.join(predecessor_names) if predecessor_names else 'None'}"
                            ]
                        ))

    def _check_dependency_validity(
        self,
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Check that dependencies reference valid tasks

        Args:
            timeline: Timeline being validated
            issues: List to append issues to
        """
        task_ids = {task.id for task in timeline.tasks}

        for dep in timeline.dependencies:
            # Check if predecessor exists
            if dep.predecessor_id not in task_ids:
                issues.append(ValidationIssue(
                    rule_id="DEP-005",
                    severity=IssueSeverity.ERROR,
                    category=IssueCategory.DEPENDENCIES,
                    message=f"Invalid dependency: predecessor '{dep.predecessor_id}' not found",
                    detail=f"Dependency references non-existent task '{dep.predecessor_id}'",
                    suggested_fix=f"Remove this dependency or add task with ID '{dep.predecessor_id}'",
                    confidence=1.0
                ))

            # Check if successor exists
            if dep.successor_id not in task_ids:
                issues.append(ValidationIssue(
                    rule_id="DEP-005",
                    severity=IssueSeverity.ERROR,
                    category=IssueCategory.DEPENDENCIES,
                    message=f"Invalid dependency: successor '{dep.successor_id}' not found",
                    detail=f"Dependency references non-existent task '{dep.successor_id}'",
                    suggested_fix=f"Remove this dependency or add task with ID '{dep.successor_id}'",
                    confidence=1.0
                ))

            # Check for self-dependency
            if dep.predecessor_id == dep.successor_id:
                issues.append(ValidationIssue(
                    rule_id="DEP-006",
                    severity=IssueSeverity.ERROR,
                    category=IssueCategory.DEPENDENCIES,
                    task_id=dep.predecessor_id,
                    message="Task depends on itself",
                    detail=f"Task '{dep.predecessor_id}' has a dependency pointing to itself",
                    suggested_fix="Remove this self-referencing dependency",
                    confidence=1.0
                ))

    def _get_task_name_by_id(self, timeline: Timeline, task_id: str) -> str:
        """
        Get task name by ID

        Args:
            timeline: Timeline to search
            task_id: Task ID to find

        Returns:
            Task name or task ID if not found
        """
        task = self._find_task_by_id(timeline, task_id)
        return task.name if task else task_id


__all__ = ["DependencyValidator"]
