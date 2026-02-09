"""
Resource Collision Detection Engine
Identifies resource conflicts across multiple studies in an organization's portfolio
"""

from typing import List, Dict, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class ResourceAssignment:
    """Represents a resource assignment to a study"""
    resource_id: str
    resource_name: str
    resource_type: str  # 'site', 'vendor', 'personnel', 'equipment'
    study_id: str
    study_name: str
    start_date: str
    end_date: str
    utilization_percent: float = 100.0  # Percentage of resource capacity used


@dataclass
class ResourceCollision:
    """Represents a detected resource collision"""
    resource_id: str
    resource_name: str
    resource_type: str
    conflicting_studies: List[Dict[str, Any]]
    overlap_start: str
    overlap_end: str
    overlap_days: int
    severity: str  # 'critical', 'warning', 'info'
    total_utilization: float  # Combined utilization across studies
    recommendations: List[str]


class ResourceCollisionDetector:
    """
    Detects resource collisions and capacity conflicts across
    multiple studies in a portfolio
    """

    def __init__(self):
        self.critical_utilization = 100.0  # Over 100% = critical
        self.warning_utilization = 80.0    # 80-100% = warning

    def detect_collisions(
        self,
        org_id: str,
        resource_assignments: List[ResourceAssignment]
    ) -> Dict[str, Any]:
        """
        Detect resource collisions across all studies

        Args:
            org_id: Organization identifier
            resource_assignments: List of resource assignments across studies

        Returns:
            Collision report with detected conflicts and recommendations
        """
        if not resource_assignments:
            return self._empty_report(org_id)

        # Group assignments by resource
        resource_map = self._group_by_resource(resource_assignments)

        # Detect collisions for each resource
        collisions = []
        for resource_id, assignments in resource_map.items():
            resource_collisions = self._detect_resource_collisions(
                resource_id,
                assignments
            )
            collisions.extend(resource_collisions)

        # Calculate summary statistics
        summary = self._calculate_summary(collisions, resource_assignments)

        # Generate recommendations
        recommendations = self._generate_recommendations(collisions)

        return {
            'org_id': org_id,
            'collisions': [self._collision_to_dict(c) for c in collisions],
            'summary': summary,
            'recommendations': recommendations,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _group_by_resource(
        self,
        assignments: List[ResourceAssignment]
    ) -> Dict[str, List[ResourceAssignment]]:
        """Group resource assignments by resource ID"""
        resource_map = defaultdict(list)
        for assignment in assignments:
            resource_map[assignment.resource_id].append(assignment)
        return resource_map

    def _detect_resource_collisions(
        self,
        resource_id: str,
        assignments: List[ResourceAssignment]
    ) -> List[ResourceCollision]:
        """
        Detect collisions for a specific resource

        Collision occurs when the same resource is assigned to
        multiple studies with overlapping time periods
        """
        if len(assignments) < 2:
            return []

        collisions = []

        # Sort assignments by start date
        sorted_assignments = sorted(
            assignments,
            key=lambda a: a.start_date
        )

        # Check each pair for overlap
        for i in range(len(sorted_assignments)):
            for j in range(i + 1, len(sorted_assignments)):
                a1 = sorted_assignments[i]
                a2 = sorted_assignments[j]

                overlap = self._calculate_overlap(a1, a2)

                if overlap:
                    overlap_start, overlap_end, overlap_days = overlap

                    # Calculate total utilization during overlap
                    total_utilization = a1.utilization_percent + a2.utilization_percent

                    # Determine severity
                    severity = self._determine_severity(total_utilization)

                    # Generate recommendations
                    recommendations = self._get_collision_recommendations(
                        a1, a2, total_utilization, overlap_days
                    )

                    collision = ResourceCollision(
                        resource_id=resource_id,
                        resource_name=a1.resource_name,
                        resource_type=a1.resource_type,
                        conflicting_studies=[
                            {
                                'study_id': a1.study_id,
                                'study_name': a1.study_name,
                                'start_date': a1.start_date,
                                'end_date': a1.end_date,
                                'utilization': a1.utilization_percent
                            },
                            {
                                'study_id': a2.study_id,
                                'study_name': a2.study_name,
                                'start_date': a2.start_date,
                                'end_date': a2.end_date,
                                'utilization': a2.utilization_percent
                            }
                        ],
                        overlap_start=overlap_start,
                        overlap_end=overlap_end,
                        overlap_days=overlap_days,
                        severity=severity,
                        total_utilization=total_utilization,
                        recommendations=recommendations
                    )

                    collisions.append(collision)

        return collisions

    def _calculate_overlap(
        self,
        a1: ResourceAssignment,
        a2: ResourceAssignment
    ) -> Optional[Tuple[str, str, int]]:
        """
        Calculate overlap between two resource assignments

        Returns:
            Tuple of (overlap_start, overlap_end, overlap_days) or None if no overlap
        """
        start1 = datetime.fromisoformat(a1.start_date.replace('Z', '+00:00'))
        end1 = datetime.fromisoformat(a1.end_date.replace('Z', '+00:00'))
        start2 = datetime.fromisoformat(a2.start_date.replace('Z', '+00:00'))
        end2 = datetime.fromisoformat(a2.end_date.replace('Z', '+00:00'))

        # Calculate overlap
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)

        if overlap_start < overlap_end:
            overlap_days = (overlap_end - overlap_start).days
            return (
                overlap_start.isoformat(),
                overlap_end.isoformat(),
                overlap_days
            )

        return None

    def _determine_severity(self, total_utilization: float) -> str:
        """Determine collision severity based on utilization"""
        if total_utilization > self.critical_utilization:
            return 'critical'
        elif total_utilization > self.warning_utilization:
            return 'warning'
        else:
            return 'info'

    def _get_collision_recommendations(
        self,
        a1: ResourceAssignment,
        a2: ResourceAssignment,
        total_utilization: float,
        overlap_days: int
    ) -> List[str]:
        """Generate recommendations for resolving collision"""
        recommendations = []

        if total_utilization > 100:
            recommendations.append(
                f"Resource is over-allocated ({total_utilization:.0f}%). "
                f"Consider reducing workload or adding capacity."
            )

        if a1.resource_type == 'site':
            recommendations.append(
                f"Site {a1.resource_name} is assigned to multiple studies. "
                f"Verify site has capacity for parallel enrollment."
            )
        elif a1.resource_type == 'vendor':
            recommendations.append(
                f"Vendor {a1.resource_name} may need additional staff "
                f"to support {len([a1, a2])} concurrent studies."
            )
        elif a1.resource_type == 'personnel':
            recommendations.append(
                f"Personnel {a1.resource_name} is assigned to multiple studies. "
                f"Consider delegating tasks or adjusting timelines."
            )

        if overlap_days > 180:
            recommendations.append(
                f"Long overlap period ({overlap_days} days). "
                f"Consider staggering study timelines to reduce contention."
            )

        return recommendations

    def _calculate_summary(
        self,
        collisions: List[ResourceCollision],
        all_assignments: List[ResourceAssignment]
    ) -> Dict[str, Any]:
        """Calculate summary statistics for collision report"""
        if not collisions:
            return {
                'total_collisions': 0,
                'critical_collisions': 0,
                'warning_collisions': 0,
                'info_collisions': 0,
                'affected_resources': 0,
                'affected_studies': 0,
                'total_resources_tracked': len(set(a.resource_id for a in all_assignments))
            }

        critical = sum(1 for c in collisions if c.severity == 'critical')
        warning = sum(1 for c in collisions if c.severity == 'warning')
        info_col = sum(1 for c in collisions if c.severity == 'info')

        affected_resources = len(set(c.resource_id for c in collisions))

        affected_studies = set()
        for collision in collisions:
            for study in collision.conflicting_studies:
                affected_studies.add(study['study_id'])

        # Calculate collision rate by resource type
        collisions_by_type = defaultdict(int)
        for collision in collisions:
            collisions_by_type[collision.resource_type] += 1

        return {
            'total_collisions': len(collisions),
            'critical_collisions': critical,
            'warning_collisions': warning,
            'info_collisions': info_col,
            'affected_resources': affected_resources,
            'affected_studies': len(affected_studies),
            'total_resources_tracked': len(set(a.resource_id for a in all_assignments)),
            'collision_rate': round(affected_resources / len(set(a.resource_id for a in all_assignments)) * 100, 1),
            'collisions_by_type': dict(collisions_by_type)
        }

    def _generate_recommendations(
        self,
        collisions: List[ResourceCollision]
    ) -> List[str]:
        """Generate portfolio-level recommendations"""
        recommendations = []

        if not collisions:
            recommendations.append("No resource collisions detected. Portfolio capacity is healthy.")
            return recommendations

        critical_count = sum(1 for c in collisions if c.severity == 'critical')
        warning_count = sum(1 for c in collisions if c.severity == 'warning')

        if critical_count > 0:
            recommendations.append(
                f"⚠️ {critical_count} critical resource collision(s) detected. "
                f"Immediate action required to resolve capacity conflicts."
            )

        if warning_count > 0:
            recommendations.append(
                f"⚡ {warning_count} resource(s) approaching capacity limits. "
                f"Monitor utilization and plan for additional capacity."
            )

        # Check for specific resource type patterns
        site_collisions = [c for c in collisions if c.resource_type == 'site']
        if len(site_collisions) > 3:
            recommendations.append(
                f"Multiple site capacity issues detected ({len(site_collisions)} sites). "
                f"Consider expanding site network or staggering enrollment timelines."
            )

        vendor_collisions = [c for c in collisions if c.resource_type == 'vendor']
        if len(vendor_collisions) > 2:
            recommendations.append(
                f"Vendor capacity constraints detected ({len(vendor_collisions)} vendors). "
                f"Negotiate expanded service agreements or engage backup vendors."
            )

        return recommendations

    def _collision_to_dict(self, collision: ResourceCollision) -> Dict[str, Any]:
        """Convert ResourceCollision dataclass to dictionary"""
        return {
            'resource_id': collision.resource_id,
            'resource_name': collision.resource_name,
            'resource_type': collision.resource_type,
            'conflicting_studies': collision.conflicting_studies,
            'overlap_start': collision.overlap_start,
            'overlap_end': collision.overlap_end,
            'overlap_days': collision.overlap_days,
            'severity': collision.severity,
            'total_utilization': collision.total_utilization,
            'recommendations': collision.recommendations
        }

    def _empty_report(self, org_id: str) -> Dict[str, Any]:
        """Return empty collision report"""
        return {
            'org_id': org_id,
            'collisions': [],
            'summary': {
                'total_collisions': 0,
                'critical_collisions': 0,
                'warning_collisions': 0,
                'info_collisions': 0,
                'affected_resources': 0,
                'affected_studies': 0,
                'total_resources_tracked': 0
            },
            'recommendations': ['No resource assignments to analyze.'],
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_resource_utilization_timeline(
        self,
        resource_id: str,
        assignments: List[ResourceAssignment],
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get utilization timeline for a specific resource

        Returns day-by-day utilization for visualization
        """
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))

        # Filter assignments for this resource
        resource_assignments = [a for a in assignments if a.resource_id == resource_id]

        timeline = []
        current_date = start

        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')

            # Calculate utilization for this date
            utilization = 0
            active_studies = []

            for assignment in resource_assignments:
                assign_start = datetime.fromisoformat(assignment.start_date.replace('Z', '+00:00'))
                assign_end = datetime.fromisoformat(assignment.end_date.replace('Z', '+00:00'))

                if assign_start <= current_date <= assign_end:
                    utilization += assignment.utilization_percent
                    active_studies.append(assignment.study_name)

            timeline.append({
                'date': date_str,
                'utilization': utilization,
                'active_studies': active_studies,
                'status': 'over_capacity' if utilization > 100 else 'at_capacity' if utilization >= 80 else 'available'
            })

            current_date += timedelta(days=1)

        return timeline
