"""
ML Advisory Endpoints

Provides ML-powered advisory services including duration prediction
and risk scoring for clinical trial timelines.

Version 3.0: Enhanced with international regulatory workflow recommendations
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Set
from backend.models.timeline import Timeline, Task
from backend.ml_advisory import DurationPredictor, RiskScorer
from backend.ml_advisory.workflow_matcher import WorkflowMatcher
from backend.config import load_config

router = APIRouter()

# Load configuration once at startup
config = load_config()
duration_predictor = DurationPredictor(config)
risk_scorer = RiskScorer(config)

# Initialize workflow matcher for country-specific recommendations
try:
    workflow_matcher = WorkflowMatcher()
except Exception as e:
    print(f"Warning: Could not load WorkflowMatcher: {e}")
    workflow_matcher = None


@router.post("/advisory/duration")
async def predict_duration(task: Task):
    """
    Get ML-powered duration prediction for a task
    
    Provides predicted duration with confidence intervals based on
    historical data from similar tasks.
    
    Args:
        task: Task object with task details
    
    Returns:
        Duration prediction with:
        - predicted_duration_days: Predicted duration
        - confidence_interval: Lower and upper bounds
        - confidence_score: Confidence in prediction (0-1)
        - explanation: Human-readable explanation
        - comparable_tasks: Similar historical tasks
    
    Example Request:
        ```json
        {
            "id": "T1",
            "name": "IND Submission",
            "duration_days": 45,
            "category": "Regulatory",
            "phase": "Phase II",
            "authority": "FDA",
            "is_mandatory": true
        }
        ```
    
    Example Response:
        ```json
        {
            "predicted_duration_days": 60,
            "confidence_interval": {
                "lower": 30,
                "upper": 90
            },
            "confidence_score": 0.85,
            "explanation": "Based on historical data for IND Submission (FDA). Typical duration: 60 days. Your duration of 45 days is aggressive (below minimum).",
            "comparable_tasks": [
                {
                    "name": "IND/CTA Submission",
                    "typical_duration": 60,
                    "category": "Regulatory",
                    "authority": "FDA"
                }
            ],
            "model_version": "heuristic-v1"
        }
        ```
    """
    try:
        prediction = duration_predictor.predict_duration(task)
        return prediction
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Duration prediction failed: {str(e)}"
        )


@router.post("/advisory/risk")
async def score_risk(task: Task):
    """
    Get ML-powered risk score for a task
    
    Analyzes multiple risk factors to provide a risk score (0-100)
    and mitigation suggestions.
    
    Args:
        task: Task object with task details
    
    Returns:
        Risk assessment with:
        - risk_score: Score from 0-100
        - risk_level: low/medium/high/critical
        - risk_factors: List of identified risk factors
        - mitigation_suggestions: Recommended actions
        - confidence: Confidence in assessment (0-1)
    
    Example Response:
        ```json
        {
            "risk_score": 65,
            "risk_level": "high",
            "risk_factors": [
                "Aggressive duration (45d vs typical 60d)",
                "Regulatory tasks often face delays due to authority review times",
                "Mandatory task - delays directly impact project completion"
            ],
            "mitigation_suggestions": [
                "Add buffer time to duration estimate",
                "Engage regulatory consultant early",
                "Consider pre-submission meeting with authority"
            ],
            "confidence": 0.85,
            "model_version": "heuristic-v1"
        }
        ```
    """
    try:
        risk = risk_scorer.score_risk(task)
        return risk
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Risk scoring failed: {str(e)}"
        )


@router.post("/advisory/timeline")
async def analyze_timeline(timeline: Timeline):
    """
    Get comprehensive ML-powered advisory for entire timeline
    
    Combines duration predictions and risk assessments for all tasks
    in the timeline, providing a complete advisory report.
    
    Args:
        timeline: Timeline object with tasks and dependencies
    
    Returns:
        Comprehensive advisory with:
        - duration_predictions: Duration predictions for all tasks
        - risk_analysis: Risk scores for all tasks
        - high_risk_tasks: Tasks requiring attention
        - summary_statistics: Overall metrics
        - recommendations: Timeline-wide recommendations
    
    Example Response:
        ```json
        {
            "duration_predictions": {
                "predictions": [...],
                "average_confidence": 0.72,
                "total_tasks": 10
            },
            "risk_analysis": {
                "risk_scores": [...],
                "high_risk_tasks": [...],
                "average_risk": 42,
                "high_risk_count": 3
            },
            "summary_statistics": {
                "total_tasks": 10,
                "avg_predicted_duration": 45,
                "avg_risk_score": 42,
                "critical_risk_count": 1,
                "high_risk_count": 2
            },
            "recommendations": [
                "3 tasks have high risk scores - review mitigation strategies",
                "2 tasks have aggressive durations - consider adding buffer time",
                "Schedule pre-submission meetings for all regulatory tasks"
            ]
        }
        ```
    """
    try:
        # Get duration predictions for all tasks
        duration_analysis = duration_predictor.predict_timeline_durations(timeline.tasks)
        
        # Get risk scores for all tasks
        risk_analysis = risk_scorer.score_timeline_risks(timeline)
        
        # Calculate summary statistics
        summary = _calculate_summary_statistics(
            duration_analysis,
            risk_analysis,
            timeline
        )
        
        # Extract countries from timeline for workflow recommendations
        countries_in_timeline = set()
        if workflow_matcher:
            for task in timeline.tasks:
                country_code = workflow_matcher.extract_country_code(task.name)
                if country_code:
                    countries_in_timeline.add(country_code)

        # Generate recommendations (includes country-specific workflow recommendations)
        recommendations = _generate_timeline_recommendations(
            duration_analysis,
            risk_analysis,
            timeline,
            countries_in_timeline
        )

        # Determine model version
        model_version = duration_analysis.get('model_version', 'heuristic-v1')

        return {
            "study_name": timeline.study_name,
            "phase": timeline.phase.value,
            "authority": timeline.authority.value,
            "duration_predictions": duration_analysis,
            "risk_analysis": risk_analysis,
            "summary_statistics": summary,
            "recommendations": recommendations,
            "model_version": model_version
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Timeline analysis failed: {str(e)}"
        )


def _calculate_summary_statistics(
    duration_analysis: Dict,
    risk_analysis: Dict,
    timeline: Timeline
) -> Dict:
    """Calculate summary statistics for timeline"""
    
    # Duration statistics
    predictions = duration_analysis.get('predictions', [])
    avg_predicted = sum(
        p['prediction']['predicted_duration_days'] 
        for p in predictions
    ) / len(predictions) if predictions else 0
    
    # Risk statistics
    risk_scores = risk_analysis.get('risk_scores', [])
    critical_count = sum(1 for r in risk_scores if r['risk_level'] == 'critical')
    high_count = sum(1 for r in risk_scores if r['risk_level'] == 'high')
    medium_count = sum(1 for r in risk_scores if r['risk_level'] == 'medium')
    
    # Aggressive durations
    aggressive_count = sum(
        1 for p in predictions
        if p['current_duration'] < p['prediction']['confidence_interval']['lower']
    )
    
    return {
        "total_tasks": len(timeline.tasks),
        "avg_predicted_duration": round(avg_predicted, 1),
        "avg_risk_score": round(risk_analysis.get('average_risk', 0), 1),
        "critical_risk_count": critical_count,
        "high_risk_count": high_count,
        "medium_risk_count": medium_count,
        "aggressive_duration_count": aggressive_count,
        "avg_prediction_confidence": round(duration_analysis.get('average_confidence', 0), 2)
    }


def _generate_timeline_recommendations(
    duration_analysis: Dict,
    risk_analysis: Dict,
    timeline: Timeline,
    countries: Set[str] = None
) -> list[str]:
    """
    Generate timeline-wide recommendations

    Args:
        duration_analysis: Duration prediction results
        risk_analysis: Risk assessment results
        timeline: Timeline object
        countries: Set of country codes found in timeline tasks

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # PRIORITY 1: Country-specific workflow recommendations
    if countries and workflow_matcher:
        for country_code in sorted(countries):
            country_recs = workflow_matcher.get_workflow_recommendations(country_code)
            # Add country-specific recommendations (limit to avoid overwhelming)
            recommendations.extend(country_recs[:3])  # Top 3 per country

    # Risk-based recommendations
    high_risk_count = len(risk_analysis.get('high_risk_tasks', []))
    if high_risk_count > 0:
        recommendations.append(
            f"{high_risk_count} task(s) have high/critical risk scores - "
            f"review mitigation strategies before execution"
        )
    
    # Duration-based recommendations
    predictions = duration_analysis.get('predictions', [])
    aggressive_tasks = [
        p for p in predictions
        if p['current_duration'] < p['prediction']['confidence_interval']['lower']
    ]
    
    if len(aggressive_tasks) > 0:
        recommendations.append(
            f"{len(aggressive_tasks)} task(s) have aggressive durations - "
            f"consider adding buffer time to reduce schedule risk"
        )
    
    # Low confidence predictions
    low_confidence = [
        p for p in predictions
        if p['prediction']['confidence_score'] < 0.6
    ]
    
    if len(low_confidence) > 0:
        recommendations.append(
            f"{len(low_confidence)} task(s) have low confidence predictions - "
            f"validate durations with clinical operations team"
        )
    
    # Category-specific recommendations
    regulatory_tasks = [t for t in timeline.tasks if t.category.value == 'Regulatory']
    if len(regulatory_tasks) >= 2:
        recommendations.append(
            "Schedule pre-submission meetings with regulatory authority "
            "to reduce approval timeline uncertainty"
        )
    
    # Critical path recommendation
    from backend.graph_analytics import DependencyGraph
    graph = DependencyGraph(timeline)
    cp = graph.get_critical_path()
    critical_count = cp.get('task_count', 0)
    
    if critical_count > len(timeline.tasks) * 0.5:
        recommendations.append(
            f"{critical_count} of {len(timeline.tasks)} tasks are on critical path - "
            f"look for parallelization opportunities to reduce project duration"
        )
    
    # Default recommendation if none generated
    if not recommendations:
        recommendations.append(
            "Timeline appears well-structured with acceptable risk levels"
        )
    
    return recommendations[:5]  # Limit to top 5


__all__ = ["router"]
