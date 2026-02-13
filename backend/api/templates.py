"""
Template Generation API Endpoints

Provides endpoints for generating country-specific clinical trial timeline templates.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from models.timeline import Timeline
from services.template_generator import TemplateGenerator
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory cache for template generation (reduces response time for repeated requests)
_template_cache = {}
_CACHE_MAX_SIZE = 100  # Limit cache to 100 entries to prevent memory issues


class TemplateRequest(BaseModel):
    """Request model for template generation"""
    country_code: str = Field(
        ...,
        description="ISO country code (e.g., 'US', 'KE', 'VN')",
        min_length=2,
        max_length=2
    )
    study_phase: str = Field(
        ...,
        description="Study phase",
        pattern="^Phase (I|II|III|IV)$"
    )
    therapeutic_area: str = Field(
        ...,
        description="Therapeutic area (e.g., 'Oncology', 'Infectious Disease')",
        min_length=1
    )
    include_optional: bool = Field(
        default=True,
        description="Include optional tasks in the template"
    )

    class Config:
        schema_extra = {
            "example": {
                "country_code": "KE",
                "study_phase": "Phase III",
                "therapeutic_area": "Infectious Disease",
                "include_optional": True
            }
        }


@router.post("/templates/generate", response_model=Timeline)
async def generate_country_template(request: TemplateRequest) -> Timeline:
    """
    Generate country-specific timeline template

    Combines:
    - Country-specific regulatory workflows (from regulatory_workflows.yaml)
    - All 92 tasks from task ontology with country variations (task_ontology.yaml)
    - Industry-standard CRO timelines (study startup, site activation, closeout)

    **Example Usage:**

    ```json
    {
      "country_code": "KE",
      "study_phase": "Phase III",
      "therapeutic_area": "Infectious Disease",
      "include_optional": true
    }
    ```

    **Returns Timeline with:**
    - EC Approval (variable days)
    - PPB Approval (30 days)
    - NACOSTI Research Clearance (30 days)
    - Protocol Development (180 days)
    - Data Collection Forms (28 days after protocol)
    - Site Training (3 days before activation)
    - Study closeout tasks
    - Dependencies between tasks

    **Supported Countries (23):**
    US, AU, BD, CA, CN, CD, GN, IN, KE, LR, MW, ML, MX, PE, SL, TZ, ZA, TH, UG, GB, VN, ZW

    **Workflow Types:**
    - Parallel (US, AU, CA, GB) - 30 days
    - Sequential (BD, GN, MW, ML, MX, PE, SL) - 30-120 days
    - Three-layer Sequential (KE) - 60+ days
    - Four-layer Sequential (VN) - 60+ days
    - Multi-body (TZ, UG, ZW) - 90-120+ days

    Raises:
        HTTPException: 400 if country_code not supported
        HTTPException: 500 if template generation fails
    """
    try:
        logger.info(f"Generating template: {request.country_code} {request.study_phase} {request.therapeutic_area}")

        generator = TemplateGenerator()
        timeline = generator.generate_template(
            country_code=request.country_code.upper(),
            study_phase=request.study_phase,
            therapeutic_area=request.therapeutic_area,
            include_optional=request.include_optional
        )

        logger.info(f"Template generated successfully: {len(timeline.tasks)} tasks, "
                   f"{len(timeline.dependencies)} dependencies")

        return timeline

    except ValueError as e:
        # Country not found or invalid input
        logger.error(f"Template generation failed (validation): {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Unexpected error
        logger.error(f"Template generation failed (unexpected): {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Template generation failed: {str(e)}"
        )


@router.get("/templates/countries")
async def get_supported_countries():
    """
    Get list of supported countries for template generation

    Returns summary of each country's regulatory workflow.

    **Returns:**
    ```json
    {
      "countries": [
        {
          "code": "KE",
          "name": "Kenya",
          "workflow_type": "three_layer_sequential",
          "complexity_level": 4,
          "total_timeline_days": 60
        },
        ...
      ]
    }
    ```
    """
    try:
        generator = TemplateGenerator()

        countries = []
        for workflow in generator.workflows:
            countries.append({
                "code": workflow['country_code'],
                "name": workflow['country_name'],
                "workflow_type": workflow['workflow_type'],
                "complexity_level": workflow['complexity_level'],
                "total_timeline_days": workflow.get('total_timeline_days'),
                "regulatory_authority": workflow['regulatory_authority']['code'],
                "ethics_authority": workflow['ethics_authority']['code']
            })

        return {
            "countries": sorted(countries, key=lambda x: x['name']),
            "count": len(countries)
        }

    except Exception as e:
        logger.error(f"Failed to get countries: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class SiteTemplateRequest(BaseModel):
    """Request model for site-specific template generation"""
    country_code: str = Field(
        ...,
        description="ISO country code (e.g., 'US', 'KE', 'VN')",
        min_length=2,
        max_length=2
    )
    template_type: str = Field(
        ...,
        description="Template type: 'site_startup', 'site_closeout', 'study_closeout'",
        pattern="^(site_startup|site_closeout|study_closeout)$"
    )
    site_id: str = Field(
        ...,
        description="Site identifier (e.g., 'SITE-001')",
        min_length=1
    )
    study_phase: str = Field(
        ...,
        description="Study phase",
        pattern="^Phase (I|II|III|IV)$"
    )
    therapeutic_area: str = Field(
        ...,
        description="Therapeutic area (e.g., 'Oncology', 'Infectious Disease')",
        min_length=1
    )
    include_optional: bool = Field(
        default=True,
        description="Include optional tasks in the template"
    )

    class Config:
        schema_extra = {
            "example": {
                "country_code": "UG",
                "template_type": "site_startup",
                "site_id": "SITE-001",
                "study_phase": "Phase III",
                "therapeutic_area": "Oncology",
                "include_optional": True
            }
        }


@router.post("/templates/generate-site-startup", response_model=Timeline)
async def generate_site_startup_template(request: SiteTemplateRequest) -> Timeline:
    """
    Generate site startup timeline template with authority-specific details

    Returns tasks specific to activating a clinical trial site, including:
    - Authority-specific regulatory submissions (e.g., "Submit IRAS Application to MHRA" for UK)
    - Multi-authority workflows (e.g., NDA + UNCST for Uganda)
    - Site readiness and training tasks
    - GCP compliance and monitoring setup

    **Example for Uganda (UG):**
    - Submit to National Drug Authority (NDA) - 7 days preparation
    - Obtain UNCST Research Permit - 30 days (gated by NDA approval)
    - Submit to Ethics Committee - 30-60 days
    - Site Initiation Visit - 3 days

    **Example for UK (GB):**
    - Submit IRAS Application to MHRA - 14 days preparation
    - REC (Research Ethics Committee) Review - 60 days
    - NHS R&D Approval - 30 days
    - Site Initiation Visit - 3 days

    Raises:
        HTTPException: 400 if country_code not supported
        HTTPException: 500 if template generation fails
    """
    try:
        logger.info(f"Generating site startup template: {request.country_code} site {request.site_id}")

        generator = TemplateGenerator()
        timeline = generator.generate_site_startup(
            country_code=request.country_code.upper(),
            site_id=request.site_id,
            study_phase=request.study_phase,
            therapeutic_area=request.therapeutic_area,
            include_optional=request.include_optional
        )

        # Log authority information for debugging
        authorities = set()
        for task in timeline.tasks:
            if hasattr(task, 'authority') and task.authority:
                authorities.add(f"{task.authority} ({task.authority_full_name})" if hasattr(task, 'authority_full_name') else task.authority)

        logger.info(f"Site startup template generated: {len(timeline.tasks)} tasks, "
                   f"Authorities involved: {', '.join(authorities) if authorities else 'None'}")

        return timeline

    except ValueError as e:
        logger.error(f"Site startup template generation failed (validation): {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Site startup template generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Template generation failed: {str(e)}")


@router.post("/templates/generate-site-closeout", response_model=Timeline)
async def generate_site_closeout_template(request: SiteTemplateRequest) -> Timeline:
    """
    Generate site closeout timeline template with authority-specific details

    Returns tasks specific to closing a clinical trial site, including:
    - Final monitoring visits
    - IP accountability and destruction
    - Essential document archiving
    - Authority-specific closeout reporting (e.g., "Submit Study Completion Notice to MHRA" for UK)
    - Site closure letters

    **Example for Uganda (UG):**
    - Submit Completion Report to NDA - 7 days
    - Submit Final Report to UNCST - 7 days
    - Notify Ethics Committee - 3 days
    - Close-out monitoring visit - 5 days

    **Example for UK (GB):**
    - Submit Study Completion Notice to MHRA - 15 days
    - Final REC Report - 7 days
    - NHS R&D Notification - 3 days
    - Site closure visit - 5 days

    Raises:
        HTTPException: 400 if country_code not supported
        HTTPException: 500 if template generation fails
    """
    try:
        logger.info(f"Generating site closeout template: {request.country_code} site {request.site_id}")

        generator = TemplateGenerator()
        timeline = generator.generate_site_closeout(
            country_code=request.country_code.upper(),
            site_id=request.site_id,
            study_phase=request.study_phase,
            therapeutic_area=request.therapeutic_area,
            include_optional=request.include_optional
        )

        # Log authority information
        authorities = set()
        for task in timeline.tasks:
            if hasattr(task, 'authority') and task.authority:
                authorities.add(f"{task.authority} ({task.authority_full_name})" if hasattr(task, 'authority_full_name') else task.authority)

        logger.info(f"Site closeout template generated: {len(timeline.tasks)} tasks, "
                   f"Authorities involved: {', '.join(authorities) if authorities else 'None'}")

        return timeline

    except ValueError as e:
        logger.error(f"Site closeout template generation failed (validation): {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Site closeout template generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Template generation failed: {str(e)}")


@router.post("/templates/generate-study-closeout", response_model=Timeline)
async def generate_study_closeout_template(request: SiteTemplateRequest) -> Timeline:
    """
    Generate study-wide closeout timeline template

    Returns study-level closeout tasks that occur after all sites are closed, including:
    - Database lock and data analysis
    - Clinical Study Report (CSR) preparation
    - Final regulatory submissions to all authorities
    - Study archiving

    **Study-level tasks apply across all sites/countries.**

    Raises:
        HTTPException: 400 if country_code not supported
        HTTPException: 500 if template generation fails
    """
    try:
        logger.info(f"Generating study closeout template: {request.country_code}")

        generator = TemplateGenerator()
        timeline = generator.generate_study_closeout(
            country_code=request.country_code.upper(),
            study_phase=request.study_phase,
            therapeutic_area=request.therapeutic_area,
            include_optional=request.include_optional
        )

        logger.info(f"Study closeout template generated: {len(timeline.tasks)} tasks")

        return timeline

    except ValueError as e:
        logger.error(f"Study closeout template generation failed (validation): {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Study closeout template generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Template generation failed: {str(e)}")


# ============================================================================
# New Database-Backed Timeline Template Endpoints
# ============================================================================

@router.get("/templates/library")
async def list_timeline_templates(org_id: Optional[str] = None):
    """
    Get list of available timeline templates from database

    Returns system templates and optionally org-specific custom templates.

    Args:
        org_id: Optional organization ID to include custom templates

    Returns:
        List of timeline templates with metadata

    Example Response:
        {
          "templates": [
            {
              "template_id": "TPL_001",
              "template_name": "Study Startup",
              "template_type": "study_startup",
              "description": "Study startup activities from Study Award to FPI",
              "total_task_count": 86,
              "is_system_template": true
            },
            ...
          ],
          "count": 5
        }
    """
    try:
        import sqlite3
        from pathlib import Path

        db_path = Path(__file__).parent.parent / "database" / "feedback.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get system templates (org_id IS NULL)
        cursor.execute("""
            SELECT
                template_id,
                template_name,
                template_type,
                version,
                description,
                total_task_count,
                estimated_duration_days
            FROM timeline_templates
            WHERE org_id IS NULL
            ORDER BY
                CASE template_type
                    WHEN 'study_startup' THEN 1
                    WHEN 'implementation' THEN 2
                    WHEN 'closeout' THEN 3
                    WHEN 'site_activation' THEN 4
                    WHEN 'site_closeout' THEN 5
                    ELSE 6
                END
        """)

        system_templates = [dict(row) for row in cursor.fetchall()]

        # Add is_system_template flag
        for template in system_templates:
            template['is_system_template'] = True

        # Get org-specific templates if org_id provided
        org_templates = []
        if org_id:
            cursor.execute("""
                SELECT
                    template_id,
                    template_name,
                    template_type,
                    version,
                    description,
                    total_task_count,
                    estimated_duration_days
                FROM timeline_templates
                WHERE org_id = ?
                ORDER BY template_name
            """, (org_id,))

            org_templates = [dict(row) for row in cursor.fetchall()]
            for template in org_templates:
                template['is_system_template'] = False

        conn.close()

        all_templates = system_templates + org_templates

        logger.info(f"Retrieved {len(all_templates)} timeline templates ({len(system_templates)} system, {len(org_templates)} org-specific)")

        return {
            "templates": all_templates,
            "count": len(all_templates)
        }

    except Exception as e:
        logger.error(f"Failed to list templates: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.get("/templates/library/{template_id}")
async def get_timeline_template(template_id: str):
    """
    Get detailed timeline template with all tasks and dependencies

    Args:
        template_id: Template identifier (e.g., "TPL_001")

    Returns:
        Complete template with tasks, dependencies, and metadata

    Example Response:
        {
          "template": {
            "template_id": "TPL_001",
            "template_name": "Study Startup",
            "template_type": "study_startup",
            "total_task_count": 86,
            "description": "Study startup activities..."
          },
          "tasks": [
            {
              "task_id": "SS_001",
              "task_name": "Internal Transition Meeting",
              "category": "Initiation",
              "typical_duration_days": 7,
              "is_milestone": false,
              "responsible_role": "Project Manager",
              "sort_order": 1
            },
            ...
          ],
          "dependencies": [
            {
              "predecessor_task_id": "SS_001",
              "successor_task_id": "SS_005",
              "dependency_type": "finish-to-start"
            },
            ...
          ]
        }
    """
    try:
        import sqlite3
        from pathlib import Path

        db_path = Path(__file__).parent.parent / "database" / "feedback.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get template
        cursor.execute("""
            SELECT
                template_id,
                template_name,
                template_type,
                version,
                description,
                total_task_count,
                estimated_duration_days,
                org_id
            FROM timeline_templates
            WHERE template_id = ?
        """, (template_id,))

        template_row = cursor.fetchone()

        if not template_row:
            conn.close()
            raise HTTPException(
                status_code=404,
                detail=f"Template not found: {template_id}"
            )

        template = dict(template_row)

        # Get tasks
        cursor.execute("""
            SELECT
                task_id,
                task_name,
                task_code,
                category,
                typical_duration_days,
                min_duration_days,
                max_duration_days,
                p25_duration_days,
                p75_duration_days,
                is_milestone,
                is_critical_path,
                description,
                responsible_role,
                parent_task_id,
                sort_order,
                outline_level
            FROM template_tasks
            WHERE template_id = ?
            ORDER BY sort_order
        """, (template_id,))

        tasks = [dict(row) for row in cursor.fetchall()]

        # Get dependencies
        cursor.execute("""
            SELECT
                dependency_id,
                predecessor_task_id,
                successor_task_id,
                dependency_type,
                lag_days,
                is_hard_dependency
            FROM template_dependencies
            WHERE template_id = ?
        """, (template_id,))

        dependencies = [dict(row) for row in cursor.fetchall()]

        conn.close()

        logger.info(f"Retrieved template {template_id}: {len(tasks)} tasks, {len(dependencies)} dependencies")

        return {
            "template": template,
            "tasks": tasks,
            "dependencies": dependencies
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template {template_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get template: {str(e)}"
        )


@router.get("/templates/library/{template_id}/tasks")
async def get_template_tasks(
    template_id: str,
    include_headers: bool = True
):
    """
    Get tasks for a specific template

    Args:
        template_id: Template identifier
        include_headers: Include category headers (outline_level=1)

    Returns:
        List of tasks with metadata
    """
    try:
        import sqlite3
        from pathlib import Path

        db_path = Path(__file__).parent.parent / "database" / "feedback.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Build query based on include_headers
        if include_headers:
            query = """
                SELECT
                    task_id,
                    task_name,
                    task_code,
                    category,
                    typical_duration_days,
                    is_milestone,
                    is_critical_path,
                    description,
                    responsible_role,
                    parent_task_id,
                    sort_order,
                    outline_level
                FROM template_tasks
                WHERE template_id = ?
                ORDER BY sort_order
            """
        else:
            query = """
                SELECT
                    task_id,
                    task_name,
                    task_code,
                    category,
                    typical_duration_days,
                    is_milestone,
                    is_critical_path,
                    description,
                    responsible_role,
                    parent_task_id,
                    sort_order,
                    outline_level
                FROM template_tasks
                WHERE template_id = ? AND outline_level = 2
                ORDER BY sort_order
            """

        cursor.execute(query, (template_id,))
        tasks = [dict(row) for row in cursor.fetchall()]

        conn.close()

        logger.info(f"Retrieved {len(tasks)} tasks for template {template_id}")

        return {
            "template_id": template_id,
            "tasks": tasks,
            "count": len(tasks)
        }

    except Exception as e:
        logger.error(f"Failed to get template tasks: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get template tasks: {str(e)}"
        )
