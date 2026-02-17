"""
Account Management API Endpoints

Provides REST API for Account Admin functions:
- User & seat management
- Tracker configuration (column mappings)
- Organization settings
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import uuid
import logging
from pathlib import Path
import pandas as pd
from database.connection import get_db_connection

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class ColumnMappingRequest(BaseModel):
    """Request to save column mappings"""
    org_id: str
    tracker_type: str = Field(..., description="Tracker type: risk_log, tmf_completeness, budget, vendor")
    column_mappings: Dict[str, str] = Field(..., description="Map: org_column_name -> seleen_field_name")
    transformation_rules: Optional[Dict] = Field(None, description="Optional transformation rules")


class TrackerTemplateDownload(BaseModel):
    """Response for template download"""
    tracker_type: str
    template_url: str
    required_columns: List[str]
    optional_columns: List[str]


# ============================================================================
# Tracker Configuration Endpoints
# ============================================================================

@router.get("/account/trackers/available")
async def get_available_trackers(
    org_id: str = Query(..., description="Organization ID")
):
    """
    Get list of available tracker types

    Returns all tracker definitions that can be configured.

    **Response:**
    ```json
    {
      "trackers": [
        {
          "tracker_type": "risk_log",
          "tracker_name": "Risk Log",
          "required_fields": ["risk_number", "category", "risk_detail", ...],
          "optional_fields": ["mitigation_plan", "owner", ...],
          "is_configured": true
        },
        {
          "tracker_type": "tmf_completeness",
          "tracker_name": "TMF Completeness Tracker",
          "required_fields": ["artifact_number", "artifact_name", "status"],
          "optional_fields": [...],
          "is_configured": false
        }
      ]
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all tracker definitions
        cursor.execute("""
            SELECT tracker_def_id, tracker_name, tracker_type, schema_definition
            FROM tracker_definitions
            ORDER BY tracker_name
        """)

        trackers = []
        for row in cursor.fetchall():
            schema = json.loads(row['schema_definition'])

            # Check if configured for this org
            cursor.execute("""
                SELECT mapping_id
                FROM tracker_column_mappings
                WHERE org_id = ? AND tracker_type = ?
            """, (org_id, row['tracker_type']))

            is_configured = cursor.fetchone() is not None

            trackers.append({
                "tracker_type": row['tracker_type'],
                "tracker_name": row['tracker_name'],
                "required_fields": [f['field_name'] for f in schema.get('required_fields', [])],
                "optional_fields": [f['field_name'] for f in schema.get('optional_fields', [])],
                "is_configured": is_configured
            })

        conn.close()

        return {"trackers": trackers}

    except Exception as e:
        logger.error(f"Failed to get available trackers: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available trackers: {str(e)}"
        )


@router.post("/account/trackers/upload-sample")
async def upload_sample_tracker(
    org_id: str = Query(..., description="Organization ID"),
    tracker_type: str = Query(..., description="Tracker type"),
    file: UploadFile = File(...)
):
    """
    Upload sample tracker file for column mapping

    Account Admin uploads sample file, system detects columns and suggests mappings.

    **Response:**
    ```json
    {
      "detected_columns": ["ID", "Risk Type", "Description", "Severity", ...],
      "suggested_mappings": {
        "ID": "risk_number",
        "Risk Type": "category",
        "Description": "risk_detail",
        ...
      },
      "required_fields": ["risk_number", "category", "risk_detail", ...],
      "unmapped_required": ["probability"]
    }
    ```
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Must be Excel (.xlsx, .xls) or CSV (.csv)"
            )

        # Read file to detect columns
        contents = await file.read()

        if file.filename.endswith('.csv'):
            import io
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        detected_columns = df.columns.tolist()

        # Get tracker schema
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT schema_definition
            FROM tracker_definitions
            WHERE tracker_type = ?
        """, (tracker_type,))

        tracker_row = cursor.fetchone()
        if not tracker_row:
            conn.close()
            raise HTTPException(status_code=404, detail="Tracker type not found")

        schema = json.loads(tracker_row['schema_definition'])
        conn.close()

        required_fields = [f['field_name'] for f in schema.get('required_fields', [])]

        # Auto-suggest mappings (simple fuzzy matching)
        suggested_mappings = {}
        for org_col in detected_columns:
            org_col_lower = org_col.lower().strip()

            # Direct matches
            if org_col_lower in ['id', 'risk id', 'risk number', 'risk #']:
                suggested_mappings[org_col] = 'risk_number'
            elif org_col_lower in ['risk type', 'category', 'type']:
                suggested_mappings[org_col] = 'category'
            elif org_col_lower in ['description', 'risk description', 'risk detail', 'detail']:
                suggested_mappings[org_col] = 'risk_detail'
            elif org_col_lower in ['impact', 'severity']:
                suggested_mappings[org_col] = 'impact'
            elif org_col_lower in ['probability', 'likelihood']:
                suggested_mappings[org_col] = 'probability'
            elif org_col_lower in ['priority', 'score', 'risk score']:
                suggested_mappings[org_col] = 'priority'
            elif org_col_lower in ['mitigation', 'mitigation plan']:
                suggested_mappings[org_col] = 'mitigation_plan'
            elif org_col_lower in ['owner', 'risk owner']:
                suggested_mappings[org_col] = 'owner'
            elif org_col_lower in ['target date', 'due date', 'target']:
                suggested_mappings[org_col] = 'target_date'
            elif org_col_lower in ['status']:
                suggested_mappings[org_col] = 'status'
            elif org_col_lower in ['escalation notes', 'escalation']:
                suggested_mappings[org_col] = 'escalation_notes'

            # TMF fields
            elif org_col_lower in ['artifact number', 'artifact #', 'number']:
                suggested_mappings[org_col] = 'artifact_number'
            elif org_col_lower in ['artifact name', 'name', 'artifact']:
                suggested_mappings[org_col] = 'artifact_name'

        # Check which required fields are unmapped
        mapped_seleen_fields = set(suggested_mappings.values())
        unmapped_required = [f for f in required_fields if f not in mapped_seleen_fields]

        return {
            "detected_columns": detected_columns,
            "suggested_mappings": suggested_mappings,
            "required_fields": required_fields,
            "unmapped_required": unmapped_required,
            "sample_data": df.head(3).to_dict('records')  # First 3 rows for preview
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload sample tracker: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload sample tracker: {str(e)}"
        )


@router.post("/account/trackers/save-mapping")
async def save_column_mapping(
    mapping: ColumnMappingRequest,
    created_by: str = Query(..., description="User ID saving mapping")
):
    """
    Save column mappings for tracker

    Account Admin saves org-specific column mappings after reviewing suggestions.

    **Request Body:**
    ```json
    {
      "org_id": "org_123",
      "tracker_type": "risk_log",
      "column_mappings": {
        "ID": "risk_number",
        "Risk Type": "category",
        "Description": "risk_detail",
        "Severity": "impact",
        "Likelihood": "probability",
        "Score": "priority"
      }
    }
    ```

    **Response:**
    ```json
    {
      "success": true,
      "mapping_id": "map_123",
      "message": "Column mappings saved successfully. CPMs can now upload Risk Log via MS Project add-in."
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Validate tracker type exists
        cursor.execute("""
            SELECT tracker_def_id
            FROM tracker_definitions
            WHERE tracker_type = ?
        """, (mapping.tracker_type,))

        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="Tracker type not found")

        # Create or update mapping
        mapping_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT OR REPLACE INTO tracker_column_mappings (
                mapping_id, org_id, tracker_type, column_mappings,
                transformation_rules, created_by, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            mapping_id,
            mapping.org_id,
            mapping.tracker_type,
            json.dumps(mapping.column_mappings),
            json.dumps(mapping.transformation_rules) if mapping.transformation_rules else None,
            created_by
        ))

        conn.commit()
        conn.close()

        logger.info(f"Saved column mappings for {mapping.tracker_type} (org: {mapping.org_id})")

        return {
            "success": True,
            "mapping_id": mapping_id,
            "message": f"Column mappings saved successfully. CPMs can now upload {mapping.tracker_type} via MS Project add-in."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save column mapping: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save column mapping: {str(e)}"
        )


@router.get("/account/trackers/{tracker_type}/mapping")
async def get_column_mapping(
    tracker_type: str,
    org_id: str = Query(..., description="Organization ID")
):
    """
    Get existing column mappings for tracker

    Returns saved column mappings if configured.

    **Response:**
    ```json
    {
      "org_id": "org_123",
      "tracker_type": "risk_log",
      "column_mappings": {
        "ID": "risk_number",
        "Risk Type": "category",
        ...
      },
      "created_at": "2026-02-01T10:30:00Z",
      "updated_at": "2026-02-10T14:20:00Z"
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT column_mappings, transformation_rules, created_at, updated_at
            FROM tracker_column_mappings
            WHERE org_id = ? AND tracker_type = ?
        """, (org_id, tracker_type))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"No column mappings found for {tracker_type}. Please configure tracker first."
            )

        return {
            "org_id": org_id,
            "tracker_type": tracker_type,
            "column_mappings": json.loads(row['column_mappings']),
            "transformation_rules": json.loads(row['transformation_rules']) if row['transformation_rules'] else None,
            "created_at": row['created_at'],
            "updated_at": row['updated_at']
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get column mapping: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get column mapping: {str(e)}"
        )


@router.get("/account/trackers/{tracker_type}/template")
async def download_tracker_template(tracker_type: str):
    """
    Download standard tracker template

    Returns information about standard template and download URL.

    **Response:**
    ```json
    {
      "tracker_type": "risk_log",
      "template_name": "Risk_Log_Template.xlsx",
      "template_url": "/templates/Risk_Log_Template.xlsx",
      "required_columns": ["Risk Number", "Category", "Risk Detail", ...],
      "optional_columns": ["Mitigation Plan", "Owner", ...],
      "instructions": "Use this template to ensure compatibility with Seleen..."
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT tracker_name, schema_definition
            FROM tracker_definitions
            WHERE tracker_type = ?
        """, (tracker_type,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Tracker type not found")

        schema = json.loads(row['schema_definition'])

        # In production, would generate actual Excel template
        return {
            "tracker_type": tracker_type,
            "template_name": f"{row['tracker_name']}_Template.xlsx",
            "template_url": f"/templates/{tracker_type}_template.xlsx",
            "required_columns": [f['field_name'] for f in schema.get('required_fields', [])],
            "optional_columns": [f['field_name'] for f in schema.get('optional_fields', [])],
            "instructions": f"Use this template to ensure compatibility with Seleen. Column names can be customized via Account Management → Tracker Configuration."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get tracker template: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tracker template: {str(e)}"
        )


# ============================================================================
# Organization Settings Endpoints
# ============================================================================

@router.get("/account/organization")
async def get_organization_settings(
    org_id: str = Query(..., description="Organization ID")
):
    """
    Get organization settings

    Returns org name, tier, settings.

    **Response:**
    ```json
    {
      "org_id": "org_123",
      "org_name": "Acme Clinical Research",
      "tier": "enterprise",
      "settings": {
        "timezone": "America/New_York",
        "notification_email": "admin@acme.com",
        "dashboard_refresh_minutes": 15
      }
    }
    ```
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT org_id, org_name, tier
            FROM organizations
            WHERE org_id = ?
        """, (org_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Organization not found")

        return {
            "org_id": row['org_id'],
            "org_name": row['org_name'],
            "tier": row['tier'],
            "settings": {
                "timezone": "America/New_York",  # Would come from settings table
                "notification_email": None,
                "dashboard_refresh_minutes": 15
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get organization settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get organization settings: {str(e)}"
        )


# ============================================================================
# User Management Endpoints (Stub)
# ============================================================================

@router.get("/account/users")
async def list_users(
    org_id: str = Query(..., description="Organization ID")
):
    """
    List users in organization

    Returns all users with their roles and seat assignments.

    **Note:** Full user management implementation in future phase.
    """
    return {
        "users": [],
        "total_seats": 10,
        "seats_used": 5,
        "seats_available": 5
    }
