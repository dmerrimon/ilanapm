"""
Configuration Endpoints

Provides access to configuration data including authorities,
task ontology, checklists, and validation rules
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from backend.config import load_config, reload_config
from pydantic import BaseModel

router = APIRouter()


class AuthoritySummary(BaseModel):
    """Summary information about a regulatory authority"""
    code: str
    name: str
    country: Optional[str] = None
    region: Optional[str] = None
    gates_count: int
    has_milestone_timelines: bool


class TaskSummary(BaseModel):
    """Summary information about a canonical task"""
    id: str
    name: str
    category: str
    typical_duration_days: int
    is_mandatory: bool = False
    has_authority_specific: bool = False


@router.get("/config/authorities", response_model=List[AuthoritySummary])
async def get_authorities():
    """
    Get list of supported regulatory authorities

    Returns summary information for all 27 supported authorities including:
    - Authority code (e.g., "FDA", "MCAZ_ZW")
    - Full name
    - Country/region
    - Number of regulatory gates
    - Whether milestone timelines are defined

    Example Response:
        ```json
        [
            {
                "code": "MCAZ_ZW",
                "name": "Medicines Control Authority of Zimbabwe",
                "country": "Zimbabwe",
                "gates_count": 2,
                "has_milestone_timelines": true
            },
            {
                "code": "FDA",
                "name": "U.S. Food and Drug Administration",
                "country": "United States",
                "gates_count": 3,
                "has_milestone_timelines": true
            }
        ]
        ```
    """
    try:
        config = load_config()
        authorities = config.get('authorities', {})

        summaries = []
        for code, data in authorities.items():
            summaries.append(AuthoritySummary(
                code=code,
                name=data.get('name', 'Unknown'),
                country=data.get('country'),
                region=data.get('region'),
                gates_count=len(data.get('regulatory_gates', [])),
                has_milestone_timelines='milestone_timelines' in data
            ))

        # Sort by country/region name
        summaries.sort(key=lambda x: x.country or x.region or x.name)

        return summaries

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load authorities: {str(e)}"
        )


@router.get("/config/authorities/{authority_code}")
async def get_authority_details(authority_code: str):
    """
    Get detailed information about a specific authority

    Args:
        authority_code: Authority code (e.g., "FDA", "MCAZ_ZW")

    Returns:
        Complete authority configuration including gates, timelines,
        requirements, and compliance notes

    Example:
        GET /config/authorities/MCAZ_ZW
    """
    try:
        config = load_config()
        authorities = config.get('authorities', {})

        # Try exact match first
        if authority_code in authorities:
            return {
                "code": authority_code,
                **authorities[authority_code]
            }

        # Try case-insensitive match
        for code, data in authorities.items():
            if code.upper() == authority_code.upper():
                return {
                    "code": code,
                    **data
                }

        raise HTTPException(
            status_code=404,
            detail=f"Authority '{authority_code}' not found. Use /config/authorities to see all available authorities."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load authority details: {str(e)}"
        )


@router.get("/config/tasks", response_model=List[TaskSummary])
async def get_task_ontology():
    """
    Get canonical task ontology

    Returns the complete list of canonical clinical trial tasks with:
    - Task ID and name
    - Category (Regulatory, Operational, Site, Data, Closeout)
    - Typical duration
    - Whether task is mandatory
    - Whether authority-specific variations exist

    This ontology helps users understand standard tasks and their
    typical characteristics across different authorities.
    """
    try:
        config = load_config()
        tasks = config.get('task_ontology', [])

        summaries = []
        for task in tasks:
            summaries.append(TaskSummary(
                id=task.get('id', 'UNKNOWN'),
                name=task.get('name', 'Unknown Task'),
                category=task.get('category', 'Unknown'),
                typical_duration_days=task.get('typical_duration_days', 0),
                is_mandatory=task.get('is_mandatory', False),
                has_authority_specific='authority_specific' in task
            ))

        return summaries

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load task ontology: {str(e)}"
        )


@router.get("/config/tasks/{task_id}")
async def get_task_details(task_id: str):
    """
    Get detailed information about a specific canonical task

    Args:
        task_id: Task ID (e.g., "REG-001", "OPS-001")

    Returns:
        Complete task definition including authority-specific variations,
        prerequisites, and gating requirements
    """
    try:
        config = load_config()
        tasks = config.get('task_ontology', [])

        for task in tasks:
            if task.get('id') == task_id:
                return task

        raise HTTPException(
            status_code=404,
            detail=f"Task '{task_id}' not found in ontology"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load task details: {str(e)}"
        )


@router.get("/config/checklists")
async def get_checklists():
    """
    Get available checklists

    Returns all defined checklists (Startup, SIV, SAV, Closeout) with
    their items and requirements.
    """
    try:
        config = load_config()
        checklists = config.get('checklists', {})
        return checklists

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load checklists: {str(e)}"
        )


@router.get("/config/checklists/{checklist_id}")
async def get_checklist(checklist_id: str):
    """
    Get a specific checklist by ID

    Args:
        checklist_id: Checklist identifier (e.g., "STARTUP", "SIV", "CLOSEOUT")

    Returns:
        Checklist with all items and requirements
    """
    try:
        config = load_config()
        checklists = config.get('checklists', {})

        if checklist_id.upper() in checklists:
            return checklists[checklist_id.upper()]

        raise HTTPException(
            status_code=404,
            detail=f"Checklist '{checklist_id}' not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load checklist: {str(e)}"
        )


@router.get("/config/sequences")
async def get_operational_sequences():
    """
    Get operational sequence rules

    Returns all defined operational sequences that define
    logical prerequisites and dependencies between tasks.
    """
    try:
        config = load_config()
        sequences = config.get('operational_sequences', [])
        return {
            "count": len(sequences),
            "sequences": sequences
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load operational sequences: {str(e)}"
        )


@router.post("/config/reload")
async def reload_configuration():
    """
    Reload configuration from disk

    Useful for hot-reloading configuration changes without restarting the server.
    Requires appropriate permissions in production environments.

    Returns:
        Status of reload operation
    """
    try:
        reload_config()
        config = load_config()

        return {
            "status": "success",
            "message": "Configuration reloaded successfully",
            "authorities_loaded": len(config.get('authorities', {})),
            "tasks_loaded": len(config.get('task_ontology', [])),
            "checklists_loaded": len(config.get('checklists', {})),
            "sequences_loaded": len(config.get('operational_sequences', []))
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload configuration: {str(e)}"
        )


@router.get("/config/summary")
async def get_config_summary():
    """
    Get configuration summary

    Returns high-level statistics about the loaded configuration.
    Useful for verifying configuration state and coverage.
    """
    try:
        config = load_config()

        authorities = config.get('authorities', {})
        tasks = config.get('task_ontology', [])
        checklists = config.get('checklists', {})
        sequences = config.get('operational_sequences', [])

        # Count regional coverage
        africa_count = sum(1 for k in authorities.keys() if any(x in k for x in ['MCAZ', 'PPB', 'LMHRA', 'DPM', 'PSLB', 'SAHPRA', 'TFDA', 'NDA', 'DGRDF', 'DNPL']))
        americas_count = sum(1 for k in authorities.keys() if any(x in k for x in ['FDA', 'ANVISA', 'COFEPRIS', 'DIGEMID', 'HEALTH']))
        asia_pacific_count = sum(1 for k in authorities.keys() if any(x in k for x in ['TGA', 'BFDA', 'NMPA', 'CDSCO', 'MOH', 'PMDA']))
        europe_count = sum(1 for k in authorities.keys() if any(x in k for x in ['EMA', 'MHRA']))

        # Count task categories
        task_categories = {}
        for task in tasks:
            category = task.get('category', 'Unknown')
            task_categories[category] = task_categories.get(category, 0) + 1

        return {
            "configuration_version": "2.0",
            "total_authorities": len(authorities),
            "regional_coverage": {
                "africa": africa_count,
                "americas": americas_count,
                "asia_pacific": asia_pacific_count,
                "europe": europe_count
            },
            "total_tasks": len(tasks),
            "tasks_by_category": task_categories,
            "total_checklists": len(checklists),
            "total_sequences": len(sequences),
            "capabilities": {
                "multi_authority_support": True,
                "authority_specific_timelines": True,
                "canonical_task_ontology": True,
                "checklist_management": True,
                "operational_sequencing": True
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate configuration summary: {str(e)}"
        )
