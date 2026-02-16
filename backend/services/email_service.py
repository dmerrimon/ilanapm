"""
Email Service for Seleen Platform

Handles all email communications including:
- Password reset emails
- Admin transfer notifications
- System alerts

Configuration via environment variables:
- EMAIL_BACKEND: 'smtp' (default), 'sendgrid', 'aws_ses', or 'console' (dev mode)
- SMTP_HOST: SMTP server hostname
- SMTP_PORT: SMTP server port (default: 587)
- SMTP_USERNAME: SMTP authentication username
- SMTP_PASSWORD: SMTP authentication password
- SMTP_FROM_EMAIL: Sender email address (default: noreply@seleen.io)
- SMTP_FROM_NAME: Sender name (default: Seleen)
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Email configuration
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'console')  # console, smtp, sendgrid, aws_ses
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', 'noreply@seleen.io')
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'Seleen')

# Portal URLs
CUSTOMER_PORTAL_URL = os.getenv('CUSTOMER_PORTAL_URL', 'https://app.seleen.io')
FOUNDER_PORTAL_URL = os.getenv('FOUNDER_PORTAL_URL', 'https://admin.seleen.io')


class EmailService:
    """Email service for sending transactional emails"""

    def __init__(self, backend: str = EMAIL_BACKEND):
        self.backend = backend
        self.from_email = SMTP_FROM_EMAIL
        self.from_name = SMTP_FROM_NAME

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email using configured backend

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional, falls back to HTML)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if self.backend == 'console':
            return self._send_console(to_email, subject, html_body, text_body)
        elif self.backend == 'smtp':
            return self._send_smtp(to_email, subject, html_body, text_body, cc, bcc)
        elif self.backend == 'sendgrid':
            return self._send_sendgrid(to_email, subject, html_body, text_body)
        elif self.backend == 'aws_ses':
            return self._send_aws_ses(to_email, subject, html_body, text_body)
        else:
            logger.error(f"Unknown email backend: {self.backend}")
            return False

    def _send_console(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str]
    ) -> bool:
        """Log email to console (development mode)"""
        logger.info("=" * 80)
        logger.info("📧 EMAIL (Console Mode - Not Actually Sent)")
        logger.info("=" * 80)
        logger.info(f"From: {self.from_name} <{self.from_email}>")
        logger.info(f"To: {to_email}")
        logger.info(f"Subject: {subject}")
        logger.info("-" * 80)
        logger.info("HTML Body:")
        logger.info(html_body)
        if text_body:
            logger.info("-" * 80)
            logger.info("Text Body:")
            logger.info(text_body)
        logger.info("=" * 80)
        return True

    def _send_smtp(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str],
        cc: Optional[List[str]],
        bcc: Optional[List[str]]
    ) -> bool:
        """Send email via SMTP server"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            # Attach text and HTML parts
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Send via SMTP
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                if SMTP_USERNAME and SMTP_PASSWORD:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)

                recipients = [to_email]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)

                server.sendmail(self.from_email, recipients, msg.as_string())

            logger.info(f"Email sent successfully to {to_email} via SMTP")
            return True

        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return False

    def _send_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str]
    ) -> bool:
        """Send email via SendGrid API"""
        # TODO: Implement SendGrid integration
        logger.warning("SendGrid backend not yet implemented, falling back to console")
        return self._send_console(to_email, subject, html_body, text_body)

    def _send_aws_ses(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str]
    ) -> bool:
        """Send email via AWS SES"""
        # TODO: Implement AWS SES integration
        logger.warning("AWS SES backend not yet implemented, falling back to console")
        return self._send_console(to_email, subject, html_body, text_body)

    # ========================================================================
    # Template Methods
    # ========================================================================

    def send_password_reset_email(
        self,
        to_email: str,
        reset_token: str,
        user_name: Optional[str] = None
    ) -> bool:
        """Send password reset email with token link"""
        reset_url = f"{CUSTOMER_PORTAL_URL}/reset-password?token={reset_token}"

        subject = "Reset Your Seleen Password"

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #000; color: #fff; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #000; color: #fff; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Seleen</h1>
        </div>
        <div class="content">
            <h2>Reset Your Password</h2>
            <p>Hello{' ' + user_name if user_name else ''},</p>
            <p>We received a request to reset your password for your Seleen account. Click the button below to create a new password:</p>
            <p style="text-align: center;">
                <a href="{reset_url}" class="button">Reset Password</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{reset_url}</p>
            <p><strong>This link will expire in 1 hour.</strong></p>
            <p>If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.</p>
        </div>
        <div class="footer">
            <p>&copy; {datetime.now().year} Seleen. All rights reserved.</p>
            <p>This is an automated message, please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""

        text_body = f"""
Seleen - Reset Your Password

Hello{' ' + user_name if user_name else ''},

We received a request to reset your password for your Seleen account.

Click here to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request a password reset, you can safely ignore this email.

© {datetime.now().year} Seleen. All rights reserved.
"""

        return self.send_email(to_email, subject, html_body, text_body)

    def send_admin_transfer_email(
        self,
        to_email: str,
        org_name: str,
        from_user_name: str,
        transfer_token: str,
        message: Optional[str] = None
    ) -> bool:
        """Send admin transfer notification email"""
        accept_url = f"{CUSTOMER_PORTAL_URL}/admin-transfer/accept?token={transfer_token}"

        subject = f"Admin Transfer Request for {org_name}"

        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #000; color: #fff; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #000; color: #fff; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .message-box {{ background-color: #fff; border-left: 4px solid #000; padding: 15px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Seleen</h1>
        </div>
        <div class="content">
            <h2>Admin Transfer Request</h2>
            <p>Hello,</p>
            <p><strong>{from_user_name}</strong> has requested to transfer admin ownership of <strong>{org_name}</strong> to you.</p>
            {'<div class="message-box"><p><strong>Message from ' + from_user_name + ':</strong></p><p>' + message + '</p></div>' if message else ''}
            <p>As the new admin, you will have full control over:</p>
            <ul>
                <li>User management</li>
                <li>License and seat management</li>
                <li>Organization settings</li>
                <li>Billing and subscriptions</li>
            </ul>
            <p style="text-align: center;">
                <a href="{accept_url}" class="button">Accept Admin Role</a>
            </p>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666;">{accept_url}</p>
            <p><strong>This link will expire in 7 days.</strong></p>
            <p>If you don't want to accept this role, you can safely ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; {datetime.now().year} Seleen. All rights reserved.</p>
            <p>This is an automated message, please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""

        text_body = f"""
Seleen - Admin Transfer Request

Hello,

{from_user_name} has requested to transfer admin ownership of {org_name} to you.

{f'Message from {from_user_name}: {message}' if message else ''}

As the new admin, you will have full control over user management, licenses, settings, and billing.

Click here to accept the admin role:
{accept_url}

This link will expire in 7 days.

If you don't want to accept this role, you can safely ignore this email.

© {datetime.now().year} Seleen. All rights reserved.
"""

        return self.send_email(to_email, subject, html_body, text_body)


# Singleton instance
email_service = EmailService()


# Convenience functions
def send_password_reset_email(to_email: str, reset_token: str, user_name: Optional[str] = None) -> bool:
    """Send password reset email"""
    return email_service.send_password_reset_email(to_email, reset_token, user_name)


def send_admin_transfer_email(
    to_email: str,
    org_name: str,
    from_user_name: str,
    transfer_token: str,
    message: Optional[str] = None
) -> bool:
    """Send admin transfer email"""
    return email_service.send_admin_transfer_email(
        to_email, org_name, from_user_name, transfer_token, message
    )
