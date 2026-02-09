"""
Calibration Processing Engine
Parses historical MS Project timelines to generate organization-specific benchmarks
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import statistics
from .task_normalizer import TaskNormalizer
from .models import (
    CalibrationResult,
    OrgBenchmark,
    PatternDetection,
    TaskPattern
)


class CalibrationEngine:
    """
    Processes historical project timelines to generate org-specific benchmarks
    and detect execution patterns
    """

    def __init__(self, task_normalizer: TaskNormalizer):
        self.task_normalizer = task_normalizer
        self.min_samples_for_benchmark = 3  # Minimum tasks needed for a reliable benchmark

    def process_mpp_file(
        self,
        file_content: bytes,
        org_id: str,
        project_metadata: Optional[Dict[str, Any]] = None
    ) -> CalibrationResult:
        """
        Parse MS Project XML file and extract calibration data

        Args:
            file_content: Raw bytes of .mpp or XML export
            org_id: Organization identifier
            project_metadata: Optional metadata (phase, therapeutic_area, country)

        Returns:
            CalibrationResult with extracted benchmarks and patterns
        """
        try:
            # Parse XML (MS Project can export to XML format)
            root = ET.fromstring(file_content)

            # Extract project info
            project_name = self._extract_text(root, './/Name', 'Unknown Project')

            # Extract all tasks
            tasks = self._extract_tasks(root)

            # Normalize task names to ontology
            normalized_tasks = self._normalize_tasks(tasks, org_id)

            # Detect execution patterns
            patterns = self._detect_patterns(normalized_tasks, project_metadata)

            # Generate org-specific benchmarks
            benchmarks = self._generate_benchmarks(normalized_tasks, org_id)

            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(normalized_tasks, benchmarks)

            return CalibrationResult(
                org_id=org_id,
                project_name=project_name,
                tasks_extracted=len(tasks),
                tasks_normalized=len(normalized_tasks),
                benchmarks_generated=len(benchmarks),
                patterns_detected=patterns,
                org_benchmarks=benchmarks,
                quality_metrics=quality_metrics,
                metadata=project_metadata or {}
            )

        except ET.ParseError as e:
            raise ValueError(f"Invalid MS Project XML format: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Calibration processing failed: {str(e)}")

    def _extract_tasks(self, root: ET.Element) -> List[Dict[str, Any]]:
        """
        Extract task information from MS Project XML

        Returns list of tasks with: id, name, duration_days, start, finish, category
        """
        tasks = []

        # MS Project XML structure: <Project><Tasks><Task>...
        for task_elem in root.findall('.//Task'):
            task_id = self._extract_text(task_elem, 'ID')
            task_name = self._extract_text(task_elem, 'Name')

            # Skip summary tasks or milestones
            if not task_name or self._is_summary_task(task_elem):
                continue

            # Extract duration (in minutes in MS Project XML)
            duration_minutes = self._extract_int(task_elem, 'Duration', 0)
            duration_days = duration_minutes / (8 * 60)  # Convert to working days (8 hours)

            # Extract dates
            start_date = self._extract_text(task_elem, 'Start')
            finish_date = self._extract_text(task_elem, 'Finish')

            # Extract custom fields if available
            category = self._extract_custom_field(task_elem, 'Text5') or 'Unknown'

            if duration_days > 0:  # Only include tasks with actual duration
                tasks.append({
                    'task_id': task_id,
                    'name': task_name,
                    'duration_days': duration_days,
                    'start_date': start_date,
                    'finish_date': finish_date,
                    'category': category
                })

        return tasks

    def _normalize_tasks(
        self,
        tasks: List[Dict[str, Any]],
        org_id: str
    ) -> List[Dict[str, Any]]:
        """
        Normalize task names to ontology using TaskNormalizer

        Returns tasks with added 'ontology_task_id' and 'ontology_task_name'
        """
        normalized = []

        for task in tasks:
            # Use task normalizer to map to ontology
            ontology_id, suggestion, unconfirmed = self.task_normalizer.normalize(
                task['name'],
                org_id,
                context={'category': task.get('category')}
            )

            if ontology_id:
                # Successfully normalized
                normalized.append({
                    **task,
                    'ontology_task_id': ontology_id,
                    'ontology_task_name': suggestion.ontology_task_name if suggestion else task['name'],
                    'confidence': suggestion.confidence if suggestion else 1.0
                })
            elif suggestion:
                # High-confidence suggestion available
                normalized.append({
                    **task,
                    'ontology_task_id': suggestion.ontology_task_id,
                    'ontology_task_name': suggestion.ontology_task_name,
                    'confidence': suggestion.confidence
                })

        return normalized

    def _detect_patterns(
        self,
        tasks: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]]
    ) -> List[PatternDetection]:
        """
        Detect organizational execution patterns

        Patterns include:
        - Consistent overestimation/underestimation by category
        - Unique sequencing or parallelization approaches
        - Consistently faster/slower than industry in specific areas
        """
        patterns = []

        # Group tasks by ontology category
        by_category = defaultdict(list)
        for task in tasks:
            if 'ontology_task_name' in task:
                category = task.get('category', 'Unknown')
                by_category[category].append(task['duration_days'])

        # Analyze each category for patterns
        for category, durations in by_category.items():
            if len(durations) >= 2:  # Need at least 2 samples
                avg_duration = statistics.mean(durations)
                std_dev = statistics.stdev(durations) if len(durations) > 1 else 0

                patterns.append(PatternDetection(
                    pattern_type='duration_consistency',
                    category=category,
                    description=f"Average {avg_duration:.1f} days with {std_dev:.1f} day std deviation",
                    confidence=min(len(durations) / 10, 1.0),  # Higher confidence with more samples
                    sample_size=len(durations)
                ))

        # Detect if organization is generally fast or slow
        all_durations = [t['duration_days'] for t in tasks if 'duration_days' in t]
        if all_durations:
            median_duration = statistics.median(all_durations)

            if median_duration < 30:
                patterns.append(PatternDetection(
                    pattern_type='execution_speed',
                    category='Overall',
                    description='Organization executes tasks faster than industry average',
                    confidence=0.7,
                    sample_size=len(all_durations)
                ))
            elif median_duration > 90:
                patterns.append(PatternDetection(
                    pattern_type='execution_speed',
                    category='Overall',
                    description='Organization takes longer than industry average for tasks',
                    confidence=0.7,
                    sample_size=len(all_durations)
                ))

        return patterns

    def _generate_benchmarks(
        self,
        tasks: List[Dict[str, Any]],
        org_id: str
    ) -> List[OrgBenchmark]:
        """
        Generate organization-specific benchmarks from normalized tasks

        Groups by ontology_task_id and calculates median, P25, P75
        """
        benchmarks = []

        # Group tasks by ontology task ID
        by_ontology_task = defaultdict(list)
        for task in tasks:
            if 'ontology_task_id' in task and 'duration_days' in task:
                by_ontology_task[task['ontology_task_id']].append({
                    'duration': task['duration_days'],
                    'name': task['ontology_task_name'],
                    'category': task.get('category', 'Unknown')
                })

        # Calculate statistics for each task type
        for ontology_id, task_samples in by_ontology_task.items():
            if len(task_samples) < self.min_samples_for_benchmark:
                continue  # Skip if not enough samples

            durations = [s['duration'] for s in task_samples]
            durations.sort()

            # Calculate percentiles
            median = statistics.median(durations)
            p25 = self._percentile(durations, 25)
            p75 = self._percentile(durations, 75)

            benchmarks.append(OrgBenchmark(
                org_id=org_id,
                ontology_task_id=ontology_id,
                task_name=task_samples[0]['name'],
                category=task_samples[0]['category'],
                median_days=round(median, 1),
                p25_days=round(p25, 1),
                p75_days=round(p75, 1),
                sample_size=len(task_samples),
                confidence=min(len(task_samples) / 10, 1.0),  # Max confidence at 10+ samples
                last_updated=datetime.utcnow().isoformat()
            ))

        return benchmarks

    def _calculate_quality_metrics(
        self,
        tasks: List[Dict[str, Any]],
        benchmarks: List[OrgBenchmark]
    ) -> Dict[str, Any]:
        """
        Calculate quality metrics for the calibration
        """
        total_tasks = len(tasks)
        normalized_tasks = len([t for t in tasks if 'ontology_task_id' in t])
        high_confidence = len([t for t in tasks if t.get('confidence', 0) >= 0.8])

        return {
            'normalization_rate': round(normalized_tasks / total_tasks * 100, 1) if total_tasks > 0 else 0,
            'high_confidence_rate': round(high_confidence / total_tasks * 100, 1) if total_tasks > 0 else 0,
            'benchmarks_created': len(benchmarks),
            'avg_sample_size': round(statistics.mean([b.sample_size for b in benchmarks]), 1) if benchmarks else 0,
            'data_quality': 'High' if normalized_tasks / total_tasks > 0.8 else 'Medium' if normalized_tasks / total_tasks > 0.5 else 'Low'
        }

    # Helper methods

    def _extract_text(self, element: ET.Element, path: str, default: str = '') -> str:
        """Extract text from XML element"""
        found = element.find(path)
        return found.text if found is not None and found.text else default

    def _extract_int(self, element: ET.Element, path: str, default: int = 0) -> int:
        """Extract integer from XML element"""
        text = self._extract_text(element, path)
        try:
            return int(text) if text else default
        except ValueError:
            return default

    def _extract_custom_field(self, task_elem: ET.Element, field_name: str) -> Optional[str]:
        """Extract value from MS Project custom field"""
        # MS Project custom fields are in ExtendedAttribute elements
        for attr in task_elem.findall('.//ExtendedAttribute'):
            field_id = self._extract_text(attr, 'FieldID')
            # Text5 is typically FieldID 188744709 in MS Project
            if field_name == 'Text5' and field_id == '188744709':
                return self._extract_text(attr, 'Value')
        return None

    def _is_summary_task(self, task_elem: ET.Element) -> bool:
        """Check if task is a summary/parent task"""
        summary = self._extract_text(task_elem, 'Summary', '0')
        return summary == '1'

    def _percentile(self, sorted_data: List[float], percentile: int) -> float:
        """Calculate percentile from sorted data"""
        if not sorted_data:
            return 0.0

        k = (len(sorted_data) - 1) * (percentile / 100)
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_data) else f

        return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])
