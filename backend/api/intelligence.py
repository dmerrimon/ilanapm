"""
Intelligence API Endpoints

Provides variance detection, benchmark retrieval, task normalization,
and metadata inference for clinical trial timelines.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging

from models.timeline import Timeline
from intelligence import (
    BenchmarkRetriever,
    FinancialImpactCalculator,
    VarianceDetectionEngine,
    TaskNormalizer,
    MetadataInferrer,
    IntelligenceConfig,
    BenchmarkData,
    VarianceReport,
    TaskMappingSuggestion,
    MetadataInference,
    require_tier,
    check_tier
)
from database.connection import get_db_connection
from config import load_config

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize intelligence components
config = load_config()
benchmark_retriever = BenchmarkRetriever()
financial_calculator = FinancialImpactCalculator()

logger.info("Intelligence API initialized")


# ============================================================================
# Request/Response Models
# ============================================================================

class BenchmarkQuery(BaseModel):
    """Query for benchmark data"""
    task_name: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    authority: Optional[str] = None
    phase: Optional[str] = None
    therapeutic_area: Optional[str] = None
    site_type: Optional[str] = None


class TaskNormalizationRequest(BaseModel):
    """Request to normalize a task name"""
    customer_task_name: str
    category: Optional[str] = None


class MetadataInferenceRequest(BaseModel):
    """Request to infer metadata from timeline"""
    timeline: Dict


class IntelligenceValidationRequest(BaseModel):
    """Request for intelligence-enhanced validation"""
    timeline: Dict
    org_id: str
    tier: str


# ============================================================================
# Core Intelligence Endpoints
# ============================================================================

@router.post("/intelligence/validate-core")
async def validate_with_intelligence(request: IntelligenceValidationRequest):
    """
    Run intelligence-only validation (variance detection)

    Core Tier Feature: Available to all customers.

    Args:
        request: Contains timeline, org_id, tier

    Returns:
        VarianceReport with detailed variance analysis
    """
    try:
        logger.info(f"Intelligence validation request from org {request.org_id}, tier {request.tier}")

        # Get org-specific config
        tier_config = _get_org_intelligence_config(request.org_id, request.tier)

        # Initialize components with database connection
        with get_db_connection() as conn:
            # Initialize task normalizer with DB connection
            ontology_tasks = config.get('tasks', [])
            task_normalizer = TaskNormalizer(
                ontology_tasks=ontology_tasks,
                db_connection=conn,
                confidence_threshold=0.7
            )

            # Initialize metadata inferrer
            metadata_inferrer = MetadataInferrer()

            # Initialize variance detection engine
            variance_engine = VarianceDetectionEngine(
                benchmark_retriever=benchmark_retriever,
                financial_calculator=financial_calculator,
                task_normalizer=task_normalizer,
                metadata_inferrer=metadata_inferrer
            )

            # Run variance detection
            variance_report = variance_engine.detect_variances(
                timeline=request.timeline,
                tier_config=tier_config,
                org_id=request.org_id
            )

            # Track usage
            _track_intelligence_usage(
                conn=conn,
                org_id=request.org_id,
                user_id=request.timeline.get('user_id'),
                feature="variance_detection",
                tasks_analyzed=variance_report.summary.total_tasks_analyzed,
                variances_detected=variance_report.summary.warning_count + variance_report.summary.critical_count,
                success=True
            )

            return variance_report

    except Exception as e:
        logger.error(f"Intelligence validation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Intelligence validation failed: {str(e)}"
        )


@router.post("/intelligence/benchmarks", response_model=BenchmarkData)
async def get_benchmark(query: BenchmarkQuery):
    """
    Retrieve benchmark for specific task criteria

    Core Tier Feature: Available to all customers.

    Args:
        query: Benchmark query parameters

    Returns:
        BenchmarkData with median, p25, p75, source
    """
    try:
        benchmark = benchmark_retriever.get_benchmark(
            task_name=query.task_name,
            category=query.category,
            country=query.country,
            authority=query.authority,
            phase=query.phase,
            therapeutic_area=query.therapeutic_area,
            site_type=query.site_type
        )

        if not benchmark:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "No benchmark found",
                    "message": "No matching benchmark found for the specified criteria",
                    "query": query.dict()
                }
            )

        return benchmark

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Benchmark retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Benchmark retrieval failed: {str(e)}"
        )


@router.get("/intelligence/tier-config")
async def get_tier_config(org_id: str):
    """
    Get organization's intelligence configuration

    Args:
        org_id: Organization ID

    Returns:
        IntelligenceConfig with thresholds and settings
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tier, intelligence_config FROM organizations WHERE org_id = ?
            """, (org_id,))

            row = cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Organization not found: {org_id}"
                )

            tier = row['tier']
            config_json = row['intelligence_config']

            # Parse JSON config
            import json
            config_dict = json.loads(config_json) if isinstance(config_json, str) else config_json

            tier_config = IntelligenceConfig(
                org_id=org_id,
                tier=tier,
                **config_dict
            )

            return tier_config

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tier config: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tier config: {str(e)}"
        )


# ============================================================================
# Task Normalization Endpoints (Configuration)
# ============================================================================

@router.post("/intelligence/normalize-task", response_model=List[TaskMappingSuggestion])
async def normalize_task_name(
    request: TaskNormalizationRequest,
    org_id: str
):
    """
    Test task normalization (returns suggested mappings)

    Core Tier: View-only
    Calibrated Tier: Can confirm mappings

    Args:
        request: Task normalization request
        org_id: Organization ID

    Returns:
        List of TaskMappingSuggestion with confidence scores
    """
    try:
        with get_db_connection() as conn:
            ontology_tasks = config.get('tasks', [])
            task_normalizer = TaskNormalizer(
                ontology_tasks=ontology_tasks,
                db_connection=conn,
                confidence_threshold=0.7
            )

            context = {'category': request.category} if request.category else None

            _, suggestion, unconfirmed = task_normalizer.normalize(
                customer_task_name=request.customer_task_name,
                org_id=org_id,
                context=context
            )

            if suggestion:
                return [suggestion]
            elif unconfirmed:
                return unconfirmed.suggestions
            else:
                return []

    except Exception as e:
        logger.error(f"Task normalization failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Task normalization failed: {str(e)}"
        )


@router.get("/intelligence/task-mappings")
async def get_task_mappings(org_id: str):
    """
    Get organization's task mappings

    Core Tier: View-only (read cached mappings)

    Args:
        org_id: Organization ID

    Returns:
        List of task mappings with confidence scores
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    mapping_id,
                    customer_task_name,
                    ontology_task_id,
                    ontology_task_name,
                    confidence,
                    confirmed_by_user,
                    created_at
                FROM task_mappings
                WHERE org_id = ?
                ORDER BY confirmed_by_user DESC, confidence DESC
            """, (org_id,))

            mappings = cursor.fetchall()

            return {
                "org_id": org_id,
                "count": len(mappings),
                "mappings": [dict(row) for row in mappings]
            }

    except Exception as e:
        logger.error(f"Failed to get task mappings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task mappings: {str(e)}"
        )


# ============================================================================
# Metadata Inference Endpoints
# ============================================================================

@router.post("/intelligence/infer-metadata")
async def infer_metadata(request: MetadataInferenceRequest):
    """
    Infer metadata from timeline content

    Core Tier Feature: Automatic inference for phase, therapeutic area, countries

    Args:
        request: Timeline data

    Returns:
        Inferred metadata with confidence scores
    """
    try:
        metadata_inferrer = MetadataInferrer()

        inferred = metadata_inferrer.infer_metadata(
            timeline=request.timeline,
            confidence_threshold=0.7
        )

        return inferred

    except Exception as e:
        logger.error(f"Metadata inference failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Metadata inference failed: {str(e)}"
        )


# ============================================================================
# Project Profiles Endpoints
# ============================================================================

@router.get("/intelligence/project-profiles")
async def get_project_profiles(org_id: str):
    """
    Get organization's project profiles

    Core Tier: Basic profiles with essential metadata

    Args:
        org_id: Organization ID

    Returns:
        List of project profiles
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    profile_id,
                    project_name,
                    study_id,
                    therapeutic_area,
                    phase,
                    primary_country,
                    additional_countries,
                    metadata,
                    created_at
                FROM project_profiles
                WHERE org_id = ?
                ORDER BY created_at DESC
            """, (org_id,))

            profiles = cursor.fetchall()

            return {
                "org_id": org_id,
                "count": len(profiles),
                "profiles": [dict(row) for row in profiles]
            }

    except Exception as e:
        logger.error(f"Failed to get project profiles: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get project profiles: {str(e)}"
        )


@router.post("/intelligence/project-profiles")
async def create_project_profile(
    org_id: str,
    profile: Dict
):
    """
    Create a new project profile

    Core Tier: Basic profiles
    Calibrated Tier: Advanced profiles with custom fields

    Args:
        org_id: Organization ID
        profile: Project profile data

    Returns:
        Created project profile
    """
    try:
        import secrets
        import json

        profile_id = f"prof_{secrets.token_urlsafe(12)}"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO project_profiles (
                    profile_id, org_id, project_name, study_id,
                    therapeutic_area, phase, primary_country,
                    additional_countries, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                org_id,
                profile.get('project_name'),
                profile.get('study_id'),
                profile.get('therapeutic_area'),
                profile.get('phase'),
                profile.get('primary_country'),
                json.dumps(profile.get('additional_countries', [])),
                json.dumps(profile.get('metadata', {}))
            ))

            conn.commit()

            return {
                "profile_id": profile_id,
                "message": "Project profile created successfully",
                **profile
            }

    except Exception as e:
        logger.error(f"Failed to create project profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create project profile: {str(e)}"
        )


# ============================================================================
# Helper Functions
# ============================================================================

def _get_org_intelligence_config(org_id: str, tier: str) -> IntelligenceConfig:
    """Get organization's intelligence configuration"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT intelligence_config FROM organizations WHERE org_id = ?
            """, (org_id,))

            row = cursor.fetchone()

            if row and row['intelligence_config']:
                import json
                config_dict = json.loads(row['intelligence_config']) if isinstance(row['intelligence_config'], str) else row['intelligence_config']
            else:
                # Default config
                config_dict = {
                    "variance_thresholds": {"warning_percent": 15.0, "critical_percent": 30.0},
                    "financial_rate_per_month_usd": 733000.0,
                    "benchmark_source": "industry_only"
                }

            return IntelligenceConfig(
                org_id=org_id,
                tier=tier,
                **config_dict
            )

    except Exception as e:
        logger.warning(f"Failed to get org config, using defaults: {e}")
        return IntelligenceConfig(
            org_id=org_id,
            tier=tier,
            variance_thresholds={"warning_percent": 15.0, "critical_percent": 30.0},
            financial_rate_per_month_usd=733000.0,
            benchmark_source="industry_only"
        )


def _track_intelligence_usage(
    conn,
    org_id: str,
    user_id: Optional[str],
    feature: str,
    tasks_analyzed: int,
    variances_detected: int,
    success: bool,
    error_message: Optional[str] = None
):
    """Track intelligence feature usage"""
    try:
        import secrets
        from datetime import datetime

        usage_id = f"usage_{secrets.token_urlsafe(12)}"

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO intelligence_usage (
                usage_id, org_id, user_id, feature, timestamp,
                tasks_analyzed, variances_detected, success, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            usage_id,
            org_id,
            user_id,
            feature,
            datetime.utcnow().isoformat(),
            tasks_analyzed,
            variances_detected,
            1 if success else 0,
            error_message
        ))

        conn.commit()
        logger.debug(f"Tracked intelligence usage: {feature} for org {org_id}")

    except Exception as e:
        logger.error(f"Failed to track intelligence usage: {e}")
        # Don't fail the request if usage tracking fails
