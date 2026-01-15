"""
ML Advisory Module

Provides ML-powered (initially heuristic-based) advisory services including:
- Duration prediction with confidence intervals
- Risk scoring for tasks
- Timeline-wide recommendations

Note: Phase 2 uses YAML-driven heuristics. Phase 5 will add trained ML models.
"""

from .duration_predictor import DurationPredictor
from .risk_scorer import RiskScorer

__all__ = ["DurationPredictor", "RiskScorer"]
