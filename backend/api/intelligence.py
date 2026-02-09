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
    CalibrationEngine,
    BenchmarkBlender,
    ConfidenceScoringEngine,
    PortfolioAggregationEngine,
    ResourceCollisionDetector,
    ResourceAssignment,
    PortfolioForecaster,
    IntelligenceConfig,
    BenchmarkData,
    VarianceReport,
    TaskMappingSuggestion,
    MetadataInference,
    CalibrationResult,
    OrgBenchmark,
    BlendedBenchmark,
    ConfidenceScore,
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
# Calibration Endpoints (Calibrated Tier)
# ============================================================================

@router.post("/calibration/upload", response_model=CalibrationResult)
@require_tier(['calibrated', 'enterprise'])
async def upload_calibration_file(
    org_id: str,
    file_content: bytes,
    project_metadata: Optional[Dict] = None
):
    """
    Upload and process historical MS Project file for calibration

    Calibrated Tier Feature: Generates org-specific benchmarks from historical data

    Args:
        org_id: Organization ID
        file_content: Raw bytes of .mpp or XML export
        project_metadata: Optional metadata (phase, therapeutic_area, country)

    Returns:
        CalibrationResult with extracted benchmarks and patterns
    """
    try:
        logger.info(f"Processing calibration upload for org {org_id}")

        with get_db_connection() as conn:
            # Initialize task normalizer
            ontology_tasks = config.get('tasks', [])
            task_normalizer = TaskNormalizer(
                ontology_tasks=ontology_tasks,
                db_connection=conn,
                confidence_threshold=0.7
            )

            # Initialize calibration engine
            calibration_engine = CalibrationEngine(task_normalizer=task_normalizer)

            # Process the file
            calibration_result = calibration_engine.process_mpp_file(
                file_content=file_content,
                org_id=org_id,
                project_metadata=project_metadata
            )

            # Store org benchmarks in database
            _store_org_benchmarks(conn, org_id, calibration_result.org_benchmarks)

            # Store calibration result
            _store_calibration_result(conn, org_id, calibration_result)

            # Track usage
            _track_intelligence_usage(
                conn=conn,
                org_id=org_id,
                user_id=None,
                feature="calibration_upload",
                tasks_analyzed=calibration_result.tasks_extracted,
                variances_detected=0,
                success=True
            )

            logger.info(f"Calibration complete: {calibration_result.benchmarks_generated} benchmarks generated")

            return calibration_result

    except ValueError as e:
        logger.error(f"Invalid file format: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Calibration upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Calibration upload failed: {str(e)}"
        )


@router.get("/calibration/results")
@require_tier(['calibrated', 'enterprise'])
async def get_calibration_results(org_id: str, limit: int = 10):
    """
    Get calibration results history for organization

    Calibrated Tier Feature: View historical calibration processing results

    Args:
        org_id: Organization ID
        limit: Maximum number of results to return

    Returns:
        List of CalibrationResult objects
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    calibration_id,
                    project_name,
                    tasks_extracted,
                    tasks_normalized,
                    benchmarks_generated,
                    patterns_detected,
                    quality_metrics,
                    metadata,
                    created_at
                FROM calibration_results
                WHERE org_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (org_id, limit))

            results = cursor.fetchall()

            return {
                "org_id": org_id,
                "count": len(results),
                "results": [dict(row) for row in results]
            }

    except Exception as e:
        logger.error(f"Failed to get calibration results: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get calibration results: {str(e)}"
        )


@router.get("/calibration/org-benchmarks", response_model=List[OrgBenchmark])
@require_tier(['calibrated', 'enterprise'])
async def get_org_benchmarks(org_id: str):
    """
    Get organization-specific benchmarks

    Calibrated Tier Feature: Retrieve org benchmarks generated from calibration

    Args:
        org_id: Organization ID

    Returns:
        List of OrgBenchmark objects
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    ontology_task_id,
                    task_name,
                    category,
                    median_days,
                    p25_days,
                    p75_days,
                    sample_size,
                    confidence,
                    last_updated
                FROM org_benchmarks
                WHERE org_id = ?
                ORDER BY category, task_name
            """, (org_id,))

            benchmarks = cursor.fetchall()

            return [
                OrgBenchmark(
                    org_id=org_id,
                    ontology_task_id=row['ontology_task_id'],
                    task_name=row['task_name'],
                    category=row['category'],
                    median_days=row['median_days'],
                    p25_days=row['p25_days'],
                    p75_days=row['p75_days'],
                    sample_size=row['sample_size'],
                    confidence=row['confidence'],
                    last_updated=row['last_updated']
                )
                for row in benchmarks
            ]

    except Exception as e:
        logger.error(f"Failed to get org benchmarks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get org benchmarks: {str(e)}"
        )


@router.get("/calibration/blended-benchmarks", response_model=List[BlendedBenchmark])
@require_tier(['calibrated', 'enterprise'])
async def get_blended_benchmarks(
    org_id: str,
    org_weight: Optional[float] = None,
    min_org_samples: int = 3
):
    """
    Get blended benchmarks (org + industry)

    Calibrated Tier Feature: Retrieve weighted blend of org and industry benchmarks

    Args:
        org_id: Organization ID
        org_weight: Optional custom org weight (default 0.7)
        min_org_samples: Minimum org samples required (default 3)

    Returns:
        List of BlendedBenchmark objects with blended values
    """
    try:
        with get_db_connection() as conn:
            # Get org benchmarks
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    ontology_task_id,
                    task_name,
                    category,
                    median_days,
                    p25_days,
                    p75_days,
                    sample_size,
                    confidence,
                    last_updated
                FROM org_benchmarks
                WHERE org_id = ?
            """, (org_id,))

            org_benchmark_rows = cursor.fetchall()
            org_benchmarks = [
                OrgBenchmark(
                    org_id=org_id,
                    ontology_task_id=row['ontology_task_id'],
                    task_name=row['task_name'],
                    category=row['category'],
                    median_days=row['median_days'],
                    p25_days=row['p25_days'],
                    p75_days=row['p75_days'],
                    sample_size=row['sample_size'],
                    confidence=row['confidence'],
                    last_updated=row['last_updated']
                )
                for row in org_benchmark_rows
            ]

            # Get industry benchmarks from ontology
            industry_benchmarks = []
            for task in config.get('tasks', []):
                if 'benchmarks' in task and 'industry' in task['benchmarks']:
                    industry_data = task['benchmarks']['industry']
                    industry_benchmarks.append(BenchmarkData(
                        task_id=task['task_id'],
                        task_name=task['name'],
                        category=task['category'],
                        median_days=industry_data.get('median_days', 0),
                        p25_days=industry_data.get('p25_days', 0),
                        p75_days=industry_data.get('p75_days', 0),
                        typical_duration_days=industry_data.get('median_days', 0),
                        source=industry_data.get('source', 'Industry'),
                        confidence=industry_data.get('confidence', 'medium')
                    ))

            # Blend benchmarks
            blender = BenchmarkBlender(default_org_weight=org_weight or 0.7)
            blended_benchmarks = blender.blend_benchmarks(
                org_benchmarks=org_benchmarks,
                industry_benchmarks=industry_benchmarks,
                org_weight=org_weight,
                min_org_samples=min_org_samples
            )

            logger.info(f"Generated {len(blended_benchmarks)} blended benchmarks for org {org_id}")

            return blended_benchmarks

    except Exception as e:
        logger.error(f"Failed to get blended benchmarks: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get blended benchmarks: {str(e)}"
        )


@router.post("/calibration/confidence-score", response_model=ConfidenceScore)
@require_tier(['calibrated', 'enterprise'])
async def calculate_confidence_score(
    org_id: str,
    task_id: str,
    task_name: str,
    task_category: str,
    customer_duration_days: int,
    dependency_count: int = 0,
    is_on_critical_path: bool = False
):
    """
    Calculate confidence score for a task estimate

    Calibrated Tier Feature: Multi-factor confidence analysis

    Args:
        org_id: Organization ID
        task_id: Task identifier
        task_name: Task name
        task_category: Task category
        customer_duration_days: Customer's estimated duration
        dependency_count: Number of dependent tasks
        is_on_critical_path: Whether task is on critical path

    Returns:
        ConfidenceScore with overall score and factor breakdown
    """
    try:
        with get_db_connection() as conn:
            # Get blended benchmark
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    ontology_task_id,
                    task_name,
                    category,
                    median_days,
                    sample_size,
                    confidence
                FROM org_benchmarks
                WHERE org_id = ? AND ontology_task_id = ?
            """, (org_id, task_id))

            org_bench_row = cursor.fetchone()

            # Get industry benchmark
            industry_benchmark = benchmark_retriever.get_benchmark(
                category=task_category
            )

            # Create blended benchmark if both available
            benchmark = None
            if org_bench_row and industry_benchmark:
                blender = BenchmarkBlender(default_org_weight=0.7)
                org_bench = OrgBenchmark(
                    org_id=org_id,
                    ontology_task_id=org_bench_row['ontology_task_id'],
                    task_name=org_bench_row['task_name'],
                    category=org_bench_row['category'],
                    median_days=org_bench_row['median_days'],
                    p25_days=0,
                    p75_days=0,
                    sample_size=org_bench_row['sample_size'],
                    confidence=org_bench_row['confidence'],
                    last_updated=''
                )

                blended = blender.blend_benchmarks(
                    org_benchmarks=[org_bench],
                    industry_benchmarks=[industry_benchmark],
                    min_org_samples=3
                )

                benchmark = blended[0] if blended else None

            # Calculate confidence
            confidence_engine = ConfidenceScoringEngine()
            has_regulatory = task_category == 'Regulatory'

            confidence_score = confidence_engine.calculate_confidence(
                task_id=task_id,
                task_name=task_name,
                task_category=task_category,
                customer_duration_days=customer_duration_days,
                benchmark=benchmark,
                org_sample_size=org_bench_row['sample_size'] if org_bench_row else 0,
                dependency_count=dependency_count,
                is_on_critical_path=is_on_critical_path,
                has_regulatory_component=has_regulatory
            )

            return confidence_score

    except Exception as e:
        logger.error(f"Failed to calculate confidence score: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate confidence score: {str(e)}"
        )


# ============================================================================
# Portfolio Endpoints (Enterprise Tier)
# ============================================================================

@router.get("/portfolio/analytics")
@require_tier(['enterprise'])
async def get_portfolio_analytics(org_id: str):
    """
    Get portfolio-level intelligence analytics

    Enterprise Tier Feature: Aggregated intelligence across all studies

    Args:
        org_id: Organization identifier

    Returns:
        Portfolio aggregation with health score, patterns, risks, metrics
    """
    try:
        logger.info(f"Portfolio analytics request for org {org_id}")

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get all active studies for organization
            cursor.execute("""
                SELECT study_id, study_name, phase, status, start_date,
                       timeline_status, created_at
                FROM studies
                WHERE org_id = ? AND status IN ('active', 'planned')
                ORDER BY created_at DESC
            """, (org_id,))

            studies = [dict(row) for row in cursor.fetchall()]

            # Get variance reports for all studies
            cursor.execute("""
                SELECT study_id, variance_report, created_at
                FROM variance_reports
                WHERE org_id = ?
                ORDER BY created_at DESC
                LIMIT 50
            """, (org_id,))

            import json
            variance_reports = []
            for row in cursor.fetchall():
                report = json.loads(row['variance_report']) if isinstance(row['variance_report'], str) else row['variance_report']
                variance_reports.append(report)

            # Get org benchmarks
            cursor.execute("""
                SELECT ontology_task_id, task_name, category, median_days,
                       p25_days, p75_days, sample_size, confidence
                FROM org_benchmarks
                WHERE org_id = ?
            """, (org_id,))

            org_benchmarks = [dict(row) for row in cursor.fetchall()]

            # Aggregate portfolio
            aggregator = PortfolioAggregationEngine()
            portfolio_analytics = aggregator.aggregate_portfolio(
                org_id=org_id,
                studies=studies,
                variance_reports=variance_reports,
                org_benchmarks=org_benchmarks
            )

            # Track usage
            _track_intelligence_usage(
                conn=conn,
                org_id=org_id,
                user_id=None,
                feature="portfolio_analytics",
                tasks_analyzed=len(studies),
                variances_detected=0,
                success=True
            )

            return portfolio_analytics

    except Exception as e:
        logger.error(f"Portfolio analytics failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio analytics failed: {str(e)}"
        )


@router.get("/portfolio/collisions")
@require_tier(['enterprise'])
async def detect_resource_collisions(org_id: str):
    """
    Detect resource collisions across portfolio

    Enterprise Tier Feature: Identifies overlapping resource assignments

    Args:
        org_id: Organization identifier

    Returns:
        Collision report with detected conflicts and recommendations
    """
    try:
        logger.info(f"Resource collision detection for org {org_id}")

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get resource assignments across all studies
            cursor.execute("""
                SELECT resource_id, resource_name, resource_type,
                       study_id, study_name, start_date, end_date,
                       utilization_percent
                FROM resource_assignments
                WHERE org_id = ? AND status = 'active'
            """, (org_id,))

            assignments_data = cursor.fetchall()

            # Convert to ResourceAssignment objects
            assignments = []
            for row in assignments_data:
                assignment = ResourceAssignment(
                    resource_id=row['resource_id'],
                    resource_name=row['resource_name'],
                    resource_type=row['resource_type'],
                    study_id=row['study_id'],
                    study_name=row['study_name'],
                    start_date=row['start_date'],
                    end_date=row['end_date'],
                    utilization_percent=row.get('utilization_percent', 100.0)
                )
                assignments.append(assignment)

            # Detect collisions
            detector = ResourceCollisionDetector()
            collision_report = detector.detect_collisions(
                org_id=org_id,
                resource_assignments=assignments
            )

            # Track usage
            _track_intelligence_usage(
                conn=conn,
                org_id=org_id,
                user_id=None,
                feature="resource_collision_detection",
                tasks_analyzed=len(assignments),
                variances_detected=collision_report['summary']['total_collisions'],
                success=True
            )

            return collision_report

    except Exception as e:
        logger.error(f"Resource collision detection failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Resource collision detection failed: {str(e)}"
        )


@router.get("/portfolio/forecast")
@require_tier(['enterprise'])
async def forecast_portfolio(
    org_id: str,
    horizon_days: int = 90
):
    """
    Generate portfolio forecast

    Enterprise Tier Feature: Projects milestones, resource needs, capacity

    Args:
        org_id: Organization identifier
        horizon_days: Forecast horizon in days (default 90)

    Returns:
        Forecast with predicted milestones, resource needs, risks
    """
    try:
        logger.info(f"Portfolio forecast for org {org_id}, horizon {horizon_days} days")

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Get active studies
            cursor.execute("""
                SELECT study_id, study_name, phase, status, start_date,
                       therapeutic_area, timeline_status
                FROM studies
                WHERE org_id = ? AND status = 'active'
            """, (org_id,))

            studies = [dict(row) for row in cursor.fetchall()]

            # Get org benchmarks
            cursor.execute("""
                SELECT ontology_task_id, task_name, category, median_days,
                       sample_size, confidence
                FROM org_benchmarks
                WHERE org_id = ?
            """, (org_id,))

            org_benchmarks = [dict(row) for row in cursor.fetchall()]

            # TODO: Get historical performance (mock for now)
            historical_performance = None

            # Generate forecast
            forecaster = PortfolioForecaster()
            forecast = forecaster.forecast_portfolio(
                org_id=org_id,
                studies=studies,
                org_benchmarks=org_benchmarks,
                historical_performance=historical_performance,
                horizon_days=horizon_days
            )

            # Track usage
            _track_intelligence_usage(
                conn=conn,
                org_id=org_id,
                user_id=None,
                feature="portfolio_forecast",
                tasks_analyzed=len(studies),
                variances_detected=0,
                success=True
            )

            return forecast

    except Exception as e:
        logger.error(f"Portfolio forecast failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Portfolio forecast failed: {str(e)}"
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


def _store_org_benchmarks(conn, org_id: str, org_benchmarks: List[OrgBenchmark]):
    """Store organization-specific benchmarks in database"""
    try:
        cursor = conn.cursor()

        for benchmark in org_benchmarks:
            # Check if benchmark exists
            cursor.execute("""
                SELECT ontology_task_id FROM org_benchmarks
                WHERE org_id = ? AND ontology_task_id = ?
            """, (org_id, benchmark.ontology_task_id))

            exists = cursor.fetchone()

            if exists:
                # Update existing
                cursor.execute("""
                    UPDATE org_benchmarks SET
                        task_name = ?,
                        category = ?,
                        median_days = ?,
                        p25_days = ?,
                        p75_days = ?,
                        sample_size = ?,
                        confidence = ?,
                        last_updated = ?
                    WHERE org_id = ? AND ontology_task_id = ?
                """, (
                    benchmark.task_name,
                    benchmark.category,
                    benchmark.median_days,
                    benchmark.p25_days,
                    benchmark.p75_days,
                    benchmark.sample_size,
                    benchmark.confidence,
                    benchmark.last_updated,
                    org_id,
                    benchmark.ontology_task_id
                ))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO org_benchmarks (
                        org_id, ontology_task_id, task_name, category,
                        median_days, p25_days, p75_days, sample_size,
                        confidence, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    org_id,
                    benchmark.ontology_task_id,
                    benchmark.task_name,
                    benchmark.category,
                    benchmark.median_days,
                    benchmark.p25_days,
                    benchmark.p75_days,
                    benchmark.sample_size,
                    benchmark.confidence,
                    benchmark.last_updated
                ))

        conn.commit()
        logger.debug(f"Stored {len(org_benchmarks)} org benchmarks for {org_id}")

    except Exception as e:
        logger.error(f"Failed to store org benchmarks: {e}")
        raise


def _store_calibration_result(conn, org_id: str, result: CalibrationResult):
    """Store calibration result in database"""
    try:
        import secrets
        import json
        from datetime import datetime

        calibration_id = f"cal_{secrets.token_urlsafe(12)}"

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO calibration_results (
                calibration_id, org_id, project_name,
                tasks_extracted, tasks_normalized, benchmarks_generated,
                patterns_detected, quality_metrics, metadata, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            calibration_id,
            org_id,
            result.project_name,
            result.tasks_extracted,
            result.tasks_normalized,
            result.benchmarks_generated,
            json.dumps([p.dict() for p in result.patterns_detected]),
            json.dumps(result.quality_metrics),
            json.dumps(result.metadata),
            datetime.utcnow().isoformat()
        ))

        conn.commit()
        logger.debug(f"Stored calibration result {calibration_id} for {org_id}")

    except Exception as e:
        logger.error(f"Failed to store calibration result: {e}")
        raise
