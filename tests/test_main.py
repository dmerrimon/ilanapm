"""
Tests for main FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns basic API info"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Ilana PM Intelligence API"
    assert data["version"] == "0.1.0"
    assert "docs" in data
    assert "health" in data


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
    assert "message" in data


def test_readiness_endpoint():
    """Test readiness check endpoint"""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert "timestamp" in data


def test_liveness_endpoint():
    """Test liveness check endpoint"""
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["alive"] is True
    assert "timestamp" in data


def test_openapi_docs():
    """Test that OpenAPI documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_docs():
    """Test that ReDoc documentation is available"""
    response = client.get("/redoc")
    assert response.status_code == 200
