"""
Admin API - Internal endpoints for managing organizations and licenses

WARNING: These endpoints should be protected with proper authentication in production.
For now, they're simple endpoints for testing and development.
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import secrets
import os
import logging

from database.connection import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/admin/test")
async def test_admin():
    """Simple test endpoint to verify admin router works"""
    return {"status": "admin router works", "db_type": os.getenv("DATABASE_URL", "sqlite")}

# Simple admin token for basic protection (set via environment variable)
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev-admin-token-change-this")


# ============================================================================
# Pydantic Models
# ============================================================================

class CreateOrgRequest(BaseModel):
    """Request to create a new organization"""
    org_name: str
    tier: str  # 'professional' or 'enterprise'
    seats_purchased: int
    subscription_days: int = 365  # Default 1 year
    primary_contact_email: EmailStr
    primary_contact_name: str


class CreateOrgResponse(BaseModel):
    """Response with org details and license key"""
    org_id: str
    org_name: str
    license_key: str
    tier: str
    seats_purchased: int
    subscription_end: str
    message: str


class ListOrgsResponse(BaseModel):
    """List of organizations"""
    organizations: list


# ============================================================================
# Helper Functions
# ============================================================================

def verify_admin_token(x_admin_token: str = Header(None)):
    """Verify admin token from request header"""
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token")
    return True


def generate_org_id():
    """Generate unique organization ID"""
    return f"org_{secrets.token_urlsafe(12)}"


def generate_license_key():
    """Generate a license key in format: ILANA-XXXX-XXXX-XXXX-XXXX"""
    parts = [secrets.token_hex(2).upper() for _ in range(4)]
    return f"ILANA-{'-'.join(parts)}"


# ============================================================================
# Admin Endpoints
# ============================================================================

@router.post("/admin/organizations", response_model=CreateOrgResponse)
async def create_organization(request: CreateOrgRequest, admin_verified: str = Header(None, alias="X-Admin-Token")):
    """
    Create a new organization with a license key (Admin only)

    Requires X-Admin-Token header for authentication.

    Example:
        curl -X POST "https://ilanapm.onrender.com/api/v1/admin/organizations" \\
             -H "Content-Type: application/json" \\
             -H "X-Admin-Token: your-admin-token" \\
             -d '{
               "org_name": "Test Org",
               "tier": "professional",
               "seats_purchased": 5,
               "primary_contact_email": "admin@test.com",
               "primary_contact_name": "Test Admin"
             }'
    """
    try:
        # Verify admin token
        if admin_verified != ADMIN_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid admin token. Set X-Admin-Token header.")

        # Validate tier
        if request.tier not in ['professional', 'enterprise']:
            raise HTTPException(status_code=400, detail="Tier must be 'professional' or 'enterprise'")

        # Validate seats
        if request.seats_purchased < 1:
            raise HTTPException(status_code=400, detail="seats_purchased must be at least 1")

        # Generate IDs
        org_id = generate_org_id()
        license_key = generate_license_key()

        # Calculate subscription dates
        subscription_start = datetime.now().date()
        subscription_end = (datetime.now() + timedelta(days=request.subscription_days)).date()

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Create organization
            cursor.execute("""
                INSERT INTO organizations (
                    org_id, org_name, tier, seats_purchased, seats_used,
                    subscription_start, subscription_end, status,
                    primary_contact_email, primary_contact_name
                )
                VALUES (?, ?, ?, ?, 0, ?, ?, 'active', ?, ?)
            """, (
                org_id,
                request.org_name,
                request.tier,
                request.seats_purchased,
                subscription_start,
                subscription_end,
                request.primary_contact_email,
                request.primary_contact_name
            ))

            # Create license key
            cursor.execute("""
                INSERT INTO license_keys (
                    license_key, org_id, tier, seats, is_active
                )
                VALUES (?, ?, ?, ?, TRUE)
            """, (license_key, org_id, request.tier, request.seats_purchased))

            logger.info(f"✅ Created organization: {org_id} ({request.org_name}) with license: {license_key}")

            return CreateOrgResponse(
                org_id=org_id,
                org_name=request.org_name,
                license_key=license_key,
                tier=request.tier,
                seats_purchased=request.seats_purchased,
                subscription_end=subscription_end.isoformat(),
                message=f"Organization created successfully. Use license key to activate desktop add-in."
            )
    except Exception as e:
        logger.error(f"❌ Failed to create organization: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/admin/organizations")
async def list_organizations(admin_verified: str = Header(None, alias="X-Admin-Token")):
    """
    List all organizations (Admin only)

    Requires X-Admin-Token header for authentication.
    """
    try:
        # Verify admin token
        if admin_verified != ADMIN_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid admin token. Set X-Admin-Token header.")

        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    o.org_id,
                    o.org_name,
                    o.tier,
                    o.seats_purchased,
                    o.seats_used,
                    o.subscription_start,
                    o.subscription_end,
                    o.status,
                    lk.license_key
                FROM organizations o
                LEFT JOIN license_keys lk ON o.org_id = lk.org_id
                ORDER BY o.created_at DESC
            """)

            orgs = []
            for row in cursor.fetchall():
                orgs.append({
                    'org_id': row['org_id'],
                    'org_name': row['org_name'],
                    'tier': row['tier'],
                    'seats_purchased': row['seats_purchased'],
                    'seats_used': row['seats_used'],
                    'subscription_start': row['subscription_start'],
                    'subscription_end': row['subscription_end'],
                    'status': row['status'],
                    'license_key': row['license_key']
                })

            return {'organizations': orgs}
    except Exception as e:
        logger.error(f"❌ Failed to list organizations: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/admin/organizations/{org_id}")
async def delete_organization(org_id: str, admin_verified: str = Header(None, alias="X-Admin-Token")):
    """
    Delete an organization and all associated data (Admin only)

    Requires X-Admin-Token header for authentication.
    WARNING: This cascades to all users, activations, and license keys.
    """
    # Verify admin token
    if admin_verified != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid admin token. Set X-Admin-Token header.")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if org exists
        cursor.execute("SELECT org_name FROM organizations WHERE org_id = ?", (org_id,))
        org = cursor.fetchone()

        if not org:
            raise HTTPException(status_code=404, detail=f"Organization {org_id} not found")

        # Delete organization (cascades to all related records)
        cursor.execute("DELETE FROM organizations WHERE org_id = ?", (org_id,))

        logger.info(f"🗑️  Deleted organization: {org_id} ({org['org_name']})")

    return {
        'message': f"Organization {org_id} deleted successfully",
        'org_id': org_id
    }
