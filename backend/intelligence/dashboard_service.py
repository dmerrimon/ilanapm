"""
Dashboard Data Aggregation Service

Aggregates intelligence data for Leadership Dashboard display:
- Study health scores (from snapshots)
- Active signals (from trackers)
- Correlations (signal → milestone impacts)
- Patterns (detected anomalies)
- Escalations (Director/VP level)
- Timeline variance
- Recommended actions

Provides both cached and real-time data access.
"""

import sqlite3
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class StudySummary:
    """Summary of a single study for dashboard display"""
    project_id: str
    project_name: str
    org_id: str

    # Health
    health_score: float
    health_status: str  # "healthy", "warning", "critical"

    # Component scores
    timeline_score: Optional[float]
    risk_score: Optional[float]
    tmf_score: Optional[float]

    # Counts
    active_signals_count: int
    open_risks_count: int
    director_escalations_count: int
    vp_escalations_count: int

    # Latest activity
    last_updated: str  # ISO datetime
    last_tracker_upload: Optional[str]

    # Key issues
    top_risk_description: Optional[str]
    critical_milestone_at_risk: Optional[str]


@dataclass
class LeadershipDashboard:
    """Complete Leadership Dashboard data"""
    org_id: str
    generated_at: datetime

    # Portfolio summary
    total_studies: int
    healthy_count: int
    warning_count: int
    critical_count: int

    # Study summaries
    studies: List[StudySummary]

    # Portfolio-wide metrics
    total_active_escalations: int
    total_director_escalations: int
    total_vp_escalations: int
    total_active_signals: int

    # Filters/sorts applied
    filters_applied: Optional[Dict]
    sort_by: Optional[str]


class DashboardService:
    """Service for aggregating dashboard data"""

    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row

    def get_leadership_dashboard(
        self,
        org_id: str,
        filters: Optional[Dict] = None,
        sort_by: str = "health_score_asc",
        use_cache: bool = True
    ) -> LeadershipDashboard:
        """
        Get complete Leadership Dashboard data

        Args:
            org_id: Organization ID
            filters: Optional filters (status, priority, etc.)
            sort_by: Sort order ("health_score_asc", "health_score_desc", "name", etc.)
            use_cache: Whether to use cached data (faster)

        Returns:
            LeadershipDashboard object with all studies and metrics
        """
        # Check cache if enabled
        if use_cache:
            cached = self._get_cached_dashboard(org_id, filters, sort_by)
            if cached:
                logger.info(f"Returning cached dashboard for org {org_id}")
                return cached

        # Generate fresh dashboard data
        logger.info(f"Generating fresh dashboard for org {org_id}")
        dashboard = self._generate_dashboard(org_id, filters, sort_by)

        # Cache for future requests
        self._cache_dashboard(org_id, dashboard, filters, sort_by)

        return dashboard

    def get_study_detail(
        self,
        project_id: str,
        org_id: str
    ) -> Dict[str, Any]:
        """
        Get detailed data for a single study

        Returns:
            Complete study details including signals, correlations, escalations, patterns
        """
        cursor = self.conn.cursor()

        # Get health snapshot
        cursor.execute("""
            SELECT
                overall_health_score, health_status,
                timeline_score, risk_score, tmf_score,
                enrollment_score, budget_score, vendor_score,
                top_risks, active_escalations_count,
                director_escalations_count, vp_escalations_count,
                recommended_actions, snapshot_date
            FROM study_health_snapshots
            WHERE project_id = ? AND org_id = ?
            ORDER BY snapshot_date DESC
            LIMIT 1
        """, (project_id, org_id))

        snapshot = cursor.fetchone()

        if not snapshot:
            return {
                "error": "No health snapshot found",
                "project_id": project_id
            }

        # Get active signals
        cursor.execute("""
            SELECT
                signal_id, signal_type, signal_category,
                signal_description, priority, status,
                date_identified, target_date, escalation_level
            FROM signals
            WHERE project_id = ? AND status != 'resolved'
            ORDER BY priority DESC, date_identified DESC
        """, (project_id,))

        signals = [dict(row) for row in cursor.fetchall()]

        # Get correlations
        cursor.execute("""
            SELECT
                correlation_id, signal_id,
                affected_milestone_name, correlation_type,
                estimated_delay_days, estimated_cost_impact,
                correlation_reasoning, confidence_score
            FROM signal_timeline_correlations
            WHERE project_id = ? AND resolved_at IS NULL
            ORDER BY estimated_delay_days DESC
        """, (project_id,))

        correlations = [dict(row) for row in cursor.fetchall()]

        # Get escalations
        cursor.execute("""
            SELECT
                escalation_id, escalation_level, escalation_reason,
                priority, status, intervention_recommended,
                created_at
            FROM escalations
            WHERE project_id = ? AND status = 'open'
            ORDER BY priority DESC, created_at DESC
        """, (project_id,))

        escalations = [dict(row) for row in cursor.fetchall()]

        # Build complete study detail
        return {
            "project_id": project_id,
            "health": {
                "overall_score": snapshot['overall_health_score'],
                "status": snapshot['health_status'],
                "component_scores": {
                    "timeline": snapshot['timeline_score'],
                    "risk": snapshot['risk_score'],
                    "tmf": snapshot['tmf_score'],
                    "enrollment": snapshot['enrollment_score'],
                    "budget": snapshot['budget_score'],
                    "vendor": snapshot['vendor_score']
                },
                "snapshot_date": snapshot['snapshot_date']
            },
            "signals": signals,
            "correlations": correlations,
            "escalations": escalations,
            "escalation_counts": {
                "active": snapshot['active_escalations_count'],
                "director": snapshot['director_escalations_count'],
                "vp": snapshot['vp_escalations_count']
            },
            "top_risks": json.loads(snapshot['top_risks']) if snapshot['top_risks'] else [],
            "recommended_actions": json.loads(snapshot['recommended_actions']) if snapshot['recommended_actions'] else []
        }

    def _generate_dashboard(
        self,
        org_id: str,
        filters: Optional[Dict],
        sort_by: str
    ) -> LeadershipDashboard:
        """Generate fresh dashboard data"""
        cursor = self.conn.cursor()

        # Get all projects for org
        cursor.execute("""
            SELECT DISTINCT project_id
            FROM signals
            WHERE org_id = ?
        """, (org_id,))

        project_ids = [row['project_id'] for row in cursor.fetchall()]

        if not project_ids:
            # No projects with signals yet
            return LeadershipDashboard(
                org_id=org_id,
                generated_at=datetime.now(),
                total_studies=0,
                healthy_count=0,
                warning_count=0,
                critical_count=0,
                studies=[],
                total_active_escalations=0,
                total_director_escalations=0,
                total_vp_escalations=0,
                total_active_signals=0,
                filters_applied=filters,
                sort_by=sort_by
            )

        # Get study summaries
        studies = []
        for project_id in project_ids:
            summary = self._get_study_summary(project_id, org_id)
            if summary:
                # Apply filters
                if self._passes_filters(summary, filters):
                    studies.append(summary)

        # Sort studies
        studies = self._sort_studies(studies, sort_by)

        # Calculate portfolio metrics
        healthy_count = sum(1 for s in studies if s.health_status == 'healthy')
        warning_count = sum(1 for s in studies if s.health_status == 'warning')
        critical_count = sum(1 for s in studies if s.health_status == 'critical')

        total_director = sum(s.director_escalations_count for s in studies)
        total_vp = sum(s.vp_escalations_count for s in studies)
        total_escalations = total_director + total_vp
        total_signals = sum(s.active_signals_count for s in studies)

        return LeadershipDashboard(
            org_id=org_id,
            generated_at=datetime.now(),
            total_studies=len(studies),
            healthy_count=healthy_count,
            warning_count=warning_count,
            critical_count=critical_count,
            studies=studies,
            total_active_escalations=total_escalations,
            total_director_escalations=total_director,
            total_vp_escalations=total_vp,
            total_active_signals=total_signals,
            filters_applied=filters,
            sort_by=sort_by
        )

    def _get_study_summary(self, project_id: str, org_id: str) -> Optional[StudySummary]:
        """Get summary for a single study"""
        cursor = self.conn.cursor()

        # Get latest health snapshot
        cursor.execute("""
            SELECT
                overall_health_score, health_status,
                timeline_score, risk_score, tmf_score,
                active_escalations_count, director_escalations_count,
                vp_escalations_count, top_risks, created_at
            FROM study_health_snapshots
            WHERE project_id = ? AND org_id = ?
            ORDER BY snapshot_date DESC
            LIMIT 1
        """, (project_id, org_id))

        snapshot = cursor.fetchone()

        if not snapshot:
            logger.warning(f"No health snapshot for project {project_id}")
            return None

        # Get signal counts
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM signals
            WHERE project_id = ? AND status != 'resolved'
        """, (project_id,))
        active_signals = cursor.fetchone()['count']

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM signals
            WHERE project_id = ? AND signal_type LIKE 'risk_%' AND status = 'open'
        """, (project_id,))
        open_risks = cursor.fetchone()['count']

        # Get last tracker upload
        cursor.execute("""
            SELECT upload_timestamp
            FROM tracker_uploads
            WHERE project_id = ?
            ORDER BY upload_timestamp DESC
            LIMIT 1
        """, (project_id,))
        upload_row = cursor.fetchone()
        last_upload = upload_row['upload_timestamp'] if upload_row else None

        # Get top risk
        top_risks = json.loads(snapshot['top_risks']) if snapshot['top_risks'] else []
        top_risk_desc = top_risks[0].get('signal_description') if top_risks else None

        # Get critical milestone at risk
        cursor.execute("""
            SELECT affected_milestone_name
            FROM signal_timeline_correlations
            WHERE project_id = ? AND correlation_type = 'blocker' AND resolved_at IS NULL
            LIMIT 1
        """, (project_id,))
        milestone_row = cursor.fetchone()
        critical_milestone = milestone_row['affected_milestone_name'] if milestone_row else None

        return StudySummary(
            project_id=project_id,
            project_name=f"Study {project_id}",  # Would come from projects table
            org_id=org_id,
            health_score=snapshot['overall_health_score'],
            health_status=snapshot['health_status'],
            timeline_score=snapshot['timeline_score'],
            risk_score=snapshot['risk_score'],
            tmf_score=snapshot['tmf_score'],
            active_signals_count=active_signals,
            open_risks_count=open_risks,
            director_escalations_count=snapshot['director_escalations_count'],
            vp_escalations_count=snapshot['vp_escalations_count'],
            last_updated=snapshot['created_at'],
            last_tracker_upload=last_upload,
            top_risk_description=top_risk_desc,
            critical_milestone_at_risk=critical_milestone
        )

    def _passes_filters(self, summary: StudySummary, filters: Optional[Dict]) -> bool:
        """Check if study summary passes filters"""
        if not filters:
            return True

        # Filter by health status
        if 'status' in filters:
            allowed_statuses = filters['status']
            if isinstance(allowed_statuses, str):
                allowed_statuses = [allowed_statuses]
            if summary.health_status not in allowed_statuses:
                return False

        # Filter by minimum health score
        if 'min_health_score' in filters:
            if summary.health_score < filters['min_health_score']:
                return False

        # Filter by escalation level
        if 'has_escalations' in filters and filters['has_escalations']:
            if summary.director_escalations_count == 0 and summary.vp_escalations_count == 0:
                return False

        return True

    def _sort_studies(self, studies: List[StudySummary], sort_by: str) -> List[StudySummary]:
        """Sort studies by specified criteria"""
        if sort_by == "health_score_asc":
            return sorted(studies, key=lambda s: s.health_score)
        elif sort_by == "health_score_desc":
            return sorted(studies, key=lambda s: s.health_score, reverse=True)
        elif sort_by == "name":
            return sorted(studies, key=lambda s: s.project_name)
        elif sort_by == "last_updated":
            return sorted(studies, key=lambda s: s.last_updated, reverse=True)
        else:
            return studies

    def _get_cached_dashboard(
        self,
        org_id: str,
        filters: Optional[Dict],
        sort_by: str
    ) -> Optional[LeadershipDashboard]:
        """Get cached dashboard if available and not expired"""
        cursor = self.conn.cursor()

        filter_json = json.dumps(filters) if filters else None

        cursor.execute("""
            SELECT view_data, generated_at, expires_at
            FROM dashboard_views
            WHERE org_id = ? AND view_type = 'leadership_dashboard'
                AND filter_criteria = ? AND sort_criteria = ?
                AND (expires_at IS NULL OR datetime(expires_at) > datetime('now'))
            ORDER BY generated_at DESC
            LIMIT 1
        """, (org_id, filter_json, sort_by))

        row = cursor.fetchone()

        if row:
            view_data = json.loads(row['view_data'])
            # Reconstruct LeadershipDashboard from cached data
            # For simplicity, return None to force regeneration
            # In production, would properly deserialize
            return None

        return None

    def _cache_dashboard(
        self,
        org_id: str,
        dashboard: LeadershipDashboard,
        filters: Optional[Dict],
        sort_by: str,
        cache_minutes: int = 15
    ):
        """Cache dashboard data for faster subsequent requests"""
        import uuid

        cursor = self.conn.cursor()

        view_id = str(uuid.uuid4())
        view_data = json.dumps(asdict(dashboard), default=str)
        filter_json = json.dumps(filters) if filters else None
        expires_at = (datetime.now() + timedelta(minutes=cache_minutes)).isoformat()

        cursor.execute("""
            INSERT INTO dashboard_views (
                view_id, org_id, view_type, view_data,
                filter_criteria, sort_criteria, expires_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            view_id, org_id, 'leadership_dashboard', view_data,
            filter_json, sort_by, expires_at
        ))

        self.conn.commit()
        logger.info(f"Cached dashboard for org {org_id} (expires in {cache_minutes} min)")


def refresh_all_health_snapshots(conn: sqlite3.Connection):
    """
    Refresh health snapshots for all projects

    Should be run:
    - Daily (scheduled job)
    - After tracker upload
    - On-demand via API
    """
    from intelligence.health_score import HealthScoreCalculator, store_health_snapshot

    cursor = conn.cursor()

    # Get all projects with signals
    cursor.execute("""
        SELECT DISTINCT org_id, project_id
        FROM signals
    """)

    projects = cursor.fetchall()

    calculator = HealthScoreCalculator(conn)

    for project in projects:
        org_id = project['org_id']
        project_id = project['project_id']

        try:
            # Get signals
            cursor.execute("""
                SELECT signal_id, signal_type, signal_category, signal_description,
                       signal_detail, priority, status, date_identified, target_date,
                       escalation_level, escalation_notes
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

            # Calculate health score
            health_score = calculator.calculate_health_score(
                project_id,
                signals,
                correlations,
                None  # Timeline data would come from MS Project sync
            )

            # Store snapshot
            store_health_snapshot(conn, project_id, org_id, health_score)

            logger.info(f"Refreshed health snapshot for project {project_id}: {health_score.overall_score}")

        except Exception as e:
            logger.error(f"Failed to refresh health snapshot for project {project_id}: {e}")

    logger.info(f"Refreshed {len(projects)} health snapshots")
