# Configuration Templates

This directory contains YAML configuration files that define the clinical intelligence rules for Ilana PM.

## Configuration Files

### Task Ontology (`task_ontology.yaml`)
Defines 100+ canonical clinical trial tasks with:
- Task categories (Regulatory, Operational, Site, Data, Closeout)
- Typical/min/max durations
- Prerequisites and dependencies
- Authority-specific variations

**Status:** To be created in Milestone 1.2

### Authority Timelines (`authority_timelines.yaml`)
Defines regulatory authority-specific requirements:
- FDA (U.S. Food and Drug Administration)
- EMA (European Medicines Agency)
- MHRA (UK Medicines and Healthcare products Regulatory Agency)
- Regulatory gates and timelines
- Required documents

**Status:** To be created in Milestone 1.2

### Checklists (`checklists.yaml`)
Defines required checklist items for:
- Study Startup
- Site Initiation Visit (SIV)
- Site Activation Visit (SAV)
- Site Closeout

**Status:** To be created in Milestone 1.2

### Duration Bounds (`duration_bounds.yaml`)
Defines acceptable duration ranges for tasks by:
- Task category
- Study phase
- Regulatory authority

**Status:** To be created in Milestone 1.2

### Operational Sequences (`operational_sequences.yaml`)
Defines logical prerequisite rules and operational dependencies

**Status:** To be created in Milestone 1.2

### Parallelization Rules (`parallelization_rules.yaml`)
Defines opportunities for parallel task execution

**Status:** To be created in Milestone 1.2

## Editing Guidelines

These YAML files are designed to be human-readable and editable by clinical domain experts.

**Best Practices:**
- Use consistent indentation (2 spaces)
- Add comments to explain complex rules
- Reference regulatory sources where applicable
- Test changes by running validation endpoint

## Version Control

All configuration changes should be:
1. Tested locally first
2. Committed to Git with descriptive messages
3. Reviewed before deployment

## Hot Reload

The configuration loader supports hot-reload, allowing changes to take effect without restarting the server (feature to be implemented in Milestone 1.5).
