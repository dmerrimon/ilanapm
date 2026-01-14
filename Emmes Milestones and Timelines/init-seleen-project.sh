#!/bin/bash

# Seleen Project Initialization Script
# This script creates the complete project structure for the Seleen clinical trial timeline intelligence system
# Usage: bash init-seleen-project.sh [project-directory]

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default project directory
PROJECT_DIR="${1:-seleen}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Seleen Project Initialization                      ║${NC}"
echo -e "${BLUE}║     Clinical Trial Timeline Intelligence              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to create directory and print status
create_dir() {
    mkdir -p "$1"
    echo -e "${GREEN}✓${NC} Created: $1"
}

# Function to create file with content
create_file() {
    local filepath="$1"
    local content="$2"
    echo "$content" > "$filepath"
    echo -e "${GREEN}✓${NC} Created: $filepath"
}

echo -e "${YELLOW}Creating project structure in: ${PROJECT_DIR}${NC}"
echo ""

# Create root directory
create_dir "$PROJECT_DIR"
cd "$PROJECT_DIR"

# ============================================================================
# BACKEND STRUCTURE (Python/FastAPI)
# ============================================================================

echo -e "${BLUE}[1/4] Setting up Backend Service...${NC}"

create_dir "backend/app"
create_dir "backend/app/services"
create_dir "backend/app/config"
create_dir "backend/app/models"
create_dir "backend/app/utils"
create_dir "backend/config"
create_dir "backend/ml_models"
create_dir "backend/tests"
create_dir "backend/tests/unit"
create_dir "backend/tests/integration"
create_dir "backend/scripts"

# Backend main.py
create_file "backend/app/main.py" "\"\"\"
Seleen Backend API - Main Application Entry Point
\"\"\"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title=\"Seleen Intelligence API\",
    description=\"Clinical Trial Timeline Intelligence Service\",
    version=\"1.0.0\"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[\"*\"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=[\"*\"],
    allow_headers=[\"*\"],
)

@app.get(\"/\")
async def root():
    return {\"message\": \"Seleen Intelligence API\", \"version\": \"1.0.0\"}

@app.get(\"/health\")
async def health_check():
    return {\"status\": \"healthy\"}

if __name__ == \"__main__\":
    uvicorn.run(app, host=\"0.0.0.0\", port=8000)
"

# Backend models.py
create_file "backend/app/models.py" "\"\"\"
Seleen Data Models - Pydantic schemas for API
\"\"\"
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class TaskCategory(str, Enum):
    REGULATORY = \"Regulatory\"
    OPERATIONAL = \"Operational\"
    SITE = \"Site\"
    DATA = \"Data\"
    CLOSEOUT = \"Closeout\"

class GatingStatus(str, Enum):
    BLOCKED = \"Blocked\"
    READY = \"Ready\"
    COMPLETE = \"Complete\"

class TaskData(BaseModel):
    id: int
    name: str
    duration_days: int
    start_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    category: TaskCategory
    regulatory_authority: Optional[str] = None
    study_phase: Optional[str] = None
    therapeutic_area: Optional[str] = None
    is_mandatory: bool = True
    predecessors: List[int] = []
    
class ProjectData(BaseModel):
    project_name: str
    tasks: List[TaskData]
    regulatory_authority: str
    study_phase: str
    therapeutic_area: str
    
class ValidationViolation(BaseModel):
    task_id: int
    task_name: str
    violation_type: str
    severity: str  # \"Error\", \"Warning\", \"Info\"
    description: str
    suggested_fix: Optional[str] = None
    
class ValidationResult(BaseModel):
    is_valid: bool
    violations: List[ValidationViolation]
    summary: str
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    
class MLPrediction(BaseModel):
    duration_min: float
    duration_max: float
    confidence_pct: float
    explanation: str
    risk_factors: List[str] = []
    
class MLAdvisory(BaseModel):
    task_id: int
    prediction: MLPrediction
    risk_score: float  # 0-100
    delay_probability: float  # 0-100
    
class TeamsSummary(BaseModel):
    project_name: str
    channel_webhook_url: str
    validation_summary: str
    risk_count: int
    violation_count: int
"

# Rules Engine
create_file "backend/app/services/rules_engine.py" "\"\"\"
Seleen Rules Engine - Configuration-driven validation
\"\"\"
from typing import List
from app.models import TaskData, ValidationViolation, ProjectData

class RulesEngine:
    \"\"\"Clinical trial timeline validation engine\"\"\"
    
    def __init__(self, config: dict):
        self.config = config
        
    def validate(self, project: ProjectData) -> List[ValidationViolation]:
        \"\"\"Run all validation rules\"\"\"
        violations = []
        
        # Regulatory gating validation
        violations.extend(self._validate_regulatory_gating(project))
        
        # Operational sequence validation
        violations.extend(self._validate_operational_sequence(project))
        
        # Duration bounds validation
        violations.extend(self._validate_duration_bounds(project))
        
        # Dependency validation
        violations.extend(self._validate_dependencies(project))
        
        return violations
    
    def _validate_regulatory_gating(self, project: ProjectData) -> List[ValidationViolation]:
        \"\"\"Validate regulatory authority-specific gating\"\"\"
        # TODO: Implement regulatory gating logic
        return []
    
    def _validate_operational_sequence(self, project: ProjectData) -> List[ValidationViolation]:
        \"\"\"Validate operational prerequisites\"\"\"
        # TODO: Implement operational sequence logic
        return []
    
    def _validate_duration_bounds(self, project: ProjectData) -> List[ValidationViolation]:
        \"\"\"Validate task durations against benchmarks\"\"\"
        # TODO: Implement duration bounds logic
        return []
    
    def _validate_dependencies(self, project: ProjectData) -> List[ValidationViolation]:
        \"\"\"Validate task dependencies and detect cycles\"\"\"
        # TODO: Implement dependency validation
        return []
"

# ML Service
create_file "backend/app/services/ml_service.py" "\"\"\"
Seleen ML Service - Duration prediction and risk scoring
\"\"\"
from app.models import TaskData, MLPrediction
import numpy as np

class MLService:
    \"\"\"Machine learning advisory service\"\"\"
    
    def __init__(self):
        # TODO: Load actual models
        self.duration_model = None
        self.risk_model = None
    
    def predict_duration(self, task: TaskData) -> MLPrediction:
        \"\"\"Predict task duration with confidence interval\"\"\"
        # TODO: Implement actual ML prediction
        # For now, return mock prediction
        return MLPrediction(
            duration_min=task.duration_days * 0.8,
            duration_max=task.duration_days * 1.2,
            confidence_pct=75.0,
            explanation=\"Prediction based on historical data for similar tasks\",
            risk_factors=[\"New therapeutic area\", \"Complex protocol\"]
        )
    
    def score_risk(self, task: TaskData, context: dict) -> float:
        \"\"\"Calculate delay probability (0-100)\"\"\"
        # TODO: Implement actual risk scoring
        return 35.0
    
    def _extract_features(self, task: TaskData) -> np.ndarray:
        \"\"\"Extract features for ML model\"\"\"
        # TODO: Implement feature extraction
        return np.array([])
"

# Graph Service
create_file "backend/app/services/graph_service.py" "\"\"\"
Seleen Graph Service - Dependency graph analysis
\"\"\"
import networkx as nx
from typing import List, Tuple
from app.models import TaskData

class GraphService:
    \"\"\"Task dependency graph analysis\"\"\"
    
    def build_graph(self, tasks: List[TaskData]) -> nx.DiGraph:
        \"\"\"Build directed graph from tasks\"\"\"
        G = nx.DiGraph()
        
        for task in tasks:
            G.add_node(task.id, 
                      name=task.name,
                      duration=task.duration_days,
                      category=task.category)
            
            for pred_id in task.predecessors:
                G.add_edge(pred_id, task.id)
        
        return G
    
    def detect_cycles(self, G: nx.DiGraph) -> List[List[int]]:
        \"\"\"Detect circular dependencies\"\"\"
        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except:
            return []
    
    def critical_path(self, G: nx.DiGraph) -> List[int]:
        \"\"\"Calculate critical path\"\"\"
        if not nx.is_directed_acyclic_graph(G):
            return []
        
        # TODO: Implement weighted longest path
        return []
    
    def calculate_slack(self, G: nx.DiGraph) -> dict:
        \"\"\"Calculate slack/float for each task\"\"\"
        # TODO: Implement slack calculation
        return {}
"

# Configuration Manager
create_file "backend/app/config/config_manager.py" "\"\"\"
Seleen Configuration Manager - YAML config loading
\"\"\"
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    \"\"\"Load and manage YAML configurations\"\"\"
    
    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self._cache = {}
    
    def load_authority_timelines(self) -> Dict[str, Any]:
        \"\"\"Load regulatory authority timelines\"\"\"
        return self._load_yaml('authority_timelines.yaml')
    
    def load_task_ontology(self) -> Dict[str, Any]:
        \"\"\"Load canonical task definitions\"\"\"
        return self._load_yaml('task_ontology.yaml')
    
    def load_checklists(self) -> Dict[str, Any]:
        \"\"\"Load checklist definitions\"\"\"
        return self._load_yaml('checklists.yaml')
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        \"\"\"Load YAML file with caching\"\"\"
        if filename in self._cache:
            return self._cache[filename]
        
        filepath = self.config_dir / filename
        if not filepath.exists():
            return {}
        
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
            self._cache[filename] = data
            return data
"

# Requirements.txt
create_file "backend/requirements.txt" "fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pyyaml==6.0.1
networkx==3.2.1
scikit-learn==1.3.2
numpy==1.26.2
pandas==2.1.3
joblib==1.3.2
python-multipart==0.0.6
pytest==7.4.3
httpx==0.25.1
"

# Docker support
create_file "backend/Dockerfile" "FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]
"

create_file "backend/.dockerignore" "__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.git
.gitignore
README.md
"

# ============================================================================
# CONFIGURATION FILES (YAML)
# ============================================================================

echo -e "${BLUE}[2/4] Setting up Configuration Templates...${NC}"

# Task Ontology
create_file "backend/config/task_ontology.yaml" "# Seleen Task Ontology
# Canonical clinical trial tasks

version: 1.0

tasks:
  - id: protocol_development
    name: Protocol Development
    category: Regulatory
    mandatory: true
    typical_duration_days: 90
    dependencies: []
    parallel_eligible: false
    description: Development and finalization of clinical study protocol
    
  - id: ind_submission
    name: IND Submission
    category: Regulatory
    mandatory: true
    typical_duration_days: 30
    dependencies: [protocol_development]
    authority_specific: [FDA]
    parallel_eligible: false
    description: Investigational New Drug application to FDA
    
  - id: irb_submission
    name: IRB Submission
    category: Regulatory
    mandatory: true
    typical_duration_days: 45
    dependencies: [protocol_development, ind_submission]
    parallel_eligible: false
    description: Institutional Review Board submission and approval
    
  - id: site_selection
    name: Site Selection
    category: Operational
    mandatory: true
    typical_duration_days: 60
    dependencies: [protocol_development]
    parallel_eligible: true
    description: Identification and qualification of clinical sites
    
  - id: siv
    name: Site Initiation Visit
    category: Operational
    mandatory: true
    typical_duration_days: 14
    dependencies: [irb_submission, site_selection]
    parallel_eligible: false
    description: On-site training and activation
    
  - id: first_patient_in
    name: First Patient Enrolled
    category: Site
    mandatory: true
    typical_duration_days: 30
    dependencies: [siv]
    parallel_eligible: false
    description: Enrollment of first study participant

# Add more canonical tasks...
"

# Authority Timelines
create_file "backend/config/authority_timelines.yaml" "# Seleen Authority Timelines
# Regulatory authority-specific timelines and gating

version: 1.0

authorities:
  FDA:
    name: US Food and Drug Administration
    country: United States
    
    review_periods:
      ind_review_days: 30
      irb_review_days: 45
      protocol_amendment_days: 30
      annual_report_days: 60
      
    gating_sequence:
      - protocol_development
      - ind_submission
      - irb_submission
      - site_selection
      - siv
      - first_patient_in
      
    mandatory_tasks:
      - ind_submission
      - irb_submission
      
  EMA:
    name: European Medicines Agency
    country: European Union
    
    review_periods:
      cta_review_days: 60
      ethics_review_days: 60
      protocol_amendment_days: 35
      annual_report_days: 70
      
    gating_sequence:
      - protocol_development
      - cta_submission
      - ethics_submission
      - site_selection
      - siv
      - first_patient_in
      
    mandatory_tasks:
      - cta_submission
      - ethics_submission
"

# Checklists
create_file "backend/config/checklists.yaml" "# Seleen Checklists
# Clinical trial milestone checklists

version: 1.0

checklists:
  startup:
    name: Study Startup Checklist
    description: Required items before study initiation
    items:
      - id: startup_01
        description: Protocol finalized and approved
        task_mapping: protocol_development
        mandatory: true
        
      - id: startup_02
        description: Budget approved by sponsor
        task_mapping: budget_approval
        mandatory: true
        
      - id: startup_03
        description: CRO contracts executed
        task_mapping: cro_contracting
        mandatory: true
        
      - id: startup_04
        description: Regulatory submissions complete
        task_mapping: ind_submission
        mandatory: true
        
      - id: startup_05
        description: Insurance coverage in place
        task_mapping: insurance_setup
        mandatory: true
        
  siv:
    name: Site Initiation Visit Checklist
    description: Required before site activation
    items:
      - id: siv_01
        description: Site training materials prepared
        task_mapping: training_materials
        mandatory: true
        
      - id: siv_02
        description: Investigational product shipped
        task_mapping: ip_shipment
        mandatory: true
        
      - id: siv_03
        description: EDC system configured
        task_mapping: edc_setup
        mandatory: true
        
      - id: siv_04
        description: Site regulatory binder complete
        task_mapping: regulatory_binder
        mandatory: true
        
  closeout:
    name: Study Closeout Checklist
    description: Required for study completion
    items:
      - id: closeout_01
        description: All data queries resolved
        task_mapping: data_cleaning
        mandatory: true
        
      - id: closeout_02
        description: Database locked
        task_mapping: database_lock
        mandatory: true
        
      - id: closeout_03
        description: Final report submitted
        task_mapping: final_report
        mandatory: true
"

# ============================================================================
# ADD-IN STRUCTURE (C#)
# ============================================================================

echo -e "${BLUE}[3/4] Setting up Add-in Project...${NC}"

create_dir "add-in"
create_dir "add-in/Seleen.AddIn"
create_dir "add-in/Seleen.AddIn/Services"
create_dir "add-in/Seleen.AddIn/Data"
create_dir "add-in/Seleen.AddIn/Views"
create_dir "add-in/Seleen.AddIn/Fields"
create_dir "add-in/Seleen.AddIn/Utils"
create_dir "add-in/Seleen.AddIn/Properties"

# Add-in project file
create_file "add-in/Seleen.AddIn/Seleen.AddIn.csproj" "<?xml version=\"1.0\" encoding=\"utf-8\"?>
<Project Sdk=\"Microsoft.NET.Sdk\">
  <PropertyGroup>
    <TargetFramework>net6.0-windows</TargetFramework>
    <UseWindowsForms>true</UseWindowsForms>
    <OutputType>Library</OutputType>
    <RootNamespace>Seleen.AddIn</RootNamespace>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include=\"Microsoft.Office.Interop.MSProject\" Version=\"15.0.4797.1000\" />
    <PackageReference Include=\"Newtonsoft.Json\" Version=\"13.0.3\" />
    <PackageReference Include=\"Microsoft.Extensions.Logging\" Version=\"6.0.0\" />
    <PackageReference Include=\"Microsoft.Extensions.DependencyInjection\" Version=\"6.0.0\" />
  </ItemGroup>
</Project>
"

# SeleenRibbon.cs
create_file "add-in/Seleen.AddIn/SeleenRibbon.cs" "using System;
using Microsoft.Office.Tools.Ribbon;
using Seleen.AddIn.Services;

namespace Seleen.AddIn
{
    public partial class SeleenRibbon
    {
        private readonly ISeleenApiClient _apiClient;
        
        private void SeleenRibbon_Load(object sender, RibbonUIEventArgs e)
        {
            // Initialize services
        }

        private void btnValidateTimeline_Click(object sender, RibbonControlEventArgs e)
        {
            // TODO: Implement validation
            System.Windows.Forms.MessageBox.Show(\"Validating timeline...\");
        }

        private void btnViewReport_Click(object sender, RibbonControlEventArgs e)
        {
            // TODO: Show validation report
        }

        private void btnMLAdvisory_Click(object sender, RibbonControlEventArgs e)
        {
            // TODO: Get ML advisory
        }

        private void btnExportToTeams_Click(object sender, RibbonControlEventArgs e)
        {
            // TODO: Export to Teams
        }

        private void btnSettings_Click(object sender, RibbonControlEventArgs e)
        {
            // TODO: Show settings dialog
        }
    }
}
"

# API Client Interface
create_file "add-in/Seleen.AddIn/Services/ISeleenApiClient.cs" "using System.Threading.Tasks;
using Seleen.AddIn.Data;

namespace Seleen.AddIn.Services
{
    public interface ISeleenApiClient
    {
        Task<ValidationResult> ValidateTimelineAsync(ProjectData project);
        Task<MLAdvisory> GetMLAdvisoryAsync(TaskData task);
        Task<ConfigData> GetConfigurationAsync();
        Task<bool> PostToTeamsAsync(TeamsSummary summary);
    }
}
"

# Data Models
create_file "add-in/Seleen.AddIn/Data/DataModels.cs" "using System;
using System.Collections.Generic;

namespace Seleen.AddIn.Data
{
    public class TaskData
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public int DurationDays { get; set; }
        public DateTime? StartDate { get; set; }
        public DateTime? FinishDate { get; set; }
        public string Category { get; set; }
        public List<int> Predecessors { get; set; } = new List<int>();
    }

    public class ProjectData
    {
        public string ProjectName { get; set; }
        public List<TaskData> Tasks { get; set; } = new List<TaskData>();
        public string RegulatoryAuthority { get; set; }
        public string StudyPhase { get; set; }
        public string TherapeuticArea { get; set; }
    }

    public class ValidationResult
    {
        public bool IsValid { get; set; }
        public List<ValidationViolation> Violations { get; set; }
        public string Summary { get; set; }
    }

    public class ValidationViolation
    {
        public int TaskId { get; set; }
        public string TaskName { get; set; }
        public string ViolationType { get; set; }
        public string Severity { get; set; }
        public string Description { get; set; }
        public string SuggestedFix { get; set; }
    }

    public class MLAdvisory
    {
        public int TaskId { get; set; }
        public MLPrediction Prediction { get; set; }
        public double RiskScore { get; set; }
    }

    public class MLPrediction
    {
        public double DurationMin { get; set; }
        public double DurationMax { get; set; }
        public double ConfidencePct { get; set; }
        public string Explanation { get; set; }
    }

    public class TeamsSummary
    {
        public string ProjectName { get; set; }
        public string ChannelWebhookUrl { get; set; }
        public string ValidationSummary { get; set; }
        public int RiskCount { get; set; }
        public int ViolationCount { get; set; }
    }

    public class ConfigData
    {
        public Dictionary<string, object> Settings { get; set; }
    }
}
"

# ============================================================================
# DOCUMENTATION & SCRIPTS
# ============================================================================

echo -e "${BLUE}[4/4] Setting up Documentation and Scripts...${NC}"

create_dir "docs"
create_dir "scripts"

# README
create_file "README.md" "# Seleen - Clinical Trial Timeline Intelligence

**Version:** 1.0  
**Platform:** Microsoft Project Desktop (Windows)

## Overview

Seleen transforms Microsoft Project into a clinical-native planning environment with:
- Embedded clinical intelligence
- Regulatory-aware validation
- ML-assisted risk and duration prediction
- Executive-ready views

## Project Structure

\`\`\`
seleen/
├── add-in/          # C# VSTO add-in for MS Project
├── backend/         # Python FastAPI intelligence service
├── backend/config/  # YAML configuration templates
├── docs/            # Documentation
└── scripts/         # Utility scripts
\`\`\`

## Quick Start

### Backend Development

\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\\Scripts\\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
\`\`\`

API will be available at: http://localhost:8000

### Add-in Development

1. Open \`add-in/Seleen.AddIn.sln\` in Visual Studio 2022
2. Build the solution
3. Debug will launch MS Project with the add-in loaded

## Configuration

Edit YAML files in \`backend/config/\`:
- \`task_ontology.yaml\` - Canonical task definitions
- \`authority_timelines.yaml\` - Regulatory authority rules
- \`checklists.yaml\` - Milestone checklists

## Testing

### Backend Tests
\`\`\`bash
cd backend
pytest tests/
\`\`\`

### Add-in Tests
Run from Visual Studio Test Explorer

## Documentation

See \`docs/\` directory for:
- Architecture overview
- API documentation
- Field definitions
- Configuration guide

## License

Proprietary - Seleen by Don Merriman

## Contact

Founder: Don Merriman  
Platform: Ilana Clinical Intelligence Platform
"

# Development setup script
create_file "scripts/setup-dev-environment.sh" "#!/bin/bash
# Development environment setup

set -e

echo \"Setting up Seleen development environment...\"

# Backend setup
echo \"Setting up Python backend...\"
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

echo \"\"
echo \"✓ Backend setup complete\"
echo \"  Start with: cd backend && source venv/bin/activate && uvicorn app.main:app --reload\"
echo \"\"
echo \"Add-in setup:\"
echo \"  1. Open add-in/Seleen.AddIn.sln in Visual Studio\"
echo \"  2. Restore NuGet packages\"
echo \"  3. Build solution\"
echo \"\"
echo \"Development environment ready!\"
"

create_file "scripts/run-backend-local.sh" "#!/bin/bash
# Run backend service locally

cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"

create_file "scripts/run-tests.sh" "#!/bin/bash
# Run all tests

set -e

echo \"Running backend tests...\"
cd backend
source venv/bin/activate
pytest tests/ -v

echo \"\"
echo \"✓ All tests passed\"
"

# .gitignore
create_file ".gitignore" "# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/

# C#
bin/
obj/
*.user
*.suo
.vs/
*.cache
*.csproj.user
packages/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Config
*.env
.env.local

# ML Models
*.pkl
*.h5
*.pb

# Temporary
tmp/
temp/
"

# Make scripts executable
chmod +x "scripts/setup-dev-environment.sh" 2>/dev/null || true
chmod +x "scripts/run-backend-local.sh" 2>/dev/null || true
chmod +x "scripts/run-tests.sh" 2>/dev/null || true

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✓ Seleen Project Initialized Successfully         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Project created in: ${PROJECT_DIR}${NC}"
echo ""
echo "Next steps:"
echo "  1. cd ${PROJECT_DIR}"
echo "  2. bash scripts/setup-dev-environment.sh"
echo "  3. Start developing!"
echo ""
echo "Structure:"
echo "  ├── add-in/          - MS Project VSTO add-in (C#)"
echo "  ├── backend/         - Intelligence service (Python/FastAPI)"
echo "  ├── backend/config/  - YAML configurations"
echo "  ├── docs/            - Documentation"
echo "  └── scripts/         - Utility scripts"
echo ""
