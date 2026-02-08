"""
Admin Portal API - Endpoints for customer and founder portals

This module provides APIs for:
- Customer Portal (app.seleen.com): Self-service license/seat management
- Founder Portal (admin.seleen.com): System-wide admin and analytics
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from typing import Optional, List
import secrets
import json
import logging
import hashlib

from database.connection import get_db_connection
from api.licensing import create_access_token, decode_token

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class AdminTransferRequest(BaseModel):
    """Request to transfer admin ownership"""
    org_id: str
    from_user_id: str
    to_user_email: EmailStr
    message: Optional[str] = None


class AdminTransferAcceptRequest(BaseModel):
    """Accept admin transfer"""
    token: str


class OrgUser(BaseModel):
    """User information for org management"""
    user_id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime


class OrgAnalytics(BaseModel):
    """Organization usage analytics"""
    org_id: str
    org_name: str
    template_count_30d: int
    feedback_count_30d: int
    active_users_30d: int
    most_used_templates: List[dict]
    most_active_users: List[dict]


class SuperAdminDashboard(BaseModel):
    """Founder portal dashboard data"""
    total_customers: int
    total_seats: int
    total_mrr: float
    system_uptime: float
    api_response_time_p95: float
    db_size_mb: float
    recent_alerts: List[dict]


class CustomerListItem(BaseModel):
    """Customer list item for founder portal"""
    org_id: str
    org_name: str
    license_key: str
    seats_used: int
    seats_purchased: int
    seat_rate: Optional[float]
    mrr: Optional[float]
    status: str
    created_at: datetime
    last_active: Optional[datetime]


class LoginRequest(BaseModel):
    """Login request for portal access"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response with JWT token"""
    access_token: str
    token_type: str
    user: dict


class ForgotPasswordRequest(BaseModel):
    """Request to reset password"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password with token"""
    token: str
    new_password: str


# ============================================================================
# Authentication Helpers
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using SHA-256 (simple hashing for MVP)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user_token(authorization: str = Header(None)):
    """
    Verify JWT token from Authorization header
    Returns user_id, org_id, role from token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        # Decode and validate JWT token using licensing.py function
        payload = decode_token(token)

        # Extract user data from payload
        user_id = payload.get("user_id")
        org_id = payload.get("org_id")
        role = payload.get("role", "user")

        if not user_id or not org_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return {
            "user_id": user_id,
            "org_id": org_id,
            "role": role,
            "email": payload.get("email")
        }
    except HTTPException:
        # Re-raise HTTP exceptions from decode_token
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")


def require_admin_role(user_data: dict = Depends(verify_user_token)):
    """Require user to have admin or super_admin role"""
    if user_data.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_data


def require_super_admin_role(user_data: dict = Depends(verify_user_token)):
    """Require user to have super_admin role"""
    if user_data.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    return user_data


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/portal/login", response_model=LoginResponse)
async def portal_login(request: LoginRequest):
    """
    Authenticate user and return JWT token
    Works for both customer portal (admins) and founder portal (super_admins)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        try:
            # Look up user by email
            cursor.execute("""
                SELECT user_id, email, password_hash, role, org_id, first_name, last_name, is_active,
                       customer_portal_access, founder_portal_access
                FROM users
                WHERE email = ?
            """, (request.email,))

            user = cursor.fetchone()

            if not user:
                # Generic error to prevent email enumeration
                raise HTTPException(status_code=401, detail="Invalid email or password")

            # Check if user is active
            if not user["is_active"]:
                raise HTTPException(status_code=401, detail="Account is inactive")

            # Verify password
            password_hash = hash_password(request.password)
            if user["password_hash"] != password_hash:
                raise HTTPException(status_code=401, detail="Invalid email or password")

            # Check portal access
            # Note: For MVP, we'll allow any user with a role to access portals
            # In production, you'd check customer_portal_access and founder_portal_access flags

            # Create JWT token with user data
            token_data = {
                "user_id": user["user_id"],
                "org_id": user["org_id"],
                "email": user["email"],
                "role": user["role"]
            }

            access_token = create_access_token(token_data)

            # Update last_login timestamp
            cursor.execute("""
                UPDATE users
                SET last_login = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (user["user_id"],))
            conn.commit()

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "user_id": user["user_id"],
                    "email": user["email"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "role": user["role"],
                    "org_id": user["org_id"]
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise HTTPException(status_code=500, detail="Login failed")


@router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """
    Initiate password reset by sending reset link to user's email

    Creates a reset token and logs the reset link (in production, would send email)
    """
    email = request.email

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT user_id, email, first_name FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        # Always return success to prevent email enumeration
        # But only create token if user exists
        if user:
            # Generate secure random token
            reset_token = secrets.token_urlsafe(32)

            # Token expires in 1 hour
            expires_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()

            # Store token in database
            cursor.execute("""
                INSERT INTO password_reset_tokens (email, token, expires_at, used)
                VALUES (?, ?, ?, FALSE)
            """, (email, reset_token, expires_at))
            conn.commit()

            # In production, send email here
            # For now, log the reset link
            reset_link = f"https://app.seleen.io/reset-password?token={reset_token}"
            logger.info(f"Password reset link for {email}: {reset_link}")

            # TODO: Send email using SendGrid or similar
            # send_password_reset_email(
            #     to_email=email,
            #     user_name=user.get('first_name') or 'User',
            #     reset_link=reset_link
            # )

        return {"message": "If an account exists with that email, you will receive a password reset link shortly."}


@router.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password using the token from email

    Validates token and updates user's password
    """
    token = request.token
    new_password = request.new_password

    # Validate password length
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Look up token
        cursor.execute("""
            SELECT email, expires_at, used
            FROM password_reset_tokens
            WHERE token = ?
        """, (token,))

        token_data = cursor.fetchone()

        if not token_data:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")

        # Handle both dict (PostgreSQL) and tuple (SQLite) row types
        if isinstance(token_data, dict):
            email = token_data["email"]
            expires_at = token_data["expires_at"]
            used = token_data["used"]
        else:
            email = token_data[0]
            expires_at = token_data[1]
            used = token_data[2]

        # Check if token is already used
        if used:
            raise HTTPException(status_code=400, detail="This reset link has already been used")

        # Check if token is expired
        expires_datetime = datetime.fromisoformat(expires_at)
        if datetime.utcnow() > expires_datetime:
            raise HTTPException(status_code=400, detail="This reset link has expired. Please request a new one")

        # Hash the new password
        password_hash = hash_password(new_password)

        # Update user's password
        cursor.execute("""
            UPDATE users
            SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
        """, (password_hash, email))

        # Mark token as used
        cursor.execute("""
            UPDATE password_reset_tokens
            SET used = TRUE
            WHERE token = ?
        """, (token,))

        conn.commit()

        logger.info(f"Password successfully reset for user: {email}")

        return {"message": "Password has been reset successfully. You can now sign in with your new password."}


# ============================================================================
# CUSTOMER PORTAL ENDPOINTS (app.seleen.com)
# ============================================================================

@router.get("/portal/customer/dashboard")
async def get_customer_dashboard(user_data: dict = Depends(require_admin_role)):
    """
    Get customer portal dashboard data
    Shows: seat usage, license status, pricing tier, next billing date
    """
    org_id = user_data["org_id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get organization details
        cursor.execute("""
            SELECT
                org_name, tier, seats_purchased, seats_used,
                subscription_start, subscription_end, status,
                seat_rate, billing_cycle, mrr, next_billing_date,
                stripe_customer_id
            FROM organizations
            WHERE org_id = ?
        """, (org_id,))

        org = cursor.fetchone()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Get license key (masked)
        cursor.execute("""
            SELECT license_key
            FROM license_keys
            WHERE org_id = ? AND is_active = TRUE
            LIMIT 1
        """, (org_id,))

        license_row = cursor.fetchone()
        license_key = license_row["license_key"] if license_row else None

        # Mask license key (show first 5 and last 4 chars)
        if license_key:
            masked_license = f"{license_key[:10]}****{license_key[-4:]}"
        else:
            masked_license = None

        # Count active devices (actual seat usage)
        cursor.execute("""
            SELECT COUNT(*) as active_devices
            FROM activations a
            JOIN users u ON a.user_id = u.user_id
            WHERE u.org_id = ? AND a.is_active = TRUE
        """, (org_id,))

        device_count = cursor.fetchone()
        active_devices = device_count["active_devices"] if device_count else 0

        # Count active users
        cursor.execute("""
            SELECT COUNT(*) as active_users
            FROM users
            WHERE org_id = ? AND is_active = TRUE
        """, (org_id,))

        user_count = cursor.fetchone()
        active_users = user_count["active_users"] if user_count else 0

        return {
            "org_name": org["org_name"],
            "license_key": masked_license,
            "status": org["status"],
            "tier": org["tier"],
            "seats_purchased": org["seats_purchased"],
            "seats_used": org["seats_used"],
            "seats_available": org["seats_purchased"] - org["seats_used"],
            "active_devices": active_devices,  # Actual count from activations table
            "active_users": active_users,      # Count of active users
            "seat_rate": float(org["seat_rate"]) if org["seat_rate"] else None,
            "billing_cycle": org["billing_cycle"],
            "mrr": float(org["mrr"]) if org["mrr"] else None,
            "next_billing_date": org["next_billing_date"],
            "subscription_start": org["subscription_start"],
            "subscription_end": org["subscription_end"]
        }


@router.get("/portal/customer/users")
async def list_org_users(user_data: dict = Depends(require_admin_role)):
    """
    List all users in the organization
    Shows: email, name, role, activation status, last login, device count
    """
    org_id = user_data["org_id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                u.user_id,
                u.email,
                u.first_name,
                u.last_name,
                u.role,
                u.is_active,
                u.last_login,
                u.created_at,
                COUNT(CASE WHEN a.is_active = TRUE THEN 1 END) as active_devices
            FROM users u
            LEFT JOIN activations a ON u.user_id = a.user_id
            WHERE u.org_id = ?
            GROUP BY u.user_id, u.email, u.first_name, u.last_name, u.role,
                     u.is_active, u.last_login, u.created_at
            ORDER BY u.created_at DESC
        """, (org_id,))

        users = cursor.fetchall()

        return {
            "users": [dict(user) for user in users],
            "total_count": len(users)
        }


@router.delete("/portal/customer/users/{user_id}")
async def deactivate_user(user_id: str, user_data: dict = Depends(require_admin_role)):
    """
    Deactivate a user (frees up a seat)
    Admin can deactivate any user except themselves
    """
    org_id = user_data["org_id"]
    admin_user_id = user_data["user_id"]

    if user_id == admin_user_id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Verify user belongs to this org
        cursor.execute("""
            SELECT user_id, is_active
            FROM users
            WHERE user_id = ? AND org_id = ?
        """, (user_id, org_id))

        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found in your organization")

        if not user["is_active"]:
            return {"message": "User already deactivated"}

        # Count active devices for this user
        cursor.execute("""
            SELECT COUNT(*) as active_device_count
            FROM activations
            WHERE user_id = ? AND is_active = TRUE
        """, (user_id,))

        device_count_row = cursor.fetchone()
        active_device_count = device_count_row["active_device_count"] if device_count_row else 0

        # Deactivate user
        cursor.execute("""
            UPDATE users
            SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_id,))

        # Deactivate all user's activations
        cursor.execute("""
            UPDATE activations
            SET is_active = FALSE, deactivated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_id,))

        # Decrement seats_used by the number of active devices
        if active_device_count > 0:
            cursor.execute("""
                UPDATE organizations
                SET seats_used = seats_used - ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE org_id = ?
            """, (active_device_count, org_id))

        # Log action
        cursor.execute("""
            INSERT INTO audit_logs (log_id, org_id, user_id, action, resource_type, resource_id, metadata, timestamp)
            VALUES (?, ?, ?, 'user_deactivated', 'user', ?, ?, CURRENT_TIMESTAMP)
        """, (
            secrets.token_urlsafe(16),
            org_id,
            admin_user_id,
            user_id,
            json.dumps({
                "deactivated_by": admin_user_id,
                "devices_deactivated": active_device_count
            })
        ))

        conn.commit()

        logger.info(f"User deactivated: user_id={user_id}, devices_deactivated={active_device_count}, admin={admin_user_id}")

        return {
            "message": f"User deactivated successfully. {active_device_count} device(s) freed.",
            "user_id": user_id,
            "devices_deactivated": active_device_count
        }


@router.get("/portal/customer/activations")
async def list_org_activations(user_data: dict = Depends(require_admin_role)):
    """
    List all active device activations for the organization
    Shows: user email, device name, activation date, last activity, MS Project version
    Allows admins to see which devices are consuming seats
    """
    org_id = user_data["org_id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.activation_id,
                a.user_id,
                u.email,
                u.first_name,
                u.last_name,
                a.device_id,
                a.device_name,
                a.is_active,
                a.activated_at,
                a.deactivated_at,
                a.last_api_call,
                a.api_call_count,
                a.ms_project_version,
                a.addin_version
            FROM activations a
            JOIN users u ON a.user_id = u.user_id
            WHERE u.org_id = ?
            ORDER BY a.is_active DESC, a.last_api_call DESC
        """, (org_id,))

        activations = cursor.fetchall()

        # Count active vs inactive
        active_count = sum(1 for a in activations if a["is_active"])
        inactive_count = len(activations) - active_count

        return {
            "activations": [dict(activation) for activation in activations],
            "total_count": len(activations),
            "active_count": active_count,
            "inactive_count": inactive_count
        }


@router.delete("/portal/customer/activations/{activation_id}")
async def deactivate_device(activation_id: str, user_data: dict = Depends(require_admin_role)):
    """
    Deactivate a specific device activation (frees up a seat)
    Admin can deactivate any device in their organization
    User will need to re-activate on that device
    """
    org_id = user_data["org_id"]
    admin_user_id = user_data["user_id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Verify activation belongs to this org and get details
        cursor.execute("""
            SELECT
                a.activation_id,
                a.user_id,
                a.device_name,
                a.is_active,
                u.email,
                u.org_id
            FROM activations a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.activation_id = ?
        """, (activation_id,))

        activation = cursor.fetchone()

        if not activation:
            raise HTTPException(status_code=404, detail="Activation not found")

        if activation["org_id"] != org_id:
            raise HTTPException(status_code=403, detail="Cannot deactivate devices from other organizations")

        if not activation["is_active"]:
            return {"message": "Device already deactivated"}

        # Deactivate the device
        cursor.execute("""
            UPDATE activations
            SET is_active = FALSE, deactivated_at = CURRENT_TIMESTAMP
            WHERE activation_id = ?
        """, (activation_id,))

        # Decrement seats_used for the organization
        cursor.execute("""
            UPDATE organizations
            SET seats_used = seats_used - 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE org_id = ?
        """, (org_id,))

        # Log action
        cursor.execute("""
            INSERT INTO audit_logs (log_id, org_id, user_id, action, resource_type, resource_id, metadata, timestamp)
            VALUES (?, ?, ?, 'device_deactivated', 'activation', ?, ?, CURRENT_TIMESTAMP)
        """, (
            secrets.token_urlsafe(16),
            org_id,
            admin_user_id,
            activation_id,
            json.dumps({
                "device_name": activation["device_name"],
                "user_email": activation["email"],
                "deactivated_by": admin_user_id
            })
        ))

        conn.commit()

        logger.info(f"Device deactivated by admin: activation_id={activation_id}, device={activation['device_name']}, admin={admin_user_id}")

        return {
            "message": "Device deactivated successfully",
            "activation_id": activation_id,
            "device_name": activation["device_name"],
            "user_email": activation["email"]
        }


@router.post("/portal/customer/admin-transfer")
async def initiate_admin_transfer(request: AdminTransferRequest, user_data: dict = Depends(require_admin_role)):
    """
    Initiate admin ownership transfer to another user in the org
    Sends email invitation to new admin
    """
    org_id = user_data["org_id"]
    from_user_id = user_data["user_id"]

    # Verify target user exists in org
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id, email, first_name, last_name
            FROM users
            WHERE email = ? AND org_id = ? AND is_active = TRUE
        """, (request.to_user_email, org_id))

        target_user = cursor.fetchone()

        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found in your organization")

        # Generate transfer token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)

        # Create transfer request
        cursor.execute("""
            INSERT INTO admin_transfer_requests
            (org_id, from_user_id, to_user_email, token, message, status, expires_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
        """, (
            org_id,
            from_user_id,
            request.to_user_email,
            token,
            request.message,
            expires_at
        ))

        # Log action
        cursor.execute("""
            INSERT INTO audit_logs (log_id, org_id, user_id, action, resource_type, resource_id, metadata, timestamp)
            VALUES (?, ?, ?, 'admin_transfer_initiated', 'admin_transfer', ?, ?, CURRENT_TIMESTAMP)
        """, (
            secrets.token_urlsafe(16),
            org_id,
            from_user_id,
            token,
            json.dumps({
                "to_email": request.to_user_email,
                "message": request.message
            })
        ))

        conn.commit()

        # TODO: Send email to target user with acceptance link
        # Email should contain: app.seleen.com/admin-transfer/accept?token={token}

        return {
            "message": "Admin transfer initiated",
            "token": token,  # In production, don't return token - send via email only
            "to_email": request.to_user_email,
            "expires_at": expires_at.isoformat()
        }


@router.post("/portal/customer/admin-transfer/accept")
async def accept_admin_transfer(request: AdminTransferAcceptRequest, user_data: dict = Depends(verify_user_token)):
    """
    Accept admin transfer (new admin confirms)
    Promotes new admin, demotes old admin to 'user' role
    """
    user_id = user_data["user_id"]
    org_id = user_data["org_id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get transfer request
        cursor.execute("""
            SELECT org_id, from_user_id, to_user_email, status, expires_at
            FROM admin_transfer_requests
            WHERE token = ?
        """, (request.token,))

        transfer = cursor.fetchone()

        if not transfer:
            raise HTTPException(status_code=404, detail="Invalid transfer token")

        if transfer["status"] != "pending":
            raise HTTPException(status_code=400, detail=f"Transfer already {transfer['status']}")

        if datetime.fromisoformat(transfer["expires_at"]) < datetime.utcnow():
            # Mark as expired
            cursor.execute("""
                UPDATE admin_transfer_requests
                SET status = 'expired'
                WHERE token = ?
            """, (request.token,))
            conn.commit()
            raise HTTPException(status_code=400, detail="Transfer token expired")

        # Verify accepting user's email matches
        cursor.execute("""
            SELECT email
            FROM users
            WHERE user_id = ?
        """, (user_id,))

        current_user = cursor.fetchone()

        if not current_user or current_user["email"] != transfer["to_user_email"]:
            raise HTTPException(status_code=403, detail="You are not the designated recipient of this transfer")

        # Promote new admin
        cursor.execute("""
            UPDATE users
            SET role = 'admin', updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_id,))

        # Demote old admin
        cursor.execute("""
            UPDATE users
            SET role = 'user', updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (transfer["from_user_id"],))

        # Mark transfer as accepted
        cursor.execute("""
            UPDATE admin_transfer_requests
            SET status = 'accepted', accepted_at = CURRENT_TIMESTAMP
            WHERE token = ?
        """, (request.token,))

        # Log action
        cursor.execute("""
            INSERT INTO audit_logs (log_id, org_id, user_id, action, resource_type, resource_id, metadata, timestamp)
            VALUES (?, ?, ?, 'admin_transfer_accepted', 'admin_transfer', ?, ?, CURRENT_TIMESTAMP)
        """, (
            secrets.token_urlsafe(16),
            transfer["org_id"],
            user_id,
            request.token,
            json.dumps({
                "from_user_id": transfer["from_user_id"],
                "to_user_id": user_id
            })
        ))

        conn.commit()

        return {
            "message": "Admin transfer completed successfully",
            "new_admin_user_id": user_id
        }


@router.get("/portal/customer/analytics")
async def get_org_analytics(user_data: dict = Depends(require_admin_role)):
    """
    Get organization usage analytics
    Shows: template generation count, feedback stats, active users, top templates
    """
    org_id = user_data["org_id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get org name
        cursor.execute("SELECT org_name FROM organizations WHERE org_id = ?", (org_id,))
        org = cursor.fetchone()

        # Template generation count (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM usage_analytics
            WHERE org_id = ?
              AND event_type = 'template_generated'
              AND timestamp >= datetime('now', '-30 days')
        """, (org_id,))

        template_count = cursor.fetchone()["count"]

        # Feedback submission count (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM usage_analytics
            WHERE org_id = ?
              AND event_type = 'feedback_submitted'
              AND timestamp >= datetime('now', '-30 days')
        """, (org_id,))

        feedback_count = cursor.fetchone()["count"]

        # Active users (last 30 days)
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as count
            FROM usage_analytics
            WHERE org_id = ?
              AND timestamp >= datetime('now', '-30 days')
        """, (org_id,))

        active_users = cursor.fetchone()["count"]

        # Most used templates (placeholder - would need to parse event_data JSON)
        most_used_templates = []

        # Most active users (placeholder)
        most_active_users = []

        return {
            "org_id": org_id,
            "org_name": org["org_name"],
            "template_count_30d": template_count,
            "feedback_count_30d": feedback_count,
            "active_users_30d": active_users,
            "most_used_templates": most_used_templates,
            "most_active_users": most_active_users
        }


# ============================================================================
# FOUNDER PORTAL ENDPOINTS (admin.seleen.com)
# ============================================================================

@router.get("/portal/founder/dashboard")
async def get_founder_dashboard(user_data: dict = Depends(require_super_admin_role)):
    """
    Get founder portal dashboard with system-wide metrics
    Shows: total customers, total revenue, system health, alerts
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total customers
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN plan_type = 'pilot' THEN 1 ELSE 0 END) as trial
            FROM organizations
        """)

        customers = cursor.fetchone()

        # Total seats
        cursor.execute("""
            SELECT SUM(seats_used) as total_seats
            FROM organizations
            WHERE status = 'active'
        """)

        seats = cursor.fetchone()

        # Total MRR
        cursor.execute("""
            SELECT SUM(mrr) as total_mrr
            FROM organizations
            WHERE status = 'active'
        """)

        revenue = cursor.fetchone()

        return {
            "total_customers": customers["total"] or 0,
            "active_customers": customers["active"] or 0,
            "trial_customers": customers["trial"] or 0,
            "total_seats": seats["total_seats"] or 0,
            "total_mrr": float(revenue["total_mrr"]) if revenue["total_mrr"] else 0.0,
            "system_uptime": 99.8,  # TODO: Get from monitoring service
            "api_response_time_p95": 150.0,  # TODO: Get from monitoring
            "db_size_mb": 2.3,  # TODO: Get actual DB size
            "recent_alerts": []  # TODO: Implement alerts system
        }


@router.get("/portal/founder/customers")
async def list_all_customers(user_data: dict = Depends(require_super_admin_role)):
    """
    List all customer organizations
    Shows: org name, license key, seats, MRR, status, activity
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                o.org_id, o.org_name, o.seats_purchased, o.seats_used,
                o.seat_rate, o.mrr, o.status, o.created_at,
                lk.license_key,
                MAX(u.last_login) as last_active
            FROM organizations o
            LEFT JOIN license_keys lk ON o.org_id = lk.org_id AND lk.is_active = TRUE
            LEFT JOIN users u ON o.org_id = u.org_id
            GROUP BY o.org_id
            ORDER BY o.created_at DESC
        """)

        customers = cursor.fetchall()

        return {
            "customers": [dict(customer) for customer in customers],
            "total_count": len(customers)
        }


@router.get("/portal/founder/customers/{org_id}")
async def get_customer_details(org_id: str, user_data: dict = Depends(require_super_admin_role)):
    """
    Get detailed information about a specific organization
    Shows: all org data, users, billing history, usage metrics
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get organization details
        cursor.execute("""
            SELECT *
            FROM organizations
            WHERE org_id = ?
        """, (org_id,))

        org = cursor.fetchone()

        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        # Get users
        cursor.execute("""
            SELECT user_id, email, first_name, last_name, role, is_active, last_login, created_at
            FROM users
            WHERE org_id = ?
        """, (org_id,))

        users = cursor.fetchall()

        # Get license keys
        cursor.execute("""
            SELECT license_key, tier, seats, created_at, expires_at, is_active
            FROM license_keys
            WHERE org_id = ?
        """, (org_id,))

        licenses = cursor.fetchall()

        return {
            "organization": dict(org),
            "users": [dict(user) for user in users],
            "licenses": [dict(lic) for lic in licenses]
        }


@router.get("/portal/founder/analytics/system")
async def get_system_analytics(user_data: dict = Depends(require_super_admin_role)):
    """
    Get system-wide analytics
    Shows: ML model performance, usage metrics, API performance
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Feedback submissions (all customers)
        cursor.execute("""
            SELECT COUNT(*) as total_feedback
            FROM task_outcomes
        """)

        feedback = cursor.fetchone()

        # Overall accuracy
        cursor.execute("""
            SELECT AVG(CAST(was_accurate AS FLOAT)) * 100 as accuracy_rate
            FROM task_outcomes
        """)

        accuracy = cursor.fetchone()

        # Template generations (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) as template_count
            FROM usage_analytics
            WHERE event_type = 'template_generated'
              AND timestamp >= datetime('now', '-30 days')
        """)

        templates = cursor.fetchone()

        return {
            "ml_performance": {
                "total_feedback": feedback["total_feedback"] or 0,
                "overall_accuracy": float(accuracy["accuracy_rate"]) if accuracy["accuracy_rate"] else 0.0
            },
            "usage_metrics": {
                "template_generations_30d": templates["template_count"] or 0
            },
            "api_performance": {
                "total_requests_30d": 0,  # TODO: Implement request tracking
                "avg_response_time_ms": 132.0,  # TODO: Get from monitoring
                "error_rate": 0.3  # TODO: Get from logs
            }
        }


@router.get("/portal/founder/activations")
async def list_all_activations(user_data: dict = Depends(require_super_admin_role)):
    """
    List all device activations across all organizations (system-wide)
    Shows: user, org, device name, activation date, last activity, MS Project version
    Allows super admins to see entire device landscape
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.activation_id,
                a.user_id,
                u.email,
                u.first_name,
                u.last_name,
                u.org_id,
                o.org_name,
                a.device_id,
                a.device_name,
                a.is_active,
                a.activated_at,
                a.deactivated_at,
                a.last_api_call,
                a.api_call_count,
                a.ms_project_version,
                a.addin_version
            FROM activations a
            JOIN users u ON a.user_id = u.user_id
            JOIN organizations o ON u.org_id = o.org_id
            ORDER BY a.is_active DESC, a.last_api_call DESC
        """)

        activations = cursor.fetchall()

        # Count active vs inactive
        active_count = sum(1 for a in activations if a["is_active"])
        inactive_count = len(activations) - active_count

        # Count by organization
        org_counts = {}
        for a in activations:
            org_id = a["org_id"]
            if org_id not in org_counts:
                org_counts[org_id] = {"org_name": a["org_name"], "active": 0, "inactive": 0}
            if a["is_active"]:
                org_counts[org_id]["active"] += 1
            else:
                org_counts[org_id]["inactive"] += 1

        return {
            "activations": [dict(activation) for activation in activations],
            "total_count": len(activations),
            "active_count": active_count,
            "inactive_count": inactive_count,
            "by_organization": [
                {"org_id": org_id, **counts}
                for org_id, counts in org_counts.items()
            ]
        }


@router.get("/portal/founder/activations/stats")
async def get_activation_stats(user_data: dict = Depends(require_super_admin_role)):
    """
    Get system-wide device activation statistics
    Shows: total devices, by org, by MS Project version, activity trends
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total active devices
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM activations
            WHERE is_active = TRUE
        """)
        active_devices = cursor.fetchone()["count"]

        # Total inactive devices
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM activations
            WHERE is_active = FALSE
        """)
        inactive_devices = cursor.fetchone()["count"]

        # Devices by MS Project version
        cursor.execute("""
            SELECT
                ms_project_version,
                COUNT(*) as count
            FROM activations
            WHERE is_active = TRUE
            GROUP BY ms_project_version
            ORDER BY count DESC
        """)
        by_version = cursor.fetchall()

        # Devices by organization (top 10)
        cursor.execute("""
            SELECT
                o.org_name,
                o.org_id,
                COUNT(CASE WHEN a.is_active = TRUE THEN 1 END) as active_devices
            FROM organizations o
            LEFT JOIN users u ON o.org_id = u.org_id
            LEFT JOIN activations a ON u.user_id = a.user_id
            GROUP BY o.org_id, o.org_name
            HAVING active_devices > 0
            ORDER BY active_devices DESC
            LIMIT 10
        """)
        top_orgs = cursor.fetchall()

        # Recent activations (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM activations
            WHERE activated_at >= datetime('now', '-7 days')
        """)
        recent_activations = cursor.fetchone()["count"]

        # Recent deactivations (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM activations
            WHERE deactivated_at >= datetime('now', '-7 days')
        """)
        recent_deactivations = cursor.fetchone()["count"]

        return {
            "total_active_devices": active_devices,
            "total_inactive_devices": inactive_devices,
            "by_ms_project_version": [dict(v) for v in by_version],
            "top_organizations": [dict(org) for org in top_orgs],
            "recent_activations_7d": recent_activations,
            "recent_deactivations_7d": recent_deactivations
        }


@router.delete("/portal/founder/activations/{activation_id}")
async def founder_deactivate_device(activation_id: str, user_data: dict = Depends(require_super_admin_role)):
    """
    Deactivate a specific device activation (super admin support function)
    Can deactivate any device across any organization for support purposes
    """
    admin_user_id = user_data["user_id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get activation details
        cursor.execute("""
            SELECT
                a.activation_id,
                a.user_id,
                a.device_name,
                a.is_active,
                u.email,
                u.org_id,
                o.org_name
            FROM activations a
            JOIN users u ON a.user_id = u.user_id
            JOIN organizations o ON u.org_id = o.org_id
            WHERE a.activation_id = ?
        """, (activation_id,))

        activation = cursor.fetchone()

        if not activation:
            raise HTTPException(status_code=404, detail="Activation not found")

        if not activation["is_active"]:
            return {"message": "Device already deactivated"}

        org_id = activation["org_id"]

        # Deactivate the device
        cursor.execute("""
            UPDATE activations
            SET is_active = FALSE, deactivated_at = CURRENT_TIMESTAMP
            WHERE activation_id = ?
        """, (activation_id,))

        # Decrement seats_used for the organization
        cursor.execute("""
            UPDATE organizations
            SET seats_used = seats_used - 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE org_id = ?
        """, (org_id,))

        # Log action
        cursor.execute("""
            INSERT INTO audit_logs (log_id, org_id, user_id, action, resource_type, resource_id, metadata, timestamp)
            VALUES (?, ?, ?, 'device_deactivated_by_support', 'activation', ?, ?, CURRENT_TIMESTAMP)
        """, (
            secrets.token_urlsafe(16),
            org_id,
            admin_user_id,
            activation_id,
            json.dumps({
                "device_name": activation["device_name"],
                "user_email": activation["email"],
                "org_name": activation["org_name"],
                "deactivated_by_support": admin_user_id,
                "reason": "Support intervention"
            })
        ))

        conn.commit()

        logger.info(f"Device deactivated by super admin: activation_id={activation_id}, org={activation['org_name']}, admin={admin_user_id}")

        return {
            "message": "Device deactivated successfully",
            "activation_id": activation_id,
            "device_name": activation["device_name"],
            "user_email": activation["email"],
            "org_name": activation["org_name"]
        }


# ============================================================================
# STRIPE INTEGRATION ENDPOINTS (for future use)
# ============================================================================

@router.post("/portal/billing/add-seats")
async def add_seats(seats_to_add: int, user_data: dict = Depends(require_admin_role)):
    """
    Purchase additional seats via Stripe
    Creates Stripe Checkout Session and returns checkout URL

    TODO: Implement Stripe integration
    """
    org_id = user_data["org_id"]

    # TODO: Calculate new pricing tier based on total seats
    # TODO: Create Stripe Checkout Session
    # TODO: Return checkout URL

    return {
        "message": "Stripe integration not yet implemented",
        "seats_to_add": seats_to_add
    }


@router.post("/webhooks/stripe")
async def stripe_webhook(payload: dict):
    """
    Stripe webhook handler
    Processes subscription events: created, updated, deleted, payment succeeded/failed

    TODO: Implement Stripe webhook processing
    """
    event_type = payload.get("type")

    # TODO: Verify webhook signature
    # TODO: Process event based on type
    # TODO: Update organizations, invoices, payment_methods tables

    logger.info(f"Received Stripe webhook: {event_type}")

    return {"received": True}
