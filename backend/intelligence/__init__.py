"""
Intelligence Module - Clinical Trial Timeline Intelligence Layer

Provides variance detection, confidence scoring, benchmark retrieval,
task normalization, and metadata inference for clinical trial timelines.

Components:
- VarianceDetectionEngine: Detect variances against industry benchmarks
- BenchmarkRetriever: Query ontology for task-specific benchmarks
- FinancialImpactCalculator: Calculate financial impact of timeline variances
- TaskNormalizer: Normalize customer task names to ontology tasks
- MetadataInferrer: Infer missing metadata from timeline content
"""

from .models import (
    BenchmarkData,
    VarianceMetrics,
    VarianceSignal,
    VarianceSummary,
    BenchmarkCoverage,
    VarianceReport,
    IntelligenceData,
    IntelligenceConfig,
    UnconfirmedMatch,
    TaskMappingSuggestion,
    MetadataInference,
    MetadataConfirmationRequired,
    OrgBenchmark,
    PatternDetection,
    TaskPattern,
    CalibrationResult,
    BlendedBenchmark,
    ConfidenceScore,
    StudyMetadata,
    MetadataValidationResult
)

from .benchmark_retriever import BenchmarkRetriever
from .financial_calculator import FinancialImpactCalculator
from .variance_detection import VarianceDetectionEngine
from .task_normalizer import TaskNormalizer
from .metadata_inferrer import MetadataInferrer
from .calibration_engine import CalibrationEngine
from .benchmark_blender import BenchmarkBlender
from .confidence_scorer import ConfidenceScoringEngine
from .portfolio_aggregator import PortfolioAggregationEngine
from .resource_collision_detector import ResourceCollisionDetector, ResourceAssignment, ResourceCollision
from .portfolio_forecaster import PortfolioForecaster
from .tier_enforcement import require_tier, check_tier

__all__ = [
    # Models
    "BenchmarkData",
    "VarianceMetrics",
    "VarianceSignal",
    "VarianceSummary",
    "BenchmarkCoverage",
    "VarianceReport",
    "IntelligenceData",
    "IntelligenceConfig",
    "UnconfirmedMatch",
    "TaskMappingSuggestion",
    "MetadataInference",
    "MetadataConfirmationRequired",
    "OrgBenchmark",
    "PatternDetection",
    "TaskPattern",
    "CalibrationResult",
    "BlendedBenchmark",
    "ConfidenceScore",
    "StudyMetadata",
    "MetadataValidationResult",
    # Classes
    "BenchmarkRetriever",
    "FinancialImpactCalculator",
    "VarianceDetectionEngine",
    "TaskNormalizer",
    "MetadataInferrer",
    "CalibrationEngine",
    "BenchmarkBlender",
    "ConfidenceScoringEngine",
    "PortfolioAggregationEngine",
    "ResourceCollisionDetector",
    "ResourceAssignment",
    "ResourceCollision",
    "PortfolioForecaster",
    # Decorators
    "require_tier",
    "check_tier",
]

__version__ = "1.0.0"
