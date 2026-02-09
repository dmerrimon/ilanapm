"""
Portfolio Forecasting Engine
Projects future milestones, resource needs, and capacity requirements
for an organization's portfolio
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


class PortfolioForecaster:
    """
    Forecasts portfolio-level metrics and milestones based on
    current portfolio state and historical performance
    """

    def __init__(self):
        # Default forecast horizon in days
        self.default_horizon = 90

        # Milestone categories and typical durations (days)
        self.milestone_durations = {
            'regulatory_submission': 45,
            'ethics_approval': 60,
            'site_initiation': 90,
            'first_patient_enrolled': 120,
            'last_patient_enrolled': 365,
            'database_lock': 45,
            'final_report': 90
        }

    def forecast_portfolio(
        self,
        org_id: str,
        studies: List[Dict[str, Any]],
        org_benchmarks: List[Dict[str, Any]],
        historical_performance: Optional[Dict[str, Any]] = None,
        horizon_days: int = 90
    ) -> Dict[str, Any]:
        """
        Generate portfolio forecast for specified time horizon

        Args:
            org_id: Organization identifier
            studies: List of active studies
            org_benchmarks: Organization-specific benchmarks
            historical_performance: Historical milestone achievement data
            horizon_days: Forecast horizon in days (default 90)

        Returns:
            Forecast with predicted milestones, resource needs, and risks
        """
        if not studies:
            return self._empty_forecast(org_id, horizon_days)

        forecast_end = datetime.utcnow() + timedelta(days=horizon_days)

        # Project upcoming milestones
        milestones = self._project_milestones(
            studies,
            org_benchmarks,
            historical_performance,
            horizon_days
        )

        # Forecast resource needs
        resource_forecast = self._forecast_resource_needs(
            studies,
            milestones,
            horizon_days
        )

        # Project capacity requirements
        capacity_forecast = self._forecast_capacity(studies, milestones)

        # Identify predicted risks
        risk_forecast = self._forecast_risks(studies, milestones, historical_performance)

        # Calculate confidence in forecast
        confidence = self._calculate_forecast_confidence(
            org_benchmarks,
            historical_performance,
            len(studies)
        )

        return {
            'org_id': org_id,
            'forecast_start': datetime.utcnow().isoformat(),
            'forecast_end': forecast_end.isoformat(),
            'horizon_days': horizon_days,
            'milestones': milestones,
            'resource_forecast': resource_forecast,
            'capacity_forecast': capacity_forecast,
            'risk_forecast': risk_forecast,
            'confidence': confidence,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _project_milestones(
        self,
        studies: List[Dict[str, Any]],
        org_benchmarks: List[Dict[str, Any]],
        historical_performance: Optional[Dict[str, Any]],
        horizon_days: int
    ) -> List[Dict[str, Any]]:
        """
        Project upcoming milestones across portfolio

        Uses org benchmarks if available, otherwise industry benchmarks
        """
        milestones = []
        forecast_end = datetime.utcnow() + timedelta(days=horizon_days)

        for study in studies:
            if study.get('status') != 'active':
                continue

            study_start = datetime.fromisoformat(
                study.get('start_date', datetime.utcnow().isoformat()).replace('Z', '+00:00')
            )

            # Project standard clinical trial milestones
            for milestone_type, base_duration in self.milestone_durations.items():
                # Adjust duration based on org benchmarks
                adjusted_duration = self._adjust_milestone_duration(
                    milestone_type,
                    base_duration,
                    org_benchmarks,
                    historical_performance
                )

                projected_date = study_start + timedelta(days=adjusted_duration)

                # Only include milestones within forecast horizon
                if projected_date <= forecast_end:
                    # Calculate probability of on-time completion
                    probability = self._calculate_milestone_probability(
                        milestone_type,
                        historical_performance
                    )

                    milestones.append({
                        'study_id': study.get('study_id'),
                        'study_name': study.get('study_name', 'Unknown'),
                        'milestone_type': milestone_type,
                        'projected_date': projected_date.isoformat(),
                        'days_from_now': (projected_date - datetime.utcnow()).days,
                        'probability_on_time': probability,
                        'confidence': 'high' if probability > 0.75 else 'medium' if probability > 0.5 else 'low'
                    })

        # Sort by projected date
        milestones.sort(key=lambda m: m['projected_date'])

        return milestones

    def _adjust_milestone_duration(
        self,
        milestone_type: str,
        base_duration: int,
        org_benchmarks: List[Dict[str, Any]],
        historical_performance: Optional[Dict[str, Any]]
    ) -> int:
        """
        Adjust milestone duration based on org-specific performance

        Uses org benchmarks and historical variance to adjust projections
        """
        # Map milestone types to task categories
        milestone_to_category = {
            'regulatory_submission': 'Regulatory',
            'ethics_approval': 'Regulatory',
            'site_initiation': 'Site Management',
            'first_patient_enrolled': 'Clinical Operations',
            'last_patient_enrolled': 'Clinical Operations',
            'database_lock': 'Data Management',
            'final_report': 'Closeout'
        }

        category = milestone_to_category.get(milestone_type, 'Unknown')

        # Find matching org benchmark
        org_duration = None
        for benchmark in org_benchmarks:
            if benchmark.get('category') == category:
                org_duration = benchmark.get('median_days')
                break

        if org_duration:
            # Use org benchmark
            return int(org_duration)

        # Apply historical variance adjustment if available
        if historical_performance and milestone_type in historical_performance:
            variance_factor = historical_performance[milestone_type].get('avg_variance_factor', 1.0)
            return int(base_duration * variance_factor)

        return base_duration

    def _calculate_milestone_probability(
        self,
        milestone_type: str,
        historical_performance: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate probability of milestone being achieved on time

        Based on historical on-time completion rates
        """
        if not historical_performance or milestone_type not in historical_performance:
            return 0.70  # Default 70% probability

        perf = historical_performance[milestone_type]
        return perf.get('on_time_rate', 0.70)

    def _forecast_resource_needs(
        self,
        studies: List[Dict[str, Any]],
        milestones: List[Dict[str, Any]],
        horizon_days: int
    ) -> Dict[str, Any]:
        """
        Forecast resource needs over forecast horizon

        Projects site activations, personnel needs, vendor requirements
        """
        # Count milestones by type in forecast period
        milestone_counts = defaultdict(int)
        for milestone in milestones:
            milestone_counts[milestone['milestone_type']] += 1

        # Calculate resource needs based on milestone types
        site_activations = milestone_counts.get('site_initiation', 0)
        enrollment_starts = milestone_counts.get('first_patient_enrolled', 0)
        data_locks = milestone_counts.get('database_lock', 0)

        # Estimate resource requirements
        return {
            'site_activations_needed': site_activations,
            'estimated_sites_required': site_activations * 3,  # Average 3 sites per study
            'enrollment_starts': enrollment_starts,
            'estimated_patients_needed': enrollment_starts * 50,  # Average 50 patients per study
            'data_management_events': data_locks,
            'peak_activity_period': self._identify_peak_period(milestones, horizon_days),
            'resource_pressure_points': self._identify_resource_pressure_points(milestones)
        }

    def _identify_peak_period(
        self,
        milestones: List[Dict[str, Any]],
        horizon_days: int
    ) -> Dict[str, Any]:
        """
        Identify periods of peak activity

        Periods with highest concentration of milestones
        """
        if not milestones:
            return {'period': 'No peak identified', 'milestone_count': 0}

        # Divide horizon into weeks
        weeks = defaultdict(int)
        for milestone in milestones:
            days_from_now = milestone.get('days_from_now', 0)
            week = days_from_now // 7
            weeks[week] += 1

        # Find week with most milestones
        peak_week = max(weeks.items(), key=lambda x: x[1]) if weeks else (0, 0)

        start_date = datetime.utcnow() + timedelta(days=peak_week[0] * 7)
        end_date = start_date + timedelta(days=7)

        return {
            'period': f"Week {peak_week[0] + 1}",
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'milestone_count': peak_week[1]
        }

    def _identify_resource_pressure_points(
        self,
        milestones: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify specific dates with high resource demands

        Dates with 3+ concurrent milestones
        """
        # Group milestones by date
        date_counts = defaultdict(list)
        for milestone in milestones:
            date = milestone.get('projected_date', '').split('T')[0]
            date_counts[date].append(milestone)

        # Find dates with multiple milestones
        pressure_points = []
        for date, milestone_list in date_counts.items():
            if len(milestone_list) >= 3:
                pressure_points.append({
                    'date': date,
                    'concurrent_milestones': len(milestone_list),
                    'studies_affected': len(set(m['study_id'] for m in milestone_list)),
                    'severity': 'high' if len(milestone_list) >= 5 else 'medium'
                })

        pressure_points.sort(key=lambda p: p['concurrent_milestones'], reverse=True)
        return pressure_points[:5]  # Return top 5

    def _forecast_capacity(
        self,
        studies: List[Dict[str, Any]],
        milestones: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Forecast capacity requirements over forecast period

        Projects team capacity needs and workload
        """
        active_studies = [s for s in studies if s.get('status') == 'active']

        # Current capacity usage (simplified)
        current_capacity = len(active_studies) * 1.5  # 1.5 FTE per study

        # Project capacity needs based on milestones
        enrollment_milestones = [m for m in milestones if 'enrolled' in m.get('milestone_type', '')]
        peak_capacity = current_capacity + (len(enrollment_milestones) * 0.5)  # Additional capacity during enrollment

        return {
            'current_capacity_fte': round(current_capacity, 1),
            'projected_peak_capacity_fte': round(peak_capacity, 1),
            'capacity_increase_needed': round(peak_capacity - current_capacity, 1),
            'capacity_utilization': round((current_capacity / 20) * 100, 1),  # Assume max 20 FTE
            'recommendation': 'Hire additional staff' if peak_capacity > 18 else 'Current capacity sufficient'
        }

    def _forecast_risks(
        self,
        studies: List[Dict[str, Any]],
        milestones: List[Dict[str, Any]],
        historical_performance: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Forecast potential risks in the portfolio

        Based on milestone concentration, historical performance, study complexity
        """
        risks = []

        # Risk 1: Milestone concentration
        milestone_counts_by_month = defaultdict(int)
        for milestone in milestones:
            month = milestone.get('projected_date', '')[:7]  # YYYY-MM
            milestone_counts_by_month[month] += 1

        for month, count in milestone_counts_by_month.items():
            if count >= 10:
                risks.append({
                    'risk_type': 'milestone_concentration',
                    'severity': 'high' if count >= 15 else 'medium',
                    'description': f"{count} milestones projected for {month}",
                    'impact': 'Resource capacity may be exceeded',
                    'mitigation': 'Consider staggering study timelines or adding capacity'
                })

        # Risk 2: Low probability milestones
        low_prob_milestones = [m for m in milestones if m.get('probability_on_time', 1.0) < 0.5]
        if len(low_prob_milestones) >= 5:
            risks.append({
                'risk_type': 'schedule_risk',
                'severity': 'high',
                'description': f"{len(low_prob_milestones)} milestones with <50% on-time probability",
                'impact': 'Multiple potential delays could cascade',
                'mitigation': 'Add buffer time to critical path milestones'
            })

        # Risk 3: Concurrent Phase III studies (high complexity)
        phase_iii_studies = [s for s in studies if s.get('phase') == 'Phase III']
        if len(phase_iii_studies) >= 3:
            risks.append({
                'risk_type': 'complexity_risk',
                'severity': 'medium',
                'description': f"{len(phase_iii_studies)} concurrent Phase III studies",
                'impact': 'High resource and regulatory demands',
                'mitigation': 'Ensure adequate regulatory and clinical operations capacity'
            })

        return risks

    def _calculate_forecast_confidence(
        self,
        org_benchmarks: List[Dict[str, Any]],
        historical_performance: Optional[Dict[str, Any]],
        study_count: int
    ) -> Dict[str, Any]:
        """
        Calculate confidence in forecast accuracy

        Higher confidence with more data (org benchmarks, historical performance)
        """
        confidence_score = 50.0  # Base confidence

        # Increase confidence with org benchmarks
        if org_benchmarks:
            benchmark_bonus = min(len(org_benchmarks) / 50 * 20, 20)  # Up to +20
            confidence_score += benchmark_bonus

        # Increase confidence with historical performance data
        if historical_performance:
            confidence_score += 15

        # Increase confidence with more studies (more data points)
        study_bonus = min(study_count / 10 * 10, 15)  # Up to +15
        confidence_score += study_bonus

        confidence_score = min(confidence_score, 95)  # Cap at 95%

        return {
            'overall_confidence': round(confidence_score, 1),
            'level': 'high' if confidence_score >= 75 else 'medium' if confidence_score >= 50 else 'low',
            'factors': {
                'org_benchmarks_available': len(org_benchmarks) > 0,
                'historical_data_available': historical_performance is not None,
                'sample_size': study_count
            }
        }

    def _empty_forecast(self, org_id: str, horizon_days: int) -> Dict[str, Any]:
        """Return empty forecast structure"""
        forecast_end = datetime.utcnow() + timedelta(days=horizon_days)

        return {
            'org_id': org_id,
            'forecast_start': datetime.utcnow().isoformat(),
            'forecast_end': forecast_end.isoformat(),
            'horizon_days': horizon_days,
            'milestones': [],
            'resource_forecast': {},
            'capacity_forecast': {},
            'risk_forecast': [],
            'confidence': {'overall_confidence': 0, 'level': 'low'},
            'timestamp': datetime.utcnow().isoformat()
        }
