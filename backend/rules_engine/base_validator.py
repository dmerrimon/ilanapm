"""
Base Validator Abstract Class

Defines the interface that all validators must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from models.timeline import Timeline, Task
from models.validation import ValidationIssue


class BaseValidator(ABC):
    """
    Abstract base class for all timeline validators

    All validators must inherit from this class and implement
    the validate() method and validator_name property.
    """

    def __init__(self, config: Dict):
        """
        Initialize validator with configuration

        Args:
            config: Dictionary containing YAML configuration data
        """
        self.config = config

    @abstractmethod
    def validate(self, timeline: Timeline) -> List[ValidationIssue]:
        """
        Validate a timeline and return list of issues found

        Args:
            timeline: Timeline object to validate

        Returns:
            List of ValidationIssue objects
        """
        pass

    @property
    @abstractmethod
    def validator_name(self) -> str:
        """
        Return the name of this validator

        Returns:
            String name of validator
        """
        pass

    def _find_task_by_name(self, timeline: Timeline, name: str, fuzzy: bool = True) -> Optional[Task]:
        """
        Find a task by name in the timeline

        Args:
            timeline: Timeline to search
            name: Task name to find
            fuzzy: If True, use fuzzy matching (substring search)

        Returns:
            Task object if found, None otherwise
        """
        name_lower = name.lower()

        for task in timeline.tasks:
            task_name_lower = task.name.lower()

            if fuzzy:
                # Fuzzy match: check if name is substring of task name
                if name_lower in task_name_lower or task_name_lower in name_lower:
                    return task
            else:
                # Exact match
                if task_name_lower == name_lower:
                    return task

        return None

    def _find_task_by_id(self, timeline: Timeline, task_id: str) -> Optional[Task]:
        """
        Find a task by ID in the timeline

        Args:
            timeline: Timeline to search
            task_id: Task ID to find

        Returns:
            Task object if found, None otherwise
        """
        for task in timeline.tasks:
            if task.id == task_id:
                return task
        return None

    def _has_dependency(self, timeline: Timeline, predecessor_id: str, successor_id: str) -> bool:
        """
        Check if a dependency exists between two tasks

        Args:
            timeline: Timeline to check
            predecessor_id: ID of predecessor task
            successor_id: ID of successor task

        Returns:
            True if dependency exists, False otherwise
        """
        for dep in timeline.dependencies:
            if dep.predecessor_id == predecessor_id and dep.successor_id == successor_id:
                return True
        return False

    def _map_authority_to_key(self, authority) -> str:
        """
        Map RegulatoryAuthority enum to configuration key

        Args:
            authority: RegulatoryAuthority enum value

        Returns:
            String key for configuration lookup
        """
        # Handle both string values and enum objects
        if hasattr(authority, 'value'):
            auth_value = authority.value
        else:
            auth_value = str(authority)

        # Map common variations to keys
        mapping = {
            "FDA": "FDA",
            "EMA": "EMA",
            "MHRA": "MHRA",
            "Health Canada": "HEALTH_CANADA",
            "PMDA": "PMDA",
            # New expanded authorities
            "FDA United States": "FDA_US",
            "MCAZ Zimbabwe": "MCAZ_ZW",
            "TGA Australia": "TGA_AU",
            "ANVISA Brazil": "ANVISA_BR",
            "MHRA United Kingdom": "MHRA_UK",
            # Add more mappings as needed
        }

        # Try direct mapping first
        if auth_value in mapping:
            return mapping[auth_value]

        # Try to find by substring matching
        auth_upper = auth_value.upper()
        for key_candidate in mapping.values():
            if key_candidate in auth_upper or auth_upper in key_candidate:
                return key_candidate

        # Default: return the value as-is
        return auth_value


__all__ = ["BaseValidator"]
