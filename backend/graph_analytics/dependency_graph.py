"""
Dependency Graph Analytics

Provides graph-based analysis of timeline dependencies including:
- Critical path calculation
- Slack/float analysis
- Parallelization opportunity detection
- Project duration estimation
"""

import networkx as nx
from typing import List, Tuple, Dict, Optional, Set
from backend.models.timeline import Timeline, Task, Dependency


class DependencyGraph:
    """
    NetworkX-based dependency graph analyzer
    
    Builds directed graph from timeline and provides analytics:
    - Critical path (longest path through project)
    - Slack/float (scheduling flexibility per task)
    - Parallelization opportunities (tasks that can run concurrently)
    - Project duration estimation
    """
    
    def __init__(self, timeline: Timeline):
        """
        Initialize dependency graph from timeline
        
        Args:
            timeline: Timeline to analyze
        """
        self.timeline = timeline
        self.graph = self._build_graph()
        self._task_map = {task.id: task for task in timeline.tasks}
        
    def _build_graph(self) -> nx.DiGraph:
        """
        Build NetworkX directed graph from timeline
        
        Returns:
            NetworkX DiGraph with tasks as nodes and dependencies as edges
        """
        G = nx.DiGraph()
        
        # Add tasks as nodes with attributes
        for task in self.timeline.tasks:
            G.add_node(
                task.id,
                name=task.name,
                duration=task.duration_days,
                category=task.category.value,
                is_mandatory=task.is_mandatory,
                checklist_completion=task.checklist_completion_pct
            )
        
        # Add dependencies as edges with lag
        for dep in self.timeline.dependencies:
            G.add_edge(
                dep.predecessor_id,
                dep.successor_id,
                lag=dep.lag_days,
                type=dep.type
            )
        
        return G
    
    def get_critical_path(self) -> Dict:
        """
        Calculate critical path (longest path through project)
        
        Returns:
            Dictionary with:
            - path: List of task IDs on critical path
            - tasks: List of task details
            - total_duration: Total project duration in days
            - task_count: Number of tasks on critical path
        """
        # Check if graph is acyclic
        if not nx.is_directed_acyclic_graph(self.graph):
            return {
                "path": [],
                "tasks": [],
                "total_duration": 0,
                "task_count": 0,
                "error": "Cannot calculate critical path: circular dependencies detected"
            }
        
        # Get topological sort
        topo_order = list(nx.topological_sort(self.graph))
        
        # Calculate earliest start times (forward pass)
        earliest_start = {node: 0 for node in self.graph.nodes()}
        earliest_finish = {node: 0 for node in self.graph.nodes()}
        
        for node in topo_order:
            duration = self.graph.nodes[node]['duration']
            earliest_finish[node] = earliest_start[node] + duration
            
            # Update successors
            for successor in self.graph.successors(node):
                lag = self.graph[node][successor].get('lag', 0)
                earliest_successor = earliest_finish[node] + lag
                
                if earliest_successor > earliest_start[successor]:
                    earliest_start[successor] = earliest_successor
        
        # Find project end time
        project_duration = max(earliest_finish.values()) if earliest_finish else 0
        
        # Calculate latest start/finish times (backward pass)
        latest_finish = {node: project_duration for node in self.graph.nodes()}
        latest_start = {node: project_duration for node in self.graph.nodes()}
        
        for node in reversed(topo_order):
            duration = self.graph.nodes[node]['duration']
            successors = list(self.graph.successors(node))
            
            if successors:
                # Latest finish = minimum of (successor latest start - lag)
                latest_finish[node] = min(
                    latest_start[succ] - self.graph[node][succ].get('lag', 0)
                    for succ in successors
                )
            else:
                # No successors - finish at project end
                latest_finish[node] = project_duration
            
            latest_start[node] = latest_finish[node] - duration
        
        # Find critical path (tasks with zero slack)
        critical_tasks = []
        for node in topo_order:
            slack = latest_start[node] - earliest_start[node]
            if slack == 0:
                critical_tasks.append(node)
        
        # Get task details for critical path
        task_details = []
        for task_id in critical_tasks:
            task = self._task_map.get(task_id)
            if task:
                task_details.append({
                    "id": task.id,
                    "name": task.name,
                    "duration_days": task.duration_days,
                    "category": task.category.value,
                    "is_mandatory": task.is_mandatory,
                    "earliest_start": earliest_start[task_id],
                    "earliest_finish": earliest_finish[task_id]
                })
        
        return {
            "path": critical_tasks,
            "tasks": task_details,
            "total_duration": project_duration,
            "task_count": len(critical_tasks)
        }
    
    def calculate_slack(self) -> Dict:
        """
        Calculate slack (float) for all tasks
        
        Slack = Latest Start - Earliest Start
        Tasks with 0 slack are on the critical path
        
        Returns:
            Dictionary with:
            - slack_by_task: List of tasks with slack information
            - critical_tasks: List of task IDs with zero slack
            - total_tasks: Total number of tasks analyzed
        """
        # Check if graph is acyclic
        if not nx.is_directed_acyclic_graph(self.graph):
            return {
                "slack_by_task": [],
                "critical_tasks": [],
                "total_tasks": 0,
                "error": "Cannot calculate slack: circular dependencies detected"
            }
        
        # Get topological sort
        topo_order = list(nx.topological_sort(self.graph))
        
        # Calculate earliest start times (forward pass)
        earliest_start = {node: 0 for node in self.graph.nodes()}
        earliest_finish = {node: 0 for node in self.graph.nodes()}
        
        for node in topo_order:
            duration = self.graph.nodes[node]['duration']
            earliest_finish[node] = earliest_start[node] + duration
            
            for successor in self.graph.successors(node):
                lag = self.graph[node][successor].get('lag', 0)
                earliest_successor = earliest_finish[node] + lag
                
                if earliest_successor > earliest_start[successor]:
                    earliest_start[successor] = earliest_successor
        
        # Find project duration
        project_duration = max(earliest_finish.values()) if earliest_finish else 0
        
        # Calculate latest start times (backward pass)
        latest_finish = {node: project_duration for node in self.graph.nodes()}
        latest_start = {node: project_duration for node in self.graph.nodes()}
        
        for node in reversed(topo_order):
            duration = self.graph.nodes[node]['duration']
            successors = list(self.graph.successors(node))
            
            if successors:
                latest_finish[node] = min(
                    latest_start[succ] - self.graph[node][succ].get('lag', 0)
                    for succ in successors
                )
            else:
                latest_finish[node] = project_duration
            
            latest_start[node] = latest_finish[node] - duration
        
        # Calculate slack for each task
        slack_data = []
        critical_tasks = []
        
        for task_id in self.graph.nodes():
            slack_days = latest_start[task_id] - earliest_start[task_id]
            task = self._task_map.get(task_id)
            
            if slack_days == 0:
                critical_tasks.append(task_id)
            
            if task:
                slack_data.append({
                    "id": task.id,
                    "name": task.name,
                    "duration_days": task.duration_days,
                    "category": task.category.value,
                    "slack_days": slack_days,
                    "on_critical_path": slack_days == 0,
                    "earliest_start": earliest_start[task_id],
                    "earliest_finish": earliest_finish[task_id],
                    "latest_start": latest_start[task_id],
                    "latest_finish": latest_finish[task_id]
                })
        
        # Sort by slack (critical path tasks first)
        slack_data.sort(key=lambda x: (x['slack_days'], x['earliest_start']))
        
        return {
            "slack_by_task": slack_data,
            "critical_tasks": critical_tasks,
            "total_tasks": len(slack_data),
            "project_duration": project_duration
        }
    
    def find_parallelization_opportunities(self) -> Dict:
        """
        Find tasks that could run in parallel
        
        Identifies:
        - Task pairs with no dependency path between them
        - Tasks in same category that could be batched
        - Potential time savings from parallelization
        
        Returns:
            Dictionary with:
            - opportunities: List of parallelization opportunities
            - potential_savings: Estimated time savings in days
            - total_opportunities: Count of opportunities found
        """
        opportunities = []
        total_savings = 0
        tasks_list = list(self.timeline.tasks)
        checked_pairs = set()
        
        for i, task1 in enumerate(tasks_list):
            for task2 in tasks_list[i+1:]:
                # Create unique pair key
                pair_key = tuple(sorted([task1.id, task2.id]))
                
                if pair_key in checked_pairs:
                    continue
                
                checked_pairs.add(pair_key)
                
                # Check if there's any dependency path between them
                has_path_1_to_2 = nx.has_path(self.graph, task1.id, task2.id)
                has_path_2_to_1 = nx.has_path(self.graph, task2.id, task1.id)
                
                if not has_path_1_to_2 and not has_path_2_to_1:
                    # No dependency - could potentially run in parallel
                    same_category = task1.category == task2.category
                    
                    # Calculate potential savings (minimum of the two durations)
                    savings = min(task1.duration_days, task2.duration_days)
                    
                    # Higher confidence if same category
                    confidence = 0.8 if same_category else 0.6
                    
                    opportunities.append({
                        "task1": {
                            "id": task1.id,
                            "name": task1.name,
                            "duration_days": task1.duration_days,
                            "category": task1.category.value
                        },
                        "task2": {
                            "id": task2.id,
                            "name": task2.name,
                            "duration_days": task2.duration_days,
                            "category": task2.category.value
                        },
                        "same_category": same_category,
                        "potential_savings_days": savings,
                        "confidence": confidence,
                        "recommendation": f"Tasks '{task1.name}' and '{task2.name}' have no dependencies and could run in parallel"
                    })
                    
                    total_savings += savings
        
        # Sort by potential savings (highest first)
        opportunities.sort(key=lambda x: x['potential_savings_days'], reverse=True)
        
        return {
            "opportunities": opportunities,
            "potential_savings_days": total_savings,
            "total_opportunities": len(opportunities),
            "analyzed_task_count": len(tasks_list)
        }
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task object or None if not found
        """
        return self._task_map.get(task_id)
    
    def get_predecessors(self, task_id: str) -> List[str]:
        """
        Get list of predecessor task IDs
        
        Args:
            task_id: Task identifier
            
        Returns:
            List of predecessor task IDs
        """
        return list(self.graph.predecessors(task_id))
    
    def get_successors(self, task_id: str) -> List[str]:
        """
        Get list of successor task IDs
        
        Args:
            task_id: Task identifier
            
        Returns:
            List of successor task IDs
        """
        return list(self.graph.successors(task_id))
    
    def has_path(self, from_task_id: str, to_task_id: str) -> bool:
        """
        Check if there's a path from one task to another
        
        Args:
            from_task_id: Starting task ID
            to_task_id: Ending task ID
            
        Returns:
            True if path exists, False otherwise
        """
        return nx.has_path(self.graph, from_task_id, to_task_id)
    
    def get_stats(self) -> Dict:
        """
        Get overall graph statistics
        
        Returns:
            Dictionary with graph statistics
        """
        return {
            "total_tasks": self.graph.number_of_nodes(),
            "total_dependencies": self.graph.number_of_edges(),
            "is_acyclic": nx.is_directed_acyclic_graph(self.graph),
            "has_cycles": not nx.is_directed_acyclic_graph(self.graph),
            "weakly_connected_components": nx.number_weakly_connected_components(self.graph),
            "density": nx.density(self.graph)
        }


__all__ = ["DependencyGraph"]
