"""
Portfolio Intelligence Service

Aggregates intelligence data across multiple studies to provide portfolio-wide insights:
- Portfolio health rollup
- Cross-study pattern detection
- Systemic issue detection
- Resource allocation analysis
- Portfolio forecasting

This builds on single-study intelligence (Phase 2 & 3) to provide executive-level portfolio views.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


@dataclass
class PortfolioHealth:
    """Portfolio-wide health summary"""
    org_id: str
    generated_at: datetime

    # Overall metrics
    total_studies: int
    average_health_score: float
    median_health_score: float

    # Health distribution
    healthy_count: int
    warning_count: int
    critical_count: int

    # Trends
    improving_count: int  # Health improving over time
    declining_count: int  # Health declining over time
    stable_count: int

    # Escalations
    total_escalations: int
    director_escalations: int
    vp_escalations: int

    # Signals
    total_active_signals: int
    total_high_priority_risks: int

    # Financial impact
    estimated_total_delay_days: int
    estimated_total_cost_impact: float

    # Studies needing attention
    studies_needing_immediate_attention: List[str]
    studies_at_risk: List[str]


@dataclass
class CrossStudyPattern:
    """Pattern detected across multiple studies"""
    pattern_id: str
    pattern_type: str  # "resource_collision", "systemic_issue", "common_risk", "timeline_correlation"
    pattern_name: str
    pattern_description: str
    severity: str  # "low", "medium", "high", "critical"

    # Affected studies
    affected_studies: List[str]
    affected_study_count: int

    # Evidence
    evidence: Dict[str, Any]
    confidence_score: float

    # Impact
    portfolio_impact: str
    recommended_action: str

    detected_at: datetime


@dataclass
class SystemicIssue:
    """Systemic issue affecting portfolio"""
    issue_id: str
    issue_type: str  # "vendor_performance", "site_activation_delays", "enrollment_challenges", "regulatory_delays"
    issue_name: str
    issue_description: str
    severity: str

    # Affected studies
    affected_studies: List[str]
    affected_study_count: int

    # Root cause analysis
    root_cause: str
    contributing_factors: List[str]

    # Impact
    portfolio_impact_description: str
    estimated_delay_days: int
    estimated_cost_impact: float

    # Recommendations
    recommended_intervention: str
    responsible_party: str  # "vp", "director", "executive"

    detected_at: datetime


@dataclass
class ResourceAllocation:
    """Resource allocation analysis"""
    org_id: str
    generated_at: datetime

    # Resource conflicts
    resource_collisions: List[Dict[str, Any]]
    overallocated_resources: List[Dict[str, Any]]

    # Resource utilization
    total_resources: int
    utilized_resources: int
    available_resources: int
    utilization_rate: float

    # Recommendations
    reallocation_recommendations: List[Dict[str, Any]]


class PortfolioService:
    """Service for portfolio-wide intelligence analysis"""

    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row

    def get_portfolio_health(
        self,
        org_id: str,
        timeframe_days: int = 30
    ) -> PortfolioHealth:
        """
        Get comprehensive portfolio health analysis

        Args:
            org_id: Organization ID
            timeframe_days: Lookback period for trend analysis

        Returns:
            PortfolioHealth object with portfolio-wide metrics
        """
        cursor = self.conn.cursor()

        # Get all studies for org
        cursor.execute("""
            SELECT DISTINCT project_id
            FROM signals
            WHERE org_id = ?
        """, (org_id,))

        all_project_ids = [row['project_id'] for row in cursor.fetchall()]

        if not all_project_ids:
            return self._empty_portfolio_health(org_id)

        # Get latest health snapshots
        health_scores = []
        for project_id in all_project_ids:
            cursor.execute("""
                SELECT overall_health_score, health_status, snapshot_date
                FROM study_health_snapshots
                WHERE project_id = ? AND org_id = ?
                ORDER BY snapshot_date DESC
                LIMIT 1
            """, (project_id, org_id))

            snapshot = cursor.fetchone()
            if snapshot:
                health_scores.append({
                    'project_id': project_id,
                    'score': snapshot['overall_health_score'],
                    'status': snapshot['health_status'],
                    'date': snapshot['snapshot_date']
                })

        # Calculate distribution
        healthy_count = sum(1 for s in health_scores if s['status'] == 'healthy')
        warning_count = sum(1 for s in health_scores if s['status'] == 'warning')
        critical_count = sum(1 for s in health_scores if s['status'] == 'critical')

        # Calculate averages
        scores_only = [s['score'] for s in health_scores]
        avg_score = statistics.mean(scores_only) if scores_only else 0
        median_score = statistics.median(scores_only) if scores_only else 0

        # Get trends (compare to previous snapshots)
        improving, declining, stable = self._analyze_trends(
            org_id,
            all_project_ids,
            timeframe_days
        )

        # Get escalation counts
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM escalations
            WHERE org_id = ? AND status = 'open'
        """, (org_id,))
        total_escalations = cursor.fetchone()['count']

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM escalations
            WHERE org_id = ? AND status = 'open' AND escalation_level = 'director'
        """, (org_id,))
        director_escalations = cursor.fetchone()['count']

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM escalations
            WHERE org_id = ? AND status = 'open' AND escalation_level = 'vp'
        """, (org_id,))
        vp_escalations = cursor.fetchone()['count']

        # Get signal counts
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM signals
            WHERE org_id = ? AND status != 'resolved'
        """, (org_id,))
        total_signals = cursor.fetchone()['count']

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM signals
            WHERE org_id = ? AND signal_type LIKE 'risk_%' AND priority >= 7 AND status = 'open'
        """, (org_id,))
        high_priority_risks = cursor.fetchone()['count']

        # Get financial impact
        cursor.execute("""
            SELECT
                SUM(estimated_delay_days) as total_delay,
                SUM(estimated_cost_impact) as total_cost
            FROM signal_timeline_correlations
            WHERE project_id IN ({}) AND resolved_at IS NULL
        """.format(','.join('?' * len(all_project_ids))), all_project_ids)

        impact_row = cursor.fetchone()
        total_delay_days = impact_row['total_delay'] or 0
        total_cost_impact = impact_row['total_cost'] or 0

        # Identify studies needing attention
        immediate_attention = [s['project_id'] for s in health_scores if s['status'] == 'critical']
        at_risk = [s['project_id'] for s in health_scores if s['status'] == 'warning']

        return PortfolioHealth(
            org_id=org_id,
            generated_at=datetime.now(),
            total_studies=len(health_scores),
            average_health_score=round(avg_score, 1),
            median_health_score=round(median_score, 1),
            healthy_count=healthy_count,
            warning_count=warning_count,
            critical_count=critical_count,
            improving_count=improving,
            declining_count=declining,
            stable_count=stable,
            total_escalations=total_escalations,
            director_escalations=director_escalations,
            vp_escalations=vp_escalations,
            total_active_signals=total_signals,
            total_high_priority_risks=high_priority_risks,
            estimated_total_delay_days=int(total_delay_days),
            estimated_total_cost_impact=float(total_cost_impact),
            studies_needing_immediate_attention=immediate_attention,
            studies_at_risk=at_risk
        )

    def detect_cross_study_patterns(
        self,
        org_id: str
    ) -> List[CrossStudyPattern]:
        """
        Detect patterns across multiple studies

        Looks for:
        - Common risks appearing in multiple studies
        - Similar timeline delays across studies
        - Resource collisions
        - Systemic issues

        Returns:
            List of CrossStudyPattern objects
        """
        patterns = []

        # Detect common risks
        common_risk_patterns = self._detect_common_risk_patterns(org_id)
        patterns.extend(common_risk_patterns)

        # Detect timeline correlations
        timeline_patterns = self._detect_timeline_correlation_patterns(org_id)
        patterns.extend(timeline_patterns)

        # Detect resource collisions
        resource_patterns = self._detect_resource_collision_patterns(org_id)
        patterns.extend(resource_patterns)

        logger.info(f"Detected {len(patterns)} cross-study patterns for org {org_id}")

        return patterns

    def detect_systemic_issues(
        self,
        org_id: str
    ) -> List[SystemicIssue]:
        """
        Detect systemic issues affecting portfolio

        Looks for:
        - Vendor performance issues across studies
        - Site activation delays across studies
        - Enrollment challenges across studies
        - Regulatory delays across studies

        Returns:
            List of SystemicIssue objects
        """
        issues = []

        # Detect vendor performance issues
        vendor_issues = self._detect_vendor_issues(org_id)
        issues.extend(vendor_issues)

        # Detect site activation issues
        site_issues = self._detect_site_activation_issues(org_id)
        issues.extend(site_issues)

        # Detect enrollment issues
        enrollment_issues = self._detect_enrollment_issues(org_id)
        issues.extend(enrollment_issues)

        # Detect regulatory issues
        regulatory_issues = self._detect_regulatory_issues(org_id)
        issues.extend(regulatory_issues)

        logger.info(f"Detected {len(issues)} systemic issues for org {org_id}")

        return issues

    def analyze_resource_allocation(
        self,
        org_id: str
    ) -> ResourceAllocation:
        """
        Analyze resource allocation across portfolio

        Identifies:
        - Resource collisions (same resource allocated to multiple studies)
        - Overallocated resources
        - Underutilized resources
        - Reallocation recommendations

        Returns:
            ResourceAllocation object
        """
        # This would integrate with resource management data
        # For now, return a basic structure

        return ResourceAllocation(
            org_id=org_id,
            generated_at=datetime.now(),
            resource_collisions=[],
            overallocated_resources=[],
            total_resources=0,
            utilized_resources=0,
            available_resources=0,
            utilization_rate=0.0,
            reallocation_recommendations=[]
        )

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _empty_portfolio_health(self, org_id: str) -> PortfolioHealth:
        """Return empty portfolio health for orgs with no studies"""
        return PortfolioHealth(
            org_id=org_id,
            generated_at=datetime.now(),
            total_studies=0,
            average_health_score=0,
            median_health_score=0,
            healthy_count=0,
            warning_count=0,
            critical_count=0,
            improving_count=0,
            declining_count=0,
            stable_count=0,
            total_escalations=0,
            director_escalations=0,
            vp_escalations=0,
            total_active_signals=0,
            total_high_priority_risks=0,
            estimated_total_delay_days=0,
            estimated_total_cost_impact=0,
            studies_needing_immediate_attention=[],
            studies_at_risk=[]
        )

    def _analyze_trends(
        self,
        org_id: str,
        project_ids: List[str],
        timeframe_days: int
    ) -> Tuple[int, int, int]:
        """
        Analyze health score trends

        Returns:
            (improving_count, declining_count, stable_count)
        """
        cursor = self.conn.cursor()

        improving = 0
        declining = 0
        stable = 0

        cutoff_date = (datetime.now() - timedelta(days=timeframe_days)).date()

        for project_id in project_ids:
            # Get recent snapshots
            cursor.execute("""
                SELECT overall_health_score, snapshot_date
                FROM study_health_snapshots
                WHERE project_id = ? AND org_id = ?
                    AND snapshot_date >= ?
                ORDER BY snapshot_date DESC
                LIMIT 10
            """, (project_id, org_id, cutoff_date.isoformat()))

            snapshots = cursor.fetchall()

            if len(snapshots) < 2:
                stable += 1
                continue

            # Calculate trend (linear regression or simple comparison)
            scores = [s['overall_health_score'] for s in snapshots]

            # Simple approach: compare most recent to oldest
            recent_avg = statistics.mean(scores[:3]) if len(scores) >= 3 else scores[0]
            older_avg = statistics.mean(scores[-3:]) if len(scores) >= 3 else scores[-1]

            diff = recent_avg - older_avg

            if diff > 5:  # Improving by >5 points
                improving += 1
            elif diff < -5:  # Declining by >5 points
                declining += 1
            else:
                stable += 1

        return improving, declining, stable

    def _detect_common_risk_patterns(self, org_id: str) -> List[CrossStudyPattern]:
        """Detect common risks appearing in multiple studies"""
        cursor = self.conn.cursor()
        patterns = []

        # Find risk categories appearing in multiple studies
        cursor.execute("""
            SELECT
                signal_category,
                COUNT(DISTINCT project_id) as study_count,
                GROUP_CONCAT(DISTINCT project_id) as affected_studies,
                AVG(priority) as avg_priority
            FROM signals
            WHERE org_id = ?
                AND signal_type LIKE 'risk_%'
                AND status = 'open'
                AND signal_category IS NOT NULL
            GROUP BY signal_category
            HAVING study_count >= 2
        """, (org_id,))

        for row in cursor.fetchall():
            category = row['signal_category']
            study_count = row['study_count']
            affected_studies = row['affected_studies'].split(',')
            avg_priority = row['avg_priority']

            # Determine severity based on study count and priority
            if study_count >= 4 and avg_priority >= 7:
                severity = "critical"
            elif study_count >= 3 or avg_priority >= 7:
                severity = "high"
            elif study_count >= 2:
                severity = "medium"
            else:
                severity = "low"

            pattern = CrossStudyPattern(
                pattern_id=f"common_risk_{category.lower().replace(' ', '_')}",
                pattern_type="common_risk",
                pattern_name=f"Common {category} Risks",
                pattern_description=f"{category} risks detected in {study_count} studies",
                severity=severity,
                affected_studies=affected_studies,
                affected_study_count=study_count,
                evidence={
                    "category": category,
                    "avg_priority": round(avg_priority, 1),
                    "study_count": study_count
                },
                confidence_score=0.85,
                portfolio_impact=f"Portfolio-wide {category.lower()} challenges may indicate systemic issue",
                recommended_action=f"Investigate root cause of {category.lower()} issues across portfolio. Consider centralized mitigation strategy.",
                detected_at=datetime.now()
            )

            patterns.append(pattern)

        return patterns

    def _detect_timeline_correlation_patterns(self, org_id: str) -> List[CrossStudyPattern]:
        """Detect similar timeline delays across studies"""
        cursor = self.conn.cursor()
        patterns = []

        # Find milestones with delays in multiple studies
        cursor.execute("""
            SELECT
                affected_milestone_name,
                COUNT(DISTINCT project_id) as study_count,
                GROUP_CONCAT(DISTINCT project_id) as affected_studies,
                AVG(estimated_delay_days) as avg_delay
            FROM signal_timeline_correlations
            WHERE project_id IN (
                SELECT DISTINCT project_id FROM signals WHERE org_id = ?
            )
            AND correlation_type IN ('risk', 'blocker')
            AND resolved_at IS NULL
            GROUP BY affected_milestone_name
            HAVING study_count >= 2
        """, (org_id,))

        for row in cursor.fetchall():
            milestone = row['affected_milestone_name']
            study_count = row['study_count']
            affected_studies = row['affected_studies'].split(',')
            avg_delay = row['avg_delay']

            if study_count >= 3:
                severity = "high"
            elif study_count >= 2:
                severity = "medium"
            else:
                severity = "low"

            pattern = CrossStudyPattern(
                pattern_id=f"timeline_correlation_{milestone.lower().replace(' ', '_')}",
                pattern_type="timeline_correlation",
                pattern_name=f"{milestone} Delays Across Portfolio",
                pattern_description=f"{milestone} milestone delayed in {study_count} studies",
                severity=severity,
                affected_studies=affected_studies,
                affected_study_count=study_count,
                evidence={
                    "milestone": milestone,
                    "avg_delay_days": round(avg_delay, 0),
                    "study_count": study_count
                },
                confidence_score=0.90,
                portfolio_impact=f"Portfolio-wide delays to {milestone} suggest systemic bottleneck",
                recommended_action=f"Investigate common causes of {milestone} delays. Consider resource reallocation or process improvements.",
                detected_at=datetime.now()
            )

            patterns.append(pattern)

        return patterns

    def _detect_resource_collision_patterns(self, org_id: str) -> List[CrossStudyPattern]:
        """Detect resource collisions across studies"""
        # This would integrate with resource management data
        # Placeholder for now
        return []

    def _detect_vendor_issues(self, org_id: str) -> List[SystemicIssue]:
        """Detect vendor performance issues across studies"""
        cursor = self.conn.cursor()
        issues = []

        # Look for vendor-related signals across multiple studies
        cursor.execute("""
            SELECT
                COUNT(DISTINCT project_id) as study_count,
                GROUP_CONCAT(DISTINCT project_id) as affected_studies,
                COUNT(*) as signal_count
            FROM signals
            WHERE org_id = ?
                AND (signal_category = 'Vendor' OR signal_description LIKE '%vendor%')
                AND status = 'open'
        """, (org_id,))

        row = cursor.fetchone()

        if row and row['study_count'] >= 2:
            study_count = row['study_count']
            affected_studies = row['affected_studies'].split(',') if row['affected_studies'] else []
            signal_count = row['signal_count']

            issue = SystemicIssue(
                issue_id=f"systemic_vendor_{org_id}",
                issue_type="vendor_performance",
                issue_name="Vendor Performance Issues",
                issue_description=f"Vendor-related issues detected in {study_count} studies ({signal_count} signals)",
                severity="high" if study_count >= 3 else "medium",
                affected_studies=affected_studies,
                affected_study_count=study_count,
                root_cause="Vendor performance or coordination challenges affecting multiple studies",
                contributing_factors=[
                    "Vendor capacity constraints",
                    "Communication gaps",
                    "Quality issues",
                    "Timeline misalignment"
                ],
                portfolio_impact_description=f"Vendor issues affecting {study_count} studies may cause portfolio-wide delays",
                estimated_delay_days=14 * study_count,  # Estimate
                estimated_cost_impact=733000 * 0.5 * study_count,  # $733K/month * 0.5 months * studies
                recommended_intervention="Conduct vendor performance review. Consider escalation to executive team. Evaluate alternative vendors.",
                responsible_party="vp",
                detected_at=datetime.now()
            )

            issues.append(issue)

        return issues

    def _detect_site_activation_issues(self, org_id: str) -> List[SystemicIssue]:
        """Detect site activation delays across studies"""
        cursor = self.conn.cursor()
        issues = []

        # Look for site activation signals/correlations
        cursor.execute("""
            SELECT
                COUNT(DISTINCT s.project_id) as study_count,
                GROUP_CONCAT(DISTINCT s.project_id) as affected_studies,
                COUNT(*) as signal_count
            FROM signals s
            LEFT JOIN signal_timeline_correlations c ON s.signal_id = c.signal_id
            WHERE s.org_id = ?
                AND (
                    s.signal_category = 'Site'
                    OR c.affected_milestone_name LIKE '%Site Activation%'
                )
                AND s.status = 'open'
        """, (org_id,))

        row = cursor.fetchone()

        if row and row['study_count'] >= 2:
            study_count = row['study_count']
            affected_studies = row['affected_studies'].split(',') if row['affected_studies'] else []

            issue = SystemicIssue(
                issue_id=f"systemic_site_activation_{org_id}",
                issue_type="site_activation_delays",
                issue_name="Site Activation Delays",
                issue_description=f"Site activation challenges detected in {study_count} studies",
                severity="high" if study_count >= 3 else "medium",
                affected_studies=affected_studies,
                affected_study_count=study_count,
                root_cause="Site activation process inefficiencies affecting multiple studies",
                contributing_factors=[
                    "Contract negotiation delays",
                    "Site qualification challenges",
                    "Regulatory approval delays",
                    "Resource constraints"
                ],
                portfolio_impact_description=f"Site activation delays affecting {study_count} studies",
                estimated_delay_days=30 * study_count,
                estimated_cost_impact=733000 * study_count,
                recommended_intervention="Review site activation process. Streamline contract templates. Consider backup sites. Allocate additional site activation resources.",
                responsible_party="director",
                detected_at=datetime.now()
            )

            issues.append(issue)

        return issues

    def _detect_enrollment_issues(self, org_id: str) -> List[SystemicIssue]:
        """Detect enrollment challenges across studies"""
        cursor = self.conn.cursor()
        issues = []

        # Look for enrollment-related signals
        cursor.execute("""
            SELECT
                COUNT(DISTINCT project_id) as study_count,
                GROUP_CONCAT(DISTINCT project_id) as affected_studies
            FROM signals
            WHERE org_id = ?
                AND (
                    signal_category = 'Clinical'
                    AND (
                        signal_description LIKE '%enrollment%'
                        OR signal_description LIKE '%screen failure%'
                        OR signal_description LIKE '%dropout%'
                    )
                )
                AND status = 'open'
        """, (org_id,))

        row = cursor.fetchone()

        if row and row['study_count'] >= 2:
            study_count = row['study_count']
            affected_studies = row['affected_studies'].split(',') if row['affected_studies'] else []

            issue = SystemicIssue(
                issue_id=f"systemic_enrollment_{org_id}",
                issue_type="enrollment_challenges",
                issue_name="Enrollment Challenges",
                issue_description=f"Enrollment issues detected in {study_count} studies",
                severity="high" if study_count >= 3 else "medium",
                affected_studies=affected_studies,
                affected_study_count=study_count,
                root_cause="Portfolio-wide enrollment challenges",
                contributing_factors=[
                    "Stringent inclusion/exclusion criteria",
                    "Competition for patients",
                    "Site performance variability",
                    "Patient recruitment challenges"
                ],
                portfolio_impact_description=f"Enrollment challenges in {study_count} studies may delay LPI milestones",
                estimated_delay_days=45 * study_count,
                estimated_cost_impact=733000 * 1.5 * study_count,
                recommended_intervention="Review protocol criteria. Increase site count. Enhance patient recruitment strategies. Consider protocol amendments.",
                responsible_party="director",
                detected_at=datetime.now()
            )

            issues.append(issue)

        return issues

    def _detect_regulatory_issues(self, org_id: str) -> List[SystemicIssue]:
        """Detect regulatory delays across studies"""
        cursor = self.conn.cursor()
        issues = []

        # Look for TMF/regulatory signals
        cursor.execute("""
            SELECT
                COUNT(DISTINCT project_id) as study_count,
                GROUP_CONCAT(DISTINCT project_id) as affected_studies
            FROM signals
            WHERE org_id = ?
                AND (
                    signal_type LIKE 'tmf_%'
                    OR signal_category = 'Regulatory'
                )
                AND status = 'open'
        """, (org_id,))

        row = cursor.fetchone()

        if row and row['study_count'] >= 2:
            study_count = row['study_count']
            affected_studies = row['affected_studies'].split(',') if row['affected_studies'] else []

            issue = SystemicIssue(
                issue_id=f"systemic_regulatory_{org_id}",
                issue_type="regulatory_delays",
                issue_name="Regulatory & TMF Issues",
                issue_description=f"TMF/regulatory issues detected in {study_count} studies",
                severity="medium",
                affected_studies=affected_studies,
                affected_study_count=study_count,
                root_cause="TMF completeness or regulatory approval delays",
                contributing_factors=[
                    "Resource constraints in regulatory team",
                    "Document preparation delays",
                    "Regulatory authority backlogs",
                    "Missing source documentation"
                ],
                portfolio_impact_description=f"Regulatory issues in {study_count} studies may delay submissions",
                estimated_delay_days=21 * study_count,
                estimated_cost_impact=733000 * 0.75 * study_count,
                recommended_intervention="Allocate additional regulatory resources. Implement document tracking system. Prioritize critical documents.",
                responsible_party="director",
                detected_at=datetime.now()
            )

            issues.append(issue)

        return issues


def store_cross_study_patterns(
    conn: sqlite3.Connection,
    patterns: List[CrossStudyPattern],
    org_id: str
):
    """Store cross-study patterns in database"""
    cursor = conn.cursor()

    for pattern in patterns:
        cursor.execute("""
            INSERT OR REPLACE INTO cross_study_patterns (
                pattern_id, org_id, pattern_type, pattern_name,
                pattern_description, severity, affected_studies,
                affected_study_count, evidence, confidence_score,
                portfolio_impact, recommended_action, detected_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern.pattern_id,
            org_id,
            pattern.pattern_type,
            pattern.pattern_name,
            pattern.pattern_description,
            pattern.severity,
            json.dumps(pattern.affected_studies),
            pattern.affected_study_count,
            json.dumps(pattern.evidence),
            pattern.confidence_score,
            pattern.portfolio_impact,
            pattern.recommended_action,
            pattern.detected_at.isoformat()
        ))

    conn.commit()
    logger.info(f"Stored {len(patterns)} cross-study patterns")


def store_systemic_issues(
    conn: sqlite3.Connection,
    issues: List[SystemicIssue],
    org_id: str
):
    """Store systemic issues in database"""
    cursor = conn.cursor()

    for issue in issues:
        cursor.execute("""
            INSERT OR REPLACE INTO systemic_issues (
                issue_id, org_id, issue_type, issue_name,
                issue_description, severity, affected_studies,
                affected_study_count, root_cause, contributing_factors,
                portfolio_impact_description, estimated_delay_days,
                estimated_cost_impact, recommended_intervention,
                responsible_party, detected_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            issue.issue_id,
            org_id,
            issue.issue_type,
            issue.issue_name,
            issue.issue_description,
            issue.severity,
            json.dumps(issue.affected_studies),
            issue.affected_study_count,
            issue.root_cause,
            json.dumps(issue.contributing_factors),
            issue.portfolio_impact_description,
            issue.estimated_delay_days,
            issue.estimated_cost_impact,
            issue.recommended_intervention,
            issue.responsible_party,
            issue.detected_at.isoformat()
        ))

    conn.commit()
    logger.info(f"Stored {len(issues)} systemic issues")
