"""
Study Health Score Calculator

Calculates comprehensive study health score (0-100) based on:
- Timeline variance (actual vs planned)
- Risk exposure (open signals by priority)
- TMF completeness
- Enrollment rate (if applicable)
- Budget variance (if available)
- Vendor performance (if available)

Output:
- Overall health score (0-100)
- Health status (healthy/warning/critical)
- Component scores
- Top risks
- Recommended actions
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class HealthScore:
    """Study health score with component breakdowns"""
    overall_score: float  # 0-100
    health_status: str  # "healthy", "warning", "critical"

    # Component scores
    timeline_score: float
    risk_score: float
    tmf_score: float
    enrollment_score: Optional[float]
    budget_score: Optional[float]
    vendor_score: Optional[float]

    # Supporting data
    top_risks: List[Dict]
    active_escalations_count: int
    director_escalations_count: int
    vp_escalations_count: int
    recommended_actions: List[str]

    # Metadata
    calculated_at: datetime


class HealthScoreCalculator:
    """Calculate study health scores"""

    # Score weights (must sum to 1.0)
    WEIGHTS = {
        'timeline_variance': 0.25,
        'risk_exposure': 0.25,
        'tmf_completeness': 0.20,
        'enrollment_rate': 0.15,
        'budget_variance': 0.10,
        'vendor_performance': 0.05
    }

    # Health status thresholds
    HEALTHY_THRESHOLD = 75  # ≥75 = healthy
    WARNING_THRESHOLD = 50  # 50-74 = warning
    # <50 = critical

    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row

    def calculate_health_score(
        self,
        project_id: str,
        signals: List[Dict],
        correlations: List[Dict],
        timeline_data: Optional[Dict] = None
    ) -> HealthScore:
        """
        Calculate comprehensive study health score

        Args:
            project_id: Project identifier
            signals: List of signals for this project
            correlations: List of correlations
            timeline_data: Optional timeline data with variance info

        Returns:
            HealthScore object
        """
        # Calculate component scores
        timeline_score = self._calculate_timeline_score(timeline_data)
        risk_score = self._calculate_risk_score(signals)
        tmf_score = self._calculate_tmf_score(signals)
        enrollment_score = self._calculate_enrollment_score(signals, timeline_data)
        budget_score = self._calculate_budget_score(signals)
        vendor_score = self._calculate_vendor_score(signals)

        # Calculate weighted overall score
        overall_score = (
            timeline_score * self.WEIGHTS['timeline_variance'] +
            risk_score * self.WEIGHTS['risk_exposure'] +
            tmf_score * self.WEIGHTS['tmf_completeness'] +
            (enrollment_score or 75) * self.WEIGHTS['enrollment_rate'] +  # Default to 75 if N/A
            (budget_score or 85) * self.WEIGHTS['budget_variance'] +      # Default to 85 if N/A
            (vendor_score or 90) * self.WEIGHTS['vendor_performance']      # Default to 90 if N/A
        )

        # Determine health status
        if overall_score >= self.HEALTHY_THRESHOLD:
            health_status = "healthy"
        elif overall_score >= self.WARNING_THRESHOLD:
            health_status = "warning"
        else:
            health_status = "critical"

        # Get top risks
        top_risks = self._get_top_risks(signals, limit=5)

        # Count escalations
        escalation_counts = self._count_escalations(signals)

        # Generate recommended actions
        recommended_actions = self._generate_recommendations(
            overall_score,
            timeline_score,
            risk_score,
            tmf_score,
            signals,
            correlations
        )

        return HealthScore(
            overall_score=round(overall_score, 1),
            health_status=health_status,
            timeline_score=round(timeline_score, 1),
            risk_score=round(risk_score, 1),
            tmf_score=round(tmf_score, 1),
            enrollment_score=round(enrollment_score, 1) if enrollment_score else None,
            budget_score=round(budget_score, 1) if budget_score else None,
            vendor_score=round(vendor_score, 1) if vendor_score else None,
            top_risks=top_risks,
            active_escalations_count=escalation_counts['active'],
            director_escalations_count=escalation_counts['director'],
            vp_escalations_count=escalation_counts['vp'],
            recommended_actions=recommended_actions,
            calculated_at=datetime.now()
        )

    def _calculate_timeline_score(self, timeline_data: Optional[Dict]) -> float:
        """
        Calculate timeline health score (0-100)

        Based on:
        - Overall percent complete vs expected
        - Critical path variance
        - Milestone delays

        Higher score = better (on track or ahead)
        """
        if not timeline_data:
            return 75.0  # Default if no timeline data

        # Get variance metrics
        schedule_variance_pct = timeline_data.get('schedule_variance_pct', 0)
        critical_path_delay_days = timeline_data.get('critical_path_delay_days', 0)
        overdue_milestones = timeline_data.get('overdue_milestones_count', 0)

        # Start with perfect score
        score = 100.0

        # Deduct for schedule variance (±20% = ±20 points)
        score -= abs(schedule_variance_pct)

        # Deduct for critical path delays (10 days = -10 points)
        score -= critical_path_delay_days

        # Deduct for overdue milestones (each = -10 points)
        score -= (overdue_milestones * 10)

        # Clamp to 0-100
        return max(0, min(100, score))

    def _calculate_risk_score(self, signals: List[Dict]) -> float:
        """
        Calculate risk exposure score (0-100)

        Based on:
        - Number of open high priority risks
        - Average risk priority
        - Risks without mitigation

        Higher score = lower risk (better)
        """
        risk_signals = [s for s in signals if s['signal_type'].startswith('risk_') and s.get('status') == 'open']

        if not risk_signals:
            return 100.0  # No risks = perfect score

        # Start with base score
        score = 100.0

        # Count high priority risks (≥6)
        high_priority_count = sum(1 for s in risk_signals if s.get('priority', 0) >= 6)

        # Count critical risks (=9)
        critical_count = sum(1 for s in risk_signals if s.get('priority', 0) == 9)

        # Count risks without mitigation
        no_mitigation_count = 0
        for signal in risk_signals:
            signal_detail = json.loads(signal.get('signal_detail', '{}'))
            if not signal_detail.get('mitigation_plan'):
                no_mitigation_count += 1

        # Deductions
        score -= (high_priority_count * 5)  # Each high priority risk = -5 points
        score -= (critical_count * 15)  # Each critical risk = -15 points
        score -= (no_mitigation_count * 8)  # Each unmitigated = -8 points

        # Clamp to 0-100
        return max(0, min(100, score))

    def _calculate_tmf_score(self, signals: List[Dict]) -> float:
        """
        Calculate TMF completeness score (0-100)

        Based on:
        - TMF missing document signals
        - TMF overdue signals
        - TMF completeness percentage (if available)

        Higher score = more complete (better)
        """
        tmf_signals = [s for s in signals if s['signal_type'].startswith('tmf_') and s.get('status') == 'open']

        if not tmf_signals:
            return 90.0  # No TMF issues = good (not perfect, as we lack data)

        # Check for completeness percentage in signal details
        for signal in tmf_signals:
            if signal['signal_type'] == 'tmf_completeness_risk':
                signal_detail = json.loads(signal.get('signal_detail', '{}'))
                completeness_pct = signal_detail.get('completeness_pct')
                if completeness_pct is not None:
                    return float(completeness_pct)

        # Otherwise, deduce from signals
        score = 100.0

        missing_docs = sum(1 for s in tmf_signals if s['signal_type'] == 'tmf_missing_document')
        overdue = sum(1 for s in tmf_signals if s['signal_type'] == 'tmf_overdue')

        score -= (missing_docs * 3)  # Each missing doc = -3 points
        score -= (overdue * 5)  # Each overdue = -5 points

        return max(0, min(100, score))

    def _calculate_enrollment_score(
        self,
        signals: List[Dict],
        timeline_data: Optional[Dict]
    ) -> Optional[float]:
        """
        Calculate enrollment rate score (0-100)

        Based on:
        - Enrollment vs target
        - Screen failure rate
        - Dropout rate

        Higher score = on track (better)

        Returns None if enrollment not applicable (e.g., startup phase)
        """
        # Check if enrollment data available
        enrollment_signals = [s for s in signals if 'enrollment' in s.get('signal_description', '').lower()]

        if not enrollment_signals and not (timeline_data and timeline_data.get('enrollment_data')):
            return None  # Enrollment not applicable

        # If we have timeline enrollment data, use it
        if timeline_data and timeline_data.get('enrollment_data'):
            enrollment_data = timeline_data['enrollment_data']
            actual = enrollment_data.get('actual_enrolled', 0)
            target = enrollment_data.get('target_enrolled', 1)
            pct = (actual / target) * 100
            return min(100, pct)

        # Otherwise, deduce from signals
        score = 75.0  # Default baseline

        # Deduct for enrollment-related risks
        for signal in enrollment_signals:
            if signal.get('status') == 'open' and signal.get('priority', 0) >= 6:
                score -= 15

        return max(0, min(100, score))

    def _calculate_budget_score(self, signals: List[Dict]) -> Optional[float]:
        """
        Calculate budget health score (0-100)

        Based on:
        - Budget variance
        - Overrun signals

        Higher score = on budget (better)

        Returns None if budget data not available
        """
        budget_signals = [s for s in signals if s['signal_type'] == 'budget_overrun']

        if not budget_signals:
            return None  # No budget data

        # Get variance from most recent signal
        latest_signal = max(budget_signals, key=lambda s: s.get('date_identified', date.min))
        signal_detail = json.loads(latest_signal.get('signal_detail', '{}'))
        variance_pct = signal_detail.get('variance_pct', 0)

        # Score = 100 - variance_pct
        # (e.g., 10% over budget = 90 score)
        score = 100 - abs(variance_pct)

        return max(0, min(100, score))

    def _calculate_vendor_score(self, signals: List[Dict]) -> Optional[float]:
        """
        Calculate vendor performance score (0-100)

        Based on:
        - Vendor-related issues
        - Delivery delays

        Higher score = vendors performing well (better)

        Returns None if vendor data not available
        """
        vendor_signals = [s for s in signals if 'vendor' in s.get('signal_description', '').lower()]

        if not vendor_signals:
            return None  # No vendor data

        # Start with baseline
        score = 100.0

        # Deduct for each vendor issue
        for signal in vendor_signals:
            if signal.get('status') == 'open':
                priority = signal.get('priority', 5)
                score -= (priority * 2)

        return max(0, min(100, score))

    def _get_top_risks(self, signals: List[Dict], limit: int = 5) -> List[Dict]:
        """Get top N risks by priority"""
        risk_signals = [s for s in signals if s['signal_type'].startswith('risk_') and s.get('status') == 'open']

        # Sort by priority (descending)
        sorted_risks = sorted(risk_signals, key=lambda s: s.get('priority', 0), reverse=True)

        return sorted_risks[:limit]

    def _count_escalations(self, signals: List[Dict]) -> Dict[str, int]:
        """Count escalations by level"""
        active = 0
        director = 0
        vp = 0

        for signal in signals:
            if signal.get('status') != 'resolved':
                escalation_level = signal.get('escalation_level')
                if escalation_level:
                    active += 1
                    if escalation_level == 'director':
                        director += 1
                    elif escalation_level == 'vp':
                        vp += 1

        return {
            'active': active,
            'director': director,
            'vp': vp
        }

    def _generate_recommendations(
        self,
        overall_score: float,
        timeline_score: float,
        risk_score: float,
        tmf_score: float,
        signals: List[Dict],
        correlations: List[Dict]
    ) -> List[str]:
        """Generate recommended actions based on scores"""
        recommendations = []

        # Overall health
        if overall_score < 50:
            recommendations.append("URGENT: Overall study health is critical. Immediate leadership intervention required.")

        # Timeline
        if timeline_score < 60:
            recommendations.append("Timeline variance exceeds acceptable threshold. Review critical path and resource allocation.")

        # Risk
        if risk_score < 60:
            risk_count = sum(1 for s in signals if s['signal_type'].startswith('risk_') and s.get('status') == 'open')
            recommendations.append(f"High risk exposure with {risk_count} open risks. Prioritize risk mitigation efforts.")

        # TMF
        if tmf_score < 75:
            recommendations.append("TMF completeness below target. Allocate additional regulatory resources.")

        # Blockers
        blocker_count = sum(1 for c in correlations if c.get('correlation_type') == 'blocker')
        if blocker_count > 0:
            recommendations.append(f"{blocker_count} timeline blocker(s) detected. Resolve immediately to prevent delays.")

        # Critical path
        critical_correlations = [c for c in correlations if c.get('estimated_delay_days', 0) > 30]
        if critical_correlations:
            recommendations.append("Multiple signals indicate potential delays >30 days. Consider timeline re-baseline.")

        # Default if all good
        if not recommendations:
            recommendations.append("Study health is good. Continue monitoring key metrics.")

        return recommendations


def store_health_snapshot(
    conn: sqlite3.Connection,
    project_id: str,
    org_id: str,
    health_score: HealthScore
):
    """Store health score snapshot in database"""
    import uuid

    cursor = conn.cursor()

    snapshot_id = str(uuid.uuid4())

    cursor.execute("""
        INSERT INTO study_health_snapshots (
            snapshot_id, org_id, project_id,
            overall_health_score, health_status,
            timeline_score, risk_score, tmf_score,
            enrollment_score, budget_score, vendor_score,
            top_risks, active_escalations_count,
            director_escalations_count, vp_escalations_count,
            recommended_actions, snapshot_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        snapshot_id,
        org_id,
        project_id,
        health_score.overall_score,
        health_score.health_status,
        health_score.timeline_score,
        health_score.risk_score,
        health_score.tmf_score,
        health_score.enrollment_score,
        health_score.budget_score,
        health_score.vendor_score,
        json.dumps(health_score.top_risks),
        health_score.active_escalations_count,
        health_score.director_escalations_count,
        health_score.vp_escalations_count,
        json.dumps(health_score.recommended_actions),
        date.today().isoformat()
    ))

    conn.commit()
    logger.info(f"Stored health snapshot for project {project_id}: {health_score.overall_score} ({health_score.health_status})")
