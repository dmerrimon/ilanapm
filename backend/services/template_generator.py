"""
Template Generator Service

Generates country-specific clinical trial timeline templates by combining:
- Country-specific regulatory workflows (23 countries)
- Canonical task ontology with country variations
- Emmes industry-standard timelines (study startup, closeout)
"""

from config import load_config
from models.timeline import Timeline, Task, Dependency
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TemplateGenerator:
    """Generates country-specific timeline templates"""

    def __init__(self):
        """Initialize template generator with config data"""
        config = load_config()
        self.tasks = config.get('task_ontology', [])
        self.workflows = config.get('regulatory_workflows', [])
        self.authorities = config.get('authorities', [])

        logger.info(f"TemplateGenerator initialized: {len(self.tasks)} tasks, {len(self.workflows)} workflows")

    def generate_template(
        self,
        country_code: str,
        study_phase: str,
        therapeutic_area: str,
        include_optional: bool = True
    ) -> Timeline:
        """
        Generate country-specific timeline template

        Args:
            country_code: ISO country code (e.g., "US", "KE", "VN")
            study_phase: Study phase ("Phase I", "Phase II", "Phase III", "Phase IV")
            therapeutic_area: Therapeutic area (e.g., "Oncology", "Infectious Disease")
            include_optional: Include optional tasks

        Returns:
            Timeline object with country-specific tasks and dependencies
            All 92 tasks from ontology are included based on category filters

        Example:
            >>> generator = TemplateGenerator()
            >>> timeline = generator.generate_template("KE", "Phase III", "Infectious Disease")
            >>> len(timeline.tasks)  # Returns task count including Kenya 3-layer workflow
        """
        # Get country workflow
        workflow = self._get_workflow(country_code)
        logger.info(f"Generating template for {workflow['country_name']} - {study_phase} - {therapeutic_area}")

        # Build regulatory tasks (country-specific)
        regulatory_tasks = self._build_regulatory_tasks(workflow, study_phase, therapeutic_area)

        # Build operational tasks
        # Fixed Bug #2: Removed redundant _build_emmes_tasks() - all 92 tasks now come from ontology
        operational_tasks = self._build_operational_tasks(
            study_phase,
            therapeutic_area,
            include_optional,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            )
        )

        # Combine all tasks
        all_tasks = regulatory_tasks + operational_tasks
        logger.info(f"Generated {len(all_tasks)} tasks: {len(regulatory_tasks)} regulatory, " +
                   f"{len(operational_tasks)} operational (from ontology)")

        # Build dependencies
        dependencies = self._build_dependencies(all_tasks, workflow)

        # Create timeline
        timeline = Timeline(
            study_name=f"{workflow['country_name']} {study_phase} - {therapeutic_area}",
            phase=study_phase,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            therapeutic_area=therapeutic_area,
            tasks=all_tasks,
            dependencies=dependencies
        )

        return timeline

    def _get_workflow(self, country_code: str) -> Dict:
        """Get regulatory workflow for a country"""
        for workflow in self.workflows:
            if workflow['country_code'] == country_code:
                return workflow

        # If not found, raise error with helpful message
        available_codes = [w['country_code'] for w in self.workflows]
        raise ValueError(
            f"No workflow found for country: {country_code}. " +
            f"Available countries: {', '.join(sorted(available_codes))}"
        )

    def _build_regulatory_tasks(
        self,
        workflow: Dict,
        phase: str,
        therapeutic_area: str
    ) -> List[Task]:
        """Build country-specific regulatory tasks"""
        tasks = []

        # Find regulatory tasks in ontology
        regulatory_task_defs = [t for t in self.tasks if t.get('category') == 'Regulatory']

        for task_def in regulatory_task_defs:
            # Apply country-specific variation
            duration = self._get_country_duration(task_def, workflow, phase)

            # Skip if duration is None (task not applicable to this country)
            if duration is None:
                continue

            task = Task(
                id=task_def['id'],
                name=f"{task_def['name']} - {workflow['country_name']}",
                duration_days=duration,
                category='Regulatory',
                phase=phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=task_def.get('is_mandatory', True)
            )
            tasks.append(task)

        # Add country-specific multi-layer approvals
        # Three-layer: e.g., Kenya EC → PPB → NACOSTI
        if workflow.get('workflow_type') == 'three_layer_sequential':
            tasks.extend(self._build_three_layer_tasks(workflow, phase, therapeutic_area))

        # Four-layer: e.g., Vietnam CEBRGL → ASTT → NECBR → Minister
        if workflow.get('workflow_type') == 'four_layer_sequential':
            tasks.extend(self._build_four_layer_tasks(workflow, phase, therapeutic_area))

        return tasks

    def _map_category(self, category: str) -> str:
        """Map ontology categories to TaskCategory enum values"""
        category_map = {
            'Planning': 'Operational',
            'Site Management': 'Site',
            'Data Management': 'Data',
            'Operational': 'Operational',
            'Regulatory': 'Regulatory',
            'Closeout': 'Closeout'
        }
        return category_map.get(category, 'Operational')

    def _map_authority(self, authority_code: str, country_code: str, country_name: str) -> str:
        """Map authority codes to RegulatoryAuthority enum values"""
        # Authority mapping based on country
        authority_map = {
            # Africa
            'MCAZ-ZW': 'MCAZ Zimbabwe',
            'PPB': 'PPB Kenya',
            'NACOSTI': 'PPB Kenya',  # Map NACOSTI to PPB Kenya (same regulatory framework)
            'LMHRA': 'LMHRA Liberia',
            'PMRA': 'MCAZ Malawi',
            'DPM': 'DPM Mali',
            'PBSL': 'PSLB Sierra Leone',
            'SAHPRA': 'SAHPRA South Africa',
            'TMDA': 'TFDA Tanzania',
            'NDA': 'NDA Uganda',
            'ACOREP': 'DGRDF DRC',
            'DNPM': 'DNPL Guinea',
            # Americas
            'FDA': 'FDA' if country_code == 'US' else 'FDA United States',
            'COFEPRIS': 'COFEPRIS Mexico',
            'INS': 'DIGEMID Peru',
            # Asia-Pacific
            'TGA': 'TGA Australia',
            'DGDA': 'BFDA Bangladesh',
            'NMPA': 'NMPA China',
            'DCGI': 'CDSCO India',
            'Thai FDA': 'FDA Thailand',
            'MOH': 'MOH Vietnam',
            'MOH_ASTT': 'MOH Vietnam',
            'CEBRGL': 'MOH Vietnam',
            'NECBR': 'MOH Vietnam',
            'Minister': 'MOH Vietnam',
            # Europe
            'MHRA': 'MHRA' if country_code == 'GB' else 'MHRA United Kingdom',
            # Ethics authorities
            'EC': 'FDA',  # Default to FDA for ethics committees
            'HREC': 'TGA Australia',
            'REB': 'Health Canada',
            'IRB': 'FDA'
        }

        mapped = authority_map.get(authority_code, authority_code)
        # If still just a code and not in the map, default to primary authority for the country
        if mapped == authority_code and authority_code not in ['FDA', 'EMA', 'MHRA', 'PMDA']:
            # Default to the country's primary regulatory authority
            country_authorities = {
                'KE': 'PPB Kenya',
                'US': 'FDA',
                'GB': 'MHRA United Kingdom',
                'AU': 'TGA Australia',
                'CA': 'Health Canada',
                'ZW': 'MCAZ Zimbabwe',
                'UG': 'NDA Uganda',
                'TZ': 'TFDA Tanzania',
                'ZA': 'SAHPRA South Africa',
                'SL': 'PSLB Sierra Leone',
                'ML': 'DPM Mali',
                'MW': 'MCAZ Malawi',
                'LR': 'LMHRA Liberia',
                'CD': 'DGRDF DRC',
                'GN': 'DNPL Guinea',
                'MX': 'COFEPRIS Mexico',
                'PE': 'DIGEMID Peru',
                'BD': 'BFDA Bangladesh',
                'CN': 'NMPA China',
                'IN': 'CDSCO India',
                'TH': 'FDA Thailand',
                'VN': 'MOH Vietnam'
            }
            return country_authorities.get(country_code, 'FDA')
        return mapped

    def _get_country_duration(self, task_def: Dict, workflow: Dict, phase: str) -> Optional[int]:
        """Get country-specific duration for a task"""
        country_code = workflow['country_code']

        # Check for country-specific variation
        country_variations = task_def.get('country_variations', {})
        if country_code in country_variations:
            return country_variations[country_code].get('duration_days', task_def['typical_duration_days'])

        # Use workflow authority review days for regulatory tasks
        if task_def.get('category') == 'Regulatory':
            return workflow['regulatory_authority'].get('review_days', task_def.get('typical_duration_days', 30))

        return task_def.get('typical_duration_days', 30)

    def _build_three_layer_tasks(
        self,
        workflow: Dict,
        phase: str,
        therapeutic_area: str
    ) -> List[Task]:
        """Build tasks for three-layer sequential workflows (e.g., Kenya: EC → PPB → NACOSTI)"""
        tasks = []

        # Layer 1: Ethics Committee (use specific authority name)
        ec_duration = workflow['ethics_authority'].get('review_days')
        if ec_duration is None:
            ec_duration = 30  # Default to 30 days if not specified

        tasks.append(Task(
            id=f"REG-{workflow['country_code']}-EC",
            name=f"{workflow['ethics_authority']['name']} Approval - {workflow['country_name']}",
            duration_days=ec_duration,
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(
                workflow['ethics_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            country=workflow['country_code'],
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Layer 2: Primary Regulatory Authority (e.g., PPB in Kenya)
        tasks.append(Task(
            id=f"REG-{workflow['country_code']}-REG",
            name=f"{workflow['regulatory_authority']['name']} Approval - {workflow['country_name']}",
            duration_days=workflow['regulatory_authority'].get('review_days', 30),
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            country=workflow['country_code'],
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Layer 3: Additional authorities/bodies (e.g., NACOSTI in Kenya)
        additional_bodies = workflow.get('additional_bodies', workflow.get('additional_authorities', []))
        for auth in additional_bodies:
            tasks.append(Task(
                id=f"REG-{workflow['country_code']}-{auth['code']}",
                name=f"{auth['name']} Clearance - {workflow['country_name']}",
                duration_days=auth.get('review_days', 30),
                category='Regulatory',
                phase=phase,
                authority=self._map_authority(
                    auth['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ))

        return tasks

    def _build_four_layer_tasks(
        self,
        workflow: Dict,
        phase: str,
        therapeutic_area: str
    ) -> List[Task]:
        """Build tasks for four-layer sequential workflows (e.g., Vietnam: CEBRGL → ASTT → NECBR → Minister)"""
        tasks = []

        # Layer 1: Local/Institutional Ethics Committee (CEBRGL)
        ec_duration = workflow['ethics_authority'].get('review_days')
        if ec_duration is None:
            ec_duration = 30  # Default to 30 days if not specified

        tasks.append(Task(
            id=f"REG-{workflow['country_code']}-EC",
            name=f"{workflow['ethics_authority']['name']} Approval - {workflow['country_name']}",
            duration_days=ec_duration,
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(
                workflow['ethics_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            country=workflow['country_code'],
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Layer 2: Regulatory Authority (ASTT in Vietnam)
        tasks.append(Task(
            id=f"REG-{workflow['country_code']}-REG",
            name=f"{workflow['regulatory_authority']['name']} Review - {workflow['country_name']}",
            duration_days=workflow['regulatory_authority'].get('review_days', 30),
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            country=workflow['country_code'],
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Layer 3 & 4: Additional bodies (NECBR, Minister)
        additional_bodies = workflow.get('additional_bodies', [])
        for auth in additional_bodies:
            tasks.append(Task(
                id=f"REG-{workflow['country_code']}-{auth['code']}",
                name=f"{auth['name']} - {workflow['country_name']}",
                duration_days=auth.get('review_days', 30),
                category='Regulatory',
                phase=phase,
                authority=self._map_authority(
                    auth['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ))

        return tasks

    def _build_operational_tasks(
        self,
        phase: str,
        therapeutic_area: str,
        include_optional: bool,
        authority: str = "FDA"
    ) -> List[Task]:
        """Build operational (non-regulatory) tasks"""
        tasks = []

        # Find operational tasks in ontology
        # Fixed: Use actual category names from task_ontology.yaml
        # Includes ALL non-regulatory categories (92 tasks total)
        operational_categories = ['Operational', 'Site', 'Data', 'Closeout',
                                 'Pharmacy', 'Laboratory', 'Documents', 'Safety']
        operational_task_defs = [
            t for t in self.tasks
            if t.get('category') in operational_categories
        ]

        for task_def in operational_task_defs:
            # Skip optional tasks if not included
            if not include_optional and not task_def.get('is_mandatory', False):
                continue

            task = Task(
                id=task_def['id'],
                name=task_def['name'],
                duration_days=task_def.get('typical_duration_days', 30),
                category=self._map_category(task_def.get('category', 'Operational')),
                phase=phase,
                authority=authority,
                therapeutic_area=therapeutic_area,
                is_mandatory=task_def.get('is_mandatory', False)
            )
            tasks.append(task)

        return tasks

    def _build_emmes_tasks(self, phase: str, therapeutic_area: str, authority: str = "FDA") -> List[Task]:
        """
        Build Emmes industry-standard timeline tasks

        Based on:
        - Emmes Study Startup Overview Timeline v3.0
        - Emmes Study Closeout Overview Timeline v3.0
        """
        emmes_tasks = []

        # ===== STUDY STARTUP TASKS =====

        # Protocol Development (~6 months)
        emmes_tasks.append(Task(
            id='EMMES-001',
            name='Protocol Development',
            duration_days=180,
            category='Operational',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Data Collection Forms (4 weeks after protocol)
        emmes_tasks.append(Task(
            id='EMMES-002',
            name='Data Collection Forms Development',
            duration_days=28,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Manual of Procedures (2 weeks after protocol)
        emmes_tasks.append(Task(
            id='EMMES-003',
            name='Manual of Procedures (MOP) v1.0',
            duration_days=14,
            category='Operational',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Data System Configuration (6 weeks after final forms)
        emmes_tasks.append(Task(
            id='EMMES-004',
            name='Data System Configuration',
            duration_days=42,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Site Training (before activation)
        emmes_tasks.append(Task(
            id='EMMES-005',
            name='Site Training',
            duration_days=3,
            category='Site',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # ===== STUDY CLOSEOUT TASKS =====

        # Clinical Data Entry (4 days after LPLV)
        emmes_tasks.append(Task(
            id='EMMES-006',
            name='Clinical Data Entry',
            duration_days=4,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Data Cleaning (2 weeks after entry)
        emmes_tasks.append(Task(
            id='EMMES-007',
            name='Data Cleaning',
            duration_days=14,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Database Lock
        emmes_tasks.append(Task(
            id='EMMES-008',
            name='Database Lock',
            duration_days=1,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Clinical Study Report (8 weeks after database lock)
        emmes_tasks.append(Task(
            id='EMMES-009',
            name='Clinical Study Report (CSR)',
            duration_days=56,
            category='Regulatory',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        return emmes_tasks

    def _build_dependencies(self, tasks: List[Task], workflow: Dict) -> List[Dependency]:
        """Build dependencies between tasks"""
        dependencies = []
        task_map = {t.id: t for t in tasks}

        # Emmes dependencies (from Emmes timeline PDFs)
        emmes_deps = [
            ('EMMES-001', 'EMMES-002'),  # Protocol → Data Collection Forms
            ('EMMES-001', 'EMMES-003'),  # Protocol → MOP
            ('EMMES-002', 'EMMES-004'),  # Final Forms → Data System
            ('EMMES-006', 'EMMES-007'),  # Data Entry → Data Cleaning
            ('EMMES-007', 'EMMES-008'),  # Data Cleaning → Database Lock
            ('EMMES-008', 'EMMES-009'),  # Database Lock → CSR
        ]

        for predecessor_id, successor_id in emmes_deps:
            if predecessor_id in task_map and successor_id in task_map:
                dependencies.append(Dependency(
                    predecessor_id=predecessor_id,
                    successor_id=successor_id,
                    type='finish-to-start',
                    lag_days=0
                ))

        # Three-layer sequential dependencies (e.g., Kenya: EC → PPB → NACOSTI)
        if workflow.get('workflow_type') == 'three_layer_sequential':
            country_code = workflow['country_code']

            # EC → Regulatory Authority
            ec_id = f"REG-{country_code}-EC"
            reg_id = f"REG-{country_code}-REG"
            if ec_id in task_map and reg_id in task_map:
                dependencies.append(Dependency(
                    predecessor_id=ec_id,
                    successor_id=reg_id,
                    type='finish-to-start',
                    lag_days=0
                ))

            # Regulatory Authority → Additional authorities/bodies
            additional_bodies = workflow.get('additional_bodies', workflow.get('additional_authorities', []))
            for auth in additional_bodies:
                auth_id = f"REG-{country_code}-{auth['code']}"
                if reg_id in task_map and auth_id in task_map:
                    dependencies.append(Dependency(
                        predecessor_id=reg_id,
                        successor_id=auth_id,
                        type='finish-to-start',
                        lag_days=0
                    ))

        # Four-layer sequential dependencies (e.g., Vietnam: CEBRGL → ASTT → NECBR → Minister)
        if workflow.get('workflow_type') == 'four_layer_sequential':
            country_code = workflow['country_code']

            # Layer 1 → Layer 2: EC → Regulatory Authority
            ec_id = f"REG-{country_code}-EC"
            reg_id = f"REG-{country_code}-REG"
            if ec_id in task_map and reg_id in task_map:
                dependencies.append(Dependency(
                    predecessor_id=ec_id,
                    successor_id=reg_id,
                    type='finish-to-start',
                    lag_days=0
                ))

            # Layer 2 → Layer 3 → Layer 4: Sequential chain through additional bodies
            additional_bodies = workflow.get('additional_bodies', [])
            predecessor_id = reg_id
            for auth in additional_bodies:
                auth_id = f"REG-{country_code}-{auth['code']}"
                if predecessor_id in task_map and auth_id in task_map:
                    dependencies.append(Dependency(
                        predecessor_id=predecessor_id,
                        successor_id=auth_id,
                        type='finish-to-start',
                        lag_days=0
                    ))
                    predecessor_id = auth_id  # Chain to next layer

        return dependencies
