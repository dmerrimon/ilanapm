# VSTO Add-in Development - Setup Checklist

**Date:** 2026-01-15
**VM:** ilana-dev-vm (East US)
**Purpose:** Microsoft Project VSTO Add-in Development Environment

---

## ✅ Prerequisites Checklist

### System Setup
- [x] Windows 11 VM created and running
- [x] Connected via Remote Desktop
- [ ] Visual Studio 2022 Community installed
- [ ] Office/SharePoint development workload installed
- [ ] Git for Windows installed
- [ ] Microsoft Project installed (or trial)

### Repository Setup
- [ ] Git repository cloned to `C:\Users\ilanaadmin\Documents\ilanapm`
- [ ] Can access production API: https://ilanapm.azurewebsites.net

---

## Installation Steps

### 1. Visual Studio 2022 Community

**Download:** https://visualstudio.microsoft.com/downloads/

**Required Workloads:**
- ✅ .NET desktop development
- ✅ Office/SharePoint development (CRITICAL!)
- ✅ ASP.NET and web development (optional)

**Installation time:** 30-60 minutes

**Verify installation:**
```powershell
# Check Visual Studio is installed
Get-Command devenv.exe
```

---

### 2. Git for Windows

**Download:** https://git-scm.com/download/win

**Installation:** Accept all defaults

**Verify installation:**
```powershell
git --version
```

---

### 3. Microsoft Project

**Option A - Free Trial (30 days):**
https://www.microsoft.com/en-us/microsoft-365/project/project-plan-1

**Option B - Microsoft 365 Subscription:**
Sign in and install from your account

**Verify installation:**
- Open Start Menu
- Search for "Project"
- Launch Microsoft Project

---

### 4. Clone Repository

**Commands:**
```powershell
cd C:\Users\ilanaadmin\Documents
git clone https://github.com/dmerrimon/ilanapm.git
cd ilanapm
dir
```

**Expected output:**
You should see folders: `backend`, `config-templates`, `docs`, `tests`

---

## Next: Create VSTO Project

Once all prerequisites are installed, we'll create the VSTO add-in project:

### VSTO Project Structure

```
ilanapm/
├── backend/                    # ✅ Already exists (Python API)
├── desktop-addin/              # 🆕 We'll create this
│   ├── IlanaPM.AddIn/         # VSTO project
│   │   ├── IlanaPMRibbon.cs   # Custom ribbon UI
│   │   ├── ThisAddIn.cs       # Add-in entry point
│   │   ├── TaskPane/          # Task pane UI
│   │   │   ├── ValidationPanel.cs
│   │   │   └── ValidationPanel.Designer.cs
│   │   ├── Services/          # API integration
│   │   │   ├── ApiClient.cs
│   │   │   └── ProjectDataExtractor.cs
│   │   └── Models/            # Data models
│   │       └── Timeline.cs
│   └── IlanaPM.AddIn.sln      # Solution file
└── docs/
```

---

## VSTO Add-in Architecture

### Components to Build

1. **Custom Ribbon** (`IlanaPMRibbon.cs`)
   - "Validate Timeline" button
   - "Get Risk Analysis" button
   - "View Analytics" button

2. **Task Pane** (`ValidationPanel.cs`)
   - Display validation results
   - Show errors/warnings
   - Display suggested fixes
   - Show risk scores

3. **API Client** (`ApiClient.cs`)
   - HTTP client to call production API
   - Endpoint: https://ilanapm.azurewebsites.net
   - POST /api/v1/validate
   - POST /api/v1/analytics/critical-path
   - POST /api/v1/advisory/timeline

4. **Project Data Extractor** (`ProjectDataExtractor.cs`)
   - Extract tasks from MS Project
   - Extract dependencies
   - Map to Timeline JSON format
   - Send to API

5. **Write-back Handler**
   - Write risk scores to custom fields
   - Update task notes with validation issues
   - Highlight critical path tasks

---

## Development Workflow

### Phase 3.1: Basic Project Setup
1. Create VSTO Project in Visual Studio
2. Add custom ribbon with one button
3. Test button click shows message box
4. Deploy and test in Microsoft Project

### Phase 3.2: Data Extraction
1. Extract tasks from Project
2. Extract dependencies
3. Convert to Timeline JSON
4. Log to console (verify data)

### Phase 3.3: API Integration
1. Create HttpClient for API calls
2. POST timeline to /api/v1/validate
3. Parse JSON response
4. Display in message box (simple test)

### Phase 3.4: Task Pane UI
1. Create Windows Forms task pane
2. Display validation results in DataGridView
3. Show error/warning/info counts
4. Click row to navigate to task

### Phase 3.5: Write-back
1. Add custom fields to Project (RiskScore, ValidationStatus)
2. Write risk scores from API response
3. Color-code tasks by risk level
4. Add validation notes to tasks

### Phase 3.6: Polish
1. Add loading indicators
2. Error handling
3. Settings panel (API URL configuration)
4. About dialog
5. Icon and branding

---

## Testing Strategy

### Unit Tests
- Test data extraction logic
- Test JSON serialization
- Mock API responses

### Integration Tests
- Test with real Project files
- Test API calls to production
- Test write-back functionality

### Manual Testing
- Create sample Project file with clinical trial timeline
- Run validation
- Verify results display correctly
- Check write-back updates fields

---

## API Endpoints Reference

**Base URL:** https://ilanapm.azurewebsites.net

### Validation
```http
POST /api/v1/validate
Content-Type: application/json

{
  "study_name": "Test Study",
  "phase": "Phase II",
  "authority": "FDA",
  "tasks": [...],
  "dependencies": [...]
}
```

**Response:**
```json
{
  "status": "warnings",
  "issues": [...],
  "error_count": 0,
  "warning_count": 3,
  "info_count": 2
}
```

### Critical Path
```http
POST /api/v1/analytics/critical-path
```

### Risk Analysis
```http
POST /api/v1/advisory/timeline
```

---

## Deployment

### For Development (F5 in Visual Studio)
- Visual Studio automatically deploys to local Project
- Add-in shows up in Project ribbon
- Can debug with breakpoints

### For Distribution (Later)
1. Create installer (ClickOnce or Windows Installer)
2. Sign with certificate
3. Distribute .msi or setup.exe
4. Users install add-in
5. Shows up in all Project instances

---

## Security Considerations

### API Communication
- Use HTTPS only (already configured)
- No authentication yet (Phase 3 - add later)
- Validate SSL certificates

### Project Data
- Data leaves user's machine to hit API
- Consider: on-premise deployment option later
- Privacy: clinical trial data may be sensitive

### Add-in Signing
- Sign with Authenticode certificate (for distribution)
- Self-signed OK for development

---

## Resources

### Microsoft Documentation
- VSTO Overview: https://docs.microsoft.com/en-us/visualstudio/vsto/
- Project Object Model: https://docs.microsoft.com/en-us/office/vba/api/overview/project
- Custom Ribbon: https://docs.microsoft.com/en-us/visualstudio/vsto/ribbon-overview

### Sample Code
- VSTO Samples: https://github.com/OfficeDev/office-developer-samples

---

## Troubleshooting

### "Office/SharePoint development" workload not visible
- Make sure you downloaded Visual Studio 2022 (not VS Code)
- Try Visual Studio Installer → Modify → check workloads

### Can't debug add-in
- Make sure Microsoft Project is installed
- Check Project version matches target framework
- Set startup project to the VSTO project

### Add-in doesn't appear in Project ribbon
- Check add-in is deployed (F5)
- Check Project Trust Center settings
- Look for errors in Output window

---

## Quick Commands Reference

### PowerShell Commands

```powershell
# Clone repo
git clone https://github.com/dmerrimon/ilanapm.git

# Check .NET version
dotnet --version

# Test API connectivity
Invoke-RestMethod -Uri "https://ilanapm.azurewebsites.net/api/v1/health"

# Build project (from solution directory)
msbuild IlanaPM.AddIn.sln /p:Configuration=Debug

# Open Visual Studio from command line
devenv IlanaPM.AddIn.sln
```

---

## Status Checklist

- [ ] Visual Studio installed with Office tools
- [ ] Git installed and repo cloned
- [ ] Microsoft Project installed
- [ ] VSTO project created
- [ ] Can build project successfully
- [ ] Can deploy to Project (F5)
- [ ] Can see custom ribbon button
- [ ] Can extract task data
- [ ] Can call production API
- [ ] Can display results in task pane
- [ ] Can write back to Project fields
- [ ] Ready for user testing

---

**Next:** Once Visual Studio is installed, we'll create the VSTO project!
