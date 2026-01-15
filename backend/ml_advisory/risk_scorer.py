"""
Risk Scorer

Scores tasks for delay risk (0-100) based on multiple risk factors.
Phase 2: Rule-based heuristics
Phase 5: Trained ML models
"""

from typing import Dict, List, Optional
from backend.models.timeline import Task, Timeline, TaskCategory


class RiskScorer:
    """
    Scores tasks for delay risk
    
    Analyzes multiple risk factors including duration, category, dependencies,
    and checklist completion to provide risk scores and mitigation suggestions.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize risk scorer
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.task_ontology = config.get('task_ontology', [])
        
    def score_risk(self, task: Task, timeline_context: Optional[Dict] = None) -> Dict:
        """
        Score task for delay risk
        
        Args:
            task: Task to score
            timeline_context: Optional context (dependencies, critical path, etc.)
            
        Returns:
            Dictionary with:
            - risk_score: int (0-100)
            - risk_level: str ("low", "medium", "high", "critical")
            - risk_factors: List[str]
            - mitigation_suggestions: List[str]
            - confidence: float (0-1)
        """
        risk_score = 0
        risk_factors = []
        
        # Factor 1: Duration compared to typical (30 points max)
        duration_risk, duration_factor = self._assess_duration_risk(task)
        risk_score += duration_risk
        if duration_factor:
            risk_factors.append(duration_factor)
        
        # Factor 2: Category-based risk (20 points max)
        category_risk, category_factor = self._assess_category_risk(task)
        risk_score += category_risk
        if category_factor:
            risk_factors.append(category_factor)
        
        # Factor 3: Mandatory task impact (15 points max)
        mandatory_risk, mandatory_factor = self._assess_mandatory_risk(task)
        risk_score += mandatory_risk
        if mandatory_factor:
            risk_factors.append(mandatory_factor)
        
        # Factor 4: Checklist completion (20 points max)
        checklist_risk, checklist_factor = self._assess_checklist_risk(task)
        risk_score += checklist_risk
        if checklist_factor:
            risk_factors.append(checklist_factor)
        
        # Factor 5: Timeline context (15 points max)
        if timeline_context:
            context_risk, context_factor = self._assess_context_risk(task, timeline_context)
            risk_score += context_risk
            if context_factor:
                risk_factors.append(context_factor)
        
        # Normalize to 0-100
        risk_score = min(risk_score, 100)
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Generate mitigation suggestions
        mitigations = self._generate_mitigations(task, risk_factors, timeline_context)
        
        # Calculate confidence
        confidence = self._calculate_confidence(task, timeline_context)
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_suggestions": mitigations,
            "confidence": confidence,
            "model_version": "heuristic-v1"
        }
    
    def score_timeline_risks(self, timeline: Timeline) -> Dict:
        """
        Score all tasks in timeline for risk
        
        Args:
            timeline: Timeline to analyze
            
        Returns:
            Dictionary with risk analysis for all tasks
        """
        from backend.graph_analytics import DependencyGraph
        
        # Build context from dependency graph
        graph = DependencyGraph(timeline)
        critical_path_result = graph.get_critical_path()
        critical_tasks = set(critical_path_result.get('path', []))
        
        timeline_context = {
            "critical_tasks": critical_tasks,
            "total_tasks": len(timeline.tasks)
        }
        
        # Score each task
        risk_scores = []
        high_risk_tasks = []
        
        for task in timeline.tasks:
            context = timeline_context.copy()
            context['on_critical_path'] = task.id in critical_tasks
            
            risk = self.score_risk(task, context)
            
            risk_scores.append({
                "task_id": task.id,
                "task_name": task.name,
                "risk_score": risk['risk_score'],
                "risk_level": risk['risk_level'],
                "on_critical_path": context['on_critical_path']
            })
            
            # Flag high/critical risk tasks
            if risk['risk_level'] in ['high', 'critical']:
                high_risk_tasks.append({
                    "task_id": task.id,
                    "task_name": task.name,
                    "risk_score": risk['risk_score'],
                    "risk_level": risk['risk_level'],
                    "risk_factors": risk['risk_factors'],
                    "mitigation_suggestions": risk['mitigation_suggestions']
                })
        
        # Calculate statistics
        avg_risk = sum(r['risk_score'] for r in risk_scores) / len(risk_scores) if risk_scores else 0
        
        return {
            "risk_scores": risk_scores,
            "high_risk_tasks": high_risk_tasks,
            "average_risk": avg_risk,
            "total_tasks": len(timeline.tasks),
            "high_risk_count": len(high_risk_tasks),
            "model_version": "heuristic-v1"
        }
    
    def _assess_duration_risk(self, task: Task) -> tuple[int, Optional[str]]:
        """Assess risk based on duration"""
        canonical = self._find_canonical_task(task)
        
        if not canonical:
            return 5, "Unknown task type - limited historical data"
        
        typical = canonical.get('typical_duration_days', task.duration_days)
        min_days = canonical.get('min_duration_days', int(typical * 0.7))
        
        if task.duration_days < min_days:
            ratio = task.duration_days / typical
            if ratio < 0.6:
                return 30, f"Very aggressive duration ({task.duration_days}d vs typical {typical}d)"
            else:
                return 20, f"Aggressive duration ({task.duration_days}d vs typical {typical}d)"
        
        return 0, None
    
    def _assess_category_risk(self, task: Task) -> tuple[int, Optional[str]]:
        """Assess risk based on task category"""
        if task.category == TaskCategory.REGULATORY:
            return 20, "Regulatory tasks often face delays due to authority review times"
        elif task.category == TaskCategory.SITE:
            return 15, "Site-related tasks depend on third-party coordination"
        elif task.category == TaskCategory.DATA:
            return 10, "Data tasks may face quality issues requiring rework"
        
        return 0, None
    
    def _assess_mandatory_risk(self, task: Task) -> tuple[int, Optional[str]]:
        """Assess risk based on mandatory status"""
        if task.is_mandatory:
            return 15, "Mandatory task - delays directly impact project completion"
        
        return 0, None
    
    def _assess_checklist_risk(self, task: Task) -> tuple[int, Optional[str]]:
        """Assess risk based on checklist completion"""
        if task.checklist_completion_pct < 50:
            return 20, f"Low checklist completion ({task.checklist_completion_pct}%)"
        elif task.checklist_completion_pct < 80:
            return 10, f"Incomplete checklist ({task.checklist_completion_pct}%)"
        
        return 0, None
    
    def _assess_context_risk(self, task: Task, context: Dict) -> tuple[int, Optional[str]]:
        """Assess risk based on timeline context"""
        if context.get('on_critical_path', False):
            return 15, "On critical path - no scheduling flexibility"
        
        return 0, None
    
    def _determine_risk_level(self, risk_score: int) -> str:
        """Determine risk level from score"""
        if risk_score >= 75:
            return "critical"
        elif risk_score >= 50:
            return "high"
        elif risk_score >= 25:
            return "medium"
        else:
            return "low"
    
    def _generate_mitigations(self, task: Task, risk_factors: List[str], 
                            context: Optional[Dict]) -> List[str]:
        """Generate mitigation suggestions"""
        mitigations = []
        
        # Duration-related mitigations
        if any("aggressive" in f.lower() for f in risk_factors):
            mitigations.append("Add buffer time to duration estimate")
            mitigations.append("Conduct detailed task breakdown to validate duration")
        
        # Checklist-related mitigations
        if any("checklist" in f.lower() for f in risk_factors):
            mitigations.append("Complete all checklist items before task starts")
            mitigations.append("Assign dedicated resource to checklist preparation")
        
        # Regulatory-specific mitigations
        if task.category == TaskCategory.REGULATORY:
            mitigations.append("Engage regulatory consultant early")
            mitigations.append("Consider pre-submission meeting with authority")
            mitigations.append("Prepare responses to anticipated questions in advance")
        
        # Site-specific mitigations
        if task.category == TaskCategory.SITE:
            mitigations.append("Establish clear communication protocols with site")
            mitigations.append("Build in contingency for site response delays")
        
        # Critical path mitigations
        if context and context.get('on_critical_path'):
            mitigations.append("Monitor daily - this task impacts project completion date")
            mitigations.append("Identify parallel activities to reduce critical path dependency")
        
        # Mandatory task mitigations
        if task.is_mandatory:
            mitigations.append("Ensure adequate resources assigned")
            mitigations.append("Create detailed risk mitigation plan for this task")
        
        return mitigations[:5]  # Limit to top 5
    
    def _calculate_confidence(self, task: Task, context: Optional[Dict]) -> float:
        """Calculate confidence in risk assessment"""
        confidence = 0.7  # Base confidence
        
        # Higher confidence if we have canonical match
        if self._find_canonical_task(task):
            confidence += 0.15
        
        # Higher confidence if we have timeline context
        if context:
            confidence += 0.10
        
        # Lower confidence for unknown categories
        if task.category not in [TaskCategory.REGULATORY, TaskCategory.OPERATIONAL, 
                                 TaskCategory.SITE, TaskCategory.DATA]:
            confidence -= 0.2
        
        return min(max(confidence, 0.0), 1.0)
    
    def _find_canonical_task(self, task: Task) -> Optional[Dict]:
        """Find matching canonical task from ontology"""
        category_matches = [
            t for t in self.task_ontology
            if t.get('category') == task.category.value
        ]
        
        if not category_matches:
            return None
        
        # Simple name matching
        for canonical in category_matches:
            if self._name_similarity(canonical['name'], task.name) > 0.5:
                return canonical
        
        return None
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity"""
        words1 = set(name1.lower().split())
        words2 = set(name2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0


__all__ = ["RiskScorer"]
