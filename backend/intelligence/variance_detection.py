"""
Variance Detection Engine - Core Intelligence Component

Detects variances between customer timelines and industry benchmarks.

Workflow:
1. Normalize task names (TaskNormalizer)
2. Retrieve benchmarks (BenchmarkRetriever)
3. Calculate variances
4. Classify severity (acceptable/warning/critical)
5. Calculate financial impact (FinancialImpactCalculator)
6. Generate comprehensive report
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .models import (
    VarianceReport,
    VarianceSignal,
    VarianceMetrics,
    VarianceSummary,
    BenchmarkCoverage,
    IntelligenceConfig
)
from .benchmark_retriever import BenchmarkRetriever
from .financial_calculator import FinancialImpactCalculator
from .task_normalizer import TaskNormalizer
from .metadata_inferrer import MetadataInferrer

logger = logging.getLogger(__name__)


class VarianceDetectionEngine:
    """
    Core variance detection engine

    Integrates:
    - BenchmarkRetriever: Get industry benchmarks
    - FinancialImpactCalculator: Calculate $ impact
    - TaskNormalizer: Handle task name mismatches
    - MetadataInferrer: Extract missing metadata
    """

    def __init__(
        self,
        benchmark_retriever: BenchmarkRetriever,
        financial_calculator: FinancialImpactCalculator,
        task_normalizer: Optional[TaskNormalizer] = None,
        metadata_inferrer: Optional[MetadataInferrer] = None
    ):
        """
        Initialize VarianceDetectionEngine

        Args:
            benchmark_retriever: BenchmarkRetriever instance
            financial_calculator: FinancialImpactCalculator instance
            task_normalizer: Optional TaskNormalizer instance
            metadata_inferrer: Optional MetadataInferrer instance
        """
        self.benchmark_retriever = benchmark_retriever
        self.financial_calculator = financial_calculator
        self.task_normalizer = task_normalizer
        self.metadata_inferrer = metadata_inferrer

        logger.info("VarianceDetectionEngine initialized")

    def detect_variances(
        self,
        timeline: Dict,
        tier_config: IntelligenceConfig,
        org_id: str
    ) -> VarianceReport:
        """
        Detect variances in timeline against benchmarks

        Args:
            timeline: Timeline data with tasks
            tier_config: Organization's intelligence configuration
            org_id: Organization ID

        Returns:
            VarianceReport with detailed variance analysis
        """
        start_time = datetime.utcnow()

        logger.info(f"Starting variance detection for org {org_id}, tier {tier_config.tier}")

        # Extract metadata if not provided
        timeline = self._ensure_metadata(timeline)

        # Process tasks
        variance_signals = []
        tasks_analyzed = 0
        tasks_with_benchmarks = 0
        unmatched_tasks = []

        match_quality = {
            "exact": 0,
            "fuzzy": 0,
            "category": 0,
            "special_case": 0
        }

        for task in timeline.get('tasks', []):
            tasks_analyzed += 1

            # Normalize task name if normalizer available
            task_name, normalized_task = self._normalize_task(
                task,
                org_id,
                timeline.get('category')
            )

            # Retrieve benchmark
            benchmark = self.benchmark_retriever.get_benchmark(
                task_name=task_name,
                category=task.get('category'),
                country=timeline.get('primary_country'),
                authority=task.get('authority'),
                phase=timeline.get('phase'),
                therapeutic_area=timeline.get('therapeutic_area'),
                site_type=task.get('site_type')
            )

            if not benchmark:
                unmatched_tasks.append(task_name)
                logger.debug(f"No benchmark found for: {task_name}")
                continue

            tasks_with_benchmarks += 1

            # Track match quality
            if normalized_task:
                if normalized_task.match_method == "exact":
                    match_quality["exact"] += 1
                elif normalized_task.match_method == "fuzzy":
                    match_quality["fuzzy"] += 1
                elif normalized_task.match_method == "cached":
                    match_quality["exact"] += 1

            # Calculate variance
            customer_duration = task.get('duration_days', 0)
            benchmark_duration = benchmark.typical_duration_days

            variance_days = customer_duration - benchmark_duration
            variance_percent = (variance_days / benchmark_duration * 100) if benchmark_duration > 0 else 0.0

            # Classify severity
            severity, classification = self._classify_variance(
                variance_percent,
                tier_config.variance_thresholds
            )

            # Calculate financial impact
            financial_impact = self.financial_calculator.calculate_impact(
                variance_days=variance_days,
                baseline_rate=tier_config.financial_rate_per_month_usd
            )

            # Generate explanation
            explanation = self._generate_explanation(
                task_name=task_name,
                customer_duration=customer_duration,
                benchmark_duration=benchmark_duration,
                variance_days=variance_days,
                severity=severity,
                classification=classification
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                severity=severity,
                classification=classification,
                variance_days=variance_days,
                benchmark=benchmark
            )

            # Create variance signal
            variance_signal = VarianceSignal(
                task_id=task.get('id', 'unknown'),
                task_name=task_name,
                customer_duration_days=customer_duration,
                benchmark=benchmark,
                variance=VarianceMetrics(
                    absolute_days=variance_days,
                    percentage=round(variance_percent, 2),
                    severity=severity,
                    classification=classification
                ),
                financial_impact_usd=round(financial_impact, 2),
                explanation=explanation,
                recommendations=recommendations if severity != "acceptable" else None
            )

            # Only include warning and critical signals in report (reduce noise)
            if severity in ["warning", "critical"]:
                variance_signals.append(variance_signal)

        # Generate summary
        summary = self._generate_summary(
            variance_signals=variance_signals,
            tasks_analyzed=tasks_analyzed,
            tasks_with_benchmarks=tasks_with_benchmarks,
            tier_config=tier_config
        )

        # Generate benchmark coverage report
        coverage = BenchmarkCoverage(
            tasks_matched=tasks_with_benchmarks,
            tasks_unmatched=len(unmatched_tasks),
            coverage_percent=round((tasks_with_benchmarks / tasks_analyzed * 100) if tasks_analyzed > 0 else 0.0, 2),
            unmatched_task_names=unmatched_tasks[:10],  # Top 10 unmatched
            match_quality=match_quality
        )

        # Build final report
        report = VarianceReport(
            tier=tier_config.tier,
            org_id=org_id,
            analysis_timestamp=datetime.utcnow().isoformat(),
            variance_signals=variance_signals,
            summary=summary,
            benchmark_coverage=coverage,
            configuration={
                "variance_thresholds": tier_config.variance_thresholds,
                "financial_rate_per_month_usd": tier_config.financial_rate_per_month_usd,
                "benchmark_source": tier_config.benchmark_source
            }
        )

        execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(f"Variance detection complete: {len(variance_signals)} signals, {execution_time:.0f}ms")

        return report

    def _ensure_metadata(self, timeline: Dict) -> Dict:
        """Ensure timeline has metadata (infer if missing)"""
        if not self.metadata_inferrer:
            return timeline

        # Check if metadata is missing
        missing_metadata = (
            not timeline.get('phase') or
            not timeline.get('therapeutic_area') or
            not timeline.get('primary_country')
        )

        if missing_metadata:
            logger.info("Inferring missing metadata from timeline")
            inferred = self.metadata_inferrer.infer_metadata(timeline)

            # Update timeline with inferred metadata (use inferred values if confident)
            if not inferred.get('needs_confirmation', False):
                if not timeline.get('phase') and inferred.get('phase'):
                    timeline['phase'] = inferred['phase']
                if not timeline.get('therapeutic_area') and inferred.get('therapeutic_area'):
                    timeline['therapeutic_area'] = inferred['therapeutic_area']
                if not timeline.get('primary_country') and inferred.get('primary_country'):
                    timeline['primary_country'] = inferred['primary_country']

        return timeline

    def _normalize_task(
        self,
        task: Dict,
        org_id: str,
        category_hint: Optional[str] = None
    ) -> Tuple[str, Optional[any]]:
        """
        Normalize task name if normalizer available

        Returns: (task_name, normalized_suggestion)
        """
        task_name = task.get('name', 'Unknown Task')

        if not self.task_normalizer:
            return (task_name, None)

        context = {'category': category_hint or task.get('category')}

        ontology_task_id, suggestion, unconfirmed = self.task_normalizer.normalize(
            customer_task_name=task_name,
            org_id=org_id,
            context=context
        )

        if suggestion and suggestion.confidence >= 0.7:
            # Use normalized name
            logger.debug(f"Task normalized: '{task_name}' -> '{suggestion.ontology_task_name}'")
            return (suggestion.ontology_task_name, suggestion)
        else:
            # Use original name
            return (task_name, None)

    def _classify_variance(
        self,
        variance_percent: float,
        thresholds: Dict[str, float]
    ) -> Tuple[str, str]:
        """
        Classify variance severity and direction

        Returns: (severity, classification)
        """
        abs_percent = abs(variance_percent)
        warning_threshold = thresholds.get("warning_percent", 15.0)
        critical_threshold = thresholds.get("critical_percent", 30.0)

        # Determine severity
        if abs_percent >= critical_threshold:
            severity = "critical"
        elif abs_percent >= warning_threshold:
            severity = "warning"
        else:
            severity = "acceptable"

        # Determine classification
        if variance_percent > 5:
            classification = "overestimate"
        elif variance_percent < -5:
            classification = "underestimate"
        else:
            classification = "on_target"

        return (severity, classification)

    def _generate_explanation(
        self,
        task_name: str,
        customer_duration: int,
        benchmark_duration: int,
        variance_days: int,
        severity: str,
        classification: str
    ) -> str:
        """Generate human-readable explanation"""
        if classification == "overestimate":
            direction = "longer than"
            impact = "wasted buffer time"
        elif classification == "underestimate":
            direction = "shorter than"
            impact = "potential delay risk"
        else:
            return f"Task '{task_name}' duration is on target with industry benchmarks."

        return (
            f"Task '{task_name}' is planned for {customer_duration} days, "
            f"which is {abs(variance_days)} days {direction} the industry benchmark "
            f"of {benchmark_duration} days. This represents {impact}."
        )

    def _generate_recommendations(
        self,
        severity: str,
        classification: str,
        variance_days: int,
        benchmark: any
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if classification == "overestimate" and severity in ["warning", "critical"]:
            recommendations.append(
                f"Consider reducing timeline by {abs(variance_days)} days to align with industry benchmarks"
            )
            recommendations.append(
                f"Review if this buffer is necessary or if tasks can be parallelized"
            )

        elif classification == "underestimate" and severity in ["warning", "critical"]:
            recommendations.append(
                f"Increase timeline by {abs(variance_days)} days to match industry benchmarks"
            )
            recommendations.append(
                f"Risk: Current timeline may lead to delays (${abs(variance_days) * 24433:,.0f} potential cost)"
            )
            if benchmark.data_quality:
                recommendations.append(f"Note: {benchmark.data_quality}")

        return recommendations

    def _generate_summary(
        self,
        variance_signals: List[VarianceSignal],
        tasks_analyzed: int,
        tasks_with_benchmarks: int,
        tier_config: IntelligenceConfig
    ) -> VarianceSummary:
        """Generate summary statistics"""
        warning_count = sum(1 for s in variance_signals if s.variance.severity == "warning")
        critical_count = sum(1 for s in variance_signals if s.variance.severity == "critical")
        acceptable_count = tasks_with_benchmarks - len(variance_signals)

        overestimate_count = sum(1 for s in variance_signals if s.variance.classification == "overestimate")
        underestimate_count = sum(1 for s in variance_signals if s.variance.classification == "underestimate")

        total_financial_impact = sum(s.financial_impact_usd for s in variance_signals)

        avg_variance_percent = (
            sum(abs(s.variance.percentage) for s in variance_signals) / len(variance_signals)
            if variance_signals else 0.0
        )

        coverage_percent = (tasks_with_benchmarks / tasks_analyzed * 100) if tasks_analyzed > 0 else 0.0

        return VarianceSummary(
            total_tasks_analyzed=tasks_analyzed,
            tasks_with_benchmarks=tasks_with_benchmarks,
            benchmark_coverage_percent=round(coverage_percent, 2),
            warning_count=warning_count,
            critical_count=critical_count,
            acceptable_count=acceptable_count,
            total_financial_impact_usd=round(total_financial_impact, 2),
            avg_variance_percent=round(avg_variance_percent, 2),
            overestimate_count=overestimate_count,
            underestimate_count=underestimate_count
        )
