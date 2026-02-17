"""
Dashboard API Endpoints (REMOVED)

HISTORICAL NOTE:
This file previously contained Leadership Dashboard and Portfolio Intelligence endpoints.
These features have been removed as part of the tracker-centric architecture redesign.

New tracker upload system uses:
- /api/v1/trackers/upload (in portal.py) - Upload trackers with signal extraction
- /api/v1/account/trackers/* (in account_management.py) - Tracker configuration
- /api/v1/signals/* (in signals.py) - Signal retrieval and escalations

The dashboard functionality has been replaced with direct tracker uploads,
signal extraction, and escalation management.

This file is kept for historical reference only. All endpoints have been removed.
"""

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# All dashboard endpoints have been removed (2026-02-17)
# See portal.py for tracker upload endpoints
# See account_management.py for tracker configuration endpoints
# See signals.py for signal and escalation retrieval endpoints
