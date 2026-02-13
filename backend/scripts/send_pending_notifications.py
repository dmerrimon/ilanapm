"""
Background Job: Send Pending Notifications

Processes pending notifications and sends them via email.

Usage:
    python3 scripts/send_pending_notifications.py

Schedule:
    Run every 5 minutes via cron:
    */5 * * * * cd /path/to/backend && python3 scripts/send_pending_notifications.py

This script:
1. Finds all notifications with status='pending'
2. Sends them via email
3. Updates status to 'sent' or 'failed'
4. Logs results
"""

import sys
import os
import logging
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import sqlite3
from intelligence.notification_service import NotificationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(backend_dir / 'logs' / 'notification_service.log')
    ]
)

logger = logging.getLogger(__name__)


def get_db_connection() -> sqlite3.Connection:
    """Get database connection"""
    db_path = backend_dir / "database" / "feedback.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def send_pending_notifications():
    """Send all pending notifications"""
    logger.info("Starting pending notification processing")

    try:
        conn = get_db_connection()

        # Optional: Load SMTP config from environment
        smtp_config = {
            "host": os.getenv("SMTP_HOST", "localhost"),
            "port": int(os.getenv("SMTP_PORT", "1025")),
            "username": os.getenv("SMTP_USERNAME"),
            "password": os.getenv("SMTP_PASSWORD"),
            "from_email": os.getenv("SMTP_FROM_EMAIL", "noreply@seleen.io"),
            "from_name": os.getenv("SMTP_FROM_NAME", "Seleen Intelligence")
        }

        notification_service = NotificationService(conn, smtp_config)

        # Send pending notifications
        stats = notification_service.send_pending_notifications()

        conn.close()

        logger.info(
            f"Notification processing complete: "
            f"{stats['sent']} sent, {stats['failed']} failed"
        )

        return stats

    except Exception as e:
        logger.error(f"Failed to process notifications: {e}", exc_info=True)
        return {"sent": 0, "failed": 0, "error": str(e)}


def main():
    """Main entry point"""
    stats = send_pending_notifications()

    # Exit with error code if processing failed
    if stats.get('error'):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
