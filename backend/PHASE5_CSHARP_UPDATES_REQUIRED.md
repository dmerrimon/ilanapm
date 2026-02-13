# Phase 5: C# Desktop Add-in Updates Required

**Date:** 2026-02-13
**Target:** MS Project Desktop Add-in (C# VSTO)
**Purpose:** Integrate Phase 5 backend features (tracker upload, dashboard exports, health snapshots)

---

## Executive Summary

The Phase 5 backend implementation is complete with:
- Daily intelligence refresh script ✅
- Dashboard export endpoints (CSV/Excel) ✅
- Tracker upload workflow documentation ✅
- API integration guide ✅
- Comprehensive test suite (17/17 passing) ✅

**C# updates required:** Add new API methods, ribbon buttons, and forms to integrate with these backend features.

---

## 1. API Client Updates (`Services/ApiClient.cs`)

### Current State
- 20 existing API methods for licensing, validation, templates, etc.
- TLS 1.2 support ✅
- Bearer token authentication ✅
- Error handling for 401/422 responses ✅

### Required New Methods

#### 1.1. Upload Tracker

```csharp
/// <summary>
/// Upload Excel tracker file (Risk Log, TMF, Budget, Vendor, etc.)
/// POST /api/v1/trackers/upload
/// </summary>
public async Task<TrackerUploadResult> UploadTrackerAsync(
    string orgId,
    string projectId,
    string trackerType,
    byte[] fileBytes,
    string fileName
)
{
    AddAuthorizationHeader();

    using (var content = new MultipartFormDataContent())
    {
        // Add file content
        var fileContent = new ByteArrayContent(fileBytes);
        fileContent.Headers.ContentType = new MediaTypeHeaderValue("application/octet-stream");
        content.Add(fileContent, "file", fileName);

        // Build URL with query parameters
        string url = $"{API_BASE_URL}/api/v1/trackers/upload?" +
                     $"org_id={Uri.EscapeDataString(orgId)}&" +
                     $"project_id={Uri.EscapeDataString(projectId)}&" +
                     $"tracker_type={Uri.EscapeDataString(trackerType)}";

        HttpResponseMessage response = await httpClient.PostAsync(url, content);
        await HandleResponseAsync(response);

        string responseBody = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<TrackerUploadResult>(responseBody);
    }
}
```

**Model Required:**
```csharp
// Models/TrackerUploadResult.cs
public class TrackerUploadResult
{
    public bool success { get; set; }
    public string upload_id { get; set; }
    public int rows_processed { get; set; }
    public int signals_extracted { get; set; }
    public int escalations_detected { get; set; }
    public double health_score { get; set; }
    public string health_status { get; set; }
    public string error_type { get; set; }
    public string error_message { get; set; }
    public List<ValidationError> validation_errors { get; set; }
}

public class ValidationError
{
    public int row_number { get; set; }
    public string field { get; set; }
    public string error_message { get; set; }
}
```

---

#### 1.2. Get Study Health Snapshot

```csharp
/// <summary>
/// Get study health snapshot with signals and correlations
/// GET /api/v1/dashboard/study/{project_id}
/// </summary>
public async Task<StudyHealthSnapshot> GetStudyHealthSnapshotAsync(
    string projectId,
    string orgId
)
{
    AddAuthorizationHeader();

    string url = $"{API_BASE_URL}/api/v1/dashboard/study/{Uri.EscapeDataString(projectId)}?" +
                 $"org_id={Uri.EscapeDataString(orgId)}";

    HttpResponseMessage response = await httpClient.GetAsync(url);
    await HandleResponseAsync(response);

    string responseBody = await response.Content.ReadAsStringAsync();
    return JsonConvert.DeserializeObject<StudyHealthSnapshot>(responseBody);
}
```

**Model Required:**
```csharp
// Models/StudyHealthSnapshot.cs
public class StudyHealthSnapshot
{
    public string project_id { get; set; }
    public string project_name { get; set; }
    public double overall_health_score { get; set; }
    public string health_status { get; set; } // "healthy", "warning", "critical"

    public double timeline_score { get; set; }
    public double risk_score { get; set; }
    public double tmf_score { get; set; }
    public double enrollment_score { get; set; }

    public List<Signal> active_signals { get; set; }
    public List<Correlation> correlations { get; set; }
    public List<Escalation> escalations { get; set; }
    public List<string> recommended_actions { get; set; }

    public string snapshot_date { get; set; }
}

public class Signal
{
    public string signal_id { get; set; }
    public string signal_type { get; set; }
    public string signal_category { get; set; }
    public string signal_description { get; set; }
    public int priority { get; set; }
    public string status { get; set; }
    public string signal_source { get; set; }
    public string date_identified { get; set; }
}

public class Correlation
{
    public string correlation_id { get; set; }
    public string signal_id { get; set; }
    public string affected_milestone_name { get; set; }
    public string correlation_type { get; set; } // "blocker", "risk", "informational"
    public double confidence_score { get; set; }
    public int estimated_delay_days { get; set; }
    public double estimated_cost_impact { get; set; }
    public string correlation_reasoning { get; set; }
}

public class Escalation
{
    public string escalation_id { get; set; }
    public string escalation_level { get; set; } // "director", "vp"
    public string escalation_reason { get; set; }
    public string status { get; set; } // "open", "acknowledged", "resolved"
    public int priority { get; set; }
    public string intervention_recommended { get; set; }
    public string created_at { get; set; }
}
```

---

#### 1.3. Export Dashboard

```csharp
/// <summary>
/// Export dashboard data to CSV or Excel
/// GET /api/v1/dashboard/export/{export_type}
/// </summary>
public async Task<byte[]> ExportDashboardAsync(
    string exportType, // "leadership", "study", "portfolio/health", etc.
    string orgId,
    string projectId = null,
    string format = "csv" // "csv" or "excel"
)
{
    AddAuthorizationHeader();

    string url = $"{API_BASE_URL}/api/v1/dashboard/export/{exportType}?" +
                 $"org_id={Uri.EscapeDataString(orgId)}&" +
                 $"format={format}";

    if (!string.IsNullOrEmpty(projectId))
    {
        url += $"&project_id={Uri.EscapeDataString(projectId)}";
    }

    HttpResponseMessage response = await httpClient.GetAsync(url);
    await HandleResponseAsync(response);

    return await response.Content.ReadAsByteArrayAsync();
}
```

---

#### 1.4. Get Leadership Dashboard URL

```csharp
/// <summary>
/// Get Leadership Dashboard web portal URL with auto-login token
/// Returns URL to app.seleen.io with authentication token
/// </summary>
public string GetLeadershipDashboardUrl()
{
    string token = SecureStorage.ReadToken();
    string orgId = SecureStorage.ReadOrgId();

    if (string.IsNullOrEmpty(token) || string.IsNullOrEmpty(orgId))
    {
        throw new Models.UnauthorizedException("No token or org_id available");
    }

    return $"https://app.seleen.io/dashboard/leadership?" +
           $"token={Uri.EscapeDataString(token)}&" +
           $"org_id={Uri.EscapeDataString(orgId)}";
}
```

---

## 2. Ribbon UI Updates (`IlanaPMRibbon.cs`)

### Current Buttons
- Validate ✅
- Settings ✅
- Load Template ✅
- Multi-Country Calculator ✅
- Critical Path ✅
- Clinical Setup ✅
- Clinical Project Manager ✅
- Tag Tasks ✅
- Reports Menu ✅

### New Buttons Required

#### 2.1. Upload Tracker Button

**Location:** Intelligence group (next to Validate button)

**XML (IlanaPMRibbon.xml):**
```xml
<button
    id="btnUploadTracker"
    label="Upload Tracker"
    size="large"
    imageMso="ImportExcel"
    onAction="btnUploadTracker_Click"
    screentip="Upload Excel Tracker"
    supertip="Upload Risk Log, TMF Tracker, Budget Tracker, or Vendor Tracker. Seleen will extract signals and update study health scores." />
```

**Event Handler (IlanaPMRibbon.cs):**
```csharp
// PHASE 5: UPLOAD TRACKER BUTTON
private async void btnUploadTracker_Click(object sender, RibbonControlEventArgs e)
{
    System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

    try
    {
        // Get org_id and project_id
        string orgId = Services.SecureStorage.ReadOrgId();
        if (string.IsNullOrEmpty(orgId))
        {
            MessageBox.Show(
                "Organization ID not found. Please re-activate your license in Settings.",
                "Configuration Required",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning
            );
            return;
        }

        // Get project_id from current MS Project file
        var app = Globals.ThisAddIn.Application;
        if (app.ActiveProject == null)
        {
            MessageBox.Show(
                "No active project. Please open or create a project first.",
                "No Active Project",
                MessageBoxButtons.OK,
                MessageBoxIcon.Warning
            );
            return;
        }

        string projectId = app.ActiveProject.Name; // Or use custom field if available

        // Show tracker upload form
        var uploadForm = new TrackerUploadForm(orgId, projectId);
        var result = uploadForm.ShowDialog();

        if (result == DialogResult.OK)
        {
            // Upload succeeded - show results
            var uploadResult = uploadForm.UploadResult;

            string healthIcon = uploadResult.health_status == "healthy" ? "✅" :
                               uploadResult.health_status == "warning" ? "⚠️" : "🔴";

            MessageBox.Show(
                $"✅ Tracker uploaded successfully!\n\n" +
                $"📊 {uploadResult.rows_processed} rows processed\n" +
                $"🔔 {uploadResult.signals_extracted} signals extracted\n" +
                $"⚠️ {uploadResult.escalations_detected} escalations detected\n\n" +
                $"{healthIcon} Study Health: {uploadResult.health_score:F1} ({uploadResult.health_status})\n\n" +
                $"View full details in Leadership Dashboard.",
                "Upload Complete",
                MessageBoxButtons.OK,
                MessageBoxIcon.Information
            );

            // Track telemetry
            var telemetryService = Globals.ThisAddIn.TelemetryService;
            if (telemetryService != null)
            {
                telemetryService.TrackEvent(TelemetryEventType.TrackerUploaded, new Dictionary<string, object>
                {
                    { "tracker_type", uploadForm.SelectedTrackerType },
                    { "rows_processed", uploadResult.rows_processed },
                    { "signals_extracted", uploadResult.signals_extracted },
                    { "escalations_detected", uploadResult.escalations_detected }
                });
            }
        }
    }
    catch (Models.UnauthorizedException ex)
    {
        MessageBox.Show(ex.Message, "License Required",
            MessageBoxButtons.OK, MessageBoxIcon.Warning);
        var activationForm = new LicenseActivationForm();
        activationForm.ShowDialog();
    }
    catch (System.Exception ex)
    {
        string detailedError = "Error uploading tracker: " + ex.Message;
        if (ex.InnerException != null)
        {
            detailedError = detailedError + "\n\nInner: " + ex.InnerException.Message;
        }
        MessageBox.Show(detailedError, "Upload Error",
            MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}
```

---

#### 2.2. Leadership Dashboard Button

**Location:** Intelligence group

**XML (IlanaPMRibbon.xml):**
```xml
<button
    id="btnLeadershipDashboard"
    label="Dashboard"
    size="large"
    imageMso="ViewDashboard"
    onAction="btnLeadershipDashboard_Click"
    screentip="Open Leadership Dashboard"
    supertip="View study health, signals, correlations, and escalations in the web portal." />
```

**Event Handler (IlanaPMRibbon.cs):**
```csharp
// PHASE 5: LEADERSHIP DASHBOARD BUTTON
private void btnLeadershipDashboard_Click(object sender, RibbonControlEventArgs e)
{
    try
    {
        var apiClient = new Services.ApiClient();
        string dashboardUrl = apiClient.GetLeadershipDashboardUrl();

        // Open in default browser
        System.Diagnostics.Process.Start(dashboardUrl);

        // Track telemetry
        var telemetryService = Globals.ThisAddIn.TelemetryService;
        if (telemetryService != null)
        {
            telemetryService.TrackEvent(TelemetryEventType.FeatureOpened, new Dictionary<string, object>
            {
                { "feature", "LeadershipDashboard" }
            });
        }
    }
    catch (Models.UnauthorizedException ex)
    {
        MessageBox.Show(ex.Message, "License Required",
            MessageBoxButtons.OK, MessageBoxIcon.Warning);
        var activationForm = new LicenseActivationForm();
        activationForm.ShowDialog();
    }
    catch (System.Exception ex)
    {
        string detailedError = "Error opening dashboard: " + ex.Message;
        if (ex.InnerException != null)
        {
            detailedError = detailedError + "\n\nInner: " + ex.InnerException.Message;
        }
        MessageBox.Show(detailedError, "Dashboard Error",
            MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}
```

---

#### 2.3. Export Dashboard Button (Optional)

**Location:** Reports menu or Intelligence group

**XML (IlanaPMRibbon.xml):**
```xml
<button
    id="btnExportDashboard"
    label="Export Data"
    size="normal"
    imageMso="ExportExcel"
    onAction="btnExportDashboard_Click"
    screentip="Export Dashboard Data"
    supertip="Export study health, signals, and escalations to CSV or Excel for offline analysis." />
```

**Event Handler (IlanaPMRibbon.cs):**
```csharp
// PHASE 5: EXPORT DASHBOARD BUTTON
private async void btnExportDashboard_Click(object sender, RibbonControlEventArgs e)
{
    System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

    try
    {
        // Show export options form
        var exportForm = new DashboardExportForm();
        var result = exportForm.ShowDialog();

        if (result == DialogResult.OK)
        {
            // Get org_id
            string orgId = Services.SecureStorage.ReadOrgId();
            if (string.IsNullOrEmpty(orgId))
            {
                MessageBox.Show("Organization ID not found.", "Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            // Export dashboard
            var apiClient = new Services.ApiClient();
            byte[] fileBytes = await apiClient.ExportDashboardAsync(
                exportForm.ExportType,
                orgId,
                exportForm.ProjectId,
                exportForm.Format
            );

            // Save file
            using (var saveDialog = new SaveFileDialog())
            {
                saveDialog.Filter = exportForm.Format == "csv"
                    ? "CSV files (*.csv)|*.csv"
                    : "Excel files (*.xlsx)|*.xlsx";
                saveDialog.FileName = $"seleen_export_{DateTime.Now:yyyyMMdd_HHmmss}.{exportForm.Format}";

                if (saveDialog.ShowDialog() == DialogResult.OK)
                {
                    System.IO.File.WriteAllBytes(saveDialog.FileName, fileBytes);

                    MessageBox.Show(
                        $"Dashboard exported successfully!\n\nFile saved to:\n{saveDialog.FileName}",
                        "Export Complete",
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Information
                    );
                }
            }
        }
    }
    catch (System.Exception ex)
    {
        string detailedError = "Error exporting dashboard: " + ex.Message;
        if (ex.InnerException != null)
        {
            detailedError = detailedError + "\n\nInner: " + ex.InnerException.Message;
        }
        MessageBox.Show(detailedError, "Export Error",
            MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}
```

---

## 3. New Forms Required

### 3.1. Tracker Upload Form (`TrackerUploadForm.cs`)

**Purpose:** File picker + tracker type selection

**UI Components:**
- Label: "Select tracker file to upload"
- TextBox: File path (read-only)
- Button: "Browse..." (opens OpenFileDialog)
- Label: "Tracker type"
- ComboBox: Tracker type dropdown
  - Risk Log
  - TMF Completeness Tracker
  - Budget Tracker
  - Vendor Management Tracker
- ProgressBar: Upload progress (indeterminate during upload)
- Button: "Upload" (primary)
- Button: "Cancel"

**Implementation:**
```csharp
public partial class TrackerUploadForm : Form
{
    private string _orgId;
    private string _projectId;
    private string _selectedFilePath;

    public string SelectedTrackerType { get; private set; }
    public TrackerUploadResult UploadResult { get; private set; }

    public TrackerUploadForm(string orgId, string projectId)
    {
        InitializeComponent();
        _orgId = orgId;
        _projectId = projectId;

        // Populate tracker type dropdown
        cmbTrackerType.Items.Add("Risk Log");
        cmbTrackerType.Items.Add("TMF Completeness Tracker");
        cmbTrackerType.Items.Add("Budget Tracker");
        cmbTrackerType.Items.Add("Vendor Management Tracker");
        cmbTrackerType.SelectedIndex = 0;
    }

    private void btnBrowse_Click(object sender, EventArgs e)
    {
        using (var openDialog = new OpenFileDialog())
        {
            openDialog.Filter = "Excel files (*.xlsx;*.xls)|*.xlsx;*.xls|CSV files (*.csv)|*.csv|All files (*.*)|*.*";
            openDialog.Title = "Select Tracker File";

            if (openDialog.ShowDialog() == DialogResult.OK)
            {
                _selectedFilePath = openDialog.FileName;
                txtFilePath.Text = _selectedFilePath;
                btnUpload.Enabled = true;
            }
        }
    }

    private async void btnUpload_Click(object sender, EventArgs e)
    {
        if (string.IsNullOrEmpty(_selectedFilePath))
        {
            MessageBox.Show("Please select a file to upload.", "File Required",
                MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        try
        {
            // Disable UI during upload
            btnBrowse.Enabled = false;
            btnUpload.Enabled = false;
            cmbTrackerType.Enabled = false;
            progressBar.Style = ProgressBarStyle.Marquee;

            // Read file bytes
            byte[] fileBytes = System.IO.File.ReadAllBytes(_selectedFilePath);
            string fileName = System.IO.Path.GetFileName(_selectedFilePath);

            // Map tracker type to API value
            string trackerType = MapTrackerType(cmbTrackerType.SelectedItem.ToString());
            SelectedTrackerType = trackerType;

            // Upload to API
            var apiClient = new Services.ApiClient();
            UploadResult = await apiClient.UploadTrackerAsync(
                _orgId,
                _projectId,
                trackerType,
                fileBytes,
                fileName
            );

            if (UploadResult.success)
            {
                DialogResult = DialogResult.OK;
                Close();
            }
            else
            {
                // Show error
                string errorMsg = UploadResult.error_message ?? "Upload failed";

                if (UploadResult.error_type == "column_mismatch")
                {
                    errorMsg += "\n\nPlease contact your Account Admin to configure this tracker type.";
                }
                else if (UploadResult.validation_errors != null && UploadResult.validation_errors.Count > 0)
                {
                    errorMsg += "\n\nValidation errors:\n";
                    foreach (var err in UploadResult.validation_errors.Take(5))
                    {
                        errorMsg += $"• Row {err.row_number}: {err.error_message}\n";
                    }
                }

                MessageBox.Show(errorMsg, "Upload Failed",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);

                // Re-enable UI
                btnBrowse.Enabled = true;
                btnUpload.Enabled = true;
                cmbTrackerType.Enabled = true;
                progressBar.Style = ProgressBarStyle.Continuous;
            }
        }
        catch (System.Exception ex)
        {
            MessageBox.Show(
                $"Error uploading file: {ex.Message}",
                "Upload Error",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error
            );

            // Re-enable UI
            btnBrowse.Enabled = true;
            btnUpload.Enabled = true;
            cmbTrackerType.Enabled = true;
            progressBar.Style = ProgressBarStyle.Continuous;
        }
    }

    private string MapTrackerType(string displayName)
    {
        switch (displayName)
        {
            case "Risk Log":
                return "risk_log";
            case "TMF Completeness Tracker":
                return "tmf_tracker";
            case "Budget Tracker":
                return "budget_tracker";
            case "Vendor Management Tracker":
                return "vendor_tracker";
            default:
                return "risk_log";
        }
    }
}
```

---

### 3.2. Dashboard Export Form (`DashboardExportForm.cs`) (Optional)

**Purpose:** Select export type and format

**UI Components:**
- Label: "Export type"
- ComboBox: Export type dropdown
  - Leadership Dashboard
  - Study Detail (Current Study)
  - Portfolio Health
  - Cross-Study Patterns
  - Systemic Issues
- Label: "Format"
- RadioButton: CSV (selected by default)
- RadioButton: Excel
- Button: "Export" (primary)
- Button: "Cancel"

**Implementation:**
```csharp
public partial class DashboardExportForm : Form
{
    public string ExportType { get; private set; }
    public string ProjectId { get; private set; }
    public string Format { get; private set; }

    public DashboardExportForm()
    {
        InitializeComponent();

        // Populate export type dropdown
        cmbExportType.Items.Add("Leadership Dashboard");
        cmbExportType.Items.Add("Study Detail (Current Study)");
        cmbExportType.Items.Add("Portfolio Health");
        cmbExportType.Items.Add("Cross-Study Patterns");
        cmbExportType.Items.Add("Systemic Issues");
        cmbExportType.SelectedIndex = 0;

        // Default format
        rbCSV.Checked = true;
    }

    private void btnExport_Click(object sender, EventArgs e)
    {
        // Map export type
        string selectedType = cmbExportType.SelectedItem.ToString();

        switch (selectedType)
        {
            case "Leadership Dashboard":
                ExportType = "leadership";
                break;
            case "Study Detail (Current Study)":
                ExportType = "study";
                ProjectId = Globals.ThisAddIn.Application.ActiveProject?.Name;
                break;
            case "Portfolio Health":
                ExportType = "portfolio/health";
                break;
            case "Cross-Study Patterns":
                ExportType = "portfolio/patterns";
                break;
            case "Systemic Issues":
                ExportType = "portfolio/systemic-issues";
                break;
        }

        Format = rbCSV.Checked ? "csv" : "excel";

        DialogResult = DialogResult.OK;
        Close();
    }
}
```

---

### 3.3. Study Health Display (Optional Enhancement)

**Option 1:** Add health score to existing ValidationResultsForm

**Option 2:** Create new StudyHealthForm showing:
- Health score gauge
- Component scores (timeline, risk, TMF, enrollment)
- Top signals list
- Recommended actions
- Button to open Leadership Dashboard

---

## 4. Secure Storage Updates (`Services/SecureStorage.cs`)

### Add OrgId Storage

```csharp
private const string ORG_ID_KEY = "IlanaPM_OrgId";

public static void WriteOrgId(string orgId)
{
    try
    {
        byte[] encryptedOrgId = ProtectedData.Protect(
            Encoding.UTF8.GetBytes(orgId),
            null,
            DataProtectionScope.CurrentUser
        );

        string base64OrgId = Convert.ToBase64String(encryptedOrgId);
        Registry.SetValue(REGISTRY_PATH, ORG_ID_KEY, base64OrgId);
    }
    catch (Exception ex)
    {
        System.Diagnostics.Debug.WriteLine($"Error writing org_id: {ex.Message}");
    }
}

public static string ReadOrgId()
{
    try
    {
        object value = Registry.GetValue(REGISTRY_PATH, ORG_ID_KEY, null);
        if (value == null) return null;

        byte[] encryptedOrgId = Convert.FromBase64String(value.ToString());
        byte[] orgIdBytes = ProtectedData.Unprotect(
            encryptedOrgId,
            null,
            DataProtectionScope.CurrentUser
        );

        return Encoding.UTF8.GetString(orgIdBytes);
    }
    catch (Exception ex)
    {
        System.Diagnostics.Debug.WriteLine($"Error reading org_id: {ex.Message}");
        return null;
    }
}
```

**Update:** Ensure `org_id` is saved during license activation (in `ActivationResponse` model and `LicenseActivationForm`).

---

## 5. Telemetry Updates (`TelemetryEventType.cs`)

### Add New Event Types

```csharp
public enum TelemetryEventType
{
    // ... existing events

    // Phase 5 events
    TrackerUploaded,
    LeadershipDashboardOpened,
    DashboardExported,
    StudyHealthViewed
}
```

---

## 6. Models to Add

Create new files in `Models/` directory:

### Models/TrackerUploadResult.cs
```csharp
public class TrackerUploadResult
{
    public bool success { get; set; }
    public string upload_id { get; set; }
    public int rows_processed { get; set; }
    public int signals_extracted { get; set; }
    public int escalations_detected { get; set; }
    public double health_score { get; set; }
    public string health_status { get; set; }
    public string error_type { get; set; }
    public string error_message { get; set; }
    public List<ValidationError> validation_errors { get; set; }
}

public class ValidationError
{
    public int row_number { get; set; }
    public string field { get; set; }
    public string error_message { get; set; }
}
```

### Models/StudyHealthSnapshot.cs
```csharp
public class StudyHealthSnapshot
{
    public string project_id { get; set; }
    public string project_name { get; set; }
    public double overall_health_score { get; set; }
    public string health_status { get; set; }

    public double timeline_score { get; set; }
    public double risk_score { get; set; }
    public double tmf_score { get; set; }
    public double enrollment_score { get; set; }

    public List<Signal> active_signals { get; set; }
    public List<Correlation> correlations { get; set; }
    public List<Escalation> escalations { get; set; }
    public List<string> recommended_actions { get; set; }

    public string snapshot_date { get; set; }
}

public class Signal
{
    public string signal_id { get; set; }
    public string signal_type { get; set; }
    public string signal_category { get; set; }
    public string signal_description { get; set; }
    public int priority { get; set; }
    public string status { get; set; }
    public string signal_source { get; set; }
    public string date_identified { get; set; }
}

public class Correlation
{
    public string correlation_id { get; set; }
    public string signal_id { get; set; }
    public string affected_milestone_name { get; set; }
    public string correlation_type { get; set; }
    public double confidence_score { get; set; }
    public int estimated_delay_days { get; set; }
    public double estimated_cost_impact { get; set; }
    public string correlation_reasoning { get; set; }
}

public class Escalation
{
    public string escalation_id { get; set; }
    public string escalation_level { get; set; }
    public string escalation_reason { get; set; }
    public string status { get; set; }
    public int priority { get; set; }
    public string intervention_recommended { get; set; }
    public string created_at { get; set; }
}
```

---

## 7. Implementation Checklist

### Phase 5A: Core Tracker Upload (2-3 days)
- [ ] Add `UploadTrackerAsync()` to ApiClient.cs
- [ ] Create TrackerUploadResult.cs model
- [ ] Create TrackerUploadForm.cs (file picker + tracker type)
- [ ] Add "Upload Tracker" button to ribbon
- [ ] Add `btnUploadTracker_Click` event handler
- [ ] Test with Risk Log file
- [ ] Test with TMF Tracker file
- [ ] Test error handling (column mismatch, validation errors)

### Phase 5B: Leadership Dashboard Integration (1-2 days)
- [ ] Add `GetLeadershipDashboardUrl()` to ApiClient.cs
- [ ] Add "Dashboard" button to ribbon
- [ ] Add `btnLeadershipDashboard_Click` event handler
- [ ] Test opening dashboard in browser with auto-login
- [ ] Add telemetry tracking

### Phase 5C: Dashboard Exports (2-3 days) (Optional)
- [ ] Add `ExportDashboardAsync()` to ApiClient.cs
- [ ] Create DashboardExportForm.cs (export type + format selection)
- [ ] Add "Export Data" button to ribbon
- [ ] Add `btnExportDashboard_Click` event handler
- [ ] Test CSV export
- [ ] Test Excel export (if backend supports)
- [ ] Test all export types (leadership, study, portfolio)

### Phase 5D: Study Health Display (3-4 days) (Optional)
- [ ] Add `GetStudyHealthSnapshotAsync()` to ApiClient.cs
- [ ] Create StudyHealthSnapshot.cs and related models
- [ ] Create StudyHealthForm.cs (health gauge + signals list)
- [ ] Add "Study Health" button to ribbon
- [ ] Test health score display
- [ ] Test signals/correlations/escalations display
- [ ] Add recommended actions display

### Phase 5E: Integration & Testing (2-3 days)
- [ ] Add `WriteOrgId()` and `ReadOrgId()` to SecureStorage
- [ ] Update LicenseActivationForm to save org_id
- [ ] Add new TelemetryEventType enums
- [ ] Update ActivationResponse model to include org_id
- [ ] End-to-end test: Activate license → Upload tracker → View dashboard
- [ ] Test error handling across all flows
- [ ] Test with real tracker data
- [ ] Update user documentation

---

## 8. Testing Scenarios

### Scenario 1: First-Time Tracker Upload
1. CPM opens MS Project with active project
2. Clicks "Upload Tracker" button
3. Selects Risk Log file
4. Chooses "Risk Log" from dropdown
5. Clicks "Upload"
6. See progress indicator
7. Upload succeeds
8. See notification: "23 rows processed, 5 escalations detected, Health: 68 (Warning)"
9. Click "View Dashboard" to see full details

### Scenario 2: Column Mismatch Error
1. CPM uploads tracker file
2. Backend detects column mismatch (org hasn't configured this tracker type)
3. Error message: "Column mismatch detected. Contact Account Admin to configure this tracker."
4. Show download template link

### Scenario 3: Validation Errors
1. CPM uploads tracker file
2. Backend finds validation errors (e.g., Impact must be 1-3, found 5)
3. Error message shows first 5 validation errors with row numbers
4. CPM fixes errors in Excel
5. Re-uploads successfully

### Scenario 4: Leadership Dashboard Access
1. CPM clicks "Dashboard" button
2. Browser opens to app.seleen.io/dashboard/leadership
3. Auto-login with token
4. See all studies with health scores
5. Drill into specific study
6. View signals, correlations, escalations

### Scenario 5: Export Dashboard Data
1. Director clicks "Export Data" button
2. Selects "Leadership Dashboard" + CSV format
3. Saves file to desktop
4. Opens CSV in Excel
5. Sees all studies with health scores and signals

---

## 9. Dependencies

### Backend Requirements (Already Complete ✅)
- `POST /api/v1/trackers/upload` endpoint ✅
- `GET /api/v1/dashboard/study/{project_id}` endpoint ✅
- `GET /api/v1/dashboard/export/*` endpoints ✅
- TrackerUploadResult response model ✅
- StudyHealthSnapshot response model ✅

### C# Requirements
- .NET Framework 4.5.2+ (already in use)
- VSTO (Visual Studio Tools for Office) (already in use)
- Newtonsoft.Json (already in use)
- System.Net.Http (already in use)
- Windows Forms (already in use)

### Configuration Requirements
- User must have `org_id` saved (from license activation)
- User must have valid JWT token
- Account Admin must have configured tracker column mappings (one-time setup in web portal)

---

## 10. API Endpoint Reference

### Phase 5 Backend Endpoints (Already Implemented)

#### Upload Tracker
```
POST /api/v1/trackers/upload
Query Parameters:
  - org_id: string (required)
  - project_id: string (required)
  - tracker_type: string (required) - "risk_log", "tmf_tracker", "budget_tracker", "vendor_tracker"
Body: multipart/form-data with "file" field
Response: TrackerUploadResult
```

#### Get Study Health
```
GET /api/v1/dashboard/study/{project_id}
Query Parameters:
  - org_id: string (required)
Response: StudyHealthSnapshot
```

#### Export Leadership Dashboard
```
GET /api/v1/dashboard/export/leadership
Query Parameters:
  - org_id: string (required)
  - format: string (optional, default "csv") - "csv" or "excel"
  - status_filter: string (optional) - "healthy", "warning", "critical"
Response: CSV or Excel file (StreamingResponse)
```

#### Export Study Detail
```
GET /api/v1/dashboard/export/study/{project_id}
Query Parameters:
  - org_id: string (required)
  - format: string (optional, default "csv")
Response: CSV or Excel file
```

#### Export Portfolio Health
```
GET /api/v1/dashboard/export/portfolio/health
Query Parameters:
  - org_id: string (required)
  - format: string (optional, default "csv")
Response: CSV or Excel file
```

---

## 11. UI Mockups

### Upload Tracker Form
```
┌─────────────────────────────────────────────────┐
│  Upload Tracker                           [X]   │
├─────────────────────────────────────────────────┤
│                                                 │
│  Select tracker file to upload:                │
│  ┌───────────────────────────────┐  ┌────────┐ │
│  │ C:\Users\Jane\Risk_Log.xlsx   │  │Browse..│ │
│  └───────────────────────────────┘  └────────┘ │
│                                                 │
│  Tracker type:                                  │
│  ┌───────────────────────────────┐             │
│  │ Risk Log                    ▼ │             │
│  └───────────────────────────────┘             │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ ████████████████░░░░░░░░░░░░░░░░░░░░░░░ │ │
│  │ Uploading...                              │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│              ┌────────┐  ┌────────┐            │
│              │ Upload │  │ Cancel │            │
│              └────────┘  └────────┘            │
└─────────────────────────────────────────────────┘
```

### Dashboard Export Form
```
┌─────────────────────────────────────────────────┐
│  Export Dashboard                         [X]   │
├─────────────────────────────────────────────────┤
│                                                 │
│  Export type:                                   │
│  ┌───────────────────────────────┐             │
│  │ Leadership Dashboard        ▼ │             │
│  └───────────────────────────────┘             │
│                                                 │
│  Format:                                        │
│  ◉ CSV                                          │
│  ○ Excel                                        │
│                                                 │
│              ┌────────┐  ┌────────┐            │
│              │ Export │  │ Cancel │            │
│              └────────┘  └────────┘            │
└─────────────────────────────────────────────────┘
```

---

## 12. Estimated Development Time

### Minimum Viable Product (MVP)
- **Phase 5A: Core Tracker Upload** - 2-3 days
- **Phase 5B: Leadership Dashboard Button** - 1 day
- **Phase 5E: Integration & Testing** - 2 days
- **Total: 5-6 days**

### Full Implementation
- **Phase 5A: Core Tracker Upload** - 2-3 days
- **Phase 5B: Leadership Dashboard Button** - 1-2 days
- **Phase 5C: Dashboard Exports** - 2-3 days
- **Phase 5D: Study Health Display** - 3-4 days
- **Phase 5E: Integration & Testing** - 2-3 days
- **Total: 10-15 days**

### Recommendation
Start with **MVP** (Phases 5A, 5B, 5E) to get tracker upload and dashboard access working immediately. Add optional features (exports, health display) in follow-up releases based on user feedback.

---

## 13. File Structure

```
desktop-addin/IlanaPM.AddIn/
│
├── Services/
│   ├── ApiClient.cs (UPDATE: Add 4 new methods)
│   ├── SecureStorage.cs (UPDATE: Add org_id storage)
│   └── ...
│
├── Models/
│   ├── TrackerUploadResult.cs (NEW)
│   ├── StudyHealthSnapshot.cs (NEW)
│   └── ...
│
├── Forms/
│   ├── TrackerUploadForm.cs (NEW)
│   ├── TrackerUploadForm.Designer.cs (NEW)
│   ├── DashboardExportForm.cs (NEW - Optional)
│   ├── DashboardExportForm.Designer.cs (NEW - Optional)
│   ├── StudyHealthForm.cs (NEW - Optional)
│   ├── StudyHealthForm.Designer.cs (NEW - Optional)
│   └── ...
│
├── IlanaPMRibbon.cs (UPDATE: Add 2-3 button event handlers)
├── IlanaPMRibbon.Designer.cs (UPDATE: Add ribbon button declarations)
├── IlanaPMRibbon.xml (UPDATE: Add ribbon button XML)
├── TelemetryEventType.cs (UPDATE: Add 3-4 new event types)
└── ...
```

---

## 14. Summary

**What's Complete:**
- Backend Phase 5 implementation ✅
- API endpoints (tracker upload, dashboard, exports) ✅
- Database schema ✅
- Intelligence services ✅
- Test suite (17/17 passing) ✅
- Documentation (API guide, deployment, workflow) ✅

**What's Needed:**
- C# API client methods (4 new methods) ⚠️
- C# ribbon buttons (2-3 new buttons) ⚠️
- C# forms (2-3 new forms) ⚠️
- C# models (2 new model files) ⚠️
- Integration testing ⚠️

**Priority:**
1. **CRITICAL:** Tracker upload (core workflow)
2. **HIGH:** Leadership dashboard access (visibility)
3. **MEDIUM:** Dashboard exports (reporting)
4. **LOW:** Study health display (nice-to-have)

**Estimated Effort:**
- MVP: 5-6 days
- Full: 10-15 days

---

**Next Steps:**
1. Review this document with development team
2. Prioritize MVP vs full implementation
3. Assign C# developer to implement Phase 5A (tracker upload)
4. Test with real Risk Log and TMF Tracker data
5. Deploy to production after testing
