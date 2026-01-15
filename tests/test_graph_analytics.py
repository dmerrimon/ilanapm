"""
Tests for Graph Analytics Module

Tests critical path calculation, slack analysis, and parallelization detection.
"""

import pytest
from backend.models.timeline import (
    Timeline, Task, Dependency,
    StudyPhase, RegulatoryAuthority, TaskCategory
)
from backend.graph_analytics import DependencyGraph


class TestGraphAnalytics:
    """Test suite for graph analytics functionality"""
    
    def test_critical_path_simple_linear(self):
        """Test critical path with simple linear dependencies"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Task 1",
                    duration_days=10,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Task 2",
                    duration_days=20,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T3",
                    name="Task 3",
                    duration_days=15,
                    category=TaskCategory.DATA,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2"),
                Dependency(predecessor_id="T2", successor_id="T3"),
            ]
        )
        
        graph = DependencyGraph(timeline)
        result = graph.get_critical_path()
        
        assert result['task_count'] == 3
        assert result['total_duration'] == 45  # 10 + 20 + 15
        assert result['path'] == ["T1", "T2", "T3"]
        assert len(result['tasks']) == 3
    
    def test_critical_path_with_branches(self):
        """Test critical path with branching dependencies"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Start Task",
                    duration_days=10,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Branch A",
                    duration_days=30,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T3",
                    name="Branch B",
                    duration_days=50,  # Longer - should be on critical path
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T4",
                    name="End Task",
                    duration_days=10,
                    category=TaskCategory.DATA,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2"),
                Dependency(predecessor_id="T1", successor_id="T3"),
                Dependency(predecessor_id="T2", successor_id="T4"),
                Dependency(predecessor_id="T3", successor_id="T4"),
            ]
        )
        
        graph = DependencyGraph(timeline)
        result = graph.get_critical_path()
        
        # Critical path should be: T1 → T3 → T4 (longest path)
        assert result['total_duration'] == 70  # 10 + 50 + 10
        assert "T1" in result['path']
        assert "T3" in result['path']  # Longest branch
        assert "T4" in result['path']
    
    def test_critical_path_with_circular_dependency(self):
        """Test that circular dependencies are detected"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Task 1",
                    duration_days=10,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Task 2",
                    duration_days=20,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2"),
                Dependency(predecessor_id="T2", successor_id="T1"),  # Creates cycle!
            ]
        )
        
        graph = DependencyGraph(timeline)
        result = graph.get_critical_path()
        
        # Should return error for circular dependencies
        assert 'error' in result
        assert 'circular' in result['error'].lower()
        assert result['task_count'] == 0
    
    def test_slack_calculation(self):
        """Test slack/float calculation"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Critical Task 1",
                    duration_days=10,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Critical Task 2",
                    duration_days=30,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T3",
                    name="Non-critical Task",
                    duration_days=15,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T4",
                    name="End Task",
                    duration_days=10,
                    category=TaskCategory.DATA,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2"),
                Dependency(predecessor_id="T1", successor_id="T3"),
                Dependency(predecessor_id="T2", successor_id="T4"),
                Dependency(predecessor_id="T3", successor_id="T4"),
            ]
        )
        
        graph = DependencyGraph(timeline)
        result = graph.calculate_slack()
        
        assert result['total_tasks'] == 4
        assert result['project_duration'] == 50  # 10 + 30 + 10
        
        # Critical path tasks should have 0 slack
        critical_tasks = [t for t in result['slack_by_task'] if t['on_critical_path']]
        assert len(critical_tasks) == 3  # T1, T2, T4
        
        # T3 should have slack (not on critical path)
        t3_slack = next(t for t in result['slack_by_task'] if t['id'] == 'T3')
        assert t3_slack['slack_days'] > 0
        assert not t3_slack['on_critical_path']
    
    def test_parallelization_opportunities(self):
        """Test detection of tasks that could run in parallel"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Site A Setup",
                    duration_days=30,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Site B Setup",
                    duration_days=30,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T3",
                    name="Site C Setup",
                    duration_days=30,
                    category=TaskCategory.SITE,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
            ],
            dependencies=[]  # No dependencies - all could run in parallel
        )
        
        graph = DependencyGraph(timeline)
        result = graph.find_parallelization_opportunities()
        
        # Should find opportunities: T1+T2, T1+T3, T2+T3
        assert result['total_opportunities'] >= 3
        assert result['analyzed_task_count'] == 3
        
        # All opportunities should be same category
        for opp in result['opportunities']:
            assert opp['same_category'] == True
            assert opp['confidence'] >= 0.8  # High confidence for same category
    
    def test_parallelization_no_false_positives(self):
        """Test that dependent tasks are not suggested for parallelization"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Task 1",
                    duration_days=10,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Task 2",
                    duration_days=20,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2"),  # T2 depends on T1
            ]
        )
        
        graph = DependencyGraph(timeline)
        result = graph.find_parallelization_opportunities()
        
        # Should NOT suggest T1 and T2 for parallelization
        assert result['total_opportunities'] == 0
    
    def test_graph_stats(self):
        """Test graph statistics calculation"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Task 1",
                    duration_days=10,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Task 2",
                    duration_days=20,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T3",
                    name="Task 3",
                    duration_days=15,
                    category=TaskCategory.DATA,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2"),
                Dependency(predecessor_id="T2", successor_id="T3"),
            ]
        )
        
        graph = DependencyGraph(timeline)
        result = graph.get_stats()
        
        assert result['total_tasks'] == 3
        assert result['total_dependencies'] == 2
        assert result['is_acyclic'] == True
        assert result['has_cycles'] == False
        assert result['weakly_connected_components'] == 1
        assert 'density' in result
    
    def test_empty_timeline(self):
        """Test handling of empty timeline"""
        timeline = Timeline(
            study_name="Empty Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[],
            dependencies=[]
        )
        
        graph = DependencyGraph(timeline)
        
        # Critical path
        cp_result = graph.get_critical_path()
        assert cp_result['total_duration'] == 0
        assert cp_result['task_count'] == 0
        
        # Slack
        slack_result = graph.calculate_slack()
        assert slack_result['total_tasks'] == 0
        
        # Parallelization
        para_result = graph.find_parallelization_opportunities()
        assert para_result['total_opportunities'] == 0
        
        # Stats
        stats = graph.get_stats()
        assert stats['total_tasks'] == 0
        assert stats['total_dependencies'] == 0
    
    def test_complex_timeline_with_lag(self):
        """Test timeline with lag days in dependencies"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Task 1",
                    duration_days=10,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Task 2",
                    duration_days=20,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
            ],
            dependencies=[
                Dependency(
                    predecessor_id="T1",
                    successor_id="T2",
                    lag_days=5  # 5-day lag between tasks
                ),
            ]
        )
        
        graph = DependencyGraph(timeline)
        result = graph.get_critical_path()
        
        # Duration should include lag: 10 + 5 (lag) + 20 = 35
        assert result['total_duration'] == 35
    
    def test_helper_methods(self):
        """Test helper methods (get_task_by_id, get_predecessors, etc.)"""
        timeline = Timeline(
            study_name="Test Study",
            phase=StudyPhase.PHASE_II,
            authority=RegulatoryAuthority.FDA,
            tasks=[
                Task(
                    id="T1",
                    name="Task 1",
                    duration_days=10,
                    category=TaskCategory.REGULATORY,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
                Task(
                    id="T2",
                    name="Task 2",
                    duration_days=20,
                    category=TaskCategory.OPERATIONAL,
                    phase=StudyPhase.PHASE_II,
                    authority=RegulatoryAuthority.FDA
                ),
            ],
            dependencies=[
                Dependency(predecessor_id="T1", successor_id="T2"),
            ]
        )
        
        graph = DependencyGraph(timeline)
        
        # Test get_task_by_id
        task = graph.get_task_by_id("T1")
        assert task is not None
        assert task.name == "Task 1"
        
        # Test get_predecessors
        preds = graph.get_predecessors("T2")
        assert "T1" in preds
        
        # Test get_successors
        succs = graph.get_successors("T1")
        assert "T2" in succs
        
        # Test has_path
        assert graph.has_path("T1", "T2") == True
        assert graph.has_path("T2", "T1") == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
