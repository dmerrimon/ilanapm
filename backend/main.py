"""
Ilana PM - FastAPI Application Entry Point

This is the main application file that initializes the FastAPI app
and registers all API routes.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from jose import JWTError, jwt
from datetime import datetime

from api import health, validate, config, analytics, advisory, teams, feedback, templates, licensing, admin, debug, telemetry
from database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# JWT Configuration
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    # Fallback for development only (not secure for production)
    SECRET_KEY = "dev-secret-key-change-in-production"
    logger.warning("⚠️  JWT_SECRET_KEY not set! Using insecure development key. Set JWT_SECRET_KEY environment variable for production.")

ALGORITHM = "HS256"

# Security
security = HTTPBearer()


# ============================================================================
# JWT Authentication Middleware
# ============================================================================

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify JWT token from Authorization header

    Returns payload with user_id, org_id, tier if valid.
    Raises 401 HTTPException if invalid.

    Usage in protected endpoints:
        @router.get("/protected")
        async def protected_route(auth: dict = Depends(verify_token)):
            user_id = auth["user_id"]
            org_id = auth["org_id"]
            tier = auth["tier"]
    """
    token = credentials.credentials

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("user_id")
        org_id = payload.get("org_id")
        tier = payload.get("tier")

        if not user_id or not org_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if token is expired (JWT library handles this, but double-check)
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # TODO: Check subscription status in database for extra security
        # For now, we trust the JWT token

        return {
            "user_id": user_id,
            "org_id": org_id,
            "tier": tier
        }

    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Create FastAPI application
app = FastAPI(
    title="Ilana PM Intelligence API",
    description="Clinical trial timeline validation and advisory service for Microsoft Project",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for web add-in and admin portals
# NOTE: For development, we allow localhost. In production, use specific domains.
allowed_origins = [
    "https://portal.ilanapm.com",  # Customer admin portal
    "https://admin.ilanapm.com",   # Internal super admin portal
    "https://ilanapm.com",          # Marketing website
    "http://localhost:3000",        # Local development (Next.js)
    "http://localhost:5173",        # Local development (Vite)
    "http://127.0.0.1:3000",        # Local development (Next.js)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register API routes
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(licensing.router, prefix="/api/v1", tags=["licensing"])  # NEW: License activation & validation
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])  # NEW: Admin endpoints for org/license management
app.include_router(debug.router, prefix="/api/v1", tags=["debug"])  # Debug endpoints
app.include_router(validate.router, prefix="/api/v1", tags=["validation"])
app.include_router(config.router, prefix="/api/v1", tags=["configuration"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(advisory.router, prefix="/api/v1", tags=["advisory"])
app.include_router(teams.router, prefix="/api/v1", tags=["teams"])
app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])
app.include_router(templates.router, prefix="/api/v1", tags=["templates"])
app.include_router(telemetry.router, prefix="/api/v1", tags=["telemetry"])  # ML feedback loop


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Ilana PM Intelligence API starting up...")

    # Initialize feedback database
    try:
        init_db()
        logger.info("💾 Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

    # Start scheduled tasks (ML model monitoring and retraining)
    try:
        from scheduled_tasks import setup_scheduled_tasks
        scheduler = setup_scheduled_tasks()
        app.state.scheduler = scheduler
        logger.info("🔄 Scheduled tasks started (model monitoring & retraining)")
    except Exception as e:
        logger.warning(f"⚠️  Could not start scheduled tasks: {e}")

    logger.info("📍 API documentation available at: /docs")
    logger.info("🔐 Licensing endpoints: /api/v1/licensing/* (NEW)")
    logger.info("✅ Validation endpoints: /api/v1/validate")
    logger.info("📊 Analytics endpoints: /api/v1/analytics/*")
    logger.info("🤖 ML Advisory endpoints: /api/v1/advisory/*")
    logger.info("⚙️  Configuration endpoints: /api/v1/config/*")
    logger.info("📋 Template endpoints: /api/v1/templates/*")
    logger.info("📢 Teams integration: /api/v1/teams/*")
    logger.info("📝 Feedback endpoints: /api/v1/feedback/*")
    logger.info("❤️  Health check: /api/v1/health")
    logger.info("")
    logger.info("🔒 JWT authentication enabled for protected endpoints")
    logger.info("🌐 CORS configured for: portal.ilanapm.com, admin.ilanapm.com, localhost")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 Ilana PM Intelligence API shutting down...")

    # Shutdown scheduler if running
    if hasattr(app.state, 'scheduler'):
        try:
            app.state.scheduler.shutdown()
            logger.info("🔄 Scheduled tasks stopped")
        except Exception as e:
            logger.warning(f"⚠️  Error stopping scheduler: {e}")


@app.get("/")
async def root():
    """Root endpoint - basic info about the API"""
    return {
        "name": "Ilana PM Intelligence API",
        "version": "0.1.0",
        "description": "Clinical trial timeline validation and advisory service",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
