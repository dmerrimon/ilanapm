"""
Graph Analytics Module

Provides dependency graph analysis, critical path calculation,
slack/float analysis, and parallelization recommendations.
"""

from .dependency_graph import DependencyGraph

__all__ = ["DependencyGraph"]
