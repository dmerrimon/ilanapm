"""
Signal-to-Timeline Correlation Engine

Matches signals from trackers to timeline milestones using correlation rules.

Workflow:
1. Receive signals (from signal extraction)
2. Receive project timeline (from MS Project or template)
3. For each signal, find matching correlation rules
4. For each matching rule, find affected milestones in timeline
5. Calculate estimated impact (delay days, cost)
6. Generate human-readable reasoning
7. Create correlation objects for storage

Example:
    Risk #13 "Site activation slower" (Priority 7)
    → Matches Rule: "High Priority Risk → Site Activation"
    → Finds "Site Activation" milestone in timeline
    → Estimates delay: 7 × 7 = 49 days
    → Creates correlation with reasoning
"""

import sqlite3
import json
import uuid
import re
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SignalTimelineCorrelation:
    """Represents a correlation between a signal and timeline milestone"""
    correlation_id: str
    signal_id: str
    project_id: str
    affected_milestone_name: str
    affected_milestone_code: str
    affected_task_ids: List[str]
    correlation_type: str  # "blocker", "risk", "informational"
    confidence_score: float
    impact_type: str  # "delay", "cost_increase", "resource_bottleneck"
    estimated_delay_days: int
    estimated_cost_impact: float
    correlation_rule_id: str
    correlation_reasoning: str
    detected_at: datetime

    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        return {
            "correlation_id": self.correlation_id,
            "signal_id": self.signal_id,
            "project_id": self.project_id,
            "affected_milestone_name": self.affected_milestone_name,
            "affected_milestone_code": self.affected_milestone_code,
            "affected_task_ids": json.dumps(self.affected_task_ids),
            "correlation_type": self.correlation_type,
            "confidence_score": self.confidence_score,
            "impact_type": self.impact_type,
            "estimated_delay_days": self.estimated_delay_days,
            "estimated_cost_impact": self.estimated_cost_impact,
            "correlation_rule_id": self.correlation_rule_id,
            "correlation_reasoning": self.correlation_reasoning,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None
        }


class CorrelationEngine:
    """Correlate signals to timeline milestones"""

    # Cost impact constant: $733K/month industry benchmark
    COST_PER_DAY = 733000 / 30  # ~$24,433 per day

    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row

    def correlate_signals(
        self,
        signals: List[Dict],
        project_timeline: Dict,
        project_id: str
    ) -> List[SignalTimelineCorrelation]:
        """
        Match signals to timeline milestones using correlation rules

        Args:
            signals: List of signal dictionaries (from signal extraction)
            project_timeline: Project timeline with milestones/tasks
            project_id: Project identifier

        Returns:
            List of SignalTimelineCorrelation objects

        Example timeline structure:
            {
                "milestones": [
                    {
                        "milestone_name": "Site Activation",
                        "milestone_code": "SITE_ACT",
                        "task_id": "task_123",
                        "planned_date": "2026-06-15",
                        "is_critical_path": True
                    },
                    ...
                ]
            }
        """
        correlations = []

        for signal in signals:
            # Find matching correlation rules
            matching_rules = self._find_matching_rules(signal)

            for rule in matching_rules:
                # Find affected milestones in timeline
                affected_milestones = self._find_milestones_in_timeline(
                    project_timeline,
                    rule
                )

                if not affected_milestones:
                    logger.debug(f"No matching milestones found for rule {rule['rule_name']}")
                    continue

                # For each affected milestone, create a correlation
                for milestone in affected_milestones:
                    # Calculate impact
                    delay_days = self._estimate_delay(signal, rule)
                    cost_impact = delay_days * self.COST_PER_DAY

                    # Generate reasoning
                    reasoning = self._generate_reasoning(signal, rule, milestone, delay_days)

                    # Create correlation
                    correlation = SignalTimelineCorrelation(
                        correlation_id=str(uuid.uuid4()),
                        signal_id=signal['signal_id'],
                        project_id=project_id,
                        affected_milestone_name=milestone['milestone_name'],
                        affected_milestone_code=milestone.get('milestone_code', ''),
                        affected_task_ids=[milestone.get('task_id', '')],
                        correlation_type=rule['correlation_type'],
                        confidence_score=rule['confidence_score'],
                        impact_type=rule['impact_type'],
                        estimated_delay_days=delay_days,
                        estimated_cost_impact=cost_impact,
                        correlation_rule_id=rule['rule_id'],
                        correlation_reasoning=reasoning,
                        detected_at=datetime.now()
                    )

                    correlations.append(correlation)

                    logger.info(f"Created correlation: {signal['signal_type']} → {milestone['milestone_name']} (delay: {delay_days}d)")

        return correlations

    def _find_matching_rules(self, signal: Dict) -> List[Dict]:
        """Find correlation rules that match this signal"""
        cursor = self.conn.cursor()

        # Get all active rules for this signal type
        cursor.execute("""
            SELECT
                rule_id, rule_name, signal_type, signal_category,
                signal_detail_pattern, affected_milestones, affected_milestone_codes,
                correlation_type, confidence_score, impact_type,
                delay_estimation_logic, escalation_trigger, escalation_level,
                reasoning_template
            FROM correlation_rules
            WHERE signal_type = ? AND is_active = 1
        """, (signal['signal_type'],))

        rules = []
        for row in cursor.fetchall():
            rule = dict(row)

            # Parse JSON fields
            rule['signal_detail_pattern'] = json.loads(rule['signal_detail_pattern']) if rule['signal_detail_pattern'] else {}
            rule['affected_milestones'] = json.loads(rule['affected_milestones'])
            rule['affected_milestone_codes'] = json.loads(rule['affected_milestone_codes'])
            rule['delay_estimation_logic'] = json.loads(rule['delay_estimation_logic']) if rule['delay_estimation_logic'] else {}

            # Check if rule matches signal
            if self._rule_matches_signal(rule, signal):
                rules.append(rule)

        return rules

    def _rule_matches_signal(self, rule: Dict, signal: Dict) -> bool:
        """Check if correlation rule matches signal"""

        # Check category match (if rule specifies category)
        if rule['signal_category']:
            if signal.get('signal_category') != rule['signal_category']:
                return False

        # Check detail pattern match
        pattern = rule['signal_detail_pattern']
        if not pattern:
            return True  # No pattern = matches all

        pattern_type = pattern.get('pattern_type')

        if pattern_type == 'keyword_match':
            # Check if signal description contains any keywords
            keywords = pattern.get('keywords', [])
            signal_text = signal.get('signal_description', '').lower()
            signal_detail = json.loads(signal.get('signal_detail', '{}'))
            signal_detail_text = json.dumps(signal_detail).lower()

            for keyword in keywords:
                if keyword.lower() in signal_text or keyword.lower() in signal_detail_text:
                    return True
            return False

        elif pattern_type == 'task_code_match':
            # Check if signal references specific task codes
            task_codes = pattern.get('task_codes', [])
            signal_detail = json.loads(signal.get('signal_detail', '{}'))
            signal_task_code = signal_detail.get('task_code', '')

            return signal_task_code in task_codes

        elif pattern_type == 'any':
            return True

        # Unknown pattern type = no match
        return False

    def _find_milestones_in_timeline(
        self,
        project_timeline: Dict,
        rule: Dict
    ) -> List[Dict]:
        """Find milestones in timeline that match rule's affected milestones"""

        affected_codes = rule['affected_milestone_codes']
        affected_names = rule['affected_milestones']

        # Handle wildcard (affects all milestones)
        if '*' in affected_codes or '*' in affected_names:
            return project_timeline.get('milestones', [])

        # Find matching milestones
        matching_milestones = []
        for milestone in project_timeline.get('milestones', []):
            milestone_name = milestone.get('milestone_name', '')
            milestone_code = milestone.get('milestone_code', '')

            # Check if milestone matches by code or name
            if milestone_code in affected_codes or milestone_name in affected_names:
                matching_milestones.append(milestone)

        return matching_milestones

    def _estimate_delay(self, signal: Dict, rule: Dict) -> int:
        """Estimate delay in days based on signal and rule"""

        delay_logic = rule['delay_estimation_logic']
        if not delay_logic:
            return 0

        logic_type = delay_logic.get('type')

        if logic_type == 'fixed':
            # Fixed number of days
            return delay_logic.get('days', 0)

        elif logic_type == 'multiplier':
            # Multiply signal priority by factor
            formula = delay_logic.get('formula', '')
            priority = signal.get('priority', 5)

            # Parse formula: "priority * 7" → 7
            match = re.search(r'priority\s*\*\s*(\d+)', formula)
            if match:
                multiplier = int(match.group(1))
                return priority * multiplier

            return 0

        elif logic_type == 'variable':
            # Variable delay based on signal details
            signal_detail = json.loads(signal.get('signal_detail', '{}'))

            # For budget overruns, estimate based on variance percentage
            if 'variance_pct' in signal_detail:
                variance_pct = float(signal_detail['variance_pct'])
                # Rough estimate: 1% over budget = 3 days delay
                return int(variance_pct * 3)

            return 0

        return 0

    def _generate_reasoning(
        self,
        signal: Dict,
        rule: Dict,
        milestone: Dict,
        delay_days: int
    ) -> str:
        """Generate human-readable reasoning for correlation"""

        template = rule['reasoning_template']
        if not template:
            return f"Signal '{signal['signal_type']}' affects {milestone['milestone_name']}"

        # Parse signal_detail JSON
        signal_detail = json.loads(signal.get('signal_detail', '{}'))

        # Build replacement dictionary
        replacements = {
            'signal_type': signal['signal_type'],
            'signal_description': signal.get('signal_description', 'Unknown'),
            'priority': signal.get('priority', 'Unknown'),
            'milestone': milestone['milestone_name'],
            'delay_days': delay_days,
            'completeness_pct': signal_detail.get('completeness_pct', 'Unknown'),
            'missing_count': signal_detail.get('missing_count', 'Unknown'),
            'variance_pct': signal_detail.get('variance_pct', 'Unknown')
        }

        # Replace placeholders in template
        reasoning = template
        for key, value in replacements.items():
            reasoning = reasoning.replace(f'{{{key}}}', str(value))

        return reasoning


def store_correlations(
    conn: sqlite3.Connection,
    correlations: List[SignalTimelineCorrelation]
):
    """Store correlations in database"""
    cursor = conn.cursor()

    for correlation in correlations:
        corr_dict = correlation.to_dict()

        cursor.execute("""
            INSERT INTO signal_timeline_correlations (
                correlation_id, signal_id, project_id,
                affected_milestone_name, affected_milestone_code, affected_task_ids,
                correlation_type, confidence_score,
                impact_type, estimated_delay_days, estimated_cost_impact,
                correlation_rule_id, correlation_reasoning,
                detected_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            corr_dict['correlation_id'],
            corr_dict['signal_id'],
            corr_dict['project_id'],
            corr_dict['affected_milestone_name'],
            corr_dict['affected_milestone_code'],
            corr_dict['affected_task_ids'],
            corr_dict['correlation_type'],
            corr_dict['confidence_score'],
            corr_dict['impact_type'],
            corr_dict['estimated_delay_days'],
            corr_dict['estimated_cost_impact'],
            corr_dict['correlation_rule_id'],
            corr_dict['correlation_reasoning'],
            corr_dict['detected_at']
        ))

    conn.commit()
    logger.info(f"Stored {len(correlations)} correlations in database")
