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
    MetadataConfirmationRequired
)

from .benchmark_retriever import BenchmarkRetriever
from .financial_calculator import FinancialImpactCalculator
from .variance_detection import VarianceDetectionEngine
from .task_normalizer import TaskNormalizer
from .metadata_inferrer import MetadataInferrer
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
    # Classes
    "BenchmarkRetriever",
    "FinancialImpactCalculator",
    "VarianceDetectionEngine",
    "TaskNormalizer",
    "MetadataInferrer",
    # Decorators
    "require_tier",
    "check_tier",
]

__version__ = "1.0.0"
