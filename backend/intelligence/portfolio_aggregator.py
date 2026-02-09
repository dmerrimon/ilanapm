"""
Portfolio Aggregation Engine
Aggregates intelligence data across multiple studies for enterprise-tier customers
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class PortfolioAggregationEngine:
    """
    Aggregates data across all studies in a customer's portfolio
    to provide portfolio-level insights and metrics
    """

    def __init__(self):
        self.risk_thresholds = {
            'systemic_high_risk': 0.7,  # 70% of studies have high-risk tasks
            'capacity_warning': 0.8,    # 80% capacity utilization
            'timeline_slippage': 0.6    # 60% of milestones delayed
        }

    def aggregate_portfolio(
        self,
        org_id: str,
        studies: List[Dict[str, Any]],
        variance_reports: List[Dict[str, Any]],
        org_benchmarks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate portfolio-level intelligence metrics

        Args:
            org_id: Organization identifier
            studies: List of study metadata (study_id, name, phase, status, start_date, etc.)
            variance_reports: List of variance reports for each study
            org_benchmarks: Organization-specific benchmarks from calibration

        Returns:
            Portfolio aggregation with health score, patterns, risks, and metrics
        """
        if not studies:
            return self._empty_portfolio(org_id)

        # Calculate portfolio health score
        health_score = self._calculate_portfolio_health(studies, variance_reports)

        # Detect systemic patterns across studies
        patterns = self._detect_systemic_patterns(variance_reports)

        # Calculate portfolio-level risk distribution
        risk_distribution = self._calculate_risk_distribution(variance_reports)

        # Aggregate financial impact across portfolio
        financial_metrics = self._aggregate_financial_impact(variance_reports)

        # Calculate capacity utilization
        capacity = self._calculate_capacity_utilization(studies)

        # Identify common bottlenecks
        bottlenecks = self._identify_common_bottlenecks(variance_reports)

        # Calculate portfolio-level benchmark performance
        benchmark_performance = self._calculate_benchmark_performance(
            variance_reports,
            org_benchmarks
        )

        # Get active study count and distribution
        study_distribution = self._get_study_distribution(studies)

        return {
            'org_id': org_id,
            'portfolio_health_score': health_score,
            'total_studies': len(studies),
            'study_distribution': study_distribution,
            'risk_distribution': risk_distribution,
            'systemic_patterns': patterns,
            'financial_metrics': financial_metrics,
            'capacity_utilization': capacity,
            'common_bottlenecks': bottlenecks,
            'benchmark_performance': benchmark_performance,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _calculate_portfolio_health(
        self,
        studies: List[Dict[str, Any]],
        variance_reports: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate overall portfolio health score (0-100)

        Factors:
        - Study timeline health (30%)
        - Risk exposure (25%)
        - Variance from benchmarks (25%)
        - On-time milestone achievement (20%)
        """
        if not studies or not variance_reports:
            return 50.0  # Neutral score

        # Factor 1: Timeline health (percentage of studies on track)
        active_studies = [s for s in studies if s.get('status') == 'active']
        on_track = sum(1 for s in active_studies if s.get('timeline_status') == 'on_track')
        timeline_health = (on_track / len(active_studies) * 100) if active_studies else 50.0

        # Factor 2: Risk exposure (inverse of high-risk count)
        total_critical = sum(
            r.get('summary', {}).get('critical_count', 0)
            for r in variance_reports
        )
        total_tasks = sum(
            r.get('summary', {}).get('total_tasks_analyzed', 1)
            for r in variance_reports
        )
        critical_rate = (total_critical / total_tasks) if total_tasks > 0 else 0
        risk_score = max(0, 100 - (critical_rate * 200))  # Penalize critical issues heavily

        # Factor 3: Variance performance
        avg_variance = statistics.mean([
            abs(r.get('summary', {}).get('avg_variance_percent', 0))
            for r in variance_reports
        ]) if variance_reports else 0
        variance_score = max(0, 100 - (avg_variance * 2))  # Penalize high variance

        # Factor 4: Milestone achievement (mock - would come from actual milestone data)
        milestone_score = 75.0  # Placeholder

        # Weighted average
        health_score = (
            timeline_health * 0.30 +
            risk_score * 0.25 +
            variance_score * 0.25 +
            milestone_score * 0.20
        )

        return round(health_score, 1)

    def _detect_systemic_patterns(
        self,
        variance_reports: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect patterns that appear across multiple studies

        Returns patterns like:
        - Consistent underestimation of specific task categories
        - Common regulatory delays
        - Enrollment challenges across studies
        """
        patterns = []

        if not variance_reports:
            return patterns

        # Aggregate variance signals by category
        category_variances = defaultdict(list)
        for report in variance_reports:
            for signal in report.get('variance_signals', []):
                category = signal.get('benchmark', {}).get('category', 'Unknown')
                variance_pct = signal.get('variance', {}).get('percentage', 0)
                category_variances[category].append(variance_pct)

        # Identify systemic issues (category appears in 50%+ studies with consistent direction)
        study_count = len(variance_reports)
        threshold = study_count * 0.5

        for category, variances in category_variances.items():
            if len(variances) >= threshold:
                avg_variance = statistics.mean(variances)
                consistency = len([v for v in variances if (v > 0) == (avg_variance > 0)])

                if consistency >= threshold and abs(avg_variance) > 15:
                    patterns.append({
                        'pattern_type': 'systemic_variance',
                        'category': category,
                        'avg_variance_percent': round(avg_variance, 1),
                        'affected_studies': len(variances),
                        'consistency_rate': round(consistency / len(variances) * 100, 1),
                        'severity': 'high' if abs(avg_variance) > 30 else 'medium',
                        'description': f"{category} consistently {'underestimated' if avg_variance < 0 else 'overestimated'} by {abs(avg_variance):.1f}% across {len(variances)} studies"
                    })

        return patterns

    def _calculate_risk_distribution(
        self,
        variance_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate risk distribution across portfolio
        """
        if not variance_reports:
            return {
                'critical_studies': 0,
                'warning_studies': 0,
                'healthy_studies': 0,
                'critical_rate': 0,
                'warning_rate': 0,
                'healthy_rate': 0
            }

        critical = 0
        warning = 0
        healthy = 0

        for report in variance_reports:
            summary = report.get('summary', {})
            critical_count = summary.get('critical_count', 0)
            warning_count = summary.get('warning_count', 0)

            if critical_count > 5:
                critical += 1
            elif warning_count > 10 or critical_count > 0:
                warning += 1
            else:
                healthy += 1

        total = len(variance_reports)

        return {
            'critical_studies': critical,
            'warning_studies': warning,
            'healthy_studies': healthy,
            'critical_rate': round(critical / total * 100, 1),
            'warning_rate': round(warning / total * 100, 1),
            'healthy_rate': round(healthy / total * 100, 1)
        }

    def _aggregate_financial_impact(
        self,
        variance_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate financial impact across all studies
        """
        if not variance_reports:
            return {
                'total_impact_usd': 0,
                'at_risk_usd': 0,
                'potential_savings_usd': 0,
                'avg_impact_per_study': 0
            }

        total_impact = sum(
            report.get('summary', {}).get('total_financial_impact_usd', 0)
            for report in variance_reports
        )

        # Separate positive (savings) and negative (at risk)
        at_risk = sum(
            report.get('summary', {}).get('total_financial_impact_usd', 0)
            for report in variance_reports
            if report.get('summary', {}).get('total_financial_impact_usd', 0) < 0
        )

        potential_savings = sum(
            report.get('summary', {}).get('total_financial_impact_usd', 0)
            for report in variance_reports
            if report.get('summary', {}).get('total_financial_impact_usd', 0) > 0
        )

        avg_impact = total_impact / len(variance_reports) if variance_reports else 0

        return {
            'total_impact_usd': round(total_impact, 2),
            'at_risk_usd': round(abs(at_risk), 2),
            'potential_savings_usd': round(potential_savings, 2),
            'avg_impact_per_study': round(avg_impact, 2)
        }

    def _calculate_capacity_utilization(
        self,
        studies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate resource capacity utilization

        Note: This is a simplified calculation. Real implementation would
        analyze actual resource assignments from study timelines.
        """
        active_studies = [s for s in studies if s.get('status') == 'active']

        # Mock capacity calculation based on study count and phases
        phase_weights = {
            'Phase I': 1.0,
            'Phase II': 1.5,
            'Phase III': 2.5,
            'Phase IV': 1.2
        }

        capacity_used = sum(
            phase_weights.get(s.get('phase', 'Phase I'), 1.0)
            for s in active_studies
        )

        # Assume max capacity is 10 "study units"
        max_capacity = 10.0
        utilization_rate = min((capacity_used / max_capacity) * 100, 100)

        status = 'healthy'
        if utilization_rate >= 90:
            status = 'critical'
        elif utilization_rate >= 75:
            status = 'warning'

        return {
            'capacity_used': round(capacity_used, 1),
            'max_capacity': max_capacity,
            'utilization_rate': round(utilization_rate, 1),
            'status': status,
            'available_capacity': round(max_capacity - capacity_used, 1)
        }

    def _identify_common_bottlenecks(
        self,
        variance_reports: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify task categories that are bottlenecks across multiple studies
        """
        if not variance_reports:
            return []

        # Count high-variance tasks by category
        bottleneck_categories = defaultdict(lambda: {'count': 0, 'avg_variance': 0, 'total_variance': 0})

        for report in variance_reports:
            for signal in report.get('variance_signals', []):
                severity = signal.get('variance', {}).get('severity', '')
                if severity in ['critical', 'warning']:
                    category = signal.get('benchmark', {}).get('category', 'Unknown')
                    variance = abs(signal.get('variance', {}).get('percentage', 0))

                    bottleneck_categories[category]['count'] += 1
                    bottleneck_categories[category]['total_variance'] += variance

        # Calculate average and identify top bottlenecks
        bottlenecks = []
        for category, data in bottleneck_categories.items():
            if data['count'] >= 2:  # Appears in at least 2 studies
                avg_variance = data['total_variance'] / data['count']
                bottlenecks.append({
                    'category': category,
                    'affected_studies': data['count'],
                    'avg_variance_percent': round(avg_variance, 1),
                    'severity': 'high' if avg_variance > 40 else 'medium'
                })

        # Sort by affected studies (most common bottlenecks first)
        bottlenecks.sort(key=lambda x: x['affected_studies'], reverse=True)

        return bottlenecks[:5]  # Return top 5

    def _calculate_benchmark_performance(
        self,
        variance_reports: List[Dict[str, Any]],
        org_benchmarks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate portfolio-level benchmark performance
        """
        if not variance_reports:
            return {
                'avg_coverage': 0,
                'tasks_with_org_benchmarks': 0,
                'tasks_with_industry_benchmarks': 0,
                'blended_benchmark_count': 0
            }

        # Aggregate coverage across all studies
        total_coverage = sum(
            report.get('benchmark_coverage', {}).get('coverage_percent', 0)
            for report in variance_reports
        )
        avg_coverage = total_coverage / len(variance_reports) if variance_reports else 0

        return {
            'avg_coverage': round(avg_coverage, 1),
            'tasks_with_org_benchmarks': len(org_benchmarks),
            'total_variance_analyses': len(variance_reports),
            'benchmark_maturity': 'high' if len(org_benchmarks) > 50 else 'medium' if len(org_benchmarks) > 20 else 'low'
        }

    def _get_study_distribution(
        self,
        studies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get distribution of studies by status and phase
        """
        status_counts = defaultdict(int)
        phase_counts = defaultdict(int)

        for study in studies:
            status = study.get('status', 'unknown')
            phase = study.get('phase', 'unknown')
            status_counts[status] += 1
            phase_counts[phase] += 1

        return {
            'by_status': dict(status_counts),
            'by_phase': dict(phase_counts),
            'active_studies': status_counts.get('active', 0),
            'completed_studies': status_counts.get('completed', 0),
            'planned_studies': status_counts.get('planned', 0)
        }

    def _empty_portfolio(self, org_id: str) -> Dict[str, Any]:
        """Return empty portfolio structure"""
        return {
            'org_id': org_id,
            'portfolio_health_score': 0,
            'total_studies': 0,
            'study_distribution': {},
            'risk_distribution': {},
            'systemic_patterns': [],
            'financial_metrics': {},
            'capacity_utilization': {},
            'common_bottlenecks': [],
            'benchmark_performance': {},
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_portfolio_trends(
        self,
        historical_aggregations: List[Dict[str, Any]],
        time_range_days: int = 90
    ) -> Dict[str, Any]:
        """
        Calculate portfolio trends over time

        Args:
            historical_aggregations: List of previous portfolio aggregations
            time_range_days: Time range to analyze (default 90 days)

        Returns:
            Trend analysis with direction and rate of change
        """
        if len(historical_aggregations) < 2:
            return {'insufficient_data': True}

        # Sort by timestamp
        sorted_agg = sorted(
            historical_aggregations,
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )

        # Get current and previous
        current = sorted_agg[0]
        previous = sorted_agg[1] if len(sorted_agg) > 1 else current

        # Calculate trends
        health_trend = current.get('portfolio_health_score', 0) - previous.get('portfolio_health_score', 0)

        return {
            'health_score_trend': {
                'current': current.get('portfolio_health_score', 0),
                'previous': previous.get('portfolio_health_score', 0),
                'change': round(health_trend, 1),
                'direction': 'improving' if health_trend > 0 else 'declining' if health_trend < 0 else 'stable'
            },
            'study_count_trend': {
                'current': current.get('total_studies', 0),
                'previous': previous.get('total_studies', 0),
                'change': current.get('total_studies', 0) - previous.get('total_studies', 0)
            }
        }
