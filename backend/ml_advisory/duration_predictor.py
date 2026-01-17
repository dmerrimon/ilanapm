"""
Duration Predictor

Predicts task duration with confidence intervals based on historical data.
Phase 2: YAML-driven heuristics with international regulatory workflows (v3.0)
Phase 5: Trained ML models
"""

from typing import Dict, List, Optional
from backend.models.timeline import Task, StudyPhase, RegulatoryAuthority, TaskCategory
from backend.ml_advisory.workflow_matcher import WorkflowMatcher


class DurationPredictor:
    """
    Predicts task duration with confidence intervals

    Uses task ontology v3.0 with country-specific regulatory workflows and
    authority-specific adjustments to provide duration predictions.
    Currently heuristic-based; will be replaced with ML models in Phase 5.
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

        # Initialize workflow matcher for country-specific predictions
        try:
            self.workflow_matcher = WorkflowMatcher()
        except Exception as e:
            # Fallback if workflow matcher fails to load
            print(f"Warning: Could not load WorkflowMatcher: {e}")
            self.workflow_matcher = None
        
    def predict_duration(self, task: Task) -> Dict:
        """
        Predict duration for a task

        Uses WorkflowMatcher (v3.0) for country-specific predictions first,
        then falls back to canonical task matching.

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
        # PRIORITY 1: Try country-specific workflow match (v3.0)
        if self.workflow_matcher:
            country_prediction = self._predict_from_workflow(task)
            if country_prediction and country_prediction['confidence_score'] > 0.75:
                return country_prediction

        # PRIORITY 2: Find canonical task from ontology
        canonical = self._find_canonical_task(task)

        if canonical:
            return self._predict_from_canonical(task, canonical)
        else:
            return self._predict_from_defaults(task)
    
    def _predict_from_workflow(self, task: Task) -> Optional[Dict]:
        """
        Predict duration using WorkflowMatcher with country-specific data

        Args:
            task: Task to predict for

        Returns:
            Prediction dictionary or None if no country match
        """
        if not self.workflow_matcher:
            return None

        # PRIORITY 1: Use explicit country field if provided (v3.0 country configuration)
        country_code = task.country

        # If country is a full name (not a code), convert to code
        if country_code and len(country_code) > 2:
            country_code = self.workflow_matcher.get_country_code_from_name(country_code)

        # FALLBACK: Extract country code from task name (legacy support)
        if not country_code:
            country_code = self.workflow_matcher.extract_country_code(task.name)

        # Get task duration prediction from workflow matcher
        workflow_prediction = self.workflow_matcher.get_task_duration(
            task_name=task.name,
            country_code=country_code,
            authority=task.authority.value if task.authority else None,
            category=task.category.value if task.category else None
        )

        # Only use workflow prediction if confidence is acceptable
        if workflow_prediction.get('confidence', 0) < 0.75:
            return None

        # Get duration from workflow prediction
        predicted_days = workflow_prediction.get('duration_days')
        if predicted_days is None:
            return None

        # Apply authority multiplier to workflow-based predictions
        if task.authority:
            multiplier = self._get_authority_multiplier(task.authority.value)
            if multiplier != 1.0:
                predicted_days = int(predicted_days * multiplier)

        # Calculate confidence interval
        min_days = int(predicted_days * 0.8)
        max_days = int(predicted_days * 1.3)

        # Check if there's a range specified in workflow data
        if workflow_prediction.get('min_duration_days'):
            min_days = workflow_prediction['min_duration_days']
        if workflow_prediction.get('max_duration_days'):
            max_days = workflow_prediction['max_duration_days']

        # Build comparable tasks list
        comparable_tasks = []
        if workflow_prediction.get('authority_code'):
            comparable_tasks.append({
                "name": workflow_prediction.get('task_name', task.name),
                "typical_duration": predicted_days,
                "authority": workflow_prediction['authority_code'],
                "country": country_code or "Unknown"
            })

        # Analyze duration variance
        duration_variance = "reasonable"
        confidence = workflow_prediction['confidence']

        if task.duration_days < min_days:
            duration_variance = "aggressive (below minimum)"
            confidence *= 0.9
        elif task.duration_days > max_days:
            duration_variance = "conservative (above maximum)"
            confidence *= 0.95

        # Build explanation
        explanation_parts = []

        if country_code:
            explanation_parts.append(f"Based on {country_code} regulatory workflow")
        if workflow_prediction.get('workflow_type'):
            workflow_type = workflow_prediction['workflow_type'].replace('_', ' ').title()
            explanation_parts.append(f"({workflow_type})")

        # Add authority multiplier info if applied
        if task.authority:
            multiplier = self._get_authority_multiplier(task.authority.value)
            if multiplier != 1.0:
                multiplier_pct = int((multiplier - 1.0) * 100)
                if multiplier > 1.0:
                    explanation_parts.append(
                        f"with {task.authority.value} adjustment (+{multiplier_pct}% longer review times)"
                    )
                else:
                    explanation_parts.append(
                        f"with {task.authority.value} adjustment ({multiplier_pct}% faster review times)"
                    )

        if workflow_prediction.get('notes'):
            explanation_parts.append(f"{workflow_prediction['notes']}")

        explanation_parts.append(
            f"Predicted duration: {predicted_days} days. "
            f"Your duration of {task.duration_days} days is {duration_variance}."
        )

        explanation = " ".join(explanation_parts)

        return {
            "predicted_duration_days": predicted_days,
            "confidence_interval": {
                "lower": min_days,
                "upper": max_days
            },
            "confidence_score": confidence,
            "explanation": explanation,
            "comparable_tasks": comparable_tasks,
            "model_version": workflow_prediction.get('model_version', 'ontology-v3.0'),
            "matched_canonical": workflow_prediction.get('task_id'),
            "country_code": country_code,
            "workflow_type": workflow_prediction.get('workflow_type'),
            "authority_code": workflow_prediction.get('authority_code'),
            "source": workflow_prediction.get('source', 'workflow_matcher')
        }

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

        # Determine model version based on whether workflow matcher is available
        model_version = "ontology-v3.0" if self.workflow_matcher else "heuristic-v1"

        return {
            "predictions": predictions,
            "average_confidence": avg_confidence,
            "total_tasks": len(tasks),
            "model_version": model_version
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
    
    def _get_authority_multiplier(self, authority_value: str) -> float:
        """
        Get review time multiplier for an authority

        Args:
            authority_value: Authority code (e.g., "FDA", "EMA", "PPB")

        Returns:
            Multiplier (default 1.0 if not found)
        """
        if not self.authorities:
            return 1.0

        for auth in self.authorities:
            if auth.get('code') == authority_value:
                return auth.get('review_time_multiplier', 1.0)

        return 1.0

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

        # Apply authority-specific adjustments from ontology
        authority_adjustments = canonical.get('authority_specific', {})
        if task.authority.value in authority_adjustments:
            auth_data = authority_adjustments[task.authority.value]
            typical_days = auth_data.get('duration_days', typical_days)

            # Adjust bounds proportionally
            adjustment_ratio = typical_days / canonical.get('typical_duration_days', typical_days)
            min_days = int(min_days * adjustment_ratio)
            max_days = int(max_days * adjustment_ratio)
        else:
            # Apply global authority multiplier (FDA 1.2x, PMDA 1.5x, etc.)
            multiplier = self._get_authority_multiplier(task.authority.value)
            if multiplier != 1.0:
                typical_days = int(typical_days * multiplier)
                min_days = int(min_days * multiplier)
                max_days = int(max_days * multiplier)
        
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

        # Build explanation with authority multiplier info
        multiplier = self._get_authority_multiplier(task.authority.value)
        explanation_parts = [
            f"Based on historical data for {canonical['name']} ({task.authority.value})."
        ]

        if multiplier != 1.0:
            multiplier_pct = int((multiplier - 1.0) * 100)
            if multiplier > 1.0:
                explanation_parts.append(
                    f"Applied {task.authority.value} timing adjustment (+{multiplier_pct}% longer review times)."
                )
            else:
                explanation_parts.append(
                    f"Applied {task.authority.value} timing adjustment ({multiplier_pct}% faster review times)."
                )

        explanation_parts.append(
            f"Typical duration: {typical_days} days. "
            f"Your duration of {task.duration_days} days is {duration_variance}."
        )

        explanation = " ".join(explanation_parts)
        
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
