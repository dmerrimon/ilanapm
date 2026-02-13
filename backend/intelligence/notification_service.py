"""
Notification Service

Handles notifications for escalations and other intelligence events:
- Email notifications when escalations are created
- Configurable notification preferences (Director vs VP)
- Template-based notification content
- Future: Slack, SMS integrations
"""

import sqlite3
import json
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class NotificationPreferences:
    """User notification preferences"""
    user_id: str
    email: str
    notify_director_escalations: bool = True
    notify_vp_escalations: bool = True
    notify_signal_detected: bool = False
    notify_pattern_detected: bool = True
    notify_health_critical: bool = True
    digest_mode: str = "immediate"  # "immediate", "daily", "weekly"


@dataclass
class Notification:
    """Notification instance"""
    notification_id: str
    notification_type: str  # "escalation", "pattern", "health_alert"
    recipient_user_id: str
    recipient_email: str
    subject: str
    body_html: str
    body_text: str
    related_entity_id: str  # escalation_id, pattern_id, etc.
    related_entity_type: str  # "escalation", "pattern", etc.
    priority: str  # "high", "medium", "low"
    status: str = "pending"  # "pending", "sent", "failed"
    sent_at: Optional[str] = None
    error_message: Optional[str] = None


class NotificationService:
    """Service for sending notifications"""

    def __init__(self, db_connection: sqlite3.Connection, smtp_config: Optional[Dict] = None):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row
        self.smtp_config = smtp_config or self._get_default_smtp_config()

    def _get_default_smtp_config(self) -> Dict:
        """Get default SMTP configuration (would come from env vars in production)"""
        return {
            "host": "localhost",
            "port": 1025,  # Development SMTP server (mailhog)
            "username": None,
            "password": None,
            "from_email": "noreply@seleen.io",
            "from_name": "Seleen Intelligence"
        }

    def notify_escalation_created(
        self,
        escalation: Dict[str, Any],
        project_id: str,
        org_id: str
    ) -> List[str]:
        """
        Send notifications when escalation is created

        Args:
            escalation: Escalation data
            project_id: Project ID
            org_id: Organization ID

        Returns:
            List of notification IDs created
        """
        escalation_level = escalation.get('escalation_level', 'director')
        escalation_id = escalation.get('escalation_id')

        # Get users who should be notified
        recipients = self._get_notification_recipients(
            org_id,
            escalation_level
        )

        notification_ids = []

        for recipient in recipients:
            # Check user preferences
            prefs = self._get_user_preferences(recipient['user_id'])

            # Skip if user has disabled this notification type
            if escalation_level == 'director' and not prefs.notify_director_escalations:
                continue
            if escalation_level == 'vp' and not prefs.notify_vp_escalations:
                continue

            # Generate notification content
            subject, body_html, body_text = self._generate_escalation_notification(
                escalation,
                project_id,
                recipient
            )

            # Create notification
            notification = Notification(
                notification_id=self._generate_notification_id(),
                notification_type="escalation",
                recipient_user_id=recipient['user_id'],
                recipient_email=recipient['email'],
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                related_entity_id=escalation_id,
                related_entity_type="escalation",
                priority="high" if escalation_level == 'vp' else "medium"
            )

            # Store notification
            self._store_notification(notification)

            # Send immediately if not in digest mode
            if prefs.digest_mode == "immediate":
                self._send_notification(notification)

            notification_ids.append(notification.notification_id)

        logger.info(
            f"Created {len(notification_ids)} notifications for escalation {escalation_id} "
            f"(level: {escalation_level})"
        )

        return notification_ids

    def notify_pattern_detected(
        self,
        pattern: Dict[str, Any],
        project_id: str,
        org_id: str
    ) -> List[str]:
        """Send notifications when pattern is detected"""
        pattern_severity = pattern.get('severity', 'medium')

        # Only notify for high/critical patterns
        if pattern_severity not in ['high', 'critical']:
            return []

        recipients = self._get_notification_recipients(
            org_id,
            escalation_level='director'  # Patterns go to directors
        )

        notification_ids = []

        for recipient in recipients:
            prefs = self._get_user_preferences(recipient['user_id'])

            if not prefs.notify_pattern_detected:
                continue

            subject, body_html, body_text = self._generate_pattern_notification(
                pattern,
                project_id,
                recipient
            )

            notification = Notification(
                notification_id=self._generate_notification_id(),
                notification_type="pattern",
                recipient_user_id=recipient['user_id'],
                recipient_email=recipient['email'],
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                related_entity_id=pattern.get('pattern_id'),
                related_entity_type="pattern",
                priority="high" if pattern_severity == 'critical' else "medium"
            )

            self._store_notification(notification)

            if prefs.digest_mode == "immediate":
                self._send_notification(notification)

            notification_ids.append(notification.notification_id)

        return notification_ids

    def notify_health_critical(
        self,
        health_score: Dict[str, Any],
        project_id: str,
        org_id: str
    ) -> List[str]:
        """Send notifications when study health becomes critical"""
        if health_score.get('health_status') != 'critical':
            return []

        recipients = self._get_notification_recipients(
            org_id,
            escalation_level='director'
        )

        notification_ids = []

        for recipient in recipients:
            prefs = self._get_user_preferences(recipient['user_id'])

            if not prefs.notify_health_critical:
                continue

            subject, body_html, body_text = self._generate_health_alert_notification(
                health_score,
                project_id,
                recipient
            )

            notification = Notification(
                notification_id=self._generate_notification_id(),
                notification_type="health_alert",
                recipient_user_id=recipient['user_id'],
                recipient_email=recipient['email'],
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                related_entity_id=health_score.get('snapshot_id'),
                related_entity_type="health_snapshot",
                priority="high"
            )

            self._store_notification(notification)

            if prefs.digest_mode == "immediate":
                self._send_notification(notification)

            notification_ids.append(notification.notification_id)

        return notification_ids

    def _get_notification_recipients(
        self,
        org_id: str,
        escalation_level: str
    ) -> List[Dict[str, str]]:
        """Get users who should receive notifications for this escalation level"""
        cursor = self.conn.cursor()

        # Map escalation level to user roles
        role_filter = []
        if escalation_level == 'director':
            role_filter = ['director', 'vp', 'executive']
        elif escalation_level == 'vp':
            role_filter = ['vp', 'executive']
        else:
            role_filter = ['director', 'vp', 'executive']

        cursor.execute("""
            SELECT user_id, email, first_name, last_name, role
            FROM users
            WHERE org_id = ? AND role IN ({})
                AND is_active = 1
        """.format(','.join('?' * len(role_filter))), (org_id, *role_filter))

        recipients = []
        for row in cursor.fetchall():
            recipient = dict(row)
            # Construct full_name from first_name and last_name
            first_name = recipient.get('first_name', '')
            last_name = recipient.get('last_name', '')
            if first_name and last_name:
                recipient['full_name'] = f"{first_name} {last_name}"
            elif first_name:
                recipient['full_name'] = first_name
            elif last_name:
                recipient['full_name'] = last_name
            else:
                # Fallback to email if no name available
                recipient['full_name'] = recipient['email'].split('@')[0]
            recipients.append(recipient)

        return recipients

    def _get_user_preferences(self, user_id: str) -> NotificationPreferences:
        """Get user notification preferences"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT notification_preferences
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        row = cursor.fetchone()

        if row and row['notification_preferences']:
            prefs_data = json.loads(row['notification_preferences'])
            return NotificationPreferences(
                user_id=user_id,
                email=prefs_data.get('email', ''),
                notify_director_escalations=prefs_data.get('notify_director_escalations', True),
                notify_vp_escalations=prefs_data.get('notify_vp_escalations', True),
                notify_signal_detected=prefs_data.get('notify_signal_detected', False),
                notify_pattern_detected=prefs_data.get('notify_pattern_detected', True),
                notify_health_critical=prefs_data.get('notify_health_critical', True),
                digest_mode=prefs_data.get('digest_mode', 'immediate')
            )

        # Default preferences
        return NotificationPreferences(
            user_id=user_id,
            email=''
        )

    def _generate_escalation_notification(
        self,
        escalation: Dict[str, Any],
        project_id: str,
        recipient: Dict[str, str]
    ) -> tuple[str, str, str]:
        """Generate escalation notification content"""
        escalation_level = escalation.get('escalation_level', 'director').upper()
        escalation_reason = escalation.get('escalation_reason', 'N/A')
        priority = escalation.get('priority', 5)
        intervention = escalation.get('intervention_recommended', 'N/A')

        # Subject
        subject = f"[{escalation_level} ESCALATION] Study {project_id} - Priority {priority}"

        # Text body
        body_text = f"""
Seleen Intelligence Alert

{recipient['full_name']},

A {escalation_level}-level escalation has been detected for Study {project_id}.

ESCALATION DETAILS:
------------------
Level: {escalation_level}
Priority: {priority}
Reason: {escalation_reason}

RECOMMENDED INTERVENTION:
------------------------
{intervention}

ACTION REQUIRED:
---------------
Please review this escalation in the Leadership Dashboard and take appropriate action.

View Dashboard: https://app.seleen.io/dashboard/study/{project_id}

---
This is an automated notification from Seleen Intelligence.
To manage notification preferences, visit https://app.seleen.io/settings/notifications
"""

        # HTML body
        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ font-weight: bold; color: #495057; margin-bottom: 10px; }}
        .escalation-level {{ font-size: 24px; font-weight: bold; }}
        .priority {{ display: inline-block; background-color: #ffc107; color: #000; padding: 4px 12px; border-radius: 4px; }}
        .button {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin-top: 20px; }}
        .footer {{ text-align: center; color: #6c757d; font-size: 12px; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="escalation-level">{escalation_level} ESCALATION</div>
            <div>Study {project_id}</div>
        </div>

        <div class="content">
            <p>Hi {recipient['full_name']},</p>

            <p>A <strong>{escalation_level}-level escalation</strong> has been detected for Study {project_id}.</p>

            <div class="section">
                <div class="section-title">ESCALATION DETAILS:</div>
                <ul>
                    <li><strong>Level:</strong> {escalation_level}</li>
                    <li><strong>Priority:</strong> <span class="priority">{priority}</span></li>
                    <li><strong>Reason:</strong> {escalation_reason}</li>
                </ul>
            </div>

            <div class="section">
                <div class="section-title">RECOMMENDED INTERVENTION:</div>
                <p style="white-space: pre-line;">{intervention}</p>
            </div>

            <div class="section">
                <div class="section-title">ACTION REQUIRED:</div>
                <p>Please review this escalation in the Leadership Dashboard and take appropriate action.</p>
                <a href="https://app.seleen.io/dashboard/study/{project_id}" class="button">View Dashboard</a>
            </div>
        </div>

        <div class="footer">
            <p>This is an automated notification from Seleen Intelligence.</p>
            <p>To manage notification preferences, visit <a href="https://app.seleen.io/settings/notifications">Notification Settings</a></p>
        </div>
    </div>
</body>
</html>
"""

        return subject, body_html, body_text

    def _generate_pattern_notification(
        self,
        pattern: Dict[str, Any],
        project_id: str,
        recipient: Dict[str, str]
    ) -> tuple[str, str, str]:
        """Generate pattern detection notification content"""
        pattern_type = pattern.get('pattern_type', 'unknown')
        pattern_name = pattern.get('pattern_name', 'N/A')
        severity = pattern.get('severity', 'medium').upper()
        description = pattern.get('pattern_description', 'N/A')

        subject = f"[PATTERN DETECTED] Study {project_id} - {pattern_name}"

        body_text = f"""
Seleen Intelligence Alert

{recipient['full_name']},

A systemic pattern has been detected in Study {project_id}.

PATTERN DETAILS:
---------------
Type: {pattern_type}
Name: {pattern_name}
Severity: {severity}
Description: {description}

This pattern may indicate a systemic issue requiring attention.

View Dashboard: https://app.seleen.io/dashboard/study/{project_id}

---
This is an automated notification from Seleen Intelligence.
"""

        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #ffc107; color: #000; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; }}
        .button {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Pattern Detected</h2>
            <div>Study {project_id}</div>
        </div>

        <div class="content">
            <p>Hi {recipient['full_name']},</p>

            <p>A systemic pattern has been detected in Study {project_id}.</p>

            <ul>
                <li><strong>Pattern:</strong> {pattern_name}</li>
                <li><strong>Severity:</strong> {severity}</li>
                <li><strong>Description:</strong> {description}</li>
            </ul>

            <p>This pattern may indicate a systemic issue requiring attention.</p>

            <a href="https://app.seleen.io/dashboard/study/{project_id}" class="button">View Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

        return subject, body_html, body_text

    def _generate_health_alert_notification(
        self,
        health_score: Dict[str, Any],
        project_id: str,
        recipient: Dict[str, str]
    ) -> tuple[str, str, str]:
        """Generate health alert notification content"""
        score = health_score.get('overall_score', 0)
        status = health_score.get('health_status', 'unknown').upper()
        top_risks = health_score.get('top_risks', [])

        subject = f"[HEALTH ALERT] Study {project_id} - Critical Status ({score:.1f})"

        top_risks_text = "\n".join([f"- {risk.get('signal_description', 'N/A')}" for risk in top_risks[:3]])

        body_text = f"""
Seleen Intelligence Alert

{recipient['full_name']},

Study {project_id} health status is now CRITICAL.

HEALTH SCORE: {score:.1f} / 100
STATUS: {status}

TOP RISKS:
{top_risks_text}

Please review the dashboard for detailed analysis and recommended actions.

View Dashboard: https://app.seleen.io/dashboard/study/{project_id}

---
This is an automated notification from Seleen Intelligence.
"""

        body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; }}
        .score {{ font-size: 48px; font-weight: bold; color: #dc3545; }}
        .button {{ display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Health Alert: Critical Status</h2>
            <div>Study {project_id}</div>
        </div>

        <div class="content">
            <p>Hi {recipient['full_name']},</p>

            <p>Study {project_id} health status is now <strong>CRITICAL</strong>.</p>

            <div class="score">{score:.1f} / 100</div>

            <p><strong>Top Risks:</strong></p>
            <ul>
                {''.join([f'<li>{risk.get("signal_description", "N/A")}</li>' for risk in top_risks[:3]])}
            </ul>

            <p>Please review the dashboard for detailed analysis and recommended actions.</p>

            <a href="https://app.seleen.io/dashboard/study/{project_id}" class="button">View Dashboard</a>
        </div>
    </div>
</body>
</html>
"""

        return subject, body_html, body_text

    def _store_notification(self, notification: Notification):
        """Store notification in database"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO notifications (
                notification_id, notification_type, recipient_user_id,
                recipient_email, subject, body_html, body_text,
                related_entity_id, related_entity_type, priority,
                status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            notification.notification_id,
            notification.notification_type,
            notification.recipient_user_id,
            notification.recipient_email,
            notification.subject,
            notification.body_html,
            notification.body_text,
            notification.related_entity_id,
            notification.related_entity_type,
            notification.priority,
            notification.status
        ))

        self.conn.commit()

    def _send_notification(self, notification: Notification) -> bool:
        """Send notification via email"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = notification.subject
            msg['From'] = f"{self.smtp_config['from_name']} <{self.smtp_config['from_email']}>"
            msg['To'] = notification.recipient_email

            # Attach both text and HTML parts
            part1 = MIMEText(notification.body_text, 'plain')
            part2 = MIMEText(notification.body_html, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                if self.smtp_config.get('username'):
                    server.login(
                        self.smtp_config['username'],
                        self.smtp_config['password']
                    )

                server.send_message(msg)

            # Update notification status
            self._update_notification_status(
                notification.notification_id,
                'sent',
                sent_at=datetime.now().isoformat()
            )

            logger.info(f"Sent notification {notification.notification_id} to {notification.recipient_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send notification {notification.notification_id}: {e}", exc_info=True)

            self._update_notification_status(
                notification.notification_id,
                'failed',
                error_message=str(e)
            )

            return False

    def _update_notification_status(
        self,
        notification_id: str,
        status: str,
        sent_at: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Update notification status"""
        cursor = self.conn.cursor()

        cursor.execute("""
            UPDATE notifications
            SET status = ?, sent_at = ?, error_message = ?
            WHERE notification_id = ?
        """, (status, sent_at, error_message, notification_id))

        self.conn.commit()

    def _generate_notification_id(self) -> str:
        """Generate unique notification ID"""
        import uuid
        return f"notif_{uuid.uuid4()}"

    def send_pending_notifications(self) -> Dict[str, int]:
        """
        Send all pending notifications

        Used by background job to send queued notifications

        Returns:
            Stats: {'sent': N, 'failed': M}
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT notification_id, notification_type, recipient_user_id,
                   recipient_email, subject, body_html, body_text,
                   related_entity_id, related_entity_type, priority
            FROM notifications
            WHERE status = 'pending'
            ORDER BY priority DESC, created_at ASC
            LIMIT 100
        """)

        pending = cursor.fetchall()

        stats = {'sent': 0, 'failed': 0}

        for row in pending:
            notification = Notification(
                notification_id=row['notification_id'],
                notification_type=row['notification_type'],
                recipient_user_id=row['recipient_user_id'],
                recipient_email=row['recipient_email'],
                subject=row['subject'],
                body_html=row['body_html'],
                body_text=row['body_text'],
                related_entity_id=row['related_entity_id'],
                related_entity_type=row['related_entity_type'],
                priority=row['priority']
            )

            success = self._send_notification(notification)

            if success:
                stats['sent'] += 1
            else:
                stats['failed'] += 1

        logger.info(f"Sent {stats['sent']} notifications, {stats['failed']} failed")

        return stats


def integrate_with_escalation_engine(
    conn: sqlite3.Connection,
    escalation: Dict[str, Any],
    project_id: str,
    org_id: str,
    smtp_config: Optional[Dict] = None
):
    """
    Helper function to integrate notification service with escalation engine

    Call this after creating escalations in escalation_engine.py
    """
    notification_service = NotificationService(conn, smtp_config)

    notification_ids = notification_service.notify_escalation_created(
        escalation,
        project_id,
        org_id
    )

    return notification_ids
