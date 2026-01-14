# Seleen Technical Architecture

**Version:** 1.0  
**Date:** January 14, 2026  
**Author:** Claude (AI-assisted)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Security Architecture](#security-architecture)
6. [Deployment Architecture](#deployment-architecture)
7. [Development Guidelines](#development-guidelines)

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Microsoft Project Desktop                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Seleen VSTO Add-in (C#)                   │ │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────────┐  │ │
│  │  │ Ribbon   │  │  Custom  │  │  View               │  │ │
│  │  │ UI       │  │  Fields  │  │  Managers           │  │ │
│  │  └──────────┘  └──────────┘  └─────────────────────┘  │ │
│  │         │              │                 │             │ │
│  │         └──────────────┴─────────────────┘             │ │
│  │                        │                               │ │
│  │                 ┌──────▼──────┐                        │ │
│  │                 │  API Client │                        │ │
│  │                 └──────┬──────┘                        │ │
│  └────────────────────────┼────────────────────────────────┘ │
└─────────────────────────────┼──────────────────────────────┘
                              │ HTTPS/REST
                              │
          ┌───────────────────▼────────────────────┐
          │      Azure App Service (Python)        │
          │  ┌──────────────────────────────────┐  │
          │  │     FastAPI Backend Service      │  │
          │  │  ┌────────────┐  ┌────────────┐  │  │
          │  │  │   Rules    │  │     ML     │  │  │
          │  │  │   Engine   │  │   Advisory │  │  │
          │  │  └────────────┘  └────────────┘  │  │
          │  │  ┌────────────┐  ┌────────────┐  │  │
          │  │  │   Config   │  │   Graph    │  │  │
          │  │  │   Manager  │  │   Logic    │  │  │
          │  │  └────────────┘  └────────────┘  │  │
          │  └──────────────────────────────────┘  │
          └───────────────────┬────────────────────┘
                              │
          ┌───────────────────▼────────────────────┐
          │        Azure Blob Storage              │
          │  ┌──────────────────────────────────┐  │
          │  │  Config Files (YAML)             │  │
          │  │  ML Model Artifacts              │  │
          │  │  Authority Timeline Data         │  │
          │  └──────────────────────────────────┘  │
          └────────────────────────────────────────┘
                              │
          ┌───────────────────▼────────────────────┐
          │      Microsoft Teams Integration       │
          │  ┌──────────────────────────────────┐  │
          │  │  Teams Bot (Notifications)       │  │
          │  │  Channel Webhooks                │  │
          │  └──────────────────────────────────┘  │
          └────────────────────────────────────────┘
```

### 1.2 Design Principles

1. **Separation of Concerns**: Add-in handles UI/UX, backend handles intelligence
2. **Configuration-Driven**: Business logic externalized to YAML configs
3. **Explainable Intelligence**: All ML outputs include reasoning
4. **Fail-Safe Operations**: Add-in works offline with cached data
5. **Enterprise-Ready**: No PHI, audit logging, version control

---

## 2. Component Architecture

### 2.1 VSTO Add-in (C#)

**Technology**: .NET 6.0, VSTO, Microsoft.Office.Interop.MSProject

**Core Modules**:

#### 2.1.1 Ribbon Manager
```csharp
namespace Seleen.AddIn.UI
{
    public class SeleenRibbon
    {
        // Ribbon buttons and controls
        - ValidateTimeline()
        - ViewValidationReport()
        - ConfigureSettings()
        - RefreshIntelligence()
        - ExportToTeams()
    }
}
```

#### 2.1.2 Custom Field Manager
```csharp
namespace Seleen.AddIn.Fields
{
    public class CustomFieldManager
    {
        // Field definitions
        - RegulatoryAuthority (Text)
        - StudyPhase (Text: "Phase I", "Phase II", "Phase III", "Phase IV")
        - TherapeuticArea (Text)
        - TaskCategory (Text: "Regulatory", "Operational", "Site", "Data", "Closeout")
        - GatingStatus (Text: "Blocked", "Ready", "Complete")
        - ChecklistStatus (Number: 0-100%)
        - RiskScore (Number: 0-100)
        - MLPredictedDuration (Text: "X-Y days")
        - MLConfidence (Number: 0-100%)
        - IsMandatory (Yes/No)
    }
}
```

#### 2.1.3 API Client
```csharp
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
```

#### 2.1.4 Data Extractor
```csharp
namespace Seleen.AddIn.Data
{
    public class ProjectExtractor
    {
        // Extract project data
        - ExtractTasks(): List<TaskData>
        - ExtractDependencies(): List<DependencyData>
        - ExtractCustomFields(): Dictionary<string, object>
        - ExtractResources(): List<ResourceData>
        
        // Write back results
        - UpdateTaskFields(ValidationResult result)
        - ApplyRecommendations(MLAdvisory advisory)
    }
}
```

#### 2.1.5 View Manager
```csharp
namespace Seleen.AddIn.Views
{
    public class ViewManager
    {
        // Pre-built views
        - CreateValidationView()
        - CreateRiskView()
        - CreateExecutiveSummaryView()
        - CreateChecklistView()
        
        // Filters
        - FilterByRiskLevel()
        - FilterByGatingStatus()
        - FilterByAuthority()
    }
}
```

**Key Dependencies**:
- Microsoft.Office.Interop.MSProject
- System.Net.Http (API calls)
- Newtonsoft.Json
- Microsoft.Extensions.Logging

---

### 2.2 Backend Service (Python)

**Technology**: Python 3.11+, FastAPI, Pydantic

**Core Modules**:

#### 2.2.1 API Layer
```python
# app/main.py
from fastapi import FastAPI, HTTPException
from app.models import ProjectData, ValidationResult, MLAdvisory
from app.services import RulesEngine, MLService, ConfigService

app = FastAPI(title="Seleen Intelligence API", version="1.0")

@app.post("/api/v1/validate", response_model=ValidationResult)
async def validate_timeline(project: ProjectData):
    """Validate clinical trial timeline"""
    pass

@app.post("/api/v1/advisory", response_model=MLAdvisory)
async def get_ml_advisory(task: TaskData):
    """Get ML-based duration and risk predictions"""
    pass

@app.get("/api/v1/config", response_model=ConfigData)
async def get_configuration():
    """Retrieve current configuration"""
    pass

@app.post("/api/v1/teams/notify")
async def post_to_teams(summary: TeamsSummary):
    """Send notification to Teams channel"""
    pass
```

#### 2.2.2 Rules Engine
```python
# app/services/rules_engine.py
from typing import List
from app.models import Task, ValidationViolation
from app.config import RulesConfig

class RulesEngine:
    """Configuration-driven validation engine"""
    
    def __init__(self, config: RulesConfig):
        self.config = config
        self.validators = [
            RegulatoryGatingValidator(),
            OperationalSequenceValidator(),
            ChecklistCompletenessValidator(),
            DurationBoundsValidator(),
            DependencyValidator()
        ]
    
    def validate(self, tasks: List[Task]) -> List[ValidationViolation]:
        """Run all validation rules"""
        violations = []
        for validator in self.validators:
            violations.extend(validator.validate(tasks, self.config))
        return violations
```

**Validator Types**:

1. **RegulatoryGatingValidator**
   - Enforces authority-specific sequences
   - Example: FDA requires Protocol → IND → IRB → SIV
   
2. **OperationalSequenceValidator**
   - Logical prerequisites (e.g., pharmacy setup before drug shipment)
   
3. **ChecklistCompletenessValidator**
   - Maps tasks to checklists
   - Ensures all required items are present
   
4. **DurationBoundsValidator**
   - Checks against authority timelines
   - Flags unrealistic durations
   
5. **DependencyValidator**
   - Detects circular dependencies
   - Validates finish-to-start relationships

#### 2.2.3 ML Service
```python
# app/services/ml_service.py
import joblib
from sklearn.ensemble import RandomForestRegressor
from app.models import Task, MLPrediction

class MLService:
    """Machine learning advisory service"""
    
    def __init__(self):
        self.duration_model = joblib.load('models/duration_predictor.pkl')
        self.risk_model = joblib.load('models/risk_scorer.pkl')
    
    def predict_duration(self, task: Task) -> MLPrediction:
        """Predict task duration range with confidence"""
        features = self._extract_features(task)
        duration_mean = self.duration_model.predict([features])[0]
        duration_std = self._estimate_uncertainty(features)
        
        return MLPrediction(
            duration_min=duration_mean - duration_std,
            duration_max=duration_mean + duration_std,
            confidence=self._calculate_confidence(features),
            explanation=self._explain_prediction(task, features)
        )
    
    def score_risk(self, task: Task, context: dict) -> float:
        """Calculate delay probability"""
        features = self._extract_risk_features(task, context)
        return self.risk_model.predict_proba([features])[0][1]  # P(delay)
    
    def _extract_features(self, task: Task) -> List[float]:
        """Feature engineering"""
        return [
            task.phase_encoding,
            task.authority_encoding,
            task.therapeutic_area_encoding,
            task.dependency_count,
            task.resource_count,
            task.is_parallel_eligible,
            # ... historical completion time stats
        ]
```

**ML Models**:

1. **Duration Predictor**: Random Forest Regressor
   - Input: Task features, authority, phase, area
   - Output: Duration range (min, max) + confidence
   
2. **Risk Scorer**: Gradient Boosting Classifier
   - Input: Task + historical delay patterns
   - Output: Delay probability (0-100%)

#### 2.2.4 Graph Logic (NetworkX)
```python
# app/services/graph_service.py
import networkx as nx
from app.models import Task, Dependency

class GraphService:
    """Task dependency graph analysis"""
    
    def build_graph(self, tasks: List[Task], deps: List[Dependency]) -> nx.DiGraph:
        """Construct directed task graph"""
        G = nx.DiGraph()
        for task in tasks:
            G.add_node(task.id, **task.dict())
        for dep in deps:
            G.add_edge(dep.predecessor, dep.successor, type=dep.type)
        return G
    
    def detect_cycles(self, G: nx.DiGraph) -> List[List[int]]:
        """Find circular dependencies"""
        try:
            cycles = list(nx.simple_cycles(G))
            return cycles
        except nx.NetworkXNoCycle:
            return []
    
    def critical_path(self, G: nx.DiGraph) -> List[int]:
        """Compute critical path (longest path)"""
        # Weighted by task durations
        return nx.dag_longest_path(G, weight='duration')
    
    def identify_slack(self, G: nx.DiGraph) -> dict:
        """Calculate float/slack for each task"""
        # Early start, late start analysis
        pass
```

#### 2.2.5 Configuration Manager
```python
# app/config/config_manager.py
import yaml
from pathlib import Path
from app.models import RulesConfig, AuthorityTimeline, ChecklistMapping

class ConfigManager:
    """Load and manage YAML configurations"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
    
    def load_authority_timelines(self) -> dict:
        """Load regulatory authority timelines"""
        with open(self.config_dir / 'authority_timelines.yaml') as f:
            return yaml.safe_load(f)
    
    def load_checklists(self) -> dict:
        """Load checklist definitions"""
        with open(self.config_dir / 'checklists.yaml') as f:
            return yaml.safe_load(f)
    
    def load_task_ontology(self) -> dict:
        """Load canonical task definitions"""
        with open(self.config_dir / 'task_ontology.yaml') as f:
            return yaml.safe_load(f)
```

---

### 2.3 Configuration Layer (YAML)

#### 2.3.1 Task Ontology
```yaml
# config/task_ontology.yaml
tasks:
  - id: "protocol_development"
    name: "Protocol Development"
    category: "Regulatory"
    mandatory: true
    typical_duration_days: 90
    dependencies: []
    parallel_eligible: false
    
  - id: "ind_submission"
    name: "IND Submission (FDA)"
    category: "Regulatory"
    mandatory: true
    typical_duration_days: 30
    dependencies: ["protocol_development"]
    authority_specific: ["FDA"]
    
  - id: "irb_submission"
    name: "IRB Submission"
    category: "Regulatory"
    mandatory: true
    typical_duration_days: 45
    dependencies: ["protocol_development", "ind_submission"]
    
  # ... 100+ canonical tasks
```

#### 2.3.2 Authority Timelines
```yaml
# config/authority_timelines.yaml
authorities:
  FDA:
    ind_review_days: 30
    irb_review_days: 45
    protocol_amendment_days: 30
    annual_report_days: 60
    gating_sequence:
      - "protocol_development"
      - "ind_submission"
      - "irb_submission"
      - "site_selection"
      - "siv"
      - "first_patient_enrolled"
    
  EMA:
    cta_review_days: 60
    ethics_review_days: 60
    protocol_amendment_days: 35
    gating_sequence:
      - "protocol_development"
      - "cta_submission"
      - "ethics_submission"
      - "site_selection"
      - "siv"
      - "first_patient_enrolled"
```

#### 2.3.3 Checklists
```yaml
# config/checklists.yaml
checklists:
  startup:
    - item: "Protocol finalized"
      task_mapping: "protocol_development"
      mandatory: true
    - item: "Budget approved"
      task_mapping: "budget_approval"
      mandatory: true
    - item: "CRO contracts executed"
      task_mapping: "cro_contracting"
      mandatory: true
    # ... 20+ items
    
  siv:
    - item: "Site training materials prepared"
      task_mapping: "training_materials"
      mandatory: true
    - item: "IP shipped to site"
      task_mapping: "ip_shipment"
      mandatory: true
    # ... 15+ items
```

---

## 3. Data Flow

### 3.1 Validation Flow

```
1. User clicks "Validate Timeline" in MS Project
2. Add-in extracts project data (tasks, dependencies, fields)
3. Add-in serializes to JSON and POSTs to /api/v1/validate
4. Backend:
   a. Parses project data
   b. Builds dependency graph (NetworkX)
   c. Runs rules engine validators
   d. Detects violations
   e. Returns ValidationResult
5. Add-in receives result
6. Add-in updates custom fields (GatingStatus, RiskScore)
7. Add-in displays validation report in UI
```

### 3.2 ML Advisory Flow

```
1. User selects task in MS Project
2. Add-in extracts task details
3. Add-in POSTs to /api/v1/advisory
4. Backend:
   a. Extracts features from task
   b. Predicts duration with ML model
   c. Scores delay risk
   d. Generates explanation
   e. Returns MLAdvisory
5. Add-in receives advisory
6. Add-in updates MLPredictedDuration field
7. Add-in displays prediction + explanation in pane
```

### 3.3 Teams Notification Flow

```
1. User clicks "Export to Teams"
2. Add-in generates summary (milestones, risks, violations)
3. Add-in POSTs to /api/v1/teams/notify
4. Backend:
   a. Formats Teams message card
   b. POSTs to Teams webhook
   c. Returns confirmation
5. Add-in displays success message
```

---

## 4. Technology Stack

### 4.1 Add-in Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | C# | 11.0 |
| Framework | .NET | 6.0 LTS |
| Add-in Type | VSTO | 17.0 |
| MS Project API | Microsoft.Office.Interop.MSProject | 15.0+ |
| HTTP Client | System.Net.Http | 6.0 |
| JSON | Newtonsoft.Json | 13.0+ |
| Logging | Microsoft.Extensions.Logging | 6.0 |
| DI Container | Microsoft.Extensions.DependencyInjection | 6.0 |

### 4.2 Backend Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11+ |
| Web Framework | FastAPI | 0.104+ |
| Data Validation | Pydantic | 2.5+ |
| YAML Parser | PyYAML | 6.0+ |
| ML Framework | scikit-learn | 1.3+ |
| Graph Library | NetworkX | 3.2+ |
| HTTP Server | uvicorn | 0.24+ |
| Model Serialization | joblib | 1.3+ |

### 4.3 Infrastructure Stack

| Component | Technology |
|-----------|-----------|
| Cloud Platform | Microsoft Azure |
| Compute | Azure App Service (Linux) |
| Storage | Azure Blob Storage |
| Auth | Azure AD / App Registration |
| Teams Integration | Teams Incoming Webhook |
| Monitoring | Application Insights |
| CI/CD | GitHub Actions |

---

## 5. Security Architecture

### 5.1 Data Protection

**No PHI Storage**:
- Only timeline metadata (task names, durations)
- No patient-level data
- No subject identifiers

**Data in Transit**:
- TLS 1.2+ for all API calls
- Certificate pinning in add-in

**Data at Rest**:
- Azure Blob encryption
- Config files encrypted at rest

### 5.2 Authentication & Authorization

**Add-in → Backend**:
- API key (rotating, per-customer)
- Stored in Windows Credential Manager
- Transmitted via Authorization header

**Teams Integration**:
- Webhook URL (secret)
- Stored in Azure Key Vault
- Retrieved at runtime

**Future (v2)**:
- OAuth 2.0 / Azure AD integration
- User-level permissions

### 5.3 Audit Logging

All API requests logged:
- Timestamp
- Customer ID
- Endpoint
- Validation result summary
- ML predictions

**Retention**: 90 days (configurable)

---

## 6. Deployment Architecture

### 6.1 Add-in Deployment

**Installer**: MSI (WiX Toolset)

**Installation Steps**:
1. Check MS Project version (Desktop 2016+)
2. Check .NET 6 Runtime
3. Install add-in DLL to `%AppData%\Seleen`
4. Register COM add-in
5. Create registry keys
6. Prompt for API key

**Update Mechanism**:
- Check for updates on startup
- Download MSI silently
- Prompt user to restart MS Project

### 6.2 Backend Deployment

**Azure App Service**:
- Linux container
- Python 3.11 runtime
- Auto-scaling (2-10 instances)

**Deployment Pipeline**:
```
GitHub → Actions → Docker Build → Azure Container Registry → App Service
```

**Configuration**:
- Environment variables for secrets
- Blob storage mount for configs
- Application Insights for telemetry

### 6.3 Configuration Management

**Version Control**:
- YAML configs in Git
- Semantic versioning
- Change history tracked

**Deployment**:
- Configs uploaded to Blob Storage
- Backend caches configs (5 min TTL)
- Add-in refreshes configs on demand

---

## 7. Development Guidelines

### 7.1 Code Organization

**Add-in (C#)**:
```
Seleen.AddIn/
├── SeleenRibbon.cs
├── Services/
│   ├── ApiClient.cs
│   ├── ConfigCache.cs
│   └── LoggingService.cs
├── Data/
│   ├── ProjectExtractor.cs
│   └── DataModels.cs
├── Views/
│   ├── ViewManager.cs
│   └── ValidationReport.cs
├── Fields/
│   └── CustomFieldManager.cs
└── Utils/
    ├── DateHelper.cs
    └── ErrorHandler.cs
```

**Backend (Python)**:
```
seleen-backend/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── services/
│   │   ├── rules_engine.py
│   │   ├── ml_service.py
│   │   ├── graph_service.py
│   │   └── teams_service.py
│   ├── config/
│   │   ├── config_manager.py
│   │   └── validators/
│   └── utils/
├── config/
│   ├── task_ontology.yaml
│   ├── authority_timelines.yaml
│   └── checklists.yaml
├── models/
│   ├── duration_predictor.pkl
│   └── risk_scorer.pkl
├── tests/
└── requirements.txt
```

### 7.2 Error Handling

**Add-in**:
- Try-catch around MS Project API calls
- Log to file + optional telemetry
- User-friendly error messages
- Graceful degradation (offline mode)

**Backend**:
- FastAPI exception handlers
- Structured error responses
- Validation errors (422)
- Internal errors (500) with trace IDs

### 7.3 Testing Strategy

**Add-in**:
- Unit tests (xUnit)
- Integration tests with mock MS Project
- Manual testing in real MS Project

**Backend**:
- Unit tests (pytest)
- API integration tests (FastAPI TestClient)
- ML model validation tests
- YAML config validation

**End-to-End**:
- Real MS Project file validation
- Full workflow testing

### 7.4 Logging & Monitoring

**Add-in**:
- Log to: `%AppData%\Seleen\Logs\addin.log`
- Rotate daily
- Levels: Debug, Info, Warning, Error

**Backend**:
- Structured logging (JSON)
- Application Insights integration
- Metrics: API latency, validation time, ML inference time

---

## 8. Future Extensibility

### 8.1 Planned Enhancements (v2+)

1. **Project for the Web Support**
   - Web add-in (JavaScript)
   - Similar API integration
   
2. **CTMS Integration**
   - Bidirectional sync
   - Real-time updates
   
3. **Advanced AI Copilot**
   - Natural language timeline queries
   - Auto-correction suggestions
   
4. **Mobile Companion App**
   - iOS/Android
   - Executive dashboard

### 8.2 API Versioning

- API v1: `/api/v1/*`
- Future versions: `/api/v2/*`
- Maintain backward compatibility for 1 year

---

## 9. Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Validation Time | < 5 seconds | For 200-task timeline |
| ML Inference Time | < 1 second | Per task |
| API Response Time | < 500ms | 95th percentile |
| Add-in Startup Time | < 2 seconds | First ribbon load |
| Config Cache Refresh | < 1 second | Background |

---

## 10. Dependencies & Prerequisites

### 10.1 Development Environment

**Add-in Development**:
- Visual Studio 2022
- MS Project Desktop (2016, 2019, or 2021)
- .NET 6 SDK
- WiX Toolset (for installer)

**Backend Development**:
- Python 3.11+
- VS Code or PyCharm
- Docker Desktop (for local testing)

### 10.2 Runtime Requirements

**Client**:
- Windows 10/11
- MS Project Desktop (2016+)
- .NET 6 Runtime
- Internet connection (for validation)

**Server**:
- Azure subscription
- App Service (B1 or higher)
- Blob Storage account

---

**End of Technical Architecture Document**
