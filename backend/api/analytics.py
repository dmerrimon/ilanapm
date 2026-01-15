"""
Analytics Endpoints

Provides graph analytics for timelines including:
- Critical path calculation
- Slack/float analysis
- Parallelization opportunities
- Project statistics
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from backend.models.timeline import Timeline
from backend.graph_analytics import DependencyGraph

router = APIRouter()


@router.post("/analytics/critical-path")
async def get_critical_path(timeline: Timeline):
    """
    Calculate critical path for timeline
    
    The critical path is the longest path through the project,
    determining the minimum project duration.
    
    Args:
        timeline: Timeline object with tasks and dependencies
    
    Returns:
        Critical path analysis with:
        - path: List of task IDs on critical path
        - tasks: Detailed task information
        - total_duration: Project duration in days
        - task_count: Number of tasks on critical path
    
    Example Request:
        ```json
        {
            "study_name": "Phase II Trial",
            "phase": "Phase II",
            "authority": "FDA",
            "tasks": [...],
            "dependencies": [...]
        }
        ```
    
    Example Response:
        ```json
        {
            "path": ["T1", "T2", "T5", "T8"],
            "tasks": [
                {
                    "id": "T1",
                    "name": "IND Submission",
                    "duration_days": 60,
                    "category": "Regulatory",
                    "is_mandatory": true,
                    "earliest_start": 0,
                    "earliest_finish": 60
                },
                ...
            ],
            "total_duration": 450,
            "task_count": 4
        }
        ```
    """
    try:
        graph = DependencyGraph(timeline)
        result = graph.get_critical_path()
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Critical path calculation failed: {str(e)}"
        )


@router.post("/analytics/slack")
async def get_slack_analysis(timeline: Timeline):
    """
    Calculate slack (float) for all tasks
    
    Slack is the amount of time a task can be delayed without
    affecting the project completion date. Tasks with zero slack
    are on the critical path.
    
    Args:
        timeline: Timeline object with tasks and dependencies
    
    Returns:
        Slack analysis with:
        - slack_by_task: List of tasks with slack information
        - critical_tasks: Task IDs with zero slack
        - total_tasks: Number of tasks analyzed
        - project_duration: Total project duration
    
    Example Response:
        ```json
        {
            "slack_by_task": [
                {
                    "id": "T1",
                    "name": "IND Submission",
                    "duration_days": 60,
                    "category": "Regulatory",
                    "slack_days": 0,
                    "on_critical_path": true,
                    "earliest_start": 0,
                    "earliest_finish": 60,
                    "latest_start": 0,
                    "latest_finish": 60
                },
                {
                    "id": "T3",
                    "name": "Site Selection",
                    "duration_days": 30,
                    "category": "Site",
                    "slack_days": 15,
                    "on_critical_path": false,
                    "earliest_start": 60,
                    "earliest_finish": 90,
                    "latest_start": 75,
                    "latest_finish": 105
                }
            ],
            "critical_tasks": ["T1", "T2", "T5"],
            "total_tasks": 10,
            "project_duration": 450
        }
        ```
    """
    try:
        graph = DependencyGraph(timeline)
        result = graph.calculate_slack()
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Slack calculation failed: {str(e)}"
        )


@router.post("/analytics/parallelization")
async def get_parallelization_opportunities(timeline: Timeline):
    """
    Find parallelization opportunities
    
    Identifies tasks that could run in parallel to reduce
    overall project duration. Provides recommendations and
    potential time savings.
    
    Args:
        timeline: Timeline object with tasks and dependencies
    
    Returns:
        Parallelization analysis with:
        - opportunities: List of task pairs that could run in parallel
        - potential_savings_days: Total potential time savings
        - total_opportunities: Number of opportunities found
        - analyzed_task_count: Total tasks analyzed
    
    Example Response:
        ```json
        {
            "opportunities": [
                {
                    "task1": {
                        "id": "T3",
                        "name": "Site A Initiation",
                        "duration_days": 30,
                        "category": "Site"
                    },
                    "task2": {
                        "id": "T4",
                        "name": "Site B Initiation",
                        "duration_days": 30,
                        "category": "Site"
                    },
                    "same_category": true,
                    "potential_savings_days": 30,
                    "confidence": 0.8,
                    "recommendation": "Tasks 'Site A Initiation' and 'Site B Initiation' have no dependencies and could run in parallel"
                }
            ],
            "potential_savings_days": 75,
            "total_opportunities": 5,
            "analyzed_task_count": 20
        }
        ```
    """
    try:
        graph = DependencyGraph(timeline)
        result = graph.find_parallelization_opportunities()
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Parallelization analysis failed: {str(e)}"
        )


@router.post("/analytics/stats")
async def get_graph_stats(timeline: Timeline):
    """
    Get overall graph statistics
    
    Provides high-level statistics about the timeline dependency graph.
    
    Args:
        timeline: Timeline object with tasks and dependencies
    
    Returns:
        Graph statistics including:
        - total_tasks: Number of tasks
        - total_dependencies: Number of dependencies
        - is_acyclic: Whether graph has no cycles
        - has_cycles: Whether circular dependencies exist
        - weakly_connected_components: Number of disconnected subgraphs
        - density: Graph density (0-1)
    
    Example Response:
        ```json
        {
            "total_tasks": 25,
            "total_dependencies": 42,
            "is_acyclic": true,
            "has_cycles": false,
            "weakly_connected_components": 1,
            "density": 0.07
        }
        ```
    """
    try:
        graph = DependencyGraph(timeline)
        result = graph.get_stats()
        
        return result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Graph statistics calculation failed: {str(e)}"
        )


@router.post("/analytics/comprehensive")
async def get_comprehensive_analysis(timeline: Timeline):
    """
    Get comprehensive analytics report
    
    Combines critical path, slack, parallelization, and statistics
    into a single comprehensive report.
    
    Args:
        timeline: Timeline object with tasks and dependencies
    
    Returns:
        Comprehensive analytics report with all analyses combined
    """
    try:
        graph = DependencyGraph(timeline)
        
        # Get all analytics
        critical_path = graph.get_critical_path()
        slack = graph.calculate_slack()
        parallelization = graph.find_parallelization_opportunities()
        stats = graph.get_stats()
        
        return {
            "study_name": timeline.study_name,
            "phase": timeline.phase.value,
            "authority": timeline.authority.value,
            "critical_path": critical_path,
            "slack_analysis": slack,
            "parallelization_opportunities": parallelization,
            "graph_statistics": stats,
            "summary": {
                "project_duration_days": critical_path.get('total_duration', 0),
                "critical_path_task_count": critical_path.get('task_count', 0),
                "tasks_with_flexibility": len([t for t in slack.get('slack_by_task', []) if t['slack_days'] > 0]),
                "parallelization_opportunities": parallelization.get('total_opportunities', 0),
                "potential_time_savings_days": parallelization.get('potential_savings_days', 0)
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Comprehensive analysis failed: {str(e)}"
        )
