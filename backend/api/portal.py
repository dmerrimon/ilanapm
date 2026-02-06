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

        return {
            "org_name": org["org_name"],
            "license_key": masked_license,
            "status": org["status"],
            "tier": org["tier"],
            "seats_purchased": org["seats_purchased"],
            "seats_used": org["seats_used"],
            "seats_available": org["seats_purchased"] - org["seats_used"],
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
    Shows: email, name, role, activation status, last login
    """
    org_id = user_data["org_id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                user_id, email, first_name, last_name, role,
                is_active, last_login, created_at
            FROM users
            WHERE org_id = ?
            ORDER BY created_at DESC
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

        # Decrement seats_used
        cursor.execute("""
            UPDATE organizations
            SET seats_used = seats_used - 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE org_id = ?
        """, (org_id,))

        # Log action
        cursor.execute("""
            INSERT INTO audit_logs (log_id, org_id, user_id, action, resource_type, resource_id, metadata, timestamp)
            VALUES (?, ?, ?, 'user_deactivated', 'user', ?, ?, CURRENT_TIMESTAMP)
        """, (
            secrets.token_urlsafe(16),
            org_id,
            admin_user_id,
            user_id,
            json.dumps({"deactivated_by": admin_user_id})
        ))

        conn.commit()

        return {
            "message": "User deactivated successfully",
            "user_id": user_id
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
