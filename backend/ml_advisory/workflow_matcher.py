"""
Workflow Matcher Service for Task Ontology v3.0
Matches tasks to country-specific regulatory workflows for accurate duration predictions
"""

from typing import Optional, Dict, List, Any
import yaml
import re
from pathlib import Path


class WorkflowMatcher:
    """Matches tasks to country-specific regulatory workflows"""

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize workflow matcher with configuration files

        Args:
            config_dir: Path to config directory. If None, uses backend/config
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config"
        else:
            config_dir = Path(config_dir)

        # Load configuration files
        with open(config_dir / 'regulatory_workflows.yaml', 'r') as f:
            data = yaml.safe_load(f)
            self.workflows = data['regulatory_workflows']

        with open(config_dir / 'task_ontology.yaml', 'r') as f:
            data = yaml.safe_load(f)
            self.ontology_tasks = data['tasks']
            self.ontology_version = data.get('version', '3.0')

        with open(config_dir / 'authorities.yaml', 'r') as f:
            data = yaml.safe_load(f)
            self.authorities = {auth['code']: auth for auth in data['authorities']}

        # Build country code to workflow mapping for quick lookup
        self.country_workflows = {wf['country_code']: wf for wf in self.workflows}

    def get_workflow(self, country_code: str) -> Optional[Dict]:
        """
        Get regulatory workflow for a country

        Args:
            country_code: ISO 3166-1 alpha-2 country code (e.g., 'US', 'KE', 'VN')

        Returns:
            Workflow dictionary or None if not found
        """
        return self.country_workflows.get(country_code)

    def get_country_code_from_name(self, country_name: str) -> Optional[str]:
        """
        Get country code from full country name

        Args:
            country_name: Full country name (e.g., "United States", "Kenya", "Vietnam")

        Returns:
            Country code (e.g., "US", "KE", "VN") or None if not found
        """
        country_name_lower = country_name.lower().strip()

        for workflow in self.workflows:
            if workflow['country_name'].lower() == country_name_lower:
                return workflow['country_code']

        return None

    def get_authority(self, authority_code: str) -> Optional[Dict]:
        """
        Get authority information by code

        Args:
            authority_code: Authority code (e.g., 'FDA', 'MHRA', 'PPB')

        Returns:
            Authority dictionary or None if not found
        """
        return self.authorities.get(authority_code)

    def extract_country_code(self, task_name: str) -> Optional[str]:
        """
        Extract country code from task name

        Supports formats:
        - "Ethics Committee Approval - Kenya"
        - "IRB Approval (United States)"
        - "MHRA Approval - United Kingdom"
        - "Regulatory Authority Approval - Tanzania"

        Args:
            task_name: Task name string

        Returns:
            ISO country code or None
        """
        # Country name to code mapping
        country_mapping = {
            'united states': 'US',
            'usa': 'US',
            'australia': 'AU',
            'bangladesh': 'BD',
            'canada': 'CA',
            'china': 'CN',
            'democratic republic of the congo': 'CD',
            'drc': 'CD',
            'guinea': 'GN',
            'india': 'IN',
            'kenya': 'KE',
            'liberia': 'LR',
            'malawi': 'MW',
            'mali': 'ML',
            'mexico': 'MX',
            'peru': 'PE',
            'sierra leone': 'SL',
            'tanzania': 'TZ',
            'south africa': 'ZA',
            'thailand': 'TH',
            'uganda': 'UG',
            'united kingdom': 'GB',
            'uk': 'GB',
            'vietnam': 'VN',
            'zimbabwe': 'ZW'
        }

        # Try to extract country from task name
        task_lower = task_name.lower()

        # Pattern: "... - Country" or "... (Country)"
        patterns = [
            r'-\s*([a-z\s]+)$',  # Matches "... - Country"
            r'\(([a-z\s]+)\)$',  # Matches "... (Country)"
        ]

        for pattern in patterns:
            match = re.search(pattern, task_lower)
            if match:
                country_name = match.group(1).strip()
                if country_name in country_mapping:
                    return country_mapping[country_name]

        # Check if country name appears anywhere in task name
        for country_name, code in country_mapping.items():
            if country_name in task_lower:
                return code

        return None

    def find_canonical_task(self, task_name: str, category: Optional[str] = None) -> Optional[Dict]:
        """
        Find canonical task definition from ontology

        Args:
            task_name: Task name to match
            category: Optional category filter

        Returns:
            Canonical task dictionary or None
        """
        task_lower = task_name.lower()

        for canonical in self.ontology_tasks:
            # Check exact name match
            if canonical['name'].lower() == task_lower:
                return canonical

            # Check aliases if present
            if 'aliases' in canonical:
                for alias in canonical['aliases']:
                    if alias.lower() in task_lower or task_lower in alias.lower():
                        return canonical

            # Check partial name match (for flexibility)
            canonical_name_parts = canonical['name'].lower().split()
            task_name_parts = task_lower.split()

            # If at least 2 significant words match, consider it a match
            matches = sum(1 for part in canonical_name_parts
                         if len(part) > 3 and part in task_name_parts)

            if matches >= 2:
                if category is None or canonical.get('category') == category:
                    return canonical

        return None

    def get_task_duration(self, task_name: str, country_code: Optional[str] = None,
                          authority: Optional[str] = None, category: Optional[str] = None) -> Dict:
        """
        Get country-specific duration prediction for a task

        Args:
            task_name: Name of the task
            country_code: ISO country code (extracted from task name if not provided)
            authority: Authority code (e.g., 'FDA', 'MHRA')
            category: Task category (e.g., 'Regulatory', 'Operational')

        Returns:
            Dictionary with duration prediction and metadata
        """
        # Extract country code from task name if not provided
        if country_code is None:
            country_code = self.extract_country_code(task_name)

        # Find canonical task
        canonical = self.find_canonical_task(task_name, category)

        if not canonical:
            return self._default_prediction(task_name, country_code)

        # PRIORITY 1: Check for country-specific variation in canonical task
        if country_code and 'country_variations' in canonical:
            variation = canonical['country_variations'].get(country_code)
            if variation:
                # Handle null/None values by falling back to canonical duration
                duration_days = variation.get('duration_days') or canonical['typical_duration_days']

                return {
                    'task_id': canonical['id'],
                    'task_name': canonical['name'],
                    'duration_days': duration_days,
                    'authority_code': variation.get('authority_code'),
                    'workflow_type': variation.get('workflow_type'),
                    'notes': variation.get('notes', ''),
                    'confidence': 0.85,
                    'model_version': self.ontology_version,
                    'source': 'country_variation'
                }

        # PRIORITY 2: Use workflow data for country
        if country_code:
            workflow = self.get_workflow(country_code)
            if workflow:
                # Determine if this is ethics or regulatory task
                is_ethics = any(keyword in task_name.lower()
                              for keyword in ['ethics', 'irb', 'ec', 'reb', 'hrec', 'rec'])
                is_regulatory = any(keyword in task_name.lower()
                                  for keyword in ['regulatory', 'approval', 'submission', 'ind', 'cta', 'fda'])

                if is_ethics and 'ethics_authority' in workflow:
                    auth_info = workflow['ethics_authority']
                    return {
                        'task_id': canonical['id'],
                        'task_name': canonical['name'],
                        'duration_days': auth_info.get('review_days') or canonical['typical_duration_days'],
                        'authority_code': auth_info['code'],
                        'authority_name': auth_info['name'],
                        'workflow_type': workflow['workflow_type'],
                        'complexity_level': workflow['complexity_level'],
                        'notes': f"{workflow['country_name']} ethics review",
                        'confidence': 0.80,
                        'model_version': self.ontology_version,
                        'source': 'workflow_ethics'
                    }

                elif is_regulatory and 'regulatory_authority' in workflow:
                    auth_info = workflow['regulatory_authority']
                    duration = auth_info.get('review_days') or canonical['typical_duration_days']

                    # Check for fast-track or emergency options
                    if auth_info.get('emergency_review_days'):
                        duration = auth_info['emergency_review_days']
                        notes = f"Emergency review pathway available: {duration} days"
                    elif auth_info.get('fast_track_days'):
                        notes = f"Standard: {duration} days, Fast-track: {auth_info['fast_track_days']} days available"
                    else:
                        notes = f"{workflow['country_name']} regulatory review"

                    return {
                        'task_id': canonical['id'],
                        'task_name': canonical['name'],
                        'duration_days': duration,
                        'authority_code': auth_info['code'],
                        'authority_name': auth_info['name'],
                        'workflow_type': workflow['workflow_type'],
                        'complexity_level': workflow['complexity_level'],
                        'auto_approval_days': auth_info.get('auto_approval_days'),
                        'notes': notes,
                        'confidence': 0.80,
                        'model_version': self.ontology_version,
                        'source': 'workflow_regulatory'
                    }

        # PRIORITY 3: Check authority-specific duration in canonical task
        if authority and 'authority_specific' in canonical:
            auth_specific = canonical['authority_specific'].get(authority)
            if auth_specific:
                return {
                    'task_id': canonical['id'],
                    'task_name': canonical['name'],
                    'duration_days': auth_specific.get('duration_days', canonical['typical_duration_days']),
                    'authority_code': authority,
                    'notes': auth_specific.get('notes', ''),
                    'confidence': 0.75,
                    'model_version': self.ontology_version,
                    'source': 'authority_specific'
                }

        # PRIORITY 4: Apply authority review time multiplier
        if authority and authority in self.authorities:
            auth_data = self.authorities[authority]
            multiplier = auth_data.get('review_time_multiplier', 1.0)
            base_duration = canonical['typical_duration_days']
            adjusted_duration = int(base_duration * multiplier)

            return {
                'task_id': canonical['id'],
                'task_name': canonical['name'],
                'duration_days': adjusted_duration,
                'authority_code': authority,
                'authority_name': auth_data['name'],
                'multiplier': multiplier,
                'notes': f"Adjusted for {auth_data['name']} (multiplier: {multiplier})",
                'confidence': 0.70,
                'model_version': self.ontology_version,
                'source': 'authority_multiplier'
            }

        # FALLBACK: Use canonical task typical duration
        return {
            'task_id': canonical['id'],
            'task_name': canonical['name'],
            'duration_days': canonical['typical_duration_days'],
            'min_duration_days': canonical.get('min_duration_days'),
            'max_duration_days': canonical.get('max_duration_days'),
            'notes': f"Using canonical task duration (no country-specific data for {country_code or 'unknown country'})",
            'confidence': 0.50,
            'model_version': self.ontology_version,
            'source': 'canonical_fallback'
        }

    def _default_prediction(self, task_name: str, country_code: Optional[str] = None) -> Dict:
        """
        Default prediction when no canonical task found

        Args:
            task_name: Task name
            country_code: Optional country code

        Returns:
            Default prediction dictionary
        """
        return {
            'task_id': None,
            'task_name': task_name,
            'duration_days': 30,  # Conservative default
            'notes': f"No canonical task match found. Using default duration. Country: {country_code or 'unknown'}",
            'confidence': 0.30,
            'model_version': self.ontology_version,
            'source': 'default'
        }

    def get_workflow_recommendations(self, country_code: str) -> List[str]:
        """
        Get country-specific workflow recommendations

        Args:
            country_code: ISO country code

        Returns:
            List of recommendation strings
        """
        workflow = self.get_workflow(country_code)
        if not workflow:
            return [f"No country-specific workflow data available for {country_code}"]

        recommendations = []

        # Workflow type recommendation
        workflow_type = workflow['workflow_type']
        country_name = workflow['country_name']

        if workflow_type == 'sequential':
            recommendations.append(
                f"⚠️ {country_name} requires SEQUENTIAL approval: "
                f"Ethics committee must approve BEFORE regulatory submission"
            )
        elif workflow_type == 'parallel':
            reg_auth = workflow['regulatory_authority']['code']
            eth_auth = workflow['ethics_authority']['code']
            recommendations.append(
                f"✓ {country_name} allows PARALLEL submission to "
                f"{reg_auth} and {eth_auth}"
            )
        elif workflow_type == 'flexible':
            recommendations.append(
                f"ℹ️ {country_name} has FLEXIBLE workflow: "
                f"normally sequential, but can switch to parallel for emergencies"
            )
        elif workflow_type == 'parallel_integrated':
            recommendations.append(
                f"✓ {country_name} offers INTEGRATED REVIEW: "
                f"single application with coordinated parallel review"
            )
        elif workflow_type == 'concurrent_sequential':
            recommendations.append(
                f"⚠️ {country_name} allows CONCURRENT SUBMISSION but "
                f"regulatory authority waits for ethics approval before finalizing"
            )
        elif workflow_type == 'three_layer_sequential':
            recommendations.append(
                f"⚠️ {country_name} requires THREE-LAYER SEQUENTIAL approval: "
                f"this is one of the most complex regulatory pathways"
            )
        elif workflow_type == 'four_layer_sequential':
            recommendations.append(
                f"⚠️ {country_name} requires FOUR-LAYER SEQUENTIAL approval: "
                f"this is the most complex regulatory pathway documented"
            )
        elif workflow_type == 'multi_body':
            additional_bodies = workflow.get('additional_bodies', [])
            body_count = len(additional_bodies) + 2  # +2 for regulatory + ethics
            recommendations.append(
                f"⚠️ {country_name} has MULTI-BODY SYSTEM with {body_count} approval bodies: "
                f"complex oversight requiring coordination"
            )

        # Timeline recommendation
        total_days = workflow.get('total_timeline_days')
        if total_days:
            recommendations.append(
                f"📅 Estimated total approval time: {total_days}+ days"
            )

        # Emergency/fast-track pathways
        reg_auth = workflow.get('regulatory_authority', {})
        if reg_auth.get('emergency_review_days'):
            recommendations.append(
                f"⚡ Emergency pathway available: {reg_auth['emergency_review_days']} days "
                f"(standard: {reg_auth.get('review_days', 'unknown')} days)"
            )
        elif reg_auth.get('fast_track_days'):
            recommendations.append(
                f"⚡ Fast-track available: {reg_auth['fast_track_days']} days "
                f"(standard: {reg_auth.get('review_days', 'unknown')} days)"
            )

        # Auto-approval mechanism
        if reg_auth.get('auto_approval_days'):
            recommendations.append(
                f"✓ Automatic approval if no response within {reg_auth['auto_approval_days']} days"
            )

        # Unique features
        for feature in workflow.get('unique_features', []):
            recommendations.append(f"📌 {feature}")

        # Fee information
        fees = workflow.get('fees', [])
        if fees:
            fee_info = fees[0]  # First fee entry
            amount = fee_info.get('amount', 0)
            currency = fee_info.get('currency', 'USD')
            if amount == 0:
                recommendations.append(f"💰 No regulatory fees")
            else:
                recommendations.append(f"💰 Regulatory fees: {currency} {amount:,}")

        return recommendations

    def get_complexity_analysis(self, country_code: str) -> Dict:
        """
        Get workflow complexity analysis for a country

        Args:
            country_code: ISO country code

        Returns:
            Dictionary with complexity metrics
        """
        workflow = self.get_workflow(country_code)
        if not workflow:
            return {'error': f'No workflow data for {country_code}'}

        # Count approval layers
        approval_layers = 1  # Start with regulatory
        if workflow.get('ethics_authority'):
            approval_layers += 1
        if workflow.get('additional_bodies'):
            approval_layers += len(workflow['additional_bodies'])

        # Count workflow steps
        workflow_steps = len(workflow.get('workflow_steps', []))

        # Calculate average timeline
        total_timeline = workflow.get('total_timeline_days', 0)

        return {
            'country_code': country_code,
            'country_name': workflow['country_name'],
            'complexity_level': workflow['complexity_level'],
            'workflow_type': workflow['workflow_type'],
            'approval_layers': approval_layers,
            'workflow_steps': workflow_steps,
            'total_timeline_days': total_timeline,
            'has_emergency_pathway': bool(workflow.get('regulatory_authority', {}).get('emergency_review_days')),
            'has_fast_track': bool(workflow.get('regulatory_authority', {}).get('fast_track_days')),
            'has_auto_approval': bool(workflow.get('regulatory_authority', {}).get('auto_approval_days')),
            'unique_features_count': len(workflow.get('unique_features', []))
        }
