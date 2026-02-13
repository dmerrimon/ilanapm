"""
Escalation Logic Engine

Determines what signals, correlations, and patterns require escalation and to what level.

Escalation Hierarchy:
- CPM: Daily operational noise (routine updates, minor delays <1 week)
- Director: Weekly attention (variance trends, intervention-worthy risks)
- VP: Monthly strategic view (portfolio health, systemic issues)

Escalation Triggers:
- Director: Priority ≥6 risks, TMF <75%, milestone delay >2 weeks, blockers
- VP: Priority 9 risks, safety risks, critical path delay >4 weeks, systemic patterns
"""

import sqlite3
import json
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# Escalation thresholds
ESCALATION_THRESHOLDS = {
    'director': {
        'risk_priority': 6,  # Priority ≥6 → Director
        'tmf_completeness': 75,  # <75% → Director
        'milestone_delay_weeks': 2,  # >2 weeks → Director
        'correlation_types': ['risk', 'blocker'],
    },
    'vp': {
        'risk_priority': 9,  # Priority 9 → VP
        'critical_path_delay_weeks': 4,  # >4 weeks → VP
        'safety_risk': True,  # Any safety risk → VP
        'systemic_pattern': True,  # Systemic issues → VP
        'correlation_types': ['blocker'],
    }
}


@dataclass
class Escalation:
    """Escalation object"""
    escalation_id: str
    org_id: str
    project_id: str
    trigger_type: str  # "signal", "correlation", "pattern"
    trigger_id: str  # ID of signal/correlation/pattern
    escalation_rule_id: Optional[str]
    escalation_level: str  # "director", "vp"
    escalation_reason: str
    escalation_data: Dict  # Additional context
    assigned_to: Optional[str]
    assigned_role: Optional[str]
    status: str  # "open", "acknowledged", "resolved"
    priority: int  # 1-9
    intervention_recommended: str
    intervention_taken: Optional[str]
    resolution_notes: Optional[str]
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]

    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        return {
            "escalation_id": self.escalation_id,
            "org_id": self.org_id,
            "project_id": self.project_id,
            "trigger_type": self.trigger_type,
            "trigger_id": self.trigger_id,
            "escalation_rule_id": self.escalation_rule_id,
            "escalation_level": self.escalation_level,
            "escalation_reason": self.escalation_reason,
            "escalation_data": json.dumps(self.escalation_data),
            "assigned_to": self.assigned_to,
            "assigned_role": self.assigned_role,
            "status": self.status,
            "priority": self.priority,
            "intervention_recommended": self.intervention_recommended,
            "intervention_taken": self.intervention_taken,
            "resolution_notes": self.resolution_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


class EscalationEngine:
    """Evaluate signals/correlations for escalation"""

    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row

    def evaluate_escalations(
        self,
        org_id: str,
        project_id: str,
        signals: List[Dict],
        correlations: List[Dict],
        patterns: List[Any],
        timeline: Dict
    ) -> List[Escalation]:
        """
        Determine what requires escalation

        Args:
            org_id: Organization ID
            project_id: Project ID
            signals: List of signals
            correlations: List of correlations
            patterns: List of detected patterns
            timeline: Timeline data

        Returns:
            List of Escalation objects
        """
        escalations = []

        # Evaluate signals
        for signal in signals:
            escalation = self._evaluate_signal_escalation(
                org_id, project_id, signal, correlations, patterns, timeline
            )
            if escalation:
                escalations.append(escalation)

        # Evaluate correlations (for additional context)
        for correlation in correlations:
            # Only escalate correlations that haven't been escalated via signals
            if correlation.get('escalation_trigger'):
                # Check if signal already escalated
                signal_escalated = any(
                    e.trigger_id == correlation['signal_id']
                    for e in escalations
                )
                if not signal_escalated:
                    escalation = self._evaluate_correlation_escalation(
                        org_id, project_id, correlation, timeline
                    )
                    if escalation:
                        escalations.append(escalation)

        # Evaluate patterns
        for pattern in patterns:
            escalation = self._evaluate_pattern_escalation(
                org_id, project_id, pattern
            )
            if escalation:
                escalations.append(escalation)

        logger.info(f"Generated {len(escalations)} escalations for project {project_id}")

        return escalations

    def _evaluate_signal_escalation(
        self,
        org_id: str,
        project_id: str,
        signal: Dict,
        correlations: List[Dict],
        patterns: List[Any],
        timeline: Dict
    ) -> Optional[Escalation]:
        """Evaluate if signal requires escalation"""

        # Skip resolved signals
        if signal.get('status') == 'resolved':
            return None

        # Check VP-level triggers first (highest priority)
        vp_escalation = self._check_vp_escalation(signal, correlations, patterns, timeline)
        if vp_escalation:
            return self._create_escalation(
                org_id, project_id, 'signal', signal, 'vp', correlations, patterns
            )

        # Check Director-level triggers
        director_escalation = self._check_director_escalation(signal, correlations, timeline)
        if director_escalation:
            return self._create_escalation(
                org_id, project_id, 'signal', signal, 'director', correlations, patterns
            )

        # No escalation needed (CPM-level only)
        return None

    def _check_vp_escalation(
        self,
        signal: Dict,
        correlations: List[Dict],
        patterns: List[Any],
        timeline: Dict
    ) -> bool:
        """Check if signal meets VP escalation criteria"""

        # 1. Critical priority risks (Priority = 9)
        if signal['signal_type'].startswith('risk_') and signal.get('priority') == 9:
            return True

        # 2. Safety risks (immediate VP attention)
        if signal.get('signal_category') == 'Safety' and signal.get('priority', 0) >= 6:
            return True

        # 3. Hard blockers on critical path
        signal_correlations = [c for c in correlations if c['signal_id'] == signal['signal_id']]
        for corr in signal_correlations:
            if corr.get('correlation_type') == 'blocker':
                # Check if affected milestone is on critical path
                milestone_name = corr.get('affected_milestone_name')
                if self._is_critical_path_milestone(milestone_name, timeline):
                    return True

        # 4. Systemic patterns detected
        # (patterns are evaluated separately)

        # 5. Critical path milestone delay >4 weeks
        for corr in signal_correlations:
            delay_days = corr.get('estimated_delay_days', 0)
            delay_weeks = delay_days / 7
            if delay_weeks > 4:
                milestone_name = corr.get('affected_milestone_name')
                if self._is_critical_path_milestone(milestone_name, timeline):
                    return True

        # 6. Escalation notes populated (explicit escalation)
        if signal.get('escalation_notes'):
            return True

        return False

    def _check_director_escalation(
        self,
        signal: Dict,
        correlations: List[Dict],
        timeline: Dict
    ) -> bool:
        """Check if signal meets Director escalation criteria"""

        # 1. High priority risks (Priority ≥6)
        if signal['signal_type'].startswith('risk_') and signal.get('priority', 0) >= 6:
            return True

        # 2. TMF completeness <75%
        if signal['signal_type'] == 'tmf_completeness_risk':
            signal_detail = json.loads(signal.get('signal_detail', '{}'))
            completeness = signal_detail.get('completeness_pct', 100)
            if completeness < 75:
                return True

        # 3. Milestone delay >2 weeks
        signal_correlations = [c for c in correlations if c['signal_id'] == signal['signal_id']]
        for corr in signal_correlations:
            delay_days = corr.get('estimated_delay_days', 0)
            delay_weeks = delay_days / 7
            if delay_weeks > 2:
                return True

        # 4. Blocker correlations
        for corr in signal_correlations:
            if corr.get('correlation_type') == 'blocker':
                return True

        # 5. Overdue signals (>14 days past target)
        if signal.get('target_date'):
            try:
                target_date_str = signal['target_date']
                if isinstance(target_date_str, str):
                    target_date = datetime.fromisoformat(target_date_str).date()
                else:
                    target_date = target_date_str

                days_overdue = (date.today() - target_date).days
                if days_overdue > 14:
                    return True
            except:
                pass

        return False

    def _is_critical_path_milestone(self, milestone_name: str, timeline: Dict) -> bool:
        """Check if milestone is on critical path"""
        for milestone in timeline.get('milestones', []):
            if milestone.get('milestone_name') == milestone_name:
                return milestone.get('is_critical_path', False)
        return False

    def _create_escalation(
        self,
        org_id: str,
        project_id: str,
        trigger_type: str,
        trigger_obj: Dict,
        level: str,
        correlations: List[Dict],
        patterns: List[Any]
    ) -> Escalation:
        """Create escalation object"""

        # Build escalation reason
        reason = self._build_escalation_reason(trigger_obj, level)

        # Generate intervention recommendations
        intervention = self._generate_interventions(trigger_obj, correlations, patterns, level)

        # Determine priority
        priority = trigger_obj.get('priority', 7)

        return Escalation(
            escalation_id=str(uuid.uuid4()),
            org_id=org_id,
            project_id=project_id,
            trigger_type=trigger_type,
            trigger_id=trigger_obj.get('signal_id') or trigger_obj.get('correlation_id'),
            escalation_rule_id=None,
            escalation_level=level,
            escalation_reason=reason,
            escalation_data={
                'signal_type': trigger_obj.get('signal_type'),
                'signal_category': trigger_obj.get('signal_category'),
                'priority': priority
            },
            assigned_to=None,
            assigned_role=level,  # Assigned to director or vp role
            status='open',
            priority=priority,
            intervention_recommended=intervention,
            intervention_taken=None,
            resolution_notes=None,
            created_at=datetime.now(),
            acknowledged_at=None,
            resolved_at=None
        )

    def _build_escalation_reason(self, trigger_obj: Dict, level: str) -> str:
        """Build human-readable escalation reason"""

        signal_type = trigger_obj.get('signal_type', 'Unknown')
        signal_desc = trigger_obj.get('signal_description', 'No description')
        priority = trigger_obj.get('priority', 'Unknown')

        if level == 'vp':
            return f"VP ESCALATION: {signal_type} (Priority {priority}) - {signal_desc}"
        else:
            return f"Director Escalation: {signal_type} (Priority {priority}) - {signal_desc}"

    def _generate_interventions(
        self,
        trigger_obj: Dict,
        correlations: List[Dict],
        patterns: List[Any],
        level: str
    ) -> str:
        """Generate prescriptive intervention recommendations"""

        interventions = []

        signal_type = trigger_obj.get('signal_type', '')
        signal_category = trigger_obj.get('signal_category', '')

        # Risk-specific interventions
        if signal_type.startswith('risk_'):
            if signal_category == 'Site':
                interventions.append("• Expedite site contract negotiations")
                interventions.append("• Activate backup sites")
                interventions.append("• Review site selection criteria")

            elif signal_category == 'Clinical':
                interventions.append("• Review enrollment forecasts")
                interventions.append("• Adjust screen failure assumptions")
                interventions.append("• Consider protocol amendments to widen criteria")

            elif signal_category == 'Safety':
                interventions.append("• Immediate DSMB notification")
                interventions.append("• Review AE reporting procedures")
                interventions.append("• Consider study pause if toxicity exceeds limits")

        # TMF interventions
        if signal_type.startswith('tmf_'):
            signal_detail = json.loads(trigger_obj.get('signal_detail', '{}'))
            missing_count = signal_detail.get('missing_count', 'unknown')

            interventions.append("• Allocate additional regulatory resources")
            interventions.append(f"• Prioritize {missing_count} missing artifacts")
            interventions.append("• Review department bottlenecks")

        # Correlation-specific
        signal_id = trigger_obj.get('signal_id')
        if signal_id:
            signal_correlations = [c for c in correlations if c.get('signal_id') == signal_id]
            if signal_correlations:
                affected_milestones = ', '.join(set(c.get('affected_milestone_name', '') for c in signal_correlations))
                interventions.append(f"• Affected milestones: {affected_milestones}")
                interventions.append("• Re-evaluate timeline if delays exceed 30 days")

        # Default if no specific recommendations
        if not interventions:
            interventions.append("• Immediate review and action plan required")
            interventions.append("• Escalate to leadership for guidance")

        return "\n".join(interventions)

    def _evaluate_correlation_escalation(
        self,
        org_id: str,
        project_id: str,
        correlation: Dict,
        timeline: Dict
    ) -> Optional[Escalation]:
        """Evaluate correlation for escalation"""

        # Blocker-type correlations should escalate
        if correlation.get('correlation_type') == 'blocker':
            return Escalation(
                escalation_id=str(uuid.uuid4()),
                org_id=org_id,
                project_id=project_id,
                trigger_type='correlation',
                trigger_id=correlation['correlation_id'],
                escalation_rule_id=correlation.get('correlation_rule_id'),
                escalation_level='director',
                escalation_reason=f"BLOCKER: {correlation.get('correlation_reasoning', 'Timeline blocked')}",
                escalation_data={
                    'correlation_type': 'blocker',
                    'affected_milestone': correlation.get('affected_milestone_name'),
                    'estimated_delay_days': correlation.get('estimated_delay_days')
                },
                assigned_to=None,
                assigned_role='director',
                status='open',
                priority=8,
                intervention_recommended="Resolve blocker immediately to unblock timeline",
                intervention_taken=None,
                resolution_notes=None,
                created_at=datetime.now(),
                acknowledged_at=None,
                resolved_at=None
            )

        return None

    def _evaluate_pattern_escalation(
        self,
        org_id: str,
        project_id: str,
        pattern: Any
    ) -> Optional[Escalation]:
        """Evaluate pattern for escalation"""

        # Critical or high severity patterns escalate to VP
        if pattern.severity in ['critical', 'high']:
            level = 'vp' if pattern.severity == 'critical' else 'director'

            return Escalation(
                escalation_id=str(uuid.uuid4()),
                org_id=org_id,
                project_id=project_id,
                trigger_type='pattern',
                trigger_id=pattern.pattern_id,
                escalation_rule_id=None,
                escalation_level=level,
                escalation_reason=f"PATTERN DETECTED: {pattern.pattern_name} - {pattern.description}",
                escalation_data={
                    'pattern_type': pattern.pattern_type,
                    'severity': pattern.severity,
                    'affected_signals_count': len(pattern.affected_signals)
                },
                assigned_to=None,
                assigned_role=level,
                status='open',
                priority=9 if pattern.severity == 'critical' else 7,
                intervention_recommended=pattern.recommended_action,
                intervention_taken=None,
                resolution_notes=None,
                created_at=datetime.now(),
                acknowledged_at=None,
                resolved_at=None
            )

        return None


def store_escalations(
    conn: sqlite3.Connection,
    escalations: List[Escalation],
    send_notifications: bool = True
):
    """
    Store escalations in database and send notifications

    Args:
        conn: Database connection
        escalations: List of Escalation objects
        send_notifications: Whether to send notifications (default: True)
    """
    cursor = conn.cursor()

    for escalation in escalations:
        esc_dict = escalation.to_dict()

        cursor.execute("""
            INSERT INTO escalations (
                escalation_id, org_id, project_id,
                trigger_type, trigger_id, escalation_rule_id,
                escalation_level, escalation_reason, escalation_data,
                assigned_to, assigned_role,
                status, priority,
                intervention_recommended, intervention_taken, resolution_notes,
                created_at, acknowledged_at, resolved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            esc_dict['escalation_id'],
            esc_dict['org_id'],
            esc_dict['project_id'],
            esc_dict['trigger_type'],
            esc_dict['trigger_id'],
            esc_dict['escalation_rule_id'],
            esc_dict['escalation_level'],
            esc_dict['escalation_reason'],
            esc_dict['escalation_data'],
            esc_dict['assigned_to'],
            esc_dict['assigned_role'],
            esc_dict['status'],
            esc_dict['priority'],
            esc_dict['intervention_recommended'],
            esc_dict['intervention_taken'],
            esc_dict['resolution_notes'],
            esc_dict['created_at'],
            esc_dict['acknowledged_at'],
            esc_dict['resolved_at']
        ))

    conn.commit()
    logger.info(f"Stored {len(escalations)} escalations in database")

    # Send notifications for each escalation
    if send_notifications and escalations:
        try:
            from intelligence.notification_service import NotificationService

            notification_service = NotificationService(conn)

            for escalation in escalations:
                notification_ids = notification_service.notify_escalation_created(
                    escalation=escalation.to_dict(),
                    project_id=escalation.project_id,
                    org_id=escalation.org_id
                )

                logger.info(
                    f"Created {len(notification_ids)} notifications for escalation "
                    f"{escalation.escalation_id}"
                )

        except Exception as e:
            logger.error(f"Failed to send escalation notifications: {e}", exc_info=True)
            # Don't fail the entire operation if notifications fail
