"""
Validation Endpoints

Provides timeline validation using the rules engine
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
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
