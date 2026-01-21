"""
Ilana PM - FastAPI Application Entry Point

This is the main application file that initializes the FastAPI app
and registers all API routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.api import health, validate, config, analytics, advisory, teams, feedback, templates
from backend.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Ilana PM Intelligence API",
    description="Clinical trial timeline validation and advisory service for Microsoft Project",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for web add-in
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(validate.router, prefix="/api/v1", tags=["validation"])
app.include_router(config.router, prefix="/api/v1", tags=["configuration"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(advisory.router, prefix="/api/v1", tags=["advisory"])
app.include_router(teams.router, prefix="/api/v1", tags=["teams"])
app.include_router(feedback.router, prefix="/api/v1", tags=["feedback"])
app.include_router(templates.router, prefix="/api/v1", tags=["templates"])


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("🚀 Ilana PM Intelligence API starting up...")

    # Initialize feedback database
    try:
        init_db()
        logger.info("💾 Feedback database initialized")
    except Exception as e:
        logger.warning(f"⚠️  Database initialization skipped (already exists): {e}")

    logger.info("📍 API documentation available at: /docs")
    logger.info("✅ Validation endpoints: /api/v1/validate")
    logger.info("📊 Analytics endpoints: /api/v1/analytics/*")
    logger.info("🤖 ML Advisory endpoints: /api/v1/advisory/*")
    logger.info("⚙️  Configuration endpoints: /api/v1/config/*")
    logger.info("📋 Template endpoints: /api/v1/templates/*")
    logger.info("📢 Teams integration: /api/v1/teams/*")
    logger.info("📝 Feedback endpoints: /api/v1/feedback/*")
    logger.info("❤️  Health check: /api/v1/health")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("👋 Ilana PM Intelligence API shutting down...")


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
