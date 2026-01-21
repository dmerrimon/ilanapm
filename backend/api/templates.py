"""
Template Generation API Endpoints

Provides endpoints for generating country-specific clinical trial timeline templates.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from backend.models.timeline import Timeline
from backend.services.template_generator import TemplateGenerator
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


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
