from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import httpx
import json

router = APIRouter()

class ValidationSummary(BaseModel):
    status: str
    error_count: int
    warning_count: int
    total_tasks: int

class HighRiskTaskSummary(BaseModel):
    name: str
    risk_score: int

class TeamsNotification(BaseModel):
    webhook_url: str
    study_name: str
    validation_summary: ValidationSummary
    high_risk_tasks: List[HighRiskTaskSummary]

@router.post("/teams/notify")
async def send_teams_notification(notification: TeamsNotification):
    """Send validation summary to Microsoft Teams via webhook"""

    # Build Adaptive Card
    card = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": f"Timeline Validation: {notification.study_name}",
        "themeColor": "0078D4" if notification.validation_summary.status == "passed" else "D13438",
        "title": f"📊 Timeline Validation: {notification.study_name}",
        "sections": [
            {
                "activityTitle": "Validation Summary",
                "facts": [
                    {"name": "Status", "value": notification.validation_summary.status.upper()},
                    {"name": "Errors", "value": str(notification.validation_summary.error_count)},
                    {"name": "Warnings", "value": str(notification.validation_summary.warning_count)},
                    {"name": "Total Tasks", "value": str(notification.validation_summary.total_tasks)}
                ]
            }
        ]
    }

    # Add high-risk tasks section if any
    if notification.high_risk_tasks:
        risk_section = {
            "activityTitle": "⚠️ High Risk Tasks",
            "text": "\n".join([f"• **{task.name}** (Risk: {task.risk_score}/100)" for task in notification.high_risk_tasks[:5]])
        }
        card["sections"].append(risk_section)

    # Send to Teams webhook
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                notification.webhook_url,
                json=card,
                timeout=10.0
            )
            response.raise_for_status()

        return {"status": "success", "message": "Notification sent to Teams"}

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to send Teams notification: {str(e)}")
