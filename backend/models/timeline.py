"""
Timeline Data Models

Defines the core data structures for clinical trial timelines,
including tasks, dependencies, and timeline metadata.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
from datetime import date
from enum import Enum


class StudyPhase(str, Enum):
    """Clinical trial study phases"""
    PHASE_I = "Phase I"
    PHASE_II = "Phase II"
    PHASE_III = "Phase III"
    PHASE_IV = "Phase IV"
    PILOT = "Pilot"


class RegulatoryAuthority(str, Enum):
    """Regulatory authorities for clinical trials (23 countries supported)"""
    # Original authorities
    FDA = "FDA"
    EMA = "EMA"
    MHRA = "MHRA"
    HEALTH_CANADA = "Health Canada"
    PMDA = "PMDA"

    # Expanded global coverage (23 countries total)
    # Africa
    MCAZ_ZW = "MCAZ Zimbabwe"
    PPB_KE = "PPB Kenya"
    LMHRA_LR = "LMHRA Liberia"
    MCAZ_MW = "MCAZ Malawi"
    DPM_ML = "DPM Mali"
    PSLB_SL = "PSLB Sierra Leone"
    SAHPRA_ZA = "SAHPRA South Africa"
    TFDA_TZ = "TFDA Tanzania"
    NDA_UG = "NDA Uganda"
    DGRDF_CD = "DGRDF DRC"
    DNPL_GN = "DNPL Guinea"

    # Americas
    FDA_US = "FDA United States"
    ANVISA_BR = "ANVISA Brazil"
    COFEPRIS_MX = "COFEPRIS Mexico"
    DIGEMID_PE = "DIGEMID Peru"

    # Asia-Pacific
    TGA_AU = "TGA Australia"
    BFDA_BD = "BFDA Bangladesh"
    NMPA_CN = "NMPA China"
    CDSCO_IN = "CDSCO India"
    FDA_TH = "FDA Thailand"
    MOH_VN = "MOH Vietnam"

    # Europe
    MHRA_UK = "MHRA United Kingdom"


class TaskCategory(str, Enum):
    """Categories of clinical trial tasks"""
    REGULATORY = "Regulatory"
    OPERATIONAL = "Operational"
    SITE = "Site"
    DATA = "Data"
    CLOSEOUT = "Closeout"
    PHARMACY = "Pharmacy"
    LABORATORY = "Laboratory"
    SAFETY = "Safety"
    DOCUMENTS = "Documents"


class GatingStatus(str, Enum):
    """Status of gating/blocking tasks"""
    BLOCKED = "Blocked"
    READY = "Ready"
    COMPLETE = "Complete"
    NOT_APPLICABLE = "Not Applicable"


class Task(BaseModel):
    """
    Represents a single task in a clinical trial timeline

    Fields correspond to Microsoft Project custom fields that will be
    populated by the desktop and web add-ins.
    """
    id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Task name")
    duration_days: int = Field(..., ge=0, description="Duration in days")
    start_date: Optional[date] = Field(None, description="Planned start date")
    end_date: Optional[date] = Field(None, description="Planned end date")

    # Clinical metadata
    category: TaskCategory = Field(..., description="Task category")
    phase: StudyPhase = Field(..., description="Study phase")
    authority: RegulatoryAuthority = Field(..., description="Regulatory authority")
    country: Optional[str] = Field(None, description="Country code (ISO 3166-1 alpha-2, e.g., 'US', 'KE', 'VN') for country-specific regulatory workflows")
    therapeutic_area: Optional[str] = Field(None, description="Therapeutic area (e.g., Oncology, Cardiology)")

    # Authority-specific metadata (for rich ontology templates)
    authority_full_name: Optional[str] = Field(None, description="Full authority name (e.g., 'National Drug Authority')")
    authority_type: Optional[str] = Field(None, description="Authority type: 'regulatory', 'ethics', 'permits'")
    submission_form: Optional[str] = Field(None, description="Specific submission form (e.g., 'IRAS Application', 'IND', 'CTA')")
    required_documents: Optional[List[str]] = Field(None, description="Authority-specific required documents")

    # Validation fields
    is_mandatory: bool = Field(default=False, description="Whether task is mandatory")
    gating_status: GatingStatus = Field(default=GatingStatus.NOT_APPLICABLE, description="Gating/blocking status")
    checklist_completion_pct: int = Field(default=0, ge=0, le=100, description="Checklist completion percentage")

    # Summary task fields (for category dividers)
    is_summary: bool = Field(default=False, description="Whether this is a summary/parent task (category divider)")
    outline_level: int = Field(default=2, ge=1, le=9, description="Outline level (1=summary, 2=normal task)")

    # ML advisory fields (populated by backend)
    risk_score: Optional[int] = Field(None, ge=0, le=100, description="ML-predicted delay risk score")
    ml_predicted_duration: Optional[str] = Field(None, description="ML-predicted duration range")
    ml_confidence_pct: Optional[int] = Field(None, ge=0, le=100, description="ML prediction confidence")

    # Additional metadata
    custom_fields: Dict[str, str] = Field(default_factory=dict, description="Additional custom fields")
    notes: Optional[str] = Field(None, description="Task notes")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "T001",
                "name": "IND Submission",
                "duration_days": 60,
                "start_date": "2026-03-01",
                "end_date": "2026-04-30",
                "category": "Regulatory",
                "phase": "Phase II",
                "authority": "FDA",
                "is_mandatory": True,
                "gating_status": "Ready",
                "checklist_completion_pct": 85
            }
        }
    )


class DependencyType(str, Enum):
    """Types of task dependencies"""
    FINISH_TO_START = "finish-to-start"  # Task B starts when Task A finishes
    START_TO_START = "start-to-start"    # Task B starts when Task A starts
    FINISH_TO_FINISH = "finish-to-finish"  # Task B finishes when Task A finishes
    START_TO_FINISH = "start-to-finish"  # Task B finishes when Task A starts


class Dependency(BaseModel):
    """
    Represents a dependency relationship between two tasks
    """
    predecessor_id: str = Field(..., description="ID of predecessor task")
    successor_id: str = Field(..., description="ID of successor task")
    type: DependencyType = Field(default=DependencyType.FINISH_TO_START, description="Dependency type")
    lag_days: int = Field(default=0, description="Lag time in days (can be negative for lead time)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "predecessor_id": "T001",
                "successor_id": "T002",
                "type": "finish-to-start",
                "lag_days": 0
            }
        }
    )


class Timeline(BaseModel):
    """
    Represents a complete clinical trial timeline

    This is the main data structure sent from MS Project add-ins
    to the backend API for validation and analysis.
    """
    study_name: str = Field(..., description="Name of the clinical study")
    study_id: Optional[str] = Field(None, description="Study identifier (e.g., protocol number)")
    phase: StudyPhase = Field(..., description="Study phase")
    authority: RegulatoryAuthority = Field(..., description="Primary regulatory authority")
    therapeutic_area: Optional[str] = Field(None, description="Therapeutic area")

    tasks: List[Task] = Field(..., description="List of tasks in the timeline")
    dependencies: List[Dependency] = Field(default_factory=list, description="Task dependencies")

    # Timeline metadata
    planned_start_date: Optional[date] = Field(None, description="Overall timeline start date")
    planned_end_date: Optional[date] = Field(None, description="Overall timeline end date")
    total_duration_days: Optional[int] = Field(None, ge=0, description="Total timeline duration")

    # Additional metadata
    sponsor: Optional[str] = Field(None, description="Study sponsor")
    cro: Optional[str] = Field(None, description="Contract Research Organization")
    sites_count: Optional[int] = Field(None, ge=0, description="Number of study sites")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "study_name": "ABC-123 Phase II Study",
                "study_id": "ABC-123",
                "phase": "Phase II",
                "authority": "FDA",
                "therapeutic_area": "Oncology",
                "tasks": [
                    {
                        "id": "T001",
                        "name": "IND Submission",
                        "duration_days": 60,
                        "category": "Regulatory",
                        "phase": "Phase II",
                        "authority": "FDA",
                        "is_mandatory": True
                    }
                ],
                "dependencies": [
                    {
                        "predecessor_id": "T001",
                        "successor_id": "T002",
                        "type": "finish-to-start"
                    }
                ]
            }
        }
    )
