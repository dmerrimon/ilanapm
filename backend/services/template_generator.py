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

        # Build operational tasks from ontology (92 tasks)
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

        # Build industry-standard milestone tasks (fills gaps in ontology)
        # These provide key milestones for Protocol Development, Data Entry, Data Cleaning
        # which are missing from the ontology
        industry_tasks = self._build_industry_standard_tasks(
            study_phase,
            therapeutic_area,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            )
        )

        # Combine all tasks
        all_tasks = regulatory_tasks + operational_tasks + industry_tasks
        logger.info(f"Generated {len(all_tasks)} tasks: {len(regulatory_tasks)} regulatory, " +
                   f"{len(operational_tasks)} operational (from ontology), " +
                   f"{len(industry_tasks)} industry-standard milestones")

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

    def _build_industry_standard_tasks(self, phase: str, therapeutic_area: str, authority: str = "FDA") -> List[Task]:
        """
        Build industry-standard timeline tasks

        Based on standard CRO timelines and CPM site activation checklists
        """
        industry_tasks = []

        # ===== STUDY STARTUP TASKS =====

        # Protocol Development (~6 months)
        industry_tasks.append(Task(
            id='IND-100',
            name='Protocol Development',
            duration_days=180,
            category='Operational',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Data Collection Forms (4 weeks after protocol)
        industry_tasks.append(Task(
            id='IND-101',
            name='Data Collection Forms Development',
            duration_days=28,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Manual of Procedures (2 weeks after protocol)
        industry_tasks.append(Task(
            id='IND-102',
            name='Manual of Procedures (MOP) v1.0',
            duration_days=14,
            category='Operational',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Data System Configuration (6 weeks after final forms)
        industry_tasks.append(Task(
            id='IND-103',
            name='Data System Configuration',
            duration_days=42,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Site Training (before activation)
        industry_tasks.append(Task(
            id='IND-104',
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
        industry_tasks.append(Task(
            id='IND-105',
            name='Clinical Data Entry',
            duration_days=4,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Data Cleaning (2 weeks after entry)
        industry_tasks.append(Task(
            id='IND-106',
            name='Data Cleaning',
            duration_days=14,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Database Lock
        industry_tasks.append(Task(
            id='IND-107',
            name='Database Lock',
            duration_days=1,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Clinical Study Report (8 weeks after database lock)
        industry_tasks.append(Task(
            id='IND-108',
            name='Clinical Study Report (CSR)',
            duration_days=56,
            category='Regulatory',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        return industry_tasks

    def _build_dependencies(self, tasks: List[Task], workflow: Dict) -> List[Dependency]:
        """Build dependencies between tasks"""
        dependencies = []
        task_map = {t.id: t for t in tasks}

        # ===== STUDY STARTUP DEPENDENCIES =====
        # Based on industry-standard CRO timelines
        startup_deps = [
            ('IND-100', 'IND-101'),   # Protocol Development → Data Collection Forms
            ('IND-100', 'IND-102'),   # Protocol Development → MOP
            ('IND-101', 'IND-103'),   # Data Collection Forms → Data System Configuration
            ('IND-103', 'DATA-016'),  # Data System Configuration → Database Deployed
            ('DATA-016', 'IND-104'),  # Database Deployed → Site Training
            ('IND-104', 'SITE-001'),  # Site Training → Site Initiation Visit
            ('SITE-001', 'SITE-002'), # Site Initiation Visit → Site Activation
        ]

        # ===== STUDY EXECUTION DEPENDENCIES =====
        execution_deps = [
            ('SITE-002', 'SITE-003'), # Site Activation → First Patient In
            ('SITE-003', 'SITE-004'), # First Patient In → Patient Enrollment Period
            ('SITE-004', 'SITE-005'), # Patient Enrollment Period → Last Patient Last Visit (LPLV)
        ]

        # ===== STUDY CLOSEOUT DEPENDENCIES =====
        closeout_deps = [
            ('SITE-005', 'IND-105'),  # LPLV → Clinical Data Entry
            ('IND-105', 'IND-106'),   # Clinical Data Entry → Data Cleaning
            ('IND-106', 'IND-107'),   # Data Cleaning → Database Lock (industry-standard milestone)
            ('IND-107', 'DATA-001'),  # Database Lock milestone → Clinical Database Lock (ontology task)
            ('DATA-001', 'DATA-004'), # Clinical Database Lock → CSR Writing
            ('DATA-004', 'REG-031'),  # CSR Writing → Final Regulatory Submissions
        ]

        # Combine all industry-standard dependencies
        all_industry_deps = startup_deps + execution_deps + closeout_deps

        for predecessor_id, successor_id in all_industry_deps:
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

        # ====================================================================================
        # CRITICAL: Link regulatory approvals to operational tasks
        # ====================================================================================
        # In reality, you CANNOT start site activation or patient enrollment without
        # regulatory approval. This links the final regulatory approval to key milestones.

        final_approval_task_id = self._get_final_regulatory_approval_id(workflow, task_map)

        # Tasks that require regulatory approval before starting
        tasks_requiring_approval = [
            'SITE-002',     # Site Activation
            'SITE-003',     # First Patient In (FPI)
            'SITE-004',     # Patient Enrollment Period
            'IND-018',      # Data System Opens for Enrollment
        ]

        if final_approval_task_id and final_approval_task_id in task_map:
            for task_id in tasks_requiring_approval:
                if task_id in task_map:
                    dependencies.append(Dependency(
                        predecessor_id=final_approval_task_id,
                        successor_id=task_id,
                        type='finish-to-start',
                        lag_days=0
                    ))

        return dependencies

    def _get_final_regulatory_approval_id(self, workflow: Dict, task_map: Dict) -> Optional[str]:
        """
        Get the final regulatory approval task ID for a workflow

        This is the LAST regulatory approval that must complete before
        operational activities (site activation, enrollment) can begin.

        Args:
            workflow: Country workflow configuration
            task_map: Map of task IDs to Task objects

        Returns:
            Task ID of final regulatory approval, or None if not found
        """
        workflow_type = workflow.get('workflow_type')
        country_code = workflow['country_code']

        # Three-layer sequential (e.g., Kenya: EC → PPB → NACOSTI)
        # Final approval = last additional body (NACOSTI)
        if workflow_type == 'three_layer_sequential':
            additional_bodies = workflow.get('additional_bodies', workflow.get('additional_authorities', []))
            if additional_bodies:
                # Last body in the list is the final approval
                last_auth = additional_bodies[-1]
                final_id = f"REG-{country_code}-{last_auth['code']}"
                if final_id in task_map:
                    return final_id
            # Fallback to regulatory authority if no additional bodies
            return f"REG-{country_code}-REG" if f"REG-{country_code}-REG" in task_map else None

        # Four-layer sequential (e.g., Vietnam: CEBRGL → ASTT → NECBR → Minister)
        # Final approval = last additional body (Minister)
        elif workflow_type == 'four_layer_sequential':
            additional_bodies = workflow.get('additional_bodies', [])
            if additional_bodies:
                last_auth = additional_bodies[-1]
                final_id = f"REG-{country_code}-{last_auth['code']}"
                if final_id in task_map:
                    return final_id
            # Fallback to regulatory authority
            return f"REG-{country_code}-REG" if f"REG-{country_code}-REG" in task_map else None

        # Parallel workflows (e.g., US: FDA || IRB)
        # Both must complete - we'll link BOTH to operational tasks
        # For parallel workflows, use ontology-based regulatory tasks (REG-001, REG-002)
        elif workflow_type in ['parallel', 'parallel_integrated']:
            # Check for ontology regulatory tasks that represent final approval
            # REG-001: IND/CTA Submission & Review (FDA-equivalent)
            # REG-002: IRB/EC Approval (IRB-equivalent)
            # REG-INT-003: Ministerial/Final Approval (if exists)

            # Priority: Final approval > IND/CTA > IRB/EC
            if 'REG-INT-003' in task_map:
                return 'REG-INT-003'
            elif 'REG-002' in task_map:
                return 'REG-002'  # IRB/EC approval is typically the gate for enrollment
            elif 'REG-001' in task_map:
                return 'REG-001'

            return None

        # Sequential workflows (e.g., Bangladesh: NREC → DGDA)
        # Final approval = regulatory authority (second layer)
        elif workflow_type == 'sequential':
            final_id = f"REG-{country_code}-REG"
            if final_id in task_map:
                return final_id
            # Fallback to ontology regulatory tasks
            return self._get_ontology_regulatory_fallback(task_map)

        # Concurrent-sequential (e.g., DRC, India: Submit both, but regulatory waits for EC)
        # Final approval = regulatory authority (must approve after EC)
        elif workflow_type in ['concurrent_sequential', 'concurrent_sequential_multibody']:
            final_id = f"REG-{country_code}-REG"
            if final_id in task_map:
                return final_id
            return self._get_ontology_regulatory_fallback(task_map)

        # Flexible workflows (e.g., Sierra Leone: can be sequential OR parallel)
        # Assume sequential by default - regulatory authority is final
        elif workflow_type == 'flexible':
            final_id = f"REG-{country_code}-REG"
            if final_id in task_map:
                return final_id
            return self._get_ontology_regulatory_fallback(task_map)

        # Multi-body systems (e.g., Tanzania: TMDA + NatHREC + COSTECH)
        # Final approval = regulatory authority (TMDA in Tanzania)
        elif workflow_type in ['three_body_hybrid', 'four_body_parallel']:
            final_id = f"REG-{country_code}-REG"
            if final_id in task_map:
                return final_id
            return self._get_ontology_regulatory_fallback(task_map)

        # Dual pathway (China: standard vs HGR)
        # Assume standard pathway - regulatory authority
        elif workflow_type == 'dual_pathway':
            final_id = f"REG-{country_code}-REG"
            if final_id in task_map:
                return final_id
            return self._get_ontology_regulatory_fallback(task_map)

        # Default fallback - use ontology tasks
        return self._get_ontology_regulatory_fallback(task_map)

    def _get_ontology_regulatory_fallback(self, task_map: Dict) -> Optional[str]:
        """
        Fallback to ontology-based regulatory tasks when country-specific tasks don't exist

        For countries using parallel or other workflows that don't create custom regulatory
        tasks, we fall back to the ontology tasks.

        Args:
            task_map: Map of task IDs to Task objects

        Returns:
            Task ID of ontology regulatory task, or None
        """
        # Priority order:
        # 1. Ministerial/Final Approval (highest authority)
        # 2. IRB/EC Approval (required for patient protection)
        # 3. IND/CTA Submission (regulatory submission)

        if 'REG-INT-003' in task_map:
            return 'REG-INT-003'  # Ministerial/Final Approval
        elif 'REG-002' in task_map:
            return 'REG-002'  # IRB/EC Approval
        elif 'REG-001' in task_map:
            return 'REG-001'  # IND/CTA Submission & Review

        return None
