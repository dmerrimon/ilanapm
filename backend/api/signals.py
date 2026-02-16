"""
Signal and Escalation Retrieval Endpoints

Provides REST API for retrieving signals, escalations, and health data
after tracker uploads.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import sqlite3
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class TrackerUploadSummary(BaseModel):
    """Summary of a tracker upload"""
    upload_id: str
    tracker_type: str
    uploaded_by: str
    upload_timestamp: str
    original_filename: str
    rows_parsed: int
    signals_extracted: int
    parse_status: str


class SignalDetail(BaseModel):
    """Detailed signal information"""
    signal_id: str
    upload_id: str
    signal_type: str
    signal_category: Optional[str]
    signal_source: str
    signal_description: str
    priority: int
    status: str
    date_identified: str
    escalation_level: Optional[str]
    created_at: str


class EscalationDetail(BaseModel):
    """Detailed escalation information"""
    escalation_id: str
    trigger_type: str
    escalation_level: str
    escalation_reason: str
    priority: int
    status: str
    intervention_recommended: str
    created_at: str


class HealthSnapshot(BaseModel):
    """Health score snapshot"""
    snapshot_id: str
    overall_health_score: float
    health_status: str
    snapshot_date: str
    active_escalations_count: int
    director_escalations_count: int
    vp_escalations_count: int


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
# Tracker Upload Endpoints
# ============================================================================

@router.get("/trackers/uploads")
async def list_tracker_uploads(
    org_id: str = Query(..., description="Organization ID"),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    tracker_type: Optional[str] = Query(None, description="Filter by tracker type"),
    limit: int = Query(50, description="Max results to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """
    List tracker upload history

    Returns list of tracker uploads with metadata and summary stats.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query with filters
        query = """
            SELECT
                u.upload_id,
                u.project_id,
                u.tracker_def_id as tracker_type,
                u.uploaded_by,
                u.upload_timestamp,
                u.original_filename,
                u.rows_parsed,
                u.parse_status,
                COUNT(DISTINCT s.signal_id) as signals_extracted
            FROM tracker_uploads u
            LEFT JOIN signals s ON u.upload_id = s.upload_id
            WHERE u.org_id = ?
        """

        params = [org_id]

        if project_id:
            query += " AND u.project_id = ?"
            params.append(project_id)

        if tracker_type:
            query += " AND u.tracker_def_id = ?"
            params.append(tracker_type)

        query += """
            GROUP BY u.upload_id
            ORDER BY u.upload_timestamp DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        cursor.execute(query, params)
        uploads = [dict(row) for row in cursor.fetchall()]

        # Get total count
        count_query = "SELECT COUNT(*) as total FROM tracker_uploads WHERE org_id = ?"
        count_params = [org_id]

        if project_id:
            count_query += " AND project_id = ?"
            count_params.append(project_id)

        if tracker_type:
            count_query += " AND tracker_def_id = ?"
            count_params.append(tracker_type)

        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']

        conn.close()

        return {
            "uploads": uploads,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Failed to list tracker uploads: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trackers/uploads/{upload_id}")
async def get_tracker_upload(
    upload_id: str,
    org_id: str = Query(..., description="Organization ID")
):
    """
    Get details of a specific tracker upload

    Returns upload metadata and summary of extracted signals.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get upload details
        cursor.execute("""
            SELECT
                upload_id,
                project_id,
                tracker_def_id as tracker_type,
                uploaded_by,
                upload_timestamp,
                original_filename,
                rows_parsed,
                parse_status,
                parse_errors
            FROM tracker_uploads
            WHERE upload_id = ? AND org_id = ?
        """, (upload_id, org_id))

        upload = cursor.fetchone()
        if not upload:
            conn.close()
            raise HTTPException(status_code=404, detail="Upload not found")

        upload_dict = dict(upload)

        # Get signal counts by type
        cursor.execute("""
            SELECT
                signal_type,
                COUNT(*) as count,
                AVG(priority) as avg_priority
            FROM signals
            WHERE upload_id = ?
            GROUP BY signal_type
        """, (upload_id,))

        signal_summary = [dict(row) for row in cursor.fetchall()]

        # Get escalation counts
        cursor.execute("""
            SELECT
                escalation_level,
                COUNT(*) as count
            FROM escalations
            WHERE trigger_type = 'signal'
            AND trigger_id IN (SELECT signal_id FROM signals WHERE upload_id = ?)
            GROUP BY escalation_level
        """, (upload_id,))

        escalation_summary = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return {
            **upload_dict,
            "signal_summary": signal_summary,
            "escalation_summary": escalation_summary
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tracker upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Signal Endpoints
# ============================================================================

@router.get("/signals")
async def list_signals(
    org_id: str = Query(..., description="Organization ID"),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    signal_type: Optional[str] = Query(None, description="Filter by signal type"),
    status: Optional[str] = Query(None, description="Filter by status (open, acknowledged, resolved)"),
    priority_min: Optional[int] = Query(None, description="Minimum priority"),
    escalation_level: Optional[str] = Query(None, description="Filter by escalation level"),
    limit: int = Query(50, description="Max results to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """
    List signals with filtering and pagination

    Returns signals extracted from tracker uploads.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query with filters
        query = """
            SELECT
                signal_id,
                upload_id,
                project_id,
                signal_type,
                signal_category,
                signal_source,
                signal_description,
                priority,
                status,
                date_identified,
                escalation_level,
                created_at
            FROM signals
            WHERE org_id = ?
        """

        params = [org_id]

        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)

        if signal_type:
            query += " AND signal_type = ?"
            params.append(signal_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        if priority_min is not None:
            query += " AND priority >= ?"
            params.append(priority_min)

        if escalation_level:
            query += " AND escalation_level = ?"
            params.append(escalation_level)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        signals = [dict(row) for row in cursor.fetchall()]

        # Get total count
        count_query = "SELECT COUNT(*) as total FROM signals WHERE org_id = ?"
        count_params = [org_id]

        if project_id:
            count_query += " AND project_id = ?"
            count_params.append(project_id)

        if signal_type:
            count_query += " AND signal_type = ?"
            count_params.append(signal_type)

        if status:
            count_query += " AND status = ?"
            count_params.append(status)

        if priority_min is not None:
            count_query += " AND priority >= ?"
            count_params.append(priority_min)

        if escalation_level:
            count_query += " AND escalation_level = ?"
            count_params.append(escalation_level)

        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']

        conn.close()

        return {
            "signals": signals,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Failed to list signals: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals/{signal_id}")
async def get_signal(
    signal_id: str,
    org_id: str = Query(..., description="Organization ID")
):
    """
    Get details of a specific signal
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM signals
            WHERE signal_id = ? AND org_id = ?
        """, (signal_id, org_id))

        signal = cursor.fetchone()
        if not signal:
            conn.close()
            raise HTTPException(status_code=404, detail="Signal not found")

        conn.close()

        return dict(signal)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get signal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Escalation Endpoints
# ============================================================================

@router.get("/escalations")
async def list_escalations(
    org_id: str = Query(..., description="Organization ID"),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    escalation_level: Optional[str] = Query(None, description="Filter by level (director, vp)"),
    status: Optional[str] = Query(None, description="Filter by status (open, acknowledged, resolved)"),
    limit: int = Query(50, description="Max results to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """
    List escalations with filtering and pagination
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                escalation_id,
                project_id,
                trigger_type,
                trigger_id,
                escalation_level,
                escalation_reason,
                priority,
                status,
                intervention_recommended,
                created_at,
                acknowledged_at,
                resolved_at
            FROM escalations
            WHERE org_id = ?
        """

        params = [org_id]

        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)

        if escalation_level:
            query += " AND escalation_level = ?"
            params.append(escalation_level)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        escalations = [dict(row) for row in cursor.fetchall()]

        # Get total count
        count_query = "SELECT COUNT(*) as total FROM escalations WHERE org_id = ?"
        count_params = [org_id]

        if project_id:
            count_query += " AND project_id = ?"
            count_params.append(project_id)

        if escalation_level:
            count_query += " AND escalation_level = ?"
            count_params.append(escalation_level)

        if status:
            count_query += " AND status = ?"
            count_params.append(status)

        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']

        conn.close()

        return {
            "escalations": escalations,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Failed to list escalations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health Score Endpoints
# ============================================================================

@router.get("/health/history")
async def get_health_history(
    org_id: str = Query(..., description="Organization ID"),
    project_id: str = Query(..., description="Project ID"),
    limit: int = Query(30, description="Max snapshots to return")
):
    """
    Get health score history for a project

    Returns time-series health score data for trending.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                snapshot_id,
                overall_health_score,
                health_status,
                timeline_score,
                risk_score,
                tmf_score,
                enrollment_score,
                budget_score,
                vendor_score,
                active_escalations_count,
                director_escalations_count,
                vp_escalations_count,
                snapshot_date,
                created_at
            FROM study_health_snapshots
            WHERE org_id = ? AND project_id = ?
            ORDER BY snapshot_date DESC
            LIMIT ?
        """, (org_id, project_id, limit))

        snapshots = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return {
            "project_id": project_id,
            "snapshots": snapshots,
            "count": len(snapshots)
        }

    except Exception as e:
        logger.error(f"Failed to get health history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects")
async def list_projects(
    org_id: str = Query(..., description="Organization ID")
):
    """
    List all projects for an organization with latest health scores

    Returns project list with current health status.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get unique projects with latest health scores
        cursor.execute("""
            SELECT DISTINCT
                u.project_id,
                COUNT(DISTINCT u.upload_id) as upload_count,
                COUNT(DISTINCT s.signal_id) as signal_count,
                COUNT(DISTINCT e.escalation_id) as escalation_count,
                MAX(u.upload_timestamp) as last_upload
            FROM tracker_uploads u
            LEFT JOIN signals s ON u.upload_id = s.upload_id
            LEFT JOIN escalations e ON u.project_id = e.project_id AND e.status = 'open'
            WHERE u.org_id = ?
            GROUP BY u.project_id
            ORDER BY last_upload DESC
        """, (org_id,))

        projects = [dict(row) for row in cursor.fetchall()]

        # Get latest health score for each project
        for project in projects:
            cursor.execute("""
                SELECT overall_health_score, health_status
                FROM study_health_snapshots
                WHERE org_id = ? AND project_id = ?
                ORDER BY snapshot_date DESC
                LIMIT 1
            """, (org_id, project['project_id']))

            health = cursor.fetchone()
            if health:
                project['health_score'] = health['overall_health_score']
                project['health_status'] = health['health_status']
            else:
                project['health_score'] = None
                project['health_status'] = 'unknown'

        conn.close()

        return {
            "projects": projects,
            "total": len(projects)
        }

    except Exception as e:
        logger.error(f"Failed to list projects: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Signal Management Endpoints
# ============================================================================

@router.patch("/signals/{signal_id}/status")
async def update_signal_status(
    signal_id: str,
    org_id: str = Query(..., description="Organization ID"),
    status: str = Query(..., description="New status (open, acknowledged, resolved)"),
    updated_by: str = Query(..., description="User ID making the update")
):
    """
    Update signal status

    Allowed transitions:
    - open → acknowledged
    - open → resolved
    - acknowledged → resolved
    """
    try:
        if status not in ['open', 'acknowledged', 'resolved']:
            raise HTTPException(status_code=400, detail="Invalid status")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify signal exists and belongs to org
        cursor.execute("""
            SELECT status FROM signals
            WHERE signal_id = ? AND org_id = ?
        """, (signal_id, org_id))

        signal = cursor.fetchone()
        if not signal:
            conn.close()
            raise HTTPException(status_code=404, detail="Signal not found")

        # Update status
        cursor.execute("""
            UPDATE signals
            SET status = ?, updated_at = datetime('now'), updated_by = ?
            WHERE signal_id = ? AND org_id = ?
        """, (status, updated_by, signal_id, org_id))

        conn.commit()
        conn.close()

        logger.info(f"Signal {signal_id} status updated to {status} by {updated_by}")

        return {
            "success": True,
            "signal_id": signal_id,
            "status": status
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update signal status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/signals/{signal_id}/assign")
async def assign_signal(
    signal_id: str,
    org_id: str = Query(..., description="Organization ID"),
    assigned_to: str = Query(..., description="User ID to assign to"),
    assigned_by: str = Query(..., description="User ID making the assignment")
):
    """
    Assign signal to a user
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify signal exists and belongs to org
        cursor.execute("""
            SELECT signal_id FROM signals
            WHERE signal_id = ? AND org_id = ?
        """, (signal_id, org_id))

        signal = cursor.fetchone()
        if not signal:
            conn.close()
            raise HTTPException(status_code=404, detail="Signal not found")

        # Update assignment
        cursor.execute("""
            UPDATE signals
            SET assigned_to = ?, updated_at = datetime('now'), updated_by = ?
            WHERE signal_id = ? AND org_id = ?
        """, (assigned_to, assigned_by, signal_id, org_id))

        conn.commit()
        conn.close()

        logger.info(f"Signal {signal_id} assigned to {assigned_to} by {assigned_by}")

        return {
            "success": True,
            "signal_id": signal_id,
            "assigned_to": assigned_to
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign signal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Escalation Management Endpoints
# ============================================================================

@router.patch("/escalations/{escalation_id}/acknowledge")
async def acknowledge_escalation(
    escalation_id: str,
    org_id: str = Query(..., description="Organization ID"),
    acknowledged_by: str = Query(..., description="User ID acknowledging"),
    notes: Optional[str] = Query(None, description="Acknowledgment notes")
):
    """
    Acknowledge escalation

    Transitions status from 'open' to 'acknowledged'
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify escalation exists and belongs to org
        cursor.execute("""
            SELECT status FROM escalations
            WHERE escalation_id = ? AND org_id = ?
        """, (escalation_id, org_id))

        escalation = cursor.fetchone()
        if not escalation:
            conn.close()
            raise HTTPException(status_code=404, detail="Escalation not found")

        if escalation['status'] != 'open':
            conn.close()
            raise HTTPException(status_code=400, detail="Can only acknowledge open escalations")

        # Update status
        cursor.execute("""
            UPDATE escalations
            SET status = 'acknowledged',
                acknowledged_at = datetime('now'),
                acknowledged_by = ?,
                acknowledgment_notes = ?
            WHERE escalation_id = ? AND org_id = ?
        """, (acknowledged_by, notes, escalation_id, org_id))

        conn.commit()
        conn.close()

        logger.info(f"Escalation {escalation_id} acknowledged by {acknowledged_by}")

        return {
            "success": True,
            "escalation_id": escalation_id,
            "status": "acknowledged"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to acknowledge escalation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/escalations/{escalation_id}/resolve")
async def resolve_escalation(
    escalation_id: str,
    org_id: str = Query(..., description="Organization ID"),
    resolved_by: str = Query(..., description="User ID resolving"),
    resolution_notes: str = Query(..., description="Resolution notes")
):
    """
    Resolve escalation

    Transitions status to 'resolved'
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify escalation exists and belongs to org
        cursor.execute("""
            SELECT status FROM escalations
            WHERE escalation_id = ? AND org_id = ?
        """, (escalation_id, org_id))

        escalation = cursor.fetchone()
        if not escalation:
            conn.close()
            raise HTTPException(status_code=404, detail="Escalation not found")

        if escalation['status'] == 'resolved':
            conn.close()
            raise HTTPException(status_code=400, detail="Escalation already resolved")

        # Update status
        cursor.execute("""
            UPDATE escalations
            SET status = 'resolved',
                resolved_at = datetime('now'),
                resolved_by = ?,
                resolution_notes = ?
            WHERE escalation_id = ? AND org_id = ?
        """, (resolved_by, resolution_notes, escalation_id, org_id))

        conn.commit()
        conn.close()

        logger.info(f"Escalation {escalation_id} resolved by {resolved_by}")

        return {
            "success": True,
            "escalation_id": escalation_id,
            "status": "resolved"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve escalation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
