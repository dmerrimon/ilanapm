"""
Health Check Endpoints

Provides health check and status endpoints for monitoring
"""

from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    version: str
    message: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns:
        HealthResponse with current status and timestamp
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0",
        message="Ilana PM Intelligence API is running"
    )


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes/Azure deployments

    Returns:
        Simple ready status
    """
    # TODO: Add checks for:
    # - Configuration files loaded
    # - Database connections (if applicable)
    # - External services availability

    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/live")
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes/Azure deployments

    Returns:
        Simple alive status
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
