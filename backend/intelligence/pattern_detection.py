"""
Pattern Detection for Single-Study Anomalies

Detects unusual patterns, trends, and anomalies within a single study:
- Clustering of similar signals (multiple site risks, multiple TMF issues)
- Escalating signal severity over time
- Signals affecting critical path milestones
- Repeated issues in same category
- Signals without mitigation plans
- Overdue signals without action

This is single-study analysis. Cross-study (portfolio) pattern detection
is implemented in Phase 4.
"""

import sqlite3
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """Detected pattern or anomaly"""
    pattern_id: str
    pattern_type: str
    pattern_name: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    affected_signals: List[str]  # signal_ids
    affected_milestones: List[str]  # milestone names
    recommended_action: str
    detected_at: datetime


class PatternDetector:
    """Detect patterns and anomalies in study signals"""

    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row

    def detect_patterns(
        self,
        project_id: str,
        signals: List[Dict],
        correlations: List[Dict],
        timeline: Dict
    ) -> List[Pattern]:
        """
        Detect patterns across all signals for a project

        Args:
            project_id: Project identifier
            signals: List of signals for this project
            correlations: List of correlations for this project
            timeline: Project timeline data

        Returns:
            List of detected Pattern objects
        """
        patterns = []

        # Pattern 1: Signal Clustering by Category
        patterns.extend(self._detect_signal_clustering(signals))

        # Pattern 2: Escalating Severity Over Time
        patterns.extend(self._detect_escalating_severity(signals))

        # Pattern 3: Critical Path Impact
        patterns.extend(self._detect_critical_path_impact(correlations, timeline))

        # Pattern 4: Repeated Issues in Same Area
        patterns.extend(self._detect_repeated_issues(signals))

        # Pattern 5: High Priority Without Mitigation
        patterns.extend(self._detect_no_mitigation(signals))

        # Pattern 6: Overdue Signals Without Action
        patterns.extend(self._detect_overdue_signals(signals))

        # Pattern 7: Multiple Blockers
        patterns.extend(self._detect_multiple_blockers(correlations))

        logger.info(f"Detected {len(patterns)} patterns for project {project_id}")

        return patterns

    def _detect_signal_clustering(self, signals: List[Dict]) -> List[Pattern]:
        """Detect clustering of similar signals (e.g., multiple site risks)"""
        patterns = []

        # Group signals by category
        category_groups = defaultdict(list)
        for signal in signals:
            if signal.get('status') == 'open':  # Only open signals
                category = signal.get('signal_category', 'Uncategorized')
                category_groups[category].append(signal)

        # Detect clusters (≥3 signals in same category)
        for category, category_signals in category_groups.items():
            if len(category_signals) >= 3:
                signal_ids = [s['signal_id'] for s in category_signals]
                avg_priority = sum(s.get('priority', 5) for s in category_signals) / len(category_signals)

                severity = "high" if avg_priority >= 7 else "medium"

                patterns.append(Pattern(
                    pattern_id=f"cluster_{category}_{len(category_signals)}",
                    pattern_type="signal_clustering",
                    pattern_name=f"Multiple {category} Signals",
                    description=f"Detected {len(category_signals)} open {category} signals. This clustering suggests a systemic issue in {category}.",
                    severity=severity,
                    affected_signals=signal_ids,
                    affected_milestones=[],
                    recommended_action=f"Review {category} processes. Consider root cause analysis if issues persist.",
                    detected_at=datetime.now()
                ))

        return patterns

    def _detect_escalating_severity(self, signals: List[Dict]) -> List[Pattern]:
        """Detect if signal severity is increasing over time"""
        patterns = []

        # Sort signals by date
        dated_signals = [s for s in signals if s.get('date_identified')]
        if len(dated_signals) < 3:
            return patterns

        dated_signals.sort(key=lambda x: x['date_identified'])

        # Look at last 3 signals vs previous signals
        recent_signals = dated_signals[-3:]
        older_signals = dated_signals[:-3]

        if not older_signals:
            return patterns

        recent_avg_priority = sum(s.get('priority', 5) for s in recent_signals) / len(recent_signals)
        older_avg_priority = sum(s.get('priority', 5) for s in older_signals) / len(older_signals)

        # Escalating if recent average is 2+ points higher
        if recent_avg_priority - older_avg_priority >= 2:
            patterns.append(Pattern(
                pattern_id="escalating_severity",
                pattern_type="escalating_severity",
                pattern_name="Escalating Signal Severity",
                description=f"Recent signals have higher average priority ({recent_avg_priority:.1f}) compared to earlier signals ({older_avg_priority:.1f}). Issues are worsening.",
                severity="high",
                affected_signals=[s['signal_id'] for s in recent_signals],
                affected_milestones=[],
                recommended_action="Immediate leadership review recommended. Escalate to VP if trend continues.",
                detected_at=datetime.now()
            ))

        return patterns

    def _detect_critical_path_impact(
        self,
        correlations: List[Dict],
        timeline: Dict
    ) -> List[Pattern]:
        """Detect signals affecting critical path milestones"""
        patterns = []

        # Get critical path milestones from timeline
        critical_milestones = [
            m for m in timeline.get('milestones', [])
            if m.get('is_critical_path', False)
        ]

        if not critical_milestones:
            return patterns

        critical_milestone_names = {m['milestone_name'] for m in critical_milestones}

        # Find correlations affecting critical path
        critical_correlations = [
            c for c in correlations
            if c.get('affected_milestone_name') in critical_milestone_names
        ]

        if len(critical_correlations) >= 2:
            total_delay = sum(c.get('estimated_delay_days', 0) for c in critical_correlations)
            affected_milestones = list(set(c['affected_milestone_name'] for c in critical_correlations))

            patterns.append(Pattern(
                pattern_id="critical_path_impact",
                pattern_type="critical_path_impact",
                pattern_name="Critical Path at Risk",
                description=f"{len(critical_correlations)} signals affecting critical path milestones: {', '.join(affected_milestones)}. Total estimated delay: {total_delay} days.",
                severity="critical",
                affected_signals=[c['signal_id'] for c in critical_correlations],
                affected_milestones=affected_milestones,
                recommended_action="Immediate intervention required. Re-baseline timeline if delay exceeds 30 days.",
                detected_at=datetime.now()
            ))

        return patterns

    def _detect_repeated_issues(self, signals: List[Dict]) -> List[Pattern]:
        """Detect repeated issues with same signal type"""
        patterns = []

        # Count signal types
        signal_type_counts = Counter(s['signal_type'] for s in signals if s.get('status') == 'open')

        # Repeated if same type appears ≥3 times
        for signal_type, count in signal_type_counts.items():
            if count >= 3:
                matching_signals = [s for s in signals if s['signal_type'] == signal_type and s.get('status') == 'open']
                signal_ids = [s['signal_id'] for s in matching_signals]

                patterns.append(Pattern(
                    pattern_id=f"repeated_{signal_type}",
                    pattern_type="repeated_issues",
                    pattern_name=f"Repeated {signal_type} Issues",
                    description=f"Signal type '{signal_type}' has occurred {count} times. Suggests recurring process failure.",
                    severity="medium",
                    affected_signals=signal_ids,
                    affected_milestones=[],
                    recommended_action=f"Investigate root cause of {signal_type}. Implement preventive controls.",
                    detected_at=datetime.now()
                ))

        return patterns

    def _detect_no_mitigation(self, signals: List[Dict]) -> List[Pattern]:
        """Detect high priority signals without mitigation plans"""
        patterns = []

        # High priority signals (≥6) without mitigation
        no_mitigation_signals = []
        for signal in signals:
            if signal.get('status') == 'open' and signal.get('priority', 0) >= 6:
                signal_detail = json.loads(signal.get('signal_detail', '{}'))
                mitigation = signal_detail.get('mitigation_plan', '')

                if not mitigation or mitigation.strip() == '':
                    no_mitigation_signals.append(signal)

        if len(no_mitigation_signals) >= 2:
            signal_ids = [s['signal_id'] for s in no_mitigation_signals]

            patterns.append(Pattern(
                pattern_id="no_mitigation_plans",
                pattern_type="missing_mitigation",
                pattern_name="High Priority Signals Without Mitigation",
                description=f"{len(no_mitigation_signals)} high priority signals (≥6) lack mitigation plans. Risk management inadequate.",
                severity="high",
                affected_signals=signal_ids,
                affected_milestones=[],
                recommended_action="Require mitigation plans for all Priority ≥6 signals within 48 hours.",
                detected_at=datetime.now()
            ))

        return patterns

    def _detect_overdue_signals(self, signals: List[Dict]) -> List[Pattern]:
        """Detect signals past target date without resolution"""
        patterns = []

        today = date.today()
        overdue_signals = []

        for signal in signals:
            if signal.get('status') != 'resolved' and signal.get('target_date'):
                try:
                    # Parse target_date (could be string or date object)
                    target_date_str = signal['target_date']
                    if isinstance(target_date_str, str):
                        target_date = datetime.fromisoformat(target_date_str).date()
                    else:
                        target_date = target_date_str

                    days_overdue = (today - target_date).days

                    if days_overdue > 0:
                        overdue_signals.append({
                            'signal': signal,
                            'days_overdue': days_overdue
                        })
                except:
                    continue

        if len(overdue_signals) >= 2:
            signal_ids = [item['signal']['signal_id'] for item in overdue_signals]
            total_days_overdue = sum(item['days_overdue'] for item in overdue_signals)
            avg_days_overdue = total_days_overdue / len(overdue_signals)

            severity = "critical" if avg_days_overdue > 30 else "high"

            patterns.append(Pattern(
                pattern_id="overdue_signals",
                pattern_type="overdue",
                pattern_name="Overdue Signals Without Action",
                description=f"{len(overdue_signals)} signals past target date. Average {avg_days_overdue:.0f} days overdue.",
                severity=severity,
                affected_signals=signal_ids,
                affected_milestones=[],
                recommended_action="Escalate overdue items. Review resource allocation and accountability.",
                detected_at=datetime.now()
            ))

        return patterns

    def _detect_multiple_blockers(self, correlations: List[Dict]) -> List[Pattern]:
        """Detect multiple blocker-type correlations"""
        patterns = []

        # Find blocker correlations
        blockers = [c for c in correlations if c.get('correlation_type') == 'blocker']

        if len(blockers) >= 2:
            affected_milestones = list(set(c['affected_milestone_name'] for c in blockers))
            signal_ids = [c['signal_id'] for c in blockers]

            patterns.append(Pattern(
                pattern_id="multiple_blockers",
                pattern_type="multiple_blockers",
                pattern_name="Multiple Timeline Blockers",
                description=f"{len(blockers)} hard blockers detected affecting: {', '.join(affected_milestones)}. Timeline cannot proceed.",
                severity="critical",
                affected_signals=signal_ids,
                affected_milestones=affected_milestones,
                recommended_action="URGENT: Resolve blockers immediately. Timeline is stalled. VP escalation required.",
                detected_at=datetime.now()
            ))

        return patterns


def get_patterns_for_project(
    conn: sqlite3.Connection,
    project_id: str
) -> List[Pattern]:
    """
    Convenience function to get all patterns for a project

    Fetches signals and correlations from database, then runs pattern detection
    """
    cursor = conn.cursor()

    # Get signals
    cursor.execute("""
        SELECT signal_id, signal_type, signal_category, signal_description,
               signal_detail, priority, status, date_identified, target_date
        FROM signals
        WHERE project_id = ?
    """, (project_id,))

    signals = [dict(row) for row in cursor.fetchall()]

    # Get correlations
    cursor.execute("""
        SELECT correlation_id, signal_id, affected_milestone_name,
               correlation_type, estimated_delay_days
        FROM signal_timeline_correlations
        WHERE project_id = ?
    """, (project_id,))

    correlations = [dict(row) for row in cursor.fetchall()]

    # Get timeline (simplified - would come from actual project timeline in production)
    timeline = {
        "milestones": []  # Would be populated from actual timeline
    }

    # Run pattern detection
    detector = PatternDetector(conn)
    patterns = detector.detect_patterns(project_id, signals, correlations, timeline)

    return patterns
