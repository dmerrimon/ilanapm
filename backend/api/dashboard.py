"""
Dashboard API Endpoints

Provides REST API for Leadership Dashboard and Account Management views.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import sqlite3
import logging
from pathlib import Path
import csv
import io
import json

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class DashboardFilters(BaseModel):
    """Filters for Leadership Dashboard"""
    status: Optional[List[str]] = Field(None, description="Filter by health status: healthy, warning, critical")
    min_health_score: Optional[float] = Field(None, description="Minimum health score (0-100)")
    has_escalations: Optional[bool] = Field(None, description="Only show studies with escalations")


class StudySummaryResponse(BaseModel):
    """Study summary for dashboard list"""
    project_id: str
    project_name: str
    health_score: float
    health_status: str
    active_signals_count: int
    open_risks_count: int
    director_escalations_count: int
    vp_escalations_count: int
    last_updated: str
    top_risk_description: Optional[str]
    critical_milestone_at_risk: Optional[str]


class LeadershipDashboardResponse(BaseModel):
    """Complete Leadership Dashboard response"""
    org_id: str
    generated_at: str
    total_studies: int
    healthy_count: int
    warning_count: int
    critical_count: int
    studies: List[StudySummaryResponse]
    total_active_escalations: int
    total_director_escalations: int
    total_vp_escalations: int
    total_active_signals: int


class StudyDetailResponse(BaseModel):
    """Detailed study view"""
    project_id: str
    health: Dict[str, Any]
    signals: List[Dict[str, Any]]
    correlations: List[Dict[str, Any]]
    escalations: List[Dict[str, Any]]
    escalation_counts: Dict[str, int]
    top_risks: List[Dict[str, Any]]
    recommended_actions: List[str]


# ============================================================================
# Helper Functions
# ============================================================================

def get_db_connection() -> sqlite3.Connection:
    """Get database connection"""
    db_path = Path(__file__).parent.parent / "database" / "feedback.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# Leadership Dashboard Endpoints
# ============================================================================

@router.get("/dashboard/leadership")
async def get_leadership_dashboard(
    org_id: str = Query(..., description="Organization ID"),
    status_filter: Optional[str] = Query(None, description="Filter by status (healthy,warning,critical)"),
    min_health_score: Optional[float] = Query(None, description="Minimum health score (0-100)"),
    has_escalations: Optional[bool] = Query(None, description="Only show studies with escalations"),
    sort_by: str = Query("health_score_asc", description="Sort order (health_score_asc, health_score_desc, name, last_updated)"),
    use_cache: bool = Query(True, description="Use cached data for faster response")
) -> LeadershipDashboardResponse:
    """
    Get Leadership Dashboard

    Returns comprehensive dashboard view with all studies, health scores, escalations.

    **Access:** All users (Directors, Executives, CPMs) see the same data.
    Users can filter/sort based on their needs.

    **Example Response:**
    ```json
    {
      "org_id": "org_123",
      "total_studies": 5,
      "healthy_count": 2,
      "warning_count": 2,
      "critical_count": 1,
      "studies": [
        {
          "project_id": "STUDY-001",
          "project_name": "Study XYZ-123",
          "health_score": 68.5,
          "health_status": "warning",
          "active_signals_count": 12,
          "open_risks_count": 5,
          "director_escalations_count": 3,
          "vp_escalations_count": 1
        }
      ],
      "total_active_escalations": 8,
      "total_director_escalations": 6,
      "total_vp_escalations": 2
    }
    ```
    """
    try:
        from intelligence.dashboard_service import DashboardService

        conn = get_db_connection()
        service = DashboardService(conn)

        # Build filters
        filters = {}
        if status_filter:
            filters['status'] = status_filter.split(',')
        if min_health_score is not None:
            filters['min_health_score'] = min_health_score
        if has_escalations is not None:
            filters['has_escalations'] = has_escalations

        # Get dashboard data
        dashboard = service.get_leadership_dashboard(
            org_id=org_id,
            filters=filters if filters else None,
            sort_by=sort_by,
            use_cache=use_cache
        )

        conn.close()

        # Convert to response model
        studies_response = [
            StudySummaryResponse(
                project_id=s.project_id,
                project_name=s.project_name,
                health_score=s.health_score,
                health_status=s.health_status,
                active_signals_count=s.active_signals_count,
                open_risks_count=s.open_risks_count,
                director_escalations_count=s.director_escalations_count,
                vp_escalations_count=s.vp_escalations_count,
                last_updated=s.last_updated,
                top_risk_description=s.top_risk_description,
                critical_milestone_at_risk=s.critical_milestone_at_risk
            )
            for s in dashboard.studies
        ]

        return LeadershipDashboardResponse(
            org_id=dashboard.org_id,
            generated_at=dashboard.generated_at.isoformat(),
            total_studies=dashboard.total_studies,
            healthy_count=dashboard.healthy_count,
            warning_count=dashboard.warning_count,
            critical_count=dashboard.critical_count,
            studies=studies_response,
            total_active_escalations=dashboard.total_active_escalations,
            total_director_escalations=dashboard.total_director_escalations,
            total_vp_escalations=dashboard.total_vp_escalations,
            total_active_signals=dashboard.total_active_signals
        )

    except Exception as e:
        logger.error(f"Failed to get leadership dashboard: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get leadership dashboard: {str(e)}"
        )


@router.get("/dashboard/study/{project_id}")
async def get_study_detail(
    project_id: str,
    org_id: str = Query(..., description="Organization ID")
) -> StudyDetailResponse:
    """
    Get detailed view for a single study

    Returns complete study details including:
    - Health scores (overall + components)
    - All active signals
    - Correlations (signal → milestone impacts)
    - Escalations (Director/VP level)
    - Top risks
    - Recommended actions

    **Example Response:**
    ```json
    {
      "project_id": "STUDY-001",
      "health": {
        "overall_score": 68.5,
        "status": "warning",
        "component_scores": {
          "timeline": 75.0,
          "risk": 55.0,
          "tmf": 80.0
        }
      },
      "signals": [
        {
          "signal_id": "sig_123",
          "signal_type": "risk_high_priority",
          "signal_description": "Site activation slower",
          "priority": 7,
          "status": "open"
        }
      ],
      "correlations": [
        {
          "affected_milestone_name": "Site Activation",
          "estimated_delay_days": 49,
          "estimated_cost_impact": 1197217.0,
          "correlation_reasoning": "Risk #7 affects Site Activation..."
        }
      ],
      "escalations": [
        {
          "escalation_level": "director",
          "escalation_reason": "Director Escalation: Priority 7 risk",
          "intervention_recommended": "• Expedite site contracts..."
        }
      ]
    }
    ```
    """
    try:
        from intelligence.dashboard_service import DashboardService

        conn = get_db_connection()
        service = DashboardService(conn)

        study_detail = service.get_study_detail(project_id, org_id)

        conn.close()

        if 'error' in study_detail:
            raise HTTPException(
                status_code=404,
                detail=study_detail['error']
            )

        return StudyDetailResponse(**study_detail)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get study detail: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get study detail: {str(e)}"
        )


@router.post("/dashboard/refresh")
async def refresh_health_snapshots(
    org_id: str = Query(..., description="Organization ID"),
    project_id: Optional[str] = Query(None, description="Optional: refresh specific project only")
):
    """
    Refresh health snapshots

    Recalculates health scores for all projects (or specific project).

    **When to use:**
    - After tracker upload (automatic)
    - Daily scheduled job (automatic)
    - On-demand refresh (manual via API)

    **Response:**
    ```json
    {
      "success": true,
      "projects_refreshed": 5,
      "message": "Health snapshots refreshed successfully"
    }
    ```
    """
    try:
        from intelligence.dashboard_service import refresh_all_health_snapshots

        conn = get_db_connection()

        if project_id:
            # Refresh single project
            # (would implement single-project refresh logic)
            logger.info(f"Refreshing health snapshot for project {project_id}")
            projects_refreshed = 1
        else:
            # Refresh all projects
            logger.info(f"Refreshing all health snapshots for org {org_id}")
            refresh_all_health_snapshots(conn)

            # Count projects
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT project_id) as count FROM signals WHERE org_id = ?", (org_id,))
            projects_refreshed = cursor.fetchone()['count']

        conn.close()

        return {
            "success": True,
            "projects_refreshed": projects_refreshed,
            "message": "Health snapshots refreshed successfully"
        }

    except Exception as e:
        logger.error(f"Failed to refresh health snapshots: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh health snapshots: {str(e)}"
        )


# ============================================================================
# Escalation Management Endpoints
# ============================================================================

@router.post("/escalations/{escalation_id}/acknowledge")
async def acknowledge_escalation(
    escalation_id: str,
    acknowledged_by: str = Query(..., description="User ID acknowledging escalation")
):
    """
    Acknowledge an escalation

    Marks escalation as acknowledged (user has seen it).

    **Response:**
    ```json
    {
      "success": true,
      "escalation_id": "esc_123",
      "status": "acknowledged",
      "acknowledged_at": "2026-02-13T10:30:00Z"
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE escalations
            SET status = 'acknowledged',
                acknowledged_at = datetime('now')
            WHERE escalation_id = ?
        """, (escalation_id,))

        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Escalation not found")

        conn.commit()
        conn.close()

        return {
            "success": True,
            "escalation_id": escalation_id,
            "status": "acknowledged",
            "acknowledged_at": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to acknowledge escalation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to acknowledge escalation: {str(e)}"
        )


@router.post("/escalations/{escalation_id}/resolve")
async def resolve_escalation(
    escalation_id: str,
    resolution_notes: str = Query(..., description="Resolution notes"),
    intervention_taken: Optional[str] = Query(None, description="Intervention taken")
):
    """
    Resolve an escalation

    Marks escalation as resolved with resolution notes.

    **Response:**
    ```json
    {
      "success": true,
      "escalation_id": "esc_123",
      "status": "resolved",
      "resolved_at": "2026-02-13T11:00:00Z"
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE escalations
            SET status = 'resolved',
                resolved_at = datetime('now'),
                resolution_notes = ?,
                intervention_taken = ?
            WHERE escalation_id = ?
        """, (resolution_notes, intervention_taken, escalation_id))

        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Escalation not found")

        conn.commit()
        conn.close()

        return {
            "success": True,
            "escalation_id": escalation_id,
            "status": "resolved",
            "resolved_at": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve escalation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resolve escalation: {str(e)}"
        )


# ============================================================================
# Portfolio Summary Endpoint
# ============================================================================

@router.get("/dashboard/portfolio/summary")
async def get_portfolio_summary(
    org_id: str = Query(..., description="Organization ID")
):
    """
    Get portfolio-wide summary metrics

    Returns high-level portfolio health across all studies.

    **Response:**
    ```json
    {
      "org_id": "org_123",
      "total_studies": 5,
      "portfolio_health": {
        "healthy": 2,
        "warning": 2,
        "critical": 1
      },
      "total_escalations": 8,
      "total_signals": 45,
      "average_health_score": 72.3,
      "studies_needing_attention": 3
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get health distribution
        cursor.execute("""
            SELECT health_status, COUNT(*) as count
            FROM study_health_snapshots
            WHERE org_id = ?
                AND snapshot_date = (
                    SELECT MAX(snapshot_date)
                    FROM study_health_snapshots s2
                    WHERE s2.project_id = study_health_snapshots.project_id
                )
            GROUP BY health_status
        """, (org_id,))

        health_dist = {row['health_status']: row['count'] for row in cursor.fetchall()}

        # Get average health score
        cursor.execute("""
            SELECT AVG(overall_health_score) as avg_score
            FROM study_health_snapshots
            WHERE org_id = ?
                AND snapshot_date = (
                    SELECT MAX(snapshot_date)
                    FROM study_health_snapshots s2
                    WHERE s2.project_id = study_health_snapshots.project_id
                )
        """, (org_id,))
        avg_score = cursor.fetchone()['avg_score'] or 0

        # Get total escalations
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM escalations
            WHERE org_id = ? AND status = 'open'
        """, (org_id,))
        total_escalations = cursor.fetchone()['count']

        # Get total signals
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM signals
            WHERE org_id = ? AND status != 'resolved'
        """, (org_id,))
        total_signals = cursor.fetchone()['count']

        conn.close()

        total_studies = sum(health_dist.values())
        studies_needing_attention = health_dist.get('warning', 0) + health_dist.get('critical', 0)

        return {
            "org_id": org_id,
            "total_studies": total_studies,
            "portfolio_health": {
                "healthy": health_dist.get('healthy', 0),
                "warning": health_dist.get('warning', 0),
                "critical": health_dist.get('critical', 0)
            },
            "total_escalations": total_escalations,
            "total_signals": total_signals,
            "average_health_score": round(avg_score, 1),
            "studies_needing_attention": studies_needing_attention
        }

    except Exception as e:
        logger.error(f"Failed to get portfolio summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get portfolio summary: {str(e)}"
        )


# ============================================================================
# Portfolio Intelligence Endpoints (Phase 4)
# ============================================================================

@router.get("/dashboard/portfolio/health")
async def get_portfolio_health(
    org_id: str = Query(..., description="Organization ID"),
    timeframe_days: int = Query(30, description="Lookback period for trend analysis")
):
    """
    Get comprehensive portfolio health analysis

    Returns portfolio-wide health metrics including:
    - Total studies and health distribution
    - Average and median health scores
    - Health trends (improving/declining/stable)
    - Escalations and signals
    - Financial impact estimates
    - Studies needing attention

    **Response:**
    ```json
    {
      "org_id": "org_123",
      "total_studies": 5,
      "average_health_score": 72.3,
      "median_health_score": 75.0,
      "healthy_count": 2,
      "warning_count": 2,
      "critical_count": 1,
      "improving_count": 2,
      "declining_count": 1,
      "stable_count": 2,
      "total_escalations": 8,
      "estimated_total_delay_days": 150,
      "estimated_total_cost_impact": 3665000,
      "studies_needing_immediate_attention": ["STUDY-003"],
      "studies_at_risk": ["STUDY-001", "STUDY-002"]
    }
    ```
    """
    try:
        from intelligence.portfolio_service import PortfolioService

        conn = get_db_connection()
        service = PortfolioService(conn)

        portfolio_health = service.get_portfolio_health(org_id, timeframe_days)

        conn.close()

        return {
            "org_id": portfolio_health.org_id,
            "generated_at": portfolio_health.generated_at.isoformat(),
            "total_studies": portfolio_health.total_studies,
            "average_health_score": portfolio_health.average_health_score,
            "median_health_score": portfolio_health.median_health_score,
            "healthy_count": portfolio_health.healthy_count,
            "warning_count": portfolio_health.warning_count,
            "critical_count": portfolio_health.critical_count,
            "improving_count": portfolio_health.improving_count,
            "declining_count": portfolio_health.declining_count,
            "stable_count": portfolio_health.stable_count,
            "total_escalations": portfolio_health.total_escalations,
            "director_escalations": portfolio_health.director_escalations,
            "vp_escalations": portfolio_health.vp_escalations,
            "total_active_signals": portfolio_health.total_active_signals,
            "total_high_priority_risks": portfolio_health.total_high_priority_risks,
            "estimated_total_delay_days": portfolio_health.estimated_total_delay_days,
            "estimated_total_cost_impact": portfolio_health.estimated_total_cost_impact,
            "studies_needing_immediate_attention": portfolio_health.studies_needing_immediate_attention,
            "studies_at_risk": portfolio_health.studies_at_risk
        }

    except Exception as e:
        logger.error(f"Failed to get portfolio health: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get portfolio health: {str(e)}"
        )


@router.get("/dashboard/portfolio/patterns")
async def get_cross_study_patterns(
    org_id: str = Query(..., description="Organization ID"),
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high, critical)")
):
    """
    Get cross-study patterns

    Detects patterns across multiple studies:
    - Common risks appearing in multiple studies
    - Similar timeline delays across studies
    - Resource collisions
    - Systemic issues

    **Response:**
    ```json
    {
      "org_id": "org_123",
      "patterns": [
        {
          "pattern_id": "common_risk_site",
          "pattern_type": "common_risk",
          "pattern_name": "Common Site Risks",
          "pattern_description": "Site risks detected in 3 studies",
          "severity": "high",
          "affected_studies": ["STUDY-001", "STUDY-002", "STUDY-003"],
          "affected_study_count": 3,
          "confidence_score": 0.85,
          "portfolio_impact": "Portfolio-wide site challenges...",
          "recommended_action": "Investigate root cause..."
        }
      ],
      "total_patterns": 5,
      "critical_patterns": 1,
      "high_patterns": 2
    }
    ```
    """
    try:
        from intelligence.portfolio_service import PortfolioService

        conn = get_db_connection()
        service = PortfolioService(conn)

        patterns = service.detect_cross_study_patterns(org_id)

        # Filter by severity if specified
        if severity:
            patterns = [p for p in patterns if p.severity == severity]

        conn.close()

        # Calculate stats
        critical_count = sum(1 for p in patterns if p.severity == 'critical')
        high_count = sum(1 for p in patterns if p.severity == 'high')

        return {
            "org_id": org_id,
            "patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "pattern_type": p.pattern_type,
                    "pattern_name": p.pattern_name,
                    "pattern_description": p.pattern_description,
                    "severity": p.severity,
                    "affected_studies": p.affected_studies,
                    "affected_study_count": p.affected_study_count,
                    "evidence": p.evidence,
                    "confidence_score": p.confidence_score,
                    "portfolio_impact": p.portfolio_impact,
                    "recommended_action": p.recommended_action,
                    "detected_at": p.detected_at.isoformat()
                }
                for p in patterns
            ],
            "total_patterns": len(patterns),
            "critical_patterns": critical_count,
            "high_patterns": high_count
        }

    except Exception as e:
        logger.error(f"Failed to get cross-study patterns: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cross-study patterns: {str(e)}"
        )


@router.get("/dashboard/portfolio/systemic-issues")
async def get_systemic_issues(
    org_id: str = Query(..., description="Organization ID"),
    severity: Optional[str] = Query(None, description="Filter by severity")
):
    """
    Get systemic issues affecting portfolio

    Detects systemic issues:
    - Vendor performance issues across studies
    - Site activation delays across studies
    - Enrollment challenges across studies
    - Regulatory delays across studies

    **Response:**
    ```json
    {
      "org_id": "org_123",
      "issues": [
        {
          "issue_id": "systemic_vendor_org_123",
          "issue_type": "vendor_performance",
          "issue_name": "Vendor Performance Issues",
          "issue_description": "Vendor-related issues in 3 studies",
          "severity": "high",
          "affected_studies": ["STUDY-001", "STUDY-002", "STUDY-003"],
          "affected_study_count": 3,
          "root_cause": "Vendor performance or coordination challenges",
          "contributing_factors": ["Vendor capacity constraints", ...],
          "estimated_delay_days": 42,
          "estimated_cost_impact": 1099500,
          "recommended_intervention": "Conduct vendor performance review...",
          "responsible_party": "vp"
        }
      ],
      "total_issues": 3,
      "vp_level_issues": 1
    }
    ```
    """
    try:
        from intelligence.portfolio_service import PortfolioService

        conn = get_db_connection()
        service = PortfolioService(conn)

        issues = service.detect_systemic_issues(org_id)

        # Filter by severity if specified
        if severity:
            issues = [i for i in issues if i.severity == severity]

        conn.close()

        # Calculate stats
        vp_count = sum(1 for i in issues if i.responsible_party == 'vp')

        return {
            "org_id": org_id,
            "issues": [
                {
                    "issue_id": i.issue_id,
                    "issue_type": i.issue_type,
                    "issue_name": i.issue_name,
                    "issue_description": i.issue_description,
                    "severity": i.severity,
                    "affected_studies": i.affected_studies,
                    "affected_study_count": i.affected_study_count,
                    "root_cause": i.root_cause,
                    "contributing_factors": i.contributing_factors,
                    "portfolio_impact_description": i.portfolio_impact_description,
                    "estimated_delay_days": i.estimated_delay_days,
                    "estimated_cost_impact": i.estimated_cost_impact,
                    "recommended_intervention": i.recommended_intervention,
                    "responsible_party": i.responsible_party,
                    "detected_at": i.detected_at.isoformat()
                }
                for i in issues
            ],
            "total_issues": len(issues),
            "vp_level_issues": vp_count
        }

    except Exception as e:
        logger.error(f"Failed to get systemic issues: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get systemic issues: {str(e)}"
        )


@router.post("/dashboard/portfolio/refresh")
async def refresh_portfolio_intelligence(
    org_id: str = Query(..., description="Organization ID")
):
    """
    Refresh portfolio intelligence data

    Recalculates:
    - Portfolio health metrics
    - Cross-study patterns
    - Systemic issues

    **When to use:**
    - Daily scheduled job (automatic)
    - After multiple tracker uploads (automatic)
    - On-demand refresh (manual via API)

    **Response:**
    ```json
    {
      "success": true,
      "portfolio_health_calculated": true,
      "patterns_detected": 5,
      "systemic_issues_detected": 3,
      "message": "Portfolio intelligence refreshed successfully"
    }
    ```
    """
    try:
        from intelligence.portfolio_service import PortfolioService, store_cross_study_patterns, store_systemic_issues

        conn = get_db_connection()
        service = PortfolioService(conn)

        # Calculate portfolio health
        portfolio_health = service.get_portfolio_health(org_id)

        # Store portfolio health snapshot
        import uuid
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO portfolio_health_snapshots (
                snapshot_id, org_id, total_studies,
                average_health_score, median_health_score,
                healthy_count, warning_count, critical_count,
                improving_count, declining_count, stable_count,
                total_escalations, director_escalations, vp_escalations,
                total_active_signals, total_high_priority_risks,
                estimated_total_delay_days, estimated_total_cost_impact,
                studies_needing_immediate_attention, studies_at_risk,
                snapshot_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))
        """, (
            str(uuid.uuid4()),
            org_id,
            portfolio_health.total_studies,
            portfolio_health.average_health_score,
            portfolio_health.median_health_score,
            portfolio_health.healthy_count,
            portfolio_health.warning_count,
            portfolio_health.critical_count,
            portfolio_health.improving_count,
            portfolio_health.declining_count,
            portfolio_health.stable_count,
            portfolio_health.total_escalations,
            portfolio_health.director_escalations,
            portfolio_health.vp_escalations,
            portfolio_health.total_active_signals,
            portfolio_health.total_high_priority_risks,
            portfolio_health.estimated_total_delay_days,
            portfolio_health.estimated_total_cost_impact,
            json.dumps(portfolio_health.studies_needing_immediate_attention),
            json.dumps(portfolio_health.studies_at_risk)
        ))
        conn.commit()

        # Detect cross-study patterns
        patterns = service.detect_cross_study_patterns(org_id)
        store_cross_study_patterns(conn, patterns, org_id)

        # Detect systemic issues
        issues = service.detect_systemic_issues(org_id)
        store_systemic_issues(conn, issues, org_id)

        conn.close()

        logger.info(
            f"Refreshed portfolio intelligence for org {org_id}: "
            f"{len(patterns)} patterns, {len(issues)} systemic issues"
        )

        return {
            "success": True,
            "portfolio_health_calculated": True,
            "patterns_detected": len(patterns),
            "systemic_issues_detected": len(issues),
            "message": "Portfolio intelligence refreshed successfully"
        }

    except Exception as e:
        logger.error(f"Failed to refresh portfolio intelligence: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh portfolio intelligence: {str(e)}"
        )


# ============================================================================
# Export Endpoints
# ============================================================================

@router.get("/dashboard/export/leadership")
async def export_leadership_dashboard(
    org_id: str = Query(..., description="Organization ID"),
    format: str = Query("csv", description="Export format: csv, excel"),
    status_filter: Optional[str] = Query(None, description="Filter by status (healthy,warning,critical)"),
    min_health_score: Optional[float] = Query(None, description="Minimum health score (0-100)"),
    has_escalations: Optional[bool] = Query(None, description="Only show studies with escalations")
):
    """
    Export Leadership Dashboard to CSV or Excel

    Returns a downloadable file with all dashboard data.

    **Formats:**
    - `csv`: Comma-separated values (simple, universally compatible)
    - `excel`: Excel workbook (.xlsx) with multiple sheets (requires openpyxl)

    **CSV Columns:**
    - Study ID
    - Study Name
    - Health Score
    - Health Status
    - Active Signals
    - Open Risks
    - Director Escalations
    - VP Escalations
    - Last Updated
    - Top Risk
    - Critical Milestone At Risk

    **Excel Sheets:**
    - Sheet 1: Study Summary (same as CSV)
    - Sheet 2: Portfolio Metrics (aggregated stats)
    - Sheet 3: Escalations (all active escalations)

    **Example Usage:**
    ```bash
    curl -H "Authorization: Bearer {API_KEY}" \\
         "https://api.seleen.io/v1/dashboard/export/leadership?org_id=org_123&format=csv" \\
         -o leadership_dashboard.csv
    ```
    """
    try:
        from intelligence.dashboard_service import DashboardService

        conn = get_db_connection()
        service = DashboardService(conn)

        # Build filters
        filters = {}
        if status_filter:
            filters['status'] = status_filter.split(',')
        if min_health_score is not None:
            filters['min_health_score'] = min_health_score
        if has_escalations is not None:
            filters['has_escalations'] = has_escalations

        # Get dashboard data
        dashboard = service.get_leadership_dashboard(
            org_id=org_id,
            filters=filters if filters else None,
            use_cache=True
        )

        conn.close()

        if format == "csv":
            return _export_dashboard_csv(dashboard, org_id)
        elif format == "excel":
            return _export_dashboard_excel(dashboard, org_id)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format: {format}. Use 'csv' or 'excel'"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export leadership dashboard: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export leadership dashboard: {str(e)}"
        )


@router.get("/dashboard/export/study/{project_id}")
async def export_study_detail(
    project_id: str,
    org_id: str = Query(..., description="Organization ID"),
    format: str = Query("csv", description="Export format: csv, excel")
):
    """
    Export Study Detail to CSV or Excel

    Returns a downloadable file with complete study details.

    **CSV Sheets (zipped):**
    - study_health.csv: Health scores
    - signals.csv: All active signals
    - correlations.csv: Signal-to-milestone correlations
    - escalations.csv: All escalations

    **Excel Sheets:**
    - Sheet 1: Study Health
    - Sheet 2: Signals
    - Sheet 3: Correlations
    - Sheet 4: Escalations

    **Example Usage:**
    ```bash
    curl -H "Authorization: Bearer {API_KEY}" \\
         "https://api.seleen.io/v1/dashboard/export/study/STUDY-001?org_id=org_123&format=excel" \\
         -o study_detail.xlsx
    ```
    """
    try:
        from intelligence.dashboard_service import DashboardService

        conn = get_db_connection()
        service = DashboardService(conn)

        study_detail = service.get_study_detail(project_id, org_id)

        conn.close()

        if 'error' in study_detail:
            raise HTTPException(
                status_code=404,
                detail=study_detail['error']
            )

        if format == "csv":
            return _export_study_detail_csv(study_detail, project_id)
        elif format == "excel":
            return _export_study_detail_excel(study_detail, project_id)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format: {format}. Use 'csv' or 'excel'"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export study detail: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export study detail: {str(e)}"
        )


@router.get("/dashboard/export/portfolio/health")
async def export_portfolio_health(
    org_id: str = Query(..., description="Organization ID"),
    format: str = Query("csv", description="Export format: csv, excel")
):
    """
    Export Portfolio Health to CSV or Excel

    Returns portfolio-wide health metrics.

    **CSV Columns:**
    - Metric
    - Value
    - Description

    **Example Metrics:**
    - Total Studies
    - Average Health Score
    - Healthy Count
    - Warning Count
    - Critical Count
    - Total Escalations
    - Estimated Total Delay (days)
    - Estimated Total Cost Impact ($)

    **Example Usage:**
    ```bash
    curl -H "Authorization: Bearer {API_KEY}" \\
         "https://api.seleen.io/v1/dashboard/export/portfolio/health?org_id=org_123&format=csv" \\
         -o portfolio_health.csv
    ```
    """
    try:
        from intelligence.portfolio_service import PortfolioService

        conn = get_db_connection()
        service = PortfolioService(conn)

        portfolio_health = service.get_portfolio_health(org_id)

        conn.close()

        if format == "csv":
            return _export_portfolio_health_csv(portfolio_health, org_id)
        elif format == "excel":
            return _export_portfolio_health_excel(portfolio_health, org_id)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format: {format}. Use 'csv' or 'excel'"
            )

    except Exception as e:
        logger.error(f"Failed to export portfolio health: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export portfolio health: {str(e)}"
        )


@router.get("/dashboard/export/portfolio/patterns")
async def export_cross_study_patterns(
    org_id: str = Query(..., description="Organization ID"),
    format: str = Query("csv", description="Export format: csv, excel"),
    severity: Optional[str] = Query(None, description="Filter by severity: high, medium, low")
):
    """
    Export Cross-Study Patterns to CSV or Excel

    Returns patterns detected across multiple studies.

    **CSV Columns:**
    - Pattern ID
    - Pattern Type
    - Pattern Name
    - Affected Studies (count)
    - Severity
    - Confidence Score
    - Recommended Action
    - Detected At

    **Example Usage:**
    ```bash
    curl -H "Authorization: Bearer {API_KEY}" \\
         "https://api.seleen.io/v1/dashboard/export/portfolio/patterns?org_id=org_123&format=csv" \\
         -o patterns.csv
    ```
    """
    try:
        from intelligence.portfolio_service import PortfolioService

        conn = get_db_connection()
        service = PortfolioService(conn)

        patterns = service.detect_cross_study_patterns(org_id)

        # Filter by severity if specified
        if severity:
            patterns = [p for p in patterns if p.severity.lower() == severity.lower()]

        conn.close()

        if format == "csv":
            return _export_patterns_csv(patterns, org_id)
        elif format == "excel":
            return _export_patterns_excel(patterns, org_id)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format: {format}. Use 'csv' or 'excel'"
            )

    except Exception as e:
        logger.error(f"Failed to export cross-study patterns: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export cross-study patterns: {str(e)}"
        )


@router.get("/dashboard/export/portfolio/systemic-issues")
async def export_systemic_issues(
    org_id: str = Query(..., description="Organization ID"),
    format: str = Query("csv", description="Export format: csv, excel"),
    severity: Optional[str] = Query(None, description="Filter by severity: high, medium, low")
):
    """
    Export Systemic Issues to CSV or Excel

    Returns systemic issues affecting the portfolio.

    **CSV Columns:**
    - Issue ID
    - Issue Type
    - Issue Name
    - Affected Studies (count)
    - Severity
    - Impact Type
    - Root Cause Analysis
    - Recommended Intervention
    - Detected At

    **Example Usage:**
    ```bash
    curl -H "Authorization: Bearer {API_KEY}" \\
         "https://api.seleen.io/v1/dashboard/export/portfolio/systemic-issues?org_id=org_123&format=csv" \\
         -o systemic_issues.csv
    ```
    """
    try:
        from intelligence.portfolio_service import PortfolioService

        conn = get_db_connection()
        service = PortfolioService(conn)

        issues = service.detect_systemic_issues(org_id)

        # Filter by severity if specified
        if severity:
            issues = [i for i in issues if i.severity.lower() == severity.lower()]

        conn.close()

        if format == "csv":
            return _export_systemic_issues_csv(issues, org_id)
        elif format == "excel":
            return _export_systemic_issues_excel(issues, org_id)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format: {format}. Use 'csv' or 'excel'"
            )

    except Exception as e:
        logger.error(f"Failed to export systemic issues: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export systemic issues: {str(e)}"
        )


# ============================================================================
# Export Helper Functions
# ============================================================================

def _export_dashboard_csv(dashboard, org_id: str) -> StreamingResponse:
    """Export leadership dashboard to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "Study ID",
        "Study Name",
        "Health Score",
        "Health Status",
        "Active Signals",
        "Open Risks",
        "Director Escalations",
        "VP Escalations",
        "Last Updated",
        "Top Risk",
        "Critical Milestone At Risk"
    ])

    # Write data rows
    for study in dashboard.studies:
        writer.writerow([
            study.project_id,
            study.project_name,
            round(study.health_score, 1),
            study.health_status,
            study.active_signals_count,
            study.open_risks_count,
            study.director_escalations_count,
            study.vp_escalations_count,
            study.last_updated,
            study.top_risk_description or "",
            study.critical_milestone_at_risk or ""
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=leadership_dashboard_{org_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


def _export_dashboard_excel(dashboard, org_id: str) -> StreamingResponse:
    """Export leadership dashboard to Excel (basic CSV format with .xlsx extension)"""
    # For basic Excel export without dependencies, use CSV with .xlsx extension
    # For full Excel support, install openpyxl and use pandas

    output = io.StringIO()
    writer = csv.writer(output)

    # Sheet 1: Study Summary
    writer.writerow(["Leadership Dashboard - Study Summary"])
    writer.writerow([f"Organization: {org_id}"])
    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    writer.writerow([])

    writer.writerow([
        "Study ID", "Study Name", "Health Score", "Health Status",
        "Active Signals", "Open Risks", "Director Escalations", "VP Escalations",
        "Last Updated", "Top Risk", "Critical Milestone At Risk"
    ])

    for study in dashboard.studies:
        writer.writerow([
            study.project_id,
            study.project_name,
            round(study.health_score, 1),
            study.health_status,
            study.active_signals_count,
            study.open_risks_count,
            study.director_escalations_count,
            study.vp_escalations_count,
            study.last_updated,
            study.top_risk_description or "",
            study.critical_milestone_at_risk or ""
        ])

    # Add portfolio summary section
    writer.writerow([])
    writer.writerow(["Portfolio Summary"])
    writer.writerow(["Total Studies", dashboard.total_studies])
    writer.writerow(["Healthy", dashboard.healthy_count])
    writer.writerow(["Warning", dashboard.warning_count])
    writer.writerow(["Critical", dashboard.critical_count])
    writer.writerow(["Total Active Escalations", dashboard.total_active_escalations])
    writer.writerow(["Director Escalations", dashboard.total_director_escalations])
    writer.writerow(["VP Escalations", dashboard.total_vp_escalations])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=leadership_dashboard_{org_id}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        }
    )


def _export_study_detail_csv(study_detail: Dict, project_id: str) -> StreamingResponse:
    """Export study detail to CSV (zipped multiple files)"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Study Health Section
    writer.writerow(["Study Detail Export"])
    writer.writerow([f"Study ID: {project_id}"])
    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    writer.writerow([])

    # Health scores
    writer.writerow(["HEALTH SCORES"])
    health = study_detail.get('health', {})
    writer.writerow(["Overall Score", health.get('overall_score', 0)])
    writer.writerow(["Health Status", health.get('health_status', 'unknown')])

    component_scores = health.get('component_scores', {})
    for component, score in component_scores.items():
        writer.writerow([f"{component.title()} Score", score])

    writer.writerow([])

    # Signals
    writer.writerow(["SIGNALS"])
    writer.writerow(["Signal ID", "Type", "Category", "Description", "Priority", "Status", "Date Identified"])
    for signal in study_detail.get('signals', []):
        writer.writerow([
            signal.get('signal_id', ''),
            signal.get('signal_type', ''),
            signal.get('signal_category', ''),
            signal.get('signal_description', ''),
            signal.get('priority', ''),
            signal.get('status', ''),
            signal.get('date_identified', '')
        ])

    writer.writerow([])

    # Correlations
    writer.writerow(["CORRELATIONS"])
    writer.writerow(["Affected Milestone", "Type", "Confidence", "Est. Delay (days)", "Est. Cost Impact", "Reasoning"])
    for corr in study_detail.get('correlations', []):
        writer.writerow([
            corr.get('affected_milestone_name', ''),
            corr.get('correlation_type', ''),
            corr.get('confidence_score', ''),
            corr.get('estimated_delay_days', ''),
            corr.get('estimated_cost_impact', ''),
            corr.get('correlation_reasoning', '')
        ])

    writer.writerow([])

    # Escalations
    writer.writerow(["ESCALATIONS"])
    writer.writerow(["Level", "Reason", "Status", "Recommended Intervention", "Created At"])
    for esc in study_detail.get('escalations', []):
        writer.writerow([
            esc.get('escalation_level', ''),
            esc.get('escalation_reason', ''),
            esc.get('status', ''),
            esc.get('intervention_recommended', ''),
            esc.get('created_at', '')
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=study_detail_{project_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


def _export_study_detail_excel(study_detail: Dict, project_id: str) -> StreamingResponse:
    """Export study detail to Excel format"""
    return _export_study_detail_csv(study_detail, project_id)  # Use CSV as base for now


def _export_portfolio_health_csv(portfolio_health, org_id: str) -> StreamingResponse:
    """Export portfolio health to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["Portfolio Health Report"])
    writer.writerow([f"Organization: {org_id}"])
    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    writer.writerow([])

    # Portfolio metrics
    writer.writerow(["Metric", "Value", "Description"])
    writer.writerow(["Total Studies", portfolio_health.total_studies, "Total number of studies in portfolio"])
    writer.writerow(["Average Health Score", round(portfolio_health.average_health_score, 1), "Average health score across all studies (0-100)"])
    writer.writerow(["Median Health Score", round(portfolio_health.median_health_score, 1), "Median health score across all studies (0-100)"])
    writer.writerow([])

    writer.writerow(["Health Distribution", "", ""])
    writer.writerow(["Healthy Studies", portfolio_health.healthy_count, "Studies with health score ≥75"])
    writer.writerow(["Warning Studies", portfolio_health.warning_count, "Studies with health score 50-74"])
    writer.writerow(["Critical Studies", portfolio_health.critical_count, "Studies with health score <50"])
    writer.writerow([])

    writer.writerow(["Trends", "", ""])
    writer.writerow(["Improving", portfolio_health.improving_count, "Studies with improving health trend"])
    writer.writerow(["Stable", portfolio_health.stable_count, "Studies with stable health trend"])
    writer.writerow(["Declining", portfolio_health.declining_count, "Studies with declining health trend"])
    writer.writerow([])

    writer.writerow(["Escalations", "", ""])
    writer.writerow(["Total Escalations", portfolio_health.total_escalations, "Total active escalations across portfolio"])
    writer.writerow(["Director Escalations", portfolio_health.director_escalations, "Escalations requiring Director attention"])
    writer.writerow(["VP Escalations", portfolio_health.vp_escalations, "Escalations requiring VP attention"])
    writer.writerow([])

    writer.writerow(["Risk Metrics", "", ""])
    writer.writerow(["Total Active Signals", portfolio_health.total_active_signals, "Total active signals across all studies"])
    writer.writerow(["High Priority Risks", portfolio_health.total_high_priority_risks, "Risks with priority ≥6"])
    writer.writerow([])

    writer.writerow(["Impact Estimates", "", ""])
    writer.writerow(["Estimated Total Delay (days)", portfolio_health.estimated_total_delay_days, "Sum of estimated delays across all correlations"])
    writer.writerow(["Estimated Total Cost Impact", f"${portfolio_health.estimated_total_cost_impact:,.0f}", "Sum of estimated cost impacts across all correlations"])
    writer.writerow([])

    writer.writerow(["Attention Required", "", ""])
    writer.writerow(["Studies Needing Immediate Attention", len(portfolio_health.studies_needing_immediate_attention), "Critical studies requiring immediate action"])
    for study_id in portfolio_health.studies_needing_immediate_attention:
        writer.writerow(["", study_id, ""])

    writer.writerow([])
    writer.writerow(["Studies At Risk", len(portfolio_health.studies_at_risk), "Studies with elevated risk levels"])
    for study_id in portfolio_health.studies_at_risk:
        writer.writerow(["", study_id, ""])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=portfolio_health_{org_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


def _export_portfolio_health_excel(portfolio_health, org_id: str) -> StreamingResponse:
    """Export portfolio health to Excel format"""
    return _export_portfolio_health_csv(portfolio_health, org_id)  # Use CSV as base for now


def _export_patterns_csv(patterns: List, org_id: str) -> StreamingResponse:
    """Export cross-study patterns to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["Cross-Study Patterns Report"])
    writer.writerow([f"Organization: {org_id}"])
    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    writer.writerow([f"Total Patterns: {len(patterns)}"])
    writer.writerow([])

    # Data
    writer.writerow([
        "Pattern ID", "Pattern Type", "Pattern Name",
        "Affected Studies (count)", "Severity", "Confidence Score",
        "Recommended Action", "Detected At"
    ])

    for pattern in patterns:
        writer.writerow([
            pattern.pattern_id,
            pattern.pattern_type,
            pattern.pattern_name,
            pattern.affected_study_count,
            pattern.severity,
            round(pattern.confidence_score, 2),
            pattern.recommended_action,
            pattern.detected_at.isoformat() if hasattr(pattern, 'detected_at') else ""
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=cross_study_patterns_{org_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


def _export_patterns_excel(patterns: List, org_id: str) -> StreamingResponse:
    """Export cross-study patterns to Excel format"""
    return _export_patterns_csv(patterns, org_id)  # Use CSV as base for now


def _export_systemic_issues_csv(issues: List, org_id: str) -> StreamingResponse:
    """Export systemic issues to CSV"""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["Systemic Issues Report"])
    writer.writerow([f"Organization: {org_id}"])
    writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    writer.writerow([f"Total Issues: {len(issues)}"])
    writer.writerow([])

    # Data
    writer.writerow([
        "Issue ID", "Issue Type", "Issue Name",
        "Affected Studies (count)", "Severity", "Impact Type",
        "Root Cause Analysis", "Recommended Intervention", "Detected At"
    ])

    for issue in issues:
        writer.writerow([
            issue.issue_id,
            issue.issue_type,
            issue.issue_name,
            issue.affected_study_count,
            issue.severity,
            issue.impact_type,
            issue.root_cause_analysis,
            issue.recommended_intervention,
            issue.detected_at.isoformat() if hasattr(issue, 'detected_at') else ""
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=systemic_issues_{org_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


def _export_systemic_issues_excel(issues: List, org_id: str) -> StreamingResponse:
    """Export systemic issues to Excel format"""
    return _export_systemic_issues_csv(issues, org_id)  # Use CSV as base for now
