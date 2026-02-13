"""
Pydantic Models for Intelligence Layer

Defines all data structures for intelligence responses including:
- Benchmark data
- Variance detection
- Task normalization
- Metadata inference
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Benchmark Models
# ============================================================================

class BenchmarkData(BaseModel):
    """Industry benchmark data for a task"""
    task_id: str
    task_name: str
    category: str
    median_days: int
    p25_days: int
    p75_days: int
    typical_duration_days: int  # Alias for median_days for backward compatibility
    sample_size: Optional[int] = None
    source: str  # "WCG", "Emmes", "Tufts CSDD", "CenterWatch", etc.
    confidence: str = "high"  # "high", "medium", "low"
    data_quality: Optional[str] = None
    last_updated: Optional[str] = None
    country_code: Optional[str] = None
    authority: Optional[str] = None
    phase: Optional[str] = None
    therapeutic_area: Optional[str] = None


# ============================================================================
# Variance Detection Models
# ============================================================================

class VarianceMetrics(BaseModel):
    """Variance metrics for a single task"""
    absolute_days: int  # Difference in days (actual - benchmark)
    percentage: float  # Variance percentage
    severity: str  # "acceptable", "warning", "critical"
    classification: str  # "overestimate", "underestimate", "on_target"


class VarianceSignal(BaseModel):
    """Individual variance signal for a task"""
    task_id: str
    task_name: str
    customer_duration_days: int
    benchmark: BenchmarkData
    variance: VarianceMetrics
    financial_impact_usd: float
    explanation: str  # Human-readable explanation
    recommendations: Optional[List[str]] = None


class VarianceSummary(BaseModel):
    """Summary statistics for variance report"""
    total_tasks_analyzed: int
    tasks_with_benchmarks: int
    benchmark_coverage_percent: float
    warning_count: int
    critical_count: int
    acceptable_count: int
    total_financial_impact_usd: float
    avg_variance_percent: float
    overestimate_count: int
    underestimate_count: int


class BenchmarkCoverage(BaseModel):
    """Benchmark coverage statistics"""
    tasks_matched: int
    tasks_unmatched: int
    coverage_percent: float
    unmatched_task_names: List[str]
    match_quality: Dict[str, int]  # {"exact": 10, "fuzzy": 5, "category": 3}


class VarianceReport(BaseModel):
    """Complete variance detection report"""
    tier: str  # "core", "calibrated", "enterprise"
    org_id: str
    analysis_timestamp: str
    variance_signals: List[VarianceSignal]
    summary: VarianceSummary
    benchmark_coverage: BenchmarkCoverage
    configuration: Optional[Dict[str, Any]] = None


class IntelligenceData(BaseModel):
    """Wrapper for intelligence data in validation response"""
    enabled: bool = True
    tier: str
    variance_report: Optional[VarianceReport] = None
    confidence_score: Optional[float] = None  # For Calibrated tier
    metadata_suggestions: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


# ============================================================================
# Task Normalization Models
# ============================================================================

class TaskMappingSuggestion(BaseModel):
    """Suggested mapping from customer task name to ontology task"""
    ontology_task_id: str
    ontology_task_name: str
    ontology_category: str
    confidence: float  # 0.0 to 1.0
    match_method: str  # "exact", "fuzzy", "keyword", "semantic"
    match_score: float
    explanation: Optional[str] = None


class UnconfirmedMatch(BaseModel):
    """Task mapping that needs user review"""
    customer_task_name: str
    suggestions: List[TaskMappingSuggestion]
    needs_review: bool = True
    reason: str = "Low confidence match"


class TaskMapping(BaseModel):
    """Confirmed task mapping"""
    mapping_id: str
    org_id: str
    customer_task_name: str
    ontology_task_id: str
    ontology_task_name: str
    confidence: float
    confirmed_by_user: bool = False
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Metadata Inference Models
# ============================================================================

class MetadataInference(BaseModel):
    """Inferred metadata with confidence"""
    field_name: str  # "phase", "therapeutic_area", "primary_country"
    inferred_value: str
    confidence: float  # 0.0 to 1.0
    evidence: List[str]  # Evidence from timeline (task names, patterns, etc.)
    inference_method: str  # "pattern_matching", "keyword_extraction", "heuristic"


class MetadataConfirmationRequired(BaseModel):
    """Metadata that needs user confirmation"""
    phase: Optional[MetadataInference] = None
    therapeutic_area: Optional[MetadataInference] = None
    primary_country: Optional[MetadataInference] = None
    additional_countries: Optional[List[MetadataInference]] = None
    needs_confirmation: bool = True
    message: str = "Please review and confirm the inferred metadata"


class ProjectProfile(BaseModel):
    """Project profile with metadata"""
    profile_id: str
    org_id: str
    project_name: str
    study_id: Optional[str] = None
    therapeutic_area: Optional[str] = None
    phase: Optional[str] = None
    primary_country: Optional[str] = None
    additional_countries: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Study Metadata Models (REQUIRED for accurate benchmarking)
# ============================================================================

class StudyMetadata(BaseModel):
    """
    Required metadata for accurate benchmark matching

    Critical for intelligence accuracy - benchmarks vary dramatically by:
    - Phase: Phase I timelines ≠ Phase III timelines
    - Therapeutic Area: Oncology ≠ Cardiology timelines
    - Country: US/FDA ≠ EU/EMA ≠ Japan/PMDA timelines
    """
    phase: str  # "Phase I", "Phase II", "Phase III", "Phase IV"
    therapeutic_area: str  # "Oncology", "Cardiology", "Neurology", etc.
    primary_country: str  # ISO country code or authority name
    additional_countries: Optional[List[str]] = None
    study_name: Optional[str] = None
    study_id: Optional[str] = None
    metadata_source: str = "user_provided"  # "user_provided", "inferred", "project_profile"

    def validate_required_fields(self) -> bool:
        """Validate that critical fields are populated"""
        return bool(self.phase and self.therapeutic_area and self.primary_country)


class MetadataValidationResult(BaseModel):
    """Result of validating study metadata against available benchmarks"""
    is_valid: bool
    coverage_percent: float
    benchmarks_available: int
    total_task_categories: int
    missing_benchmarks: List[str]
    warnings: List[str]
    recommendations: List[str]


# ============================================================================
# Configuration Models
# ============================================================================

class IntelligenceConfig(BaseModel):
    """Organization-specific intelligence configuration"""
    org_id: str
    tier: str
    variance_thresholds: Dict[str, float] = {
        "warning_percent": 15.0,
        "critical_percent": 30.0
    }
    financial_rate_per_month_usd: float = 733000.0
    financial_impact_enabled: bool = True  # NEW: Can disable financial calculations
    benchmark_source: str = "industry_only"  # "industry_only", "blended", "org_only"
    blend_ratio: Optional[Dict[str, float]] = None  # {"org": 0.7, "industry": 0.3}
    enabled_features: List[str] = ["variance_detection"]
    organization_defaults: Optional[Dict[str, Any]] = None  # Default phase, therapeutic areas, countries


class TierConfiguration(BaseModel):
    """Tier-specific feature configuration"""
    tier: str
    features_enabled: List[str]
    benchmark_source: str
    confidence_thresholds: Optional[Dict[str, float]] = None
    auto_apply_calibration: bool = False


# ============================================================================
# Calibration Models (Calibrated Tier)
# ============================================================================

class OrgBenchmark(BaseModel):
    """Organization-specific benchmark from calibration"""
    org_id: str
    ontology_task_id: str
    task_name: str
    category: str
    median_days: float
    p25_days: float
    p75_days: float
    sample_size: int
    confidence: float  # 0-1 based on sample size
    last_updated: str


class PatternDetection(BaseModel):
    """Detected organizational execution pattern"""
    pattern_type: str  # 'duration_consistency', 'execution_speed', etc.
    category: str
    description: str
    confidence: float
    sample_size: int


class TaskPattern(BaseModel):
    """Individual task execution pattern"""
    task_name: str
    avg_duration_days: float
    std_deviation: float
    sample_count: int


class CalibrationResult(BaseModel):
    """Result of processing a historical timeline for calibration"""
    org_id: str
    project_name: str
    tasks_extracted: int
    tasks_normalized: int
    benchmarks_generated: int
    patterns_detected: List[PatternDetection]
    org_benchmarks: List[OrgBenchmark]
    quality_metrics: Dict[str, Any]
    metadata: Dict[str, Any] = {}


class BlendedBenchmark(BaseModel):
    """Benchmark blending organization and industry data"""
    task_id: str
    task_name: str
    category: str
    org_median_days: Optional[float] = None
    industry_median_days: float
    blended_median_days: float
    blend_ratio: Dict[str, float]  # {"org": 0.7, "industry": 0.3}
    org_sample_size: int = 0
    confidence: float


class ConfidenceScore(BaseModel):
    """Multi-factor confidence score for a task estimate"""
    task_id: str
    task_name: str
    overall_score: float  # 0-100
    factors: Dict[str, float]  # variance, fragility, calibration, complexity
    risk_drivers: List[str]
    recommendations: List[str]
