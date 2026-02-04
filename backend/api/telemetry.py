"""
Telemetry API - Collects anonymized usage data for ML learning
Privacy-focused: User IDs are hashed, no PII is collected
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class TelemetryEvent(BaseModel):
    """Single telemetry event"""
    event_type: str
    timestamp: str
    user_id: str
    properties: Dict[str, Any] = {}


class TelemetryBatch(BaseModel):
    """Batch of telemetry events from client"""
    user_id: str
    events: List[TelemetryEvent]


@router.post("/telemetry/batch")
async def receive_telemetry_batch(batch: TelemetryBatch):
    """
    Receive batch of telemetry events for ML learning

    Privacy-focused:
    - User IDs are SHA256 hashes (cannot be reversed)
    - No PII is collected
    - Data is used only for improving duration predictions and recommendations

    Future: Store in database for ML model training
    Currently: Log for development/testing
    """
    try:
        logger.info(f"Received telemetry batch: {len(batch.events)} events from user {batch.user_id[:8]}...")

        # Log events for development (will be stored in DB for ML training in production)
        for event in batch.events:
            logger.debug(f"Event: {event.event_type} at {event.timestamp}")

            # Key events for ML learning
            if event.event_type == "TaskCompleted":
                # Track actual vs estimated duration for ML model improvement
                estimated = event.properties.get("estimated_duration_days", 0)
                actual = event.properties.get("actual_duration_days", 0)
                variance = event.properties.get("variance_days", 0)
                category = event.properties.get("category", "")
                phase = event.properties.get("phase", "")
                country = event.properties.get("country", "")

                logger.info(f"Task completion: category={category}, phase={phase}, country={country}, "
                          f"estimated={estimated:.1f}d, actual={actual:.1f}d, variance={variance:.1f}d")

        return {
            "status": "success",
            "events_received": len(batch.events),
            "message": "Telemetry data received successfully"
        }

    except Exception as e:
        logger.error(f"Telemetry batch processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process telemetry batch: {str(e)}"
        )


@router.get("/telemetry/stats")
async def get_telemetry_stats():
    """
    Get telemetry collection statistics (for monitoring)

    Returns aggregated, anonymized statistics about data collection
    No individual user data is exposed
    """
    # Future: Return aggregated stats from database
    return {
        "status": "active",
        "message": "Telemetry collection is active. Stats will be available after data accumulation."
    }
