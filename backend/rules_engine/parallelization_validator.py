"""
Parallelization Opportunities Validator

Identifies tasks that could potentially run in parallel to optimize
the timeline and reduce overall study duration.
"""

from typing import List, Dict, Tuple, Set
import networkx as nx
from .base_validator import BaseValidator
from models.timeline import Timeline, Task
from models.validation import ValidationIssue, IssueSeverity, IssueCategory


class ParallelizationValidator(BaseValidator):
    """
    Identifies parallelization opportunities

    Checks for:
    - Tasks that could run concurrently (no dependency path between them)
    - Similar tasks that could be batched
    - Sequential tasks that don't need to be sequential
    - Opportunities to compress timeline
    """

    @property
    def validator_name(self) -> str:
        return "Parallelization Opportunities"

    def validate(self, timeline: Timeline) -> List[ValidationIssue]:
        """
        Identify parallelization opportunities

        Args:
            timeline: Timeline to validate

        Returns:
            List of validation issues (opportunities) found
        """
        issues = []

        # Build dependency graph
        graph = self._build_dependency_graph(timeline)

        # Find tasks that could run in parallel
        self._find_parallel_opportunities(graph, timeline, issues)

        # Find similar tasks that could be batched
        self._find_batch_opportunities(timeline, issues)

        # Check for unnecessarily sequential tasks
        self._check_sequential_dependencies(graph, timeline, issues)

        return issues

    def _build_dependency_graph(self, timeline: Timeline) -> nx.DiGraph:
        """
        Build NetworkX directed graph from timeline

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
                duration=task.duration_days
            )

        # Add dependencies as edges
        for dep in timeline.dependencies:
            G.add_edge(
                dep.predecessor_id,
                dep.successor_id,
                lag_days=dep.lag_days
            )

        return G

    def _find_parallel_opportunities(
        self,
        graph: nx.DiGraph,
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Find tasks that could potentially run in parallel

        Args:
            graph: Dependency graph
            timeline: Timeline being validated
            issues: List to append issues to
        """
        tasks_list = list(timeline.tasks)
        opportunities_found = set()

        for i, task1 in enumerate(tasks_list):
            for task2 in tasks_list[i+1:]:
                # Skip if already found
                pair_key = tuple(sorted([task1.id, task2.id]))
                if pair_key in opportunities_found:
                    continue

                # Check if there's any path between them
                has_path_1_to_2 = nx.has_path(graph, task1.id, task2.id)
                has_path_2_to_1 = nx.has_path(graph, task2.id, task1.id)

                if not has_path_1_to_2 and not has_path_2_to_1:
                    # No dependency path - could run in parallel
                    # Check if they're in same/similar categories
                    same_category = task1.category == task2.category

                    if same_category:
                        # Same category tasks that could run in parallel
                        opportunities_found.add(pair_key)

                        # Calculate potential time savings
                        potential_savings = min(task1.duration_days, task2.duration_days)

                        issues.append(ValidationIssue(
                            rule_id="PAR-001",
                            severity=IssueSeverity.INFO,
                            category=IssueCategory.PARALLELIZATION,
                            task_id=task1.id,
                            task_name=task1.name,
                            message=f"Parallelization opportunity: {task1.name} and {task2.name}",
                            detail=f"These {task1.category.value} tasks have no dependencies and could potentially run in parallel. Potential time savings: up to {potential_savings} days.",
                            suggested_fix=f"Consider running '{task1.name}' and '{task2.name}' concurrently to compress timeline",
                            confidence=0.7,
                            evidence=[
                                f"Task 1: {task1.name} ({task1.duration_days} days)",
                                f"Task 2: {task2.name} ({task2.duration_days} days)",
                                f"No dependency path exists between tasks",
                                f"Category: {task1.category.value}"
                            ]
                        ))

    def _find_batch_opportunities(
        self,
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Find similar tasks that could be batched

        Args:
            timeline: Timeline being validated
            issues: List to append issues to
        """
        # Group tasks by category
        tasks_by_category: Dict[str, List[Task]] = {}

        for task in timeline.tasks:
            category = task.category.value
            if category not in tasks_by_category:
                tasks_by_category[category] = []
            tasks_by_category[category].append(task)

        # Check for multiple similar tasks in same category
        for category, tasks in tasks_by_category.items():
            if len(tasks) >= 3:
                # Find groups of similar tasks
                similar_groups = self._find_similar_task_groups(tasks)

                for group in similar_groups:
                    if len(group) >= 3:
                        task_names = [task.name for task in group]

                        issues.append(ValidationIssue(
                            rule_id="PAR-002",
                            severity=IssueSeverity.INFO,
                            category=IssueCategory.PARALLELIZATION,
                            task_id=group[0].id,
                            task_name=group[0].name,
                            message=f"Batch opportunity: {len(group)} similar {category} tasks",
                            detail=f"Found {len(group)} similar {category} tasks that could potentially be batched or streamlined: {', '.join(task_names[:3])}...",
                            suggested_fix=f"Consider batching these {category} tasks or using a standardized process to execute them more efficiently",
                            confidence=0.6,
                            evidence=[
                                f"Task count: {len(group)}",
                                f"Category: {category}",
                                f"Tasks: {', '.join(task_names)}"
                            ]
                        ))

    def _find_similar_task_groups(self, tasks: List[Task]) -> List[List[Task]]:
        """
        Find groups of similar tasks

        Args:
            tasks: List of tasks to group

        Returns:
            List of task groups
        """
        groups = []

        # Simple similarity: tasks with similar names or same duration
        for task in tasks:
            # Check if task fits in an existing group
            placed = False

            for group in groups:
                # Check similarity with first task in group
                if self._are_tasks_similar(task, group[0]):
                    group.append(task)
                    placed = True
                    break

            if not placed:
                # Start new group
                groups.append([task])

        # Filter out single-task groups
        return [group for group in groups if len(group) >= 2]

    def _are_tasks_similar(self, task1: Task, task2: Task) -> bool:
        """
        Check if two tasks are similar

        Args:
            task1: First task
            task2: Second task

        Returns:
            True if tasks are similar, False otherwise
        """
        # Same category
        if task1.category != task2.category:
            return False

        # Similar duration (within 20%)
        duration_ratio = min(task1.duration_days, task2.duration_days) / max(task1.duration_days, task2.duration_days)
        if duration_ratio < 0.8:
            return False

        # Similar name (word overlap)
        words1 = set(task1.name.lower().split())
        words2 = set(task2.name.lower().split())
        overlap = len(words1.intersection(words2))

        return overlap >= 2

    def _check_sequential_dependencies(
        self,
        graph: nx.DiGraph,
        timeline: Timeline,
        issues: List[ValidationIssue]
    ):
        """
        Check for unnecessarily sequential tasks

        Args:
            graph: Dependency graph
            timeline: Timeline being validated
            issues: List to append issues to
        """
        # Check for long chains of dependencies in the same category
        # that might not need to be fully sequential

        for task in timeline.tasks:
            predecessors = list(graph.predecessors(task.id))

            if len(predecessors) == 1:
                # Single predecessor - check if it's in the same category
                pred_id = predecessors[0]
                pred_task = self._find_task_by_id(timeline, pred_id)

                if pred_task and pred_task.category == task.category:
                    # Same category tasks in sequence
                    # Check if this is part of a longer chain
                    chain_length = self._get_chain_length(graph, task.id, task.category.value, timeline)

                    if chain_length >= 4:
                        issues.append(ValidationIssue(
                            rule_id="PAR-003",
                            severity=IssueSeverity.INFO,
                            category=IssueCategory.PARALLELIZATION,
                            task_id=task.id,
                            task_name=task.name,
                            message=f"Long sequential chain: {task.category.value} tasks",
                            detail=f"Task '{task.name}' is part of a chain of {chain_length} sequential {task.category.value} tasks. Consider if some could run in parallel.",
                            suggested_fix="Review dependencies to identify tasks that could run concurrently",
                            confidence=0.5,
                            evidence=[
                                f"Chain length: {chain_length} tasks",
                                f"Category: {task.category.value}"
                            ]
                        ))

    def _get_chain_length(
        self,
        graph: nx.DiGraph,
        task_id: str,
        category: str,
        timeline: Timeline
    ) -> int:
        """
        Get length of sequential chain for a task

        Args:
            graph: Dependency graph
            task_id: Task to check
            category: Category to match
            timeline: Timeline being validated

        Returns:
            Length of sequential chain
        """
        length = 1

        # Count predecessors in same category
        current = task_id
        while True:
            preds = list(graph.predecessors(current))
            if len(preds) != 1:
                break

            pred_task = self._find_task_by_id(timeline, preds[0])
            if not pred_task or pred_task.category.value != category:
                break

            length += 1
            current = preds[0]

        return length


__all__ = ["ParallelizationValidator"]
