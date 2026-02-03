"""
Licensing API - Desktop add-in license activation and validation

Handles:
- License key activation (one-time per device)
- JWT token generation and validation
- Seat management and availability checking
- Subscription status verification
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
import secrets
import logging
import json

from database.connection import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter()

# JWT Configuration
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    # Fallback for development only (not secure for production)
    SECRET_KEY = "dev-secret-key-change-in-production"
    logger.warning("⚠️  JWT_SECRET_KEY not set! Using insecure development key. Set JWT_SECRET_KEY environment variable for production.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 90  # 90-day token expiry with auto-refresh


# ============================================================================
# Pydantic Models
# ============================================================================

class ActivationRequest(BaseModel):
    """License activation request from desktop add-in"""
    license_key: str
    user_email: EmailStr
    device_id: str  # Hashed MAC address
    device_name: Optional[str] = None
    ms_project_version: Optional[str] = None
    addin_version: Optional[str] = None


class ActivationResponse(BaseModel):
    """License activation response with JWT token"""
    activation_token: str
    org_id: str
    user_id: str
    tier: str
    expires_at: str
    message: str


class ValidationRequest(BaseModel):
    """Token validation request"""
    token: str


class ValidationResponse(BaseModel):
    """Token validation response"""
    user_id: str
    org_id: str
    tier: str
    is_valid: bool
    subscription_end: str


class LicenseInfo(BaseModel):
    """License information for Settings display"""
    tier: str
    seats_purchased: int
    seats_used: int
    subscription_end: str
    org_name: str


# ============================================================================
# Helper Functions
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def generate_user_id() -> str:
    """Generate unique user ID"""
    return f"usr_{secrets.token_urlsafe(16)}"


def generate_activation_id() -> str:
    """Generate unique activation ID"""
    return f"act_{secrets.token_urlsafe(16)}"


def generate_audit_log_id() -> str:
    """Generate unique audit log ID"""
    return f"log_{secrets.token_urlsafe(16)}"


def log_audit_event(org_id: str, user_id: str, action: str, resource_type: str,
                     resource_id: str, metadata: dict, ip_address: Optional[str] = None):
    """Create audit log entry"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (log_id, org_id, user_id, ip_address, action,
                                     resource_type, resource_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            generate_audit_log_id(),
            org_id,
            user_id,
            ip_address,
            action,
            resource_type,
            resource_id,
            json.dumps(metadata)
        ))


# ============================================================================
# License Activation Endpoint
# ============================================================================

@router.post("/licensing/activate", response_model=ActivationResponse)
async def activate_license(request: ActivationRequest):
    """
    Activate a license key and return JWT token for desktop add-in

    Flow:
    1. Validate license key exists and is active
    2. Check organization subscription is active
    3. Check seat availability (seats_used < seats_purchased)
    4. Create or retrieve user record
    5. Create or update activation record
    6. Generate JWT token (90-day expiry)
    7. Return activation token
    """
    logger.info(f"License activation request: email={request.user_email}, device={request.device_id[:8]}...")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Step 1: Validate license key
        cursor.execute("""
            SELECT lk.*, o.org_name, o.tier as org_tier, o.seats_purchased, o.seats_used,
                   o.subscription_end, o.status as org_status
            FROM license_keys lk
            JOIN organizations o ON lk.org_id = o.org_id
            WHERE lk.license_key = ?
        """, (request.license_key,))

        license_row = cursor.fetchone()
        if not license_row:
            logger.warning(f"Invalid license key: {request.license_key}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid license key"
            )

        # Check if license is active
        if not license_row['is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="License key has been deactivated"
            )

        # Check if license is expired
        if license_row['expires_at']:
            expires_at = datetime.fromisoformat(license_row['expires_at']).date() if isinstance(license_row['expires_at'], str) else license_row['expires_at']
            if expires_at < datetime.now().date():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="License key has expired"
                )

        org_id = license_row['org_id']
        tier = license_row['org_tier']

        # Step 2: Check organization subscription status
        if license_row['org_status'] != 'active':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Organization subscription is {license_row['org_status']}"
            )

        # Check if subscription has expired
        subscription_end = datetime.fromisoformat(license_row['subscription_end']).date() if isinstance(license_row['subscription_end'], str) else license_row['subscription_end']
        if subscription_end < datetime.now().date():
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Subscription has expired. Please renew to continue using Ilana PM."
            )

        # Step 3: Check seat availability
        # First, check if this user+device already has an activation (reactivation scenario)
        cursor.execute("""
            SELECT user_id FROM users WHERE email = ? AND org_id = ?
        """, (request.user_email, org_id))

        existing_user = cursor.fetchone()

        if existing_user:
            user_id = existing_user['user_id']

            # Check if this device already has an activation
            cursor.execute("""
                SELECT activation_id FROM activations
                WHERE user_id = ? AND device_id = ? AND is_active = 1
            """, (user_id, request.device_id))

            existing_activation = cursor.fetchone()

            if not existing_activation:
                # New device for existing user - check seat availability
                if license_row['seats_used'] >= license_row['seats_purchased']:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"No seats available. Organization has {license_row['seats_purchased']} seats, all in use."
                    )
        else:
            # New user - check seat availability
            if license_row['seats_used'] >= license_row['seats_purchased']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"No seats available. Organization has {license_row['seats_purchased']} seats, all in use."
                )

        # Step 4: Create or retrieve user record
        if not existing_user:
            user_id = generate_user_id()

            # Extract first/last name from email (basic)
            email_parts = request.user_email.split('@')[0].split('.')
            first_name = email_parts[0].capitalize() if len(email_parts) > 0 else ""
            last_name = email_parts[1].capitalize() if len(email_parts) > 1 else ""

            cursor.execute("""
                INSERT INTO users (user_id, org_id, email, first_name, last_name, role, is_active)
                VALUES (?, ?, ?, ?, ?, 'user', 1)
            """, (user_id, org_id, request.user_email, first_name, last_name))

            logger.info(f"Created new user: {user_id} ({request.user_email})")
        else:
            user_id = existing_user['user_id']
            logger.info(f"Using existing user: {user_id} ({request.user_email})")

        # Step 5: Create or update activation record
        cursor.execute("""
            SELECT activation_id, is_active FROM activations
            WHERE user_id = ? AND device_id = ?
        """, (user_id, request.device_id))

        existing_activation = cursor.fetchone()

        # Generate JWT token
        token_expires_at = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        token_data = {
            "user_id": user_id,
            "org_id": org_id,
            "tier": tier
        }
        activation_token = create_access_token(token_data)

        if existing_activation:
            activation_id = existing_activation['activation_id']

            # Update existing activation
            cursor.execute("""
                UPDATE activations
                SET activation_token = ?,
                    token_expires_at = ?,
                    is_active = 1,
                    activated_at = CURRENT_TIMESTAMP,
                    deactivated_at = NULL,
                    ms_project_version = ?,
                    addin_version = ?,
                    device_name = ?
                WHERE activation_id = ?
            """, (
                activation_token,
                token_expires_at.isoformat(),
                request.ms_project_version,
                request.addin_version,
                request.device_name,
                activation_id
            ))

            logger.info(f"Reactivated existing activation: {activation_id}")
        else:
            activation_id = generate_activation_id()

            # Create new activation
            cursor.execute("""
                INSERT INTO activations (
                    activation_id, user_id, license_key, device_id, device_name,
                    activation_token, token_expires_at, is_active,
                    ms_project_version, addin_version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
            """, (
                activation_id,
                user_id,
                request.license_key,
                request.device_id,
                request.device_name,
                activation_token,
                token_expires_at.isoformat(),
                request.ms_project_version,
                request.addin_version
            ))

            # Increment seats_used for new activation
            cursor.execute("""
                UPDATE organizations
                SET seats_used = seats_used + 1
                WHERE org_id = ?
            """, (org_id,))

            logger.info(f"Created new activation: {activation_id}")

        # Step 6: Update user last_login
        cursor.execute("""
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?
        """, (user_id,))

        # Step 7: Create audit log
        log_audit_event(
            org_id=org_id,
            user_id=user_id,
            action="license_activated",
            resource_type="activation",
            resource_id=activation_id,
            metadata={
                "license_key": request.license_key,
                "device_id": request.device_id,
                "device_name": request.device_name,
                "ms_project_version": request.ms_project_version,
                "addin_version": request.addin_version
            }
        )

        logger.info(f"✅ License activated successfully: user={user_id}, org={org_id}, tier={tier}")

        return ActivationResponse(
            activation_token=activation_token,
            org_id=org_id,
            user_id=user_id,
            tier=tier,
            expires_at=token_expires_at.isoformat(),
            message="License activated successfully"
        )


# ============================================================================
# Token Validation Endpoint
# ============================================================================

@router.post("/licensing/validate", response_model=ValidationResponse)
async def validate_token(request: ValidationRequest):
    """
    Validate JWT token and check subscription status

    Called by desktop add-in before each API request to verify authentication.
    """
    # Decode JWT token
    try:
        payload = decode_token(request.token)
    except HTTPException:
        return ValidationResponse(
            user_id="",
            org_id="",
            tier="",
            is_valid=False,
            subscription_end=""
        )

    user_id = payload.get("user_id")
    org_id = payload.get("org_id")
    tier = payload.get("tier")

    if not user_id or not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Check subscription status in database
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT subscription_end, status FROM organizations WHERE org_id = ?
        """, (org_id,))

        org = cursor.fetchone()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check if subscription is active
        if org['status'] != 'active':
            return ValidationResponse(
                user_id=user_id,
                org_id=org_id,
                tier=tier,
                is_valid=False,
                subscription_end=org['subscription_end']
            )

        # Check if subscription has expired
        subscription_end = datetime.fromisoformat(org['subscription_end']).date() if isinstance(org['subscription_end'], str) else org['subscription_end']
        if subscription_end < datetime.now().date():
            return ValidationResponse(
                user_id=user_id,
                org_id=org_id,
                tier=tier,
                is_valid=False,
                subscription_end=org['subscription_end']
            )

        # Update last_api_call timestamp
        cursor.execute("""
            UPDATE activations
            SET last_api_call = CURRENT_TIMESTAMP,
                api_call_count = api_call_count + 1
            WHERE user_id = ? AND is_active = 1
        """, (user_id,))

        return ValidationResponse(
            user_id=user_id,
            org_id=org_id,
            tier=tier,
            is_valid=True,
            subscription_end=org['subscription_end']
        )


# ============================================================================
# License Info Endpoint (for Settings UI)
# ============================================================================

@router.get("/licensing/info", response_model=LicenseInfo)
async def get_license_info(token: str):
    """
    Get license information for display in desktop add-in Settings

    Shows: tier, seats used/purchased, subscription expiry, org name
    """
    # Decode JWT token
    payload = decode_token(token)
    org_id = payload.get("org_id")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT org_name, tier, seats_purchased, seats_used, subscription_end
            FROM organizations
            WHERE org_id = ?
        """, (org_id,))

        org = cursor.fetchone()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        return LicenseInfo(
            tier=org['tier'],
            seats_purchased=org['seats_purchased'],
            seats_used=org['seats_used'],
            subscription_end=org['subscription_end'],
            org_name=org['org_name']
        )
