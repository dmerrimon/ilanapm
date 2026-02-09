"""
Confidence Scoring Engine
Calculates multi-factor confidence scores for task duration estimates
"""

from typing import List, Dict, Optional
from .models import (
    ConfidenceScore,
    BenchmarkData,
    OrgBenchmark,
    VarianceMetrics,
    BlendedBenchmark
)


class ConfidenceScoringEngine:
    """
    Calculates confidence scores for task estimates based on multiple factors:
    - Variance from benchmarks (how far from expected)
    - Task fragility (dependency sensitivity)
    - Calibration quality (org data sample size)
    - Task complexity (inherent predictability)
    """

    def __init__(self):
        # Weighting factors for overall confidence calculation
        self.weights = {
            'variance': 0.35,      # How close to benchmark
            'fragility': 0.25,     # Dependency risk
            'calibration': 0.25,   # Data quality
            'complexity': 0.15     # Task type predictability
        }

    def calculate_confidence(
        self,
        task_id: str,
        task_name: str,
        task_category: str,
        customer_duration_days: int,
        benchmark: Optional[BlendedBenchmark],
        org_sample_size: int = 0,
        dependency_count: int = 0,
        is_on_critical_path: bool = False,
        has_regulatory_component: bool = False
    ) -> ConfidenceScore:
        """
        Calculate comprehensive confidence score for a task estimate

        Args:
            task_id: Task identifier
            task_name: Task name
            task_category: Task category
            customer_duration_days: Customer's estimated duration
            benchmark: Blended benchmark (org + industry)
            org_sample_size: Number of org historical samples
            dependency_count: Number of dependent tasks
            is_on_critical_path: Whether task is on critical path
            has_regulatory_component: Whether task involves regulatory work

        Returns:
            ConfidenceScore with overall score (0-100) and factor breakdown
        """
        factors = {}
        risk_drivers = []
        recommendations = []

        # Factor 1: Variance Score (how close to benchmark)
        variance_score = self._calculate_variance_score(
            customer_duration_days,
            benchmark,
            risk_drivers,
            recommendations
        )
        factors['variance'] = round(variance_score, 2)

        # Factor 2: Fragility Score (dependency and critical path risk)
        fragility_score = self._calculate_fragility_score(
            dependency_count,
            is_on_critical_path,
            risk_drivers,
            recommendations
        )
        factors['fragility'] = round(fragility_score, 2)

        # Factor 3: Calibration Score (org data quality)
        calibration_score = self._calculate_calibration_score(
            org_sample_size,
            benchmark,
            risk_drivers,
            recommendations
        )
        factors['calibration'] = round(calibration_score, 2)

        # Factor 4: Complexity Score (task type predictability)
        complexity_score = self._calculate_complexity_score(
            task_category,
            has_regulatory_component,
            risk_drivers,
            recommendations
        )
        factors['complexity'] = round(complexity_score, 2)

        # Calculate weighted overall score (0-100)
        overall_score = (
            factors['variance'] * self.weights['variance'] +
            factors['fragility'] * self.weights['fragility'] +
            factors['calibration'] * self.weights['calibration'] +
            factors['complexity'] * self.weights['complexity']
        )

        return ConfidenceScore(
            task_id=task_id,
            task_name=task_name,
            overall_score=round(overall_score, 1),
            factors=factors,
            risk_drivers=risk_drivers,
            recommendations=recommendations
        )

    def _calculate_variance_score(
        self,
        customer_duration: int,
        benchmark: Optional[BlendedBenchmark],
        risk_drivers: List[str],
        recommendations: List[str]
    ) -> float:
        """
        Calculate score based on variance from benchmark (0-100)

        Score = 100 when variance = 0%
        Score = 50 when variance = 30%
        Score = 0 when variance >= 100%
        """
        if not benchmark:
            risk_drivers.append("No benchmark available for comparison")
            recommendations.append("Consider adding historical data for this task type")
            return 50.0  # Medium confidence without benchmark

        variance_percent = abs(
            (customer_duration - benchmark.blended_median_days) /
            benchmark.blended_median_days * 100
        )

        # Linear decay: 100 at 0%, 0 at 100% variance
        score = max(0, 100 - variance_percent)

        if variance_percent > 50:
            risk_drivers.append(f"High variance from benchmark ({variance_percent:.1f}%)")
            recommendations.append("Review task duration estimate against industry standards")
        elif variance_percent > 30:
            risk_drivers.append(f"Moderate variance from benchmark ({variance_percent:.1f}%)")

        return score

    def _calculate_fragility_score(
        self,
        dependency_count: int,
        is_on_critical_path: bool,
        risk_drivers: List[str],
        recommendations: List[str]
    ) -> float:
        """
        Calculate score based on task fragility (0-100)

        Lower score = more fragile (high dependency, critical path)
        Higher score = more robust (independent task)
        """
        # Base score
        score = 100.0

        # Penalty for dependencies (5 points per dependency, max 40 points)
        dependency_penalty = min(dependency_count * 5, 40)
        score -= dependency_penalty

        if dependency_count > 5:
            risk_drivers.append(f"High dependency count ({dependency_count} tasks)")
            recommendations.append("Consider breaking down dependencies or adding buffer time")
        elif dependency_count > 3:
            risk_drivers.append(f"Moderate dependencies ({dependency_count} tasks)")

        # Penalty for critical path (20 points)
        if is_on_critical_path:
            score -= 20
            risk_drivers.append("Task is on critical path")
            recommendations.append("Add contingency buffer for critical path tasks")

        return max(0, score)

    def _calculate_calibration_score(
        self,
        org_sample_size: int,
        benchmark: Optional[BlendedBenchmark],
        risk_drivers: List[str],
        recommendations: List[str]
    ) -> float:
        """
        Calculate score based on calibration quality (0-100)

        Higher score = more org-specific data available
        Lower score = relying on industry-only benchmarks
        """
        if not benchmark:
            risk_drivers.append("No calibration data available")
            recommendations.append("Upload historical timelines to improve accuracy")
            return 30.0  # Low confidence without calibration

        # Check blend ratio
        org_ratio = benchmark.blend_ratio.get('org', 0.0)

        if org_ratio == 0.0:
            # Industry-only benchmark
            score = 60.0
            risk_drivers.append("Using industry-only benchmarks")
            recommendations.append("Upload historical data to calibrate for your organization")
        elif org_sample_size < 3:
            # Insufficient org data
            score = 70.0
            risk_drivers.append(f"Limited org data ({org_sample_size} samples)")
            recommendations.append("Add more historical timelines to improve calibration")
        elif org_sample_size < 5:
            # Low org sample size
            score = 80.0
        elif org_sample_size < 10:
            # Medium org sample size
            score = 90.0
        else:
            # High org sample size
            score = 100.0

        return score

    def _calculate_complexity_score(
        self,
        task_category: str,
        has_regulatory_component: bool,
        risk_drivers: List[str],
        recommendations: List[str]
    ) -> float:
        """
        Calculate score based on task complexity/predictability (0-100)

        Higher score = more predictable task type
        Lower score = less predictable (regulatory, patient-dependent, etc.)
        """
        # Base scores by category (inherent predictability)
        category_scores = {
            'Regulatory': 50,           # Moderate - authority-dependent
            'Site Management': 60,      # Moderate - site-dependent
            'Clinical Operations': 40,  # Low - patient-dependent
            'Data Management': 80,      # High - process-driven
            'Closeout': 70,            # High - checklist-driven
            'Startup': 65,             # Moderate - admin-heavy
            'Protocol Development': 75, # High - internal process
            'Budget & Finance': 85,    # High - administrative
            'Safety Monitoring': 55,   # Moderate - event-driven
            'Quality Assurance': 75    # High - audit-driven
        }

        score = category_scores.get(task_category, 60)  # Default to moderate

        # Penalty for regulatory component
        if has_regulatory_component:
            score -= 15
            risk_drivers.append("Regulatory review timelines are authority-dependent")
            recommendations.append("Consider authority-specific benchmarks for better accuracy")

        # Category-specific notes
        if task_category == 'Clinical Operations':
            risk_drivers.append("Patient enrollment is highly variable")
            recommendations.append("Use rolling forecasts and track enrollment velocity")
        elif task_category == 'Regulatory':
            risk_drivers.append("Regulatory timelines vary by authority")

        return max(0, score)

    def calculate_batch_confidence(
        self,
        tasks: List[Dict],
        benchmarks: Dict[str, BlendedBenchmark],
        task_dependencies: Dict[str, List[str]],
        critical_path_tasks: List[str]
    ) -> List[ConfidenceScore]:
        """
        Calculate confidence scores for multiple tasks in batch

        Args:
            tasks: List of task dicts with id, name, category, duration
            benchmarks: Dict mapping task_id -> BlendedBenchmark
            task_dependencies: Dict mapping task_id -> list of dependent task_ids
            critical_path_tasks: List of task_ids on critical path

        Returns:
            List of ConfidenceScore objects
        """
        confidence_scores = []

        for task in tasks:
            task_id = task['task_id']
            benchmark = benchmarks.get(task_id)
            dependency_count = len(task_dependencies.get(task_id, []))
            is_critical = task_id in critical_path_tasks

            # Determine if regulatory
            has_regulatory = task.get('category') == 'Regulatory' or \
                           'regulatory' in task.get('name', '').lower() or \
                           'approval' in task.get('name', '').lower()

            confidence = self.calculate_confidence(
                task_id=task_id,
                task_name=task.get('name', 'Unknown Task'),
                task_category=task.get('category', 'Unknown'),
                customer_duration_days=task.get('duration_days', 0),
                benchmark=benchmark,
                org_sample_size=benchmark.org_sample_size if benchmark else 0,
                dependency_count=dependency_count,
                is_on_critical_path=is_critical,
                has_regulatory_component=has_regulatory
            )

            confidence_scores.append(confidence)

        return confidence_scores

    def get_overall_timeline_confidence(
        self,
        task_confidence_scores: List[ConfidenceScore]
    ) -> Dict:
        """
        Calculate overall timeline confidence from individual task scores

        Returns:
            Dict with overall_score, risk_level, and aggregated risk_drivers
        """
        if not task_confidence_scores:
            return {
                'overall_score': 0.0,
                'risk_level': 'unknown',
                'total_tasks': 0,
                'high_confidence_tasks': 0,
                'medium_confidence_tasks': 0,
                'low_confidence_tasks': 0,
                'aggregated_risk_drivers': []
            }

        # Calculate weighted average (critical path tasks weighted higher)
        total_score = sum(score.overall_score for score in task_confidence_scores)
        overall_score = total_score / len(task_confidence_scores)

        # Classify tasks by confidence level
        high_confidence = len([s for s in task_confidence_scores if s.overall_score >= 70])
        medium_confidence = len([s for s in task_confidence_scores if 40 <= s.overall_score < 70])
        low_confidence = len([s for s in task_confidence_scores if s.overall_score < 40])

        # Determine risk level
        if overall_score >= 70:
            risk_level = 'low'
        elif overall_score >= 50:
            risk_level = 'medium'
        else:
            risk_level = 'high'

        # Aggregate most common risk drivers
        all_risk_drivers = []
        for score in task_confidence_scores:
            all_risk_drivers.extend(score.risk_drivers)

        # Count frequency and get top 5
        from collections import Counter
        risk_counter = Counter(all_risk_drivers)
        top_risk_drivers = [driver for driver, count in risk_counter.most_common(5)]

        return {
            'overall_score': round(overall_score, 1),
            'risk_level': risk_level,
            'total_tasks': len(task_confidence_scores),
            'high_confidence_tasks': high_confidence,
            'medium_confidence_tasks': medium_confidence,
            'low_confidence_tasks': low_confidence,
            'aggregated_risk_drivers': top_risk_drivers
        }
