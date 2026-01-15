"""
Duration Predictor

Predicts task duration with confidence intervals based on historical data.
Phase 2: YAML-driven heuristics
Phase 5: Trained ML models
"""

from typing import Dict, List, Optional
from backend.models.timeline import Task, StudyPhase, RegulatoryAuthority, TaskCategory


class DurationPredictor:
    """
    Predicts task duration with confidence intervals
    
    Uses task ontology and authority-specific adjustments to provide
    duration predictions. Currently heuristic-based; will be replaced
    with ML models in Phase 5.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize duration predictor
        
        Args:
            config: Configuration dictionary with task ontology
        """
        self.config = config
        self.task_ontology = config.get('task_ontology', [])
        self.authorities = config.get('authorities', {})
        
    def predict_duration(self, task: Task) -> Dict:
        """
        Predict duration for a task
        
        Args:
            task: Task to predict duration for
            
        Returns:
            Dictionary with:
            - predicted_duration_days: int
            - confidence_interval: {"lower": int, "upper": int}
            - confidence_score: float (0-1)
            - explanation: str
            - comparable_tasks: List[Dict]
            - model_version: str
        """
        # Find canonical task from ontology
        canonical = self._find_canonical_task(task)
        
        if canonical:
            return self._predict_from_canonical(task, canonical)
        else:
            return self._predict_from_defaults(task)
    
    def predict_timeline_durations(self, tasks: List[Task]) -> Dict:
        """
        Predict durations for all tasks in timeline
        
        Args:
            tasks: List of tasks to predict for
            
        Returns:
            Dictionary with predictions for each task
        """
        predictions = []
        total_confidence = 0.0
        
        for task in tasks:
            prediction = self.predict_duration(task)
            predictions.append({
                "task_id": task.id,
                "task_name": task.name,
                "current_duration": task.duration_days,
                "prediction": prediction
            })
            total_confidence += prediction['confidence_score']
        
        avg_confidence = total_confidence / len(tasks) if tasks else 0.0
        
        return {
            "predictions": predictions,
            "average_confidence": avg_confidence,
            "total_tasks": len(tasks),
            "model_version": "heuristic-v1"
        }
    
    def _find_canonical_task(self, task: Task) -> Optional[Dict]:
        """
        Find matching canonical task from ontology
        
        Args:
            task: Task to match
            
        Returns:
            Canonical task dictionary or None
        """
        # Try exact category match first
        category_matches = [
            t for t in self.task_ontology
            if t.get('category') == task.category.value
        ]
        
        if not category_matches:
            return None
        
        # Find best name match
        best_match = None
        best_score = 0.0
        
        for canonical in category_matches:
            score = self._name_similarity(canonical['name'], task.name)
            if score > best_score and score > 0.5:  # Threshold
                best_score = score
                best_match = canonical
        
        return best_match
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate name similarity score
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Similarity score (0-1)
        """
        words1 = set(name1.lower().split())
        words2 = set(name2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _predict_from_canonical(self, task: Task, canonical: Dict) -> Dict:
        """
        Predict duration from canonical task
        
        Args:
            task: Task to predict for
            canonical: Canonical task data
            
        Returns:
            Prediction dictionary
        """
        # Get base duration
        typical_days = canonical.get('typical_duration_days', task.duration_days)
        min_days = canonical.get('min_duration_days', int(typical_days * 0.7))
        max_days = canonical.get('max_duration_days', int(typical_days * 1.5))
        
        # Apply authority-specific adjustments
        authority_adjustments = canonical.get('authority_specific', {})
        if task.authority.value in authority_adjustments:
            auth_data = authority_adjustments[task.authority.value]
            typical_days = auth_data.get('duration_days', typical_days)
            
            # Adjust bounds proportionally
            adjustment_ratio = typical_days / canonical.get('typical_duration_days', typical_days)
            min_days = int(min_days * adjustment_ratio)
            max_days = int(max_days * adjustment_ratio)
        
        # Calculate confidence based on match quality
        confidence = 0.85  # High confidence for canonical match
        
        # Build comparable tasks list
        comparable_tasks = [{
            "name": canonical['name'],
            "typical_duration": typical_days,
            "category": canonical['category'],
            "authority": task.authority.value
        }]
        
        # Check if current duration is reasonable
        duration_variance = "reasonable"
        if task.duration_days < min_days:
            duration_variance = "aggressive (below minimum)"
            confidence *= 0.9
        elif task.duration_days > max_days:
            duration_variance = "conservative (above maximum)"
            confidence *= 0.95
        
        explanation = (
            f"Based on historical data for {canonical['name']} "
            f"({task.authority.value}). "
            f"Typical duration: {typical_days} days. "
            f"Your duration of {task.duration_days} days is {duration_variance}."
        )
        
        return {
            "predicted_duration_days": typical_days,
            "confidence_interval": {
                "lower": min_days,
                "upper": max_days
            },
            "confidence_score": confidence,
            "explanation": explanation,
            "comparable_tasks": comparable_tasks,
            "model_version": "heuristic-v1",
            "matched_canonical": canonical['id']
        }
    
    def _predict_from_defaults(self, task: Task) -> Dict:
        """
        Predict duration using defaults (no canonical match)
        
        Args:
            task: Task to predict for
            
        Returns:
            Prediction dictionary
        """
        # Use task's duration with conservative bounds
        typical_days = task.duration_days
        min_days = int(typical_days * 0.6)
        max_days = int(typical_days * 1.8)
        
        # Low confidence for unknown tasks
        confidence = 0.4
        
        explanation = (
            f"No historical data available for similar {task.category.value} tasks. "
            f"Using provided duration of {task.duration_days} days with conservative bounds. "
            f"Recommendation: Review with clinical operations team."
        )
        
        return {
            "predicted_duration_days": typical_days,
            "confidence_interval": {
                "lower": min_days,
                "upper": max_days
            },
            "confidence_score": confidence,
            "explanation": explanation,
            "comparable_tasks": [],
            "model_version": "heuristic-v1",
            "matched_canonical": None
        }


__all__ = ["DurationPredictor"]
