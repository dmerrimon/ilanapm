"""
Validation Endpoints

Provides timeline validation using the rules engine
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from backend.models.timeline import Timeline
from backend.models.validation import ValidationResult
from backend.rules_engine import RulesEngine
from backend.config import load_config

router = APIRouter()

# Load configuration once at startup
config = load_config()
rules_engine = RulesEngine(config)


@router.post("/validate", response_model=ValidationResult)
async def validate_timeline(timeline: Timeline):
    """
    Validate a clinical trial timeline

    This endpoint runs all validation rules against the provided timeline
    and returns a comprehensive validation result with issues found.

    Args:
        timeline: Timeline object containing tasks and dependencies

    Returns:
        ValidationResult with:
        - Overall status (passed/warnings/failed)
        - List of issues found
        - Issue counts by severity
        - Validators that were run

    Example Request:
        ```json
        {
            "study_name": "Zimbabwe Phase II Study",
            "phase": "Phase II",
            "authority": "MCAZ Zimbabwe",
            "tasks": [
                {
                    "id": "T1",
                    "name": "Clinical Trial Authorization",
                    "duration_days": 60,
                    "category": "Regulatory",
                    "phase": "Phase II",
                    "authority": "MCAZ Zimbabwe",
                    "is_mandatory": true
                }
            ],
            "dependencies": []
        }
        ```

    Example Response:
        ```json
        {
            "status": "warnings",
            "issues": [
                {
                    "rule_id": "REG-GATE-001",
                    "severity": "error",
                    "category": "regulatory",
                    "message": "Missing required gate: MRCZ Ethical Approval",
                    "detail": "Zimbabwe MCAZ requires ethics approval...",
                    "suggested_fix": "Add MRCZ Ethical Approval task...",
                    "confidence": 1.0
                }
            ],
            "error_count": 1,
            "warning_count": 2,
            "info_count": 3,
            "total_tasks_analyzed": 5,
            "validators_run": ["Regulatory Gating", "Duration Bounds", "Operational Sequences"]
        }
        ```
    """
    try:
        # Run validation through rules engine
        result = rules_engine.validate_timeline(timeline)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )


@router.post("/validate/quick")
async def quick_validate(timeline: Timeline):
    """
    Quick validation - returns only error count and status

    Useful for rapid checks without full issue details.

    Args:
        timeline: Timeline object to validate

    Returns:
        Quick validation summary with counts only
    """
    try:
        result = rules_engine.validate_timeline(timeline)

        return {
            "status": result.status.value,
            "error_count": result.error_count,
            "warning_count": result.warning_count,
            "info_count": result.info_count,
            "total_tasks": result.total_tasks_analyzed,
            "has_issues": result.error_count > 0 or result.warning_count > 0
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick validation failed: {str(e)}"
        )


@router.get("/validate/stats")
async def validation_stats():
    """
    Get validation statistics and capabilities

    Returns information about available validators, rules, and coverage.

    Returns:
        Statistics about validation capabilities
    """
    return {
        "validators_available": len(rules_engine.validators),
        "validator_names": [v.validator_name for v in rules_engine.validators],
        "authorities_supported": len(config.get('authorities', {})),
        "task_ontology_size": len(config.get('task_ontology', [])),
        "operational_sequences": len(config.get('operational_sequences', [])),
        "version": "1.0",
        "capabilities": {
            "regulatory_gating": True,
            "duration_bounds": True,
            "operational_sequences": True,
            "dependency_validation": True,   # ✅ Phase 2 - Milestone 2.1
            "checklist_validation": True,    # ✅ Phase 2 - Milestone 2.1
            "parallelization_checks": True   # ✅ Phase 2 - Milestone 2.1
        }
    }


class AutoFixResult(BaseModel):
    """Result of auto-fix operation"""
    fixes_applied: int
    issues_fixed: List[str]
    remaining_issues: int
    modified_timeline: Timeline


@router.post("/validate/autofix", response_model=AutoFixResult)
async def autofix_timeline(timeline: Timeline) -> AutoFixResult:
    """
    Automatically fix common validation issues

    This endpoint automatically fixes the following issues:
    1. Self-dependencies (task depends on itself)
    2. Invalid task references (dependencies to non-existent tasks)
    3. Duration bounds violations (too short or too long)
    4. Invalid percentages (< 0 or > 100)

    Args:
        timeline: Timeline object with potential issues

    Returns:
        AutoFixResult with:
        - fixes_applied: Number of fixes made
        - issues_fixed: List of human-readable descriptions of fixes
        - remaining_issues: Number of issues that couldn't be auto-fixed
        - modified_timeline: Timeline with fixes applied

    Example Request:
        ```json
        {
            "study_name": "Test Study",
            "phase": "Phase II",
            "authority": "FDA",
            "tasks": [
                {
                    "id": "T1",
                    "name": "Task 1",
                    "duration_days": -5,  // Invalid: negative
                    "category": "Regulatory"
                }
            ],
            "dependencies": [
                {
                    "predecessor_id": "T1",
                    "successor_id": "T1",  // Invalid: self-dependency
                    "type": "FS"
                }
            ]
        }
        ```

    Example Response:
        ```json
        {
            "fixes_applied": 2,
            "issues_fixed": [
                "Removed 1 self-referencing dependencies",
                "Increased 'Task 1' duration from -5 to 1 days"
            ],
            "remaining_issues": 0,
            "modified_timeline": {...}
        }
        ```
    """
    try:
        fixes_applied = 0
        issues_fixed = []

        # FIX 1: Remove self-dependencies
        original_dep_count = len(timeline.dependencies)
        timeline.dependencies = [
            dep for dep in timeline.dependencies
            if dep.predecessor_id != dep.successor_id
        ]
        self_deps_removed = original_dep_count - len(timeline.dependencies)
        if self_deps_removed > 0:
            fixes_applied += self_deps_removed
            issues_fixed.append(f"Removed {self_deps_removed} self-referencing dependencies")

        # FIX 2: Remove invalid task references
        valid_task_ids = {task.id for task in timeline.tasks}
        original_dep_count = len(timeline.dependencies)
        timeline.dependencies = [
            dep for dep in timeline.dependencies
            if dep.predecessor_id in valid_task_ids and dep.successor_id in valid_task_ids
        ]
        invalid_refs_removed = original_dep_count - len(timeline.dependencies)
        if invalid_refs_removed > 0:
            fixes_applied += invalid_refs_removed
            issues_fixed.append(f"Removed {invalid_refs_removed} dependencies with invalid task references")

        # FIX 3: Adjust durations to bounds
        task_ontology = config.get('task_ontology', [])
        for task in timeline.tasks:
            canonical = _find_canonical_task(task, task_ontology)

            if canonical:
                min_days = canonical.get('min_duration_days', 1)
                max_days = canonical.get('max_duration_days', 365)
                original_duration = task.duration_days

                if task.duration_days < min_days:
                    task.duration_days = min_days
                    fixes_applied += 1
                    issues_fixed.append(
                        f"Increased '{task.name}' duration from {original_duration} to {min_days} days (minimum)"
                    )
                elif task.duration_days > max_days:
                    task.duration_days = max_days
                    fixes_applied += 1
                    issues_fixed.append(
                        f"Decreased '{task.name}' duration from {original_duration} to {max_days} days (maximum)"
                    )
            else:
                # No canonical task - just ensure non-negative
                if task.duration_days < 0:
                    original_duration = task.duration_days
                    task.duration_days = 1
                    fixes_applied += 1
                    issues_fixed.append(
                        f"Increased '{task.name}' duration from {original_duration} to 1 day (was negative)"
                    )

        # FIX 4: Set invalid percentages to valid range
        for task in timeline.tasks:
            if task.checklist_completion_pct is not None:
                if task.checklist_completion_pct < 0:
                    task.checklist_completion_pct = 0
                    fixes_applied += 1
                    issues_fixed.append(f"Reset '{task.name}' checklist completion from negative to 0%")
                elif task.checklist_completion_pct > 100:
                    task.checklist_completion_pct = 100
                    fixes_applied += 1
                    issues_fixed.append(f"Capped '{task.name}' checklist completion at 100%")

        # Re-validate to count remaining issues
        validation_result = rules_engine.validate_timeline(timeline)
        remaining_issues = validation_result.error_count + validation_result.warning_count

        return AutoFixResult(
            fixes_applied=fixes_applied,
            issues_fixed=issues_fixed,
            remaining_issues=remaining_issues,
            modified_timeline=timeline
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Auto-fix failed: {str(e)}"
        )


def _find_canonical_task(task, task_ontology: List[Dict]) -> Dict | None:
    """
    Find matching canonical task from ontology

    Args:
        task: Task to match
        task_ontology: List of canonical tasks

    Returns:
        Canonical task dictionary or None
    """
    # Try exact category match first
    category_matches = [
        t for t in task_ontology
        if t.get('category') == task.category.value
    ]

    if not category_matches:
        return None

    # Find best name match
    best_match = None
    best_score = 0.0

    for canonical in category_matches:
        score = _name_similarity(canonical['name'], task.name)
        if score > best_score and score > 0.5:  # Threshold
            best_score = score
            best_match = canonical

    return best_match


def _name_similarity(name1: str, name2: str) -> float:
    """
    Calculate name similarity score

    Args:
        name1: First name
        name2: Second name

    Returns:
        Similarity score (0-1)
    """
    words1 = set(name1.lower().split())
    words2 = set(name2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union) if union else 0.0
