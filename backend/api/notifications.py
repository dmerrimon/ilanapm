"""
Notification API Endpoints

Provides REST API for notification management:
- Get user notifications
- Mark notifications as read
- Update notification preferences
- Get notification history
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class NotificationPreferencesRequest(BaseModel):
    """Request to update notification preferences"""
    notify_director_escalations: bool = Field(True, description="Notify on Director escalations")
    notify_vp_escalations: bool = Field(True, description="Notify on VP escalations")
    notify_signal_detected: bool = Field(False, description="Notify on signal detection")
    notify_pattern_detected: bool = Field(True, description="Notify on pattern detection")
    notify_health_critical: bool = Field(True, description="Notify on critical health status")
    digest_mode: str = Field("immediate", description="Digest mode: immediate, daily, weekly")


class NotificationResponse(BaseModel):
    """Notification object"""
    notification_id: str
    notification_type: str
    subject: str
    body_text: str
    related_entity_id: str
    related_entity_type: str
    priority: str
    status: str
    created_at: str
    sent_at: Optional[str]


class NotificationListResponse(BaseModel):
    """List of notifications"""
    notifications: List[NotificationResponse]
    total_count: int
    unread_count: int


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
# Notification Endpoints
# ============================================================================

@router.get("/notifications")
async def list_notifications(
    user_id: str = Query(..., description="User ID"),
    status: Optional[str] = Query(None, description="Filter by status (pending, sent)"),
    notification_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(50, description="Number of notifications to return"),
    offset: int = Query(0, description="Offset for pagination")
) -> NotificationListResponse:
    """
    Get user notifications

    Returns list of notifications for a user, with optional filters.

    **Response:**
    ```json
    {
      "notifications": [
        {
          "notification_id": "notif_123",
          "notification_type": "escalation",
          "subject": "[DIRECTOR ESCALATION] Study XYZ-123",
          "body_text": "A Director-level escalation...",
          "priority": "high",
          "status": "sent",
          "created_at": "2026-02-13T10:30:00Z"
        }
      ],
      "total_count": 23,
      "unread_count": 5
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Build WHERE clause
        where_clauses = ["recipient_user_id = ?"]
        params = [user_id]

        if status:
            where_clauses.append("status = ?")
            params.append(status)

        if notification_type:
            where_clauses.append("notification_type = ?")
            params.append(notification_type)

        where_clause = " AND ".join(where_clauses)

        # Get total count
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM notifications
            WHERE {where_clause}
        """, params)
        total_count = cursor.fetchone()['count']

        # Get unread count
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM notifications
            WHERE recipient_user_id = ? AND status = 'pending'
        """, (user_id,))
        unread_count = cursor.fetchone()['count']

        # Get notifications
        cursor.execute(f"""
            SELECT
                notification_id, notification_type, subject, body_text,
                related_entity_id, related_entity_type,
                priority, status, created_at, sent_at
            FROM notifications
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (*params, limit, offset))

        notifications = []
        for row in cursor.fetchall():
            notifications.append(NotificationResponse(
                notification_id=row['notification_id'],
                notification_type=row['notification_type'],
                subject=row['subject'],
                body_text=row['body_text'],
                related_entity_id=row['related_entity_id'],
                related_entity_type=row['related_entity_type'],
                priority=row['priority'],
                status=row['status'],
                created_at=row['created_at'],
                sent_at=row['sent_at']
            ))

        conn.close()

        return NotificationListResponse(
            notifications=notifications,
            total_count=total_count,
            unread_count=unread_count
        )

    except Exception as e:
        logger.error(f"Failed to get notifications: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get notifications: {str(e)}"
        )


@router.get("/notifications/{notification_id}")
async def get_notification(notification_id: str):
    """
    Get single notification by ID

    Returns full notification details including HTML body.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                notification_id, notification_type, recipient_user_id,
                recipient_email, subject, body_html, body_text,
                related_entity_id, related_entity_type,
                priority, status, created_at, sent_at, error_message
            FROM notifications
            WHERE notification_id = ?
        """, (notification_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Notification not found")

        return {
            "notification_id": row['notification_id'],
            "notification_type": row['notification_type'],
            "recipient_user_id": row['recipient_user_id'],
            "recipient_email": row['recipient_email'],
            "subject": row['subject'],
            "body_html": row['body_html'],
            "body_text": row['body_text'],
            "related_entity_id": row['related_entity_id'],
            "related_entity_type": row['related_entity_type'],
            "priority": row['priority'],
            "status": row['status'],
            "created_at": row['created_at'],
            "sent_at": row['sent_at'],
            "error_message": row['error_message']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get notification: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get notification: {str(e)}"
        )


@router.post("/notifications/{notification_id}/mark-read")
async def mark_notification_read(notification_id: str):
    """
    Mark notification as read

    Updates notification status to 'sent' to indicate user has seen it.

    **Response:**
    ```json
    {
      "success": true,
      "notification_id": "notif_123",
      "status": "sent"
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notifications
            SET status = 'sent'
            WHERE notification_id = ? AND status = 'pending'
        """, (notification_id,))

        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(
                status_code=404,
                detail="Notification not found or already read"
            )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "notification_id": notification_id,
            "status": "sent"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to mark notification as read: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark notification as read: {str(e)}"
        )


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(user_id: str = Query(..., description="User ID")):
    """
    Mark all user notifications as read

    **Response:**
    ```json
    {
      "success": true,
      "marked_count": 12
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notifications
            SET status = 'sent'
            WHERE recipient_user_id = ? AND status = 'pending'
        """, (user_id,))

        marked_count = cursor.rowcount

        conn.commit()
        conn.close()

        return {
            "success": True,
            "marked_count": marked_count
        }

    except Exception as e:
        logger.error(f"Failed to mark all notifications as read: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )


@router.get("/notifications/preferences")
async def get_notification_preferences(user_id: str = Query(..., description="User ID")):
    """
    Get user notification preferences

    **Response:**
    ```json
    {
      "user_id": "user_123",
      "notify_director_escalations": true,
      "notify_vp_escalations": true,
      "notify_signal_detected": false,
      "notify_pattern_detected": true,
      "notify_health_critical": true,
      "digest_mode": "immediate"
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT notification_preferences
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="User not found")

        # Parse preferences or return defaults
        if row['notification_preferences']:
            prefs = json.loads(row['notification_preferences'])
        else:
            # Default preferences
            prefs = {
                "notify_director_escalations": True,
                "notify_vp_escalations": True,
                "notify_signal_detected": False,
                "notify_pattern_detected": True,
                "notify_health_critical": True,
                "digest_mode": "immediate"
            }

        return {
            "user_id": user_id,
            **prefs
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get notification preferences: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get notification preferences: {str(e)}"
        )


@router.post("/notifications/preferences")
async def update_notification_preferences(
    user_id: str = Query(..., description="User ID"),
    preferences: NotificationPreferencesRequest = None
):
    """
    Update user notification preferences

    **Request Body:**
    ```json
    {
      "notify_director_escalations": true,
      "notify_vp_escalations": true,
      "notify_signal_detected": false,
      "notify_pattern_detected": true,
      "notify_health_critical": true,
      "digest_mode": "immediate"
    }
    ```

    **Response:**
    ```json
    {
      "success": true,
      "message": "Notification preferences updated"
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Convert preferences to JSON
        prefs_dict = {
            "notify_director_escalations": preferences.notify_director_escalations,
            "notify_vp_escalations": preferences.notify_vp_escalations,
            "notify_signal_detected": preferences.notify_signal_detected,
            "notify_pattern_detected": preferences.notify_pattern_detected,
            "notify_health_critical": preferences.notify_health_critical,
            "digest_mode": preferences.digest_mode
        }

        prefs_json = json.dumps(prefs_dict)

        cursor.execute("""
            UPDATE users
            SET notification_preferences = ?
            WHERE user_id = ?
        """, (prefs_json, user_id))

        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="User not found")

        conn.commit()
        conn.close()

        logger.info(f"Updated notification preferences for user {user_id}")

        return {
            "success": True,
            "message": "Notification preferences updated"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update notification preferences: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update notification preferences: {str(e)}"
        )


@router.get("/notifications/stats")
async def get_notification_stats(user_id: str = Query(..., description="User ID")):
    """
    Get notification statistics

    Returns counts by type, status, etc.

    **Response:**
    ```json
    {
      "total_notifications": 45,
      "unread_count": 5,
      "by_type": {
        "escalation": 23,
        "pattern": 12,
        "health_alert": 10
      },
      "by_priority": {
        "high": 15,
        "medium": 20,
        "low": 10
      }
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total notifications
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM notifications
            WHERE recipient_user_id = ?
        """, (user_id,))
        total_count = cursor.fetchone()['count']

        # Unread count
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM notifications
            WHERE recipient_user_id = ? AND status = 'pending'
        """, (user_id,))
        unread_count = cursor.fetchone()['count']

        # By type
        cursor.execute("""
            SELECT notification_type, COUNT(*) as count
            FROM notifications
            WHERE recipient_user_id = ?
            GROUP BY notification_type
        """, (user_id,))
        by_type = {row['notification_type']: row['count'] for row in cursor.fetchall()}

        # By priority
        cursor.execute("""
            SELECT priority, COUNT(*) as count
            FROM notifications
            WHERE recipient_user_id = ?
            GROUP BY priority
        """, (user_id,))
        by_priority = {row['priority']: row['count'] for row in cursor.fetchall()}

        conn.close()

        return {
            "total_notifications": total_count,
            "unread_count": unread_count,
            "by_type": by_type,
            "by_priority": by_priority
        }

    except Exception as e:
        logger.error(f"Failed to get notification stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get notification stats: {str(e)}"
        )


@router.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: str):
    """
    Delete notification

    **Response:**
    ```json
    {
      "success": true,
      "notification_id": "notif_123"
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM notifications
            WHERE notification_id = ?
        """, (notification_id,))

        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Notification not found")

        conn.commit()
        conn.close()

        return {
            "success": True,
            "notification_id": notification_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete notification: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete notification: {str(e)}"
        )
