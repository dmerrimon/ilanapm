# Windows VM Integration Guide

**Purpose:** Integrate the completed C# services into the Windows VSTO project
**Prerequisites:** Windows VM running, Visual Studio 2022 with VSTO, MS Project installed
**Estimated Time:** 2-3 hours

---

## Step 1: File Synchronization

### Option A: Copy Files Manually (Recommended)
From your Mac, sync the following files to the Windows VM:

```
Mac → Windows File Mapping:

Core Services:
~/Projects/ilana-pm/desktop-addin/ThisAddIn.cs
  → C:\Users\[user]\Projects\ilana-pm\desktop-addin\IlanaPM.AddIn\ThisAddIn.cs

~/Projects/ilana-pm/desktop-addin/Services/ProjectDataExtractor.cs
  → C:\Users\[user]\Projects\ilana-pm\desktop-addin\IlanaPM.AddIn\Services\ProjectDataExtractor.cs

~/Projects/ilana-pm/desktop-addin/Services/ProjectDataWriter.cs
  → C:\Users\[user]\Projects\ilana-pm\desktop-addin\IlanaPM.AddIn\Services\ProjectDataWriter.cs (NEW)

~/Projects/ilana-pm/desktop-addin/Services/ViewManager.cs
  → C:\Users\[user]\Projects\ilana-pm\desktop-addin\IlanaPM.AddIn\Services\ViewManager.cs (NEW)

Models:
~/Projects/ilana-pm/desktop-addin/Models/MLModels.cs
  → C:\Users\[user]\Projects\ilana-pm\desktop-addin\IlanaPM.AddIn\Models\MLModels.cs (NEW)

~/Projects/ilana-pm/desktop-addin/Models/TeamsNotification.cs
  → C:\Users\[user]\Projects\ilana-pm\desktop-addin\IlanaPM.AddIn\Models\TeamsNotification.cs (NEW)

API Client:
~/Projects/ilana-pm/desktop-addin/ApiClient.cs
  → C:\Users\[user]\Projects\ilana-pm\desktop-addin\IlanaPM.AddIn\Services\ApiClient.cs
```

### Option B: Git Pull (If Project is in Git)
```powershell
cd C:\Users\[user]\Projects\ilana-pm
git pull origin main
```

---

## Step 2: Create MLAdvisoryForm

**File:** `IlanaPM.AddIn\MLAdvisoryForm.cs`

### In Visual Studio:
1. Right-click `IlanaPM.AddIn` project
2. Add → New Item → Windows Form
3. Name: `MLAdvisoryForm.cs`
4. Click Add

### Copy this code to MLAdvisoryForm.cs:

```csharp
using System;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    public partial class MLAdvisoryForm : Form
    {
        public MLAdvisoryForm()
        {
            InitializeComponent();
        }

        public void DisplayAdvisory(Models.TimelineAdvisory advisory)
        {
            lblSummary.Text = $"Analyzed {advisory.duration_predictions.Count} tasks | High Risk Tasks: {advisory.high_risk_tasks.Count}";

            var sb = new System.Text.StringBuilder();

            // Duration Predictions
            sb.AppendLine("═══ DURATION PREDICTIONS ═══\n");
            foreach (var pred in advisory.duration_predictions)
            {
                sb.AppendLine($"Task: {pred.task_name}");
                sb.AppendLine($"Predicted: {pred.prediction.predicted_duration_days} days");
                sb.AppendLine($"Range: {pred.prediction.confidence_interval.lower}-{pred.prediction.confidence_interval.upper} days");
                sb.AppendLine($"Confidence: {(pred.prediction.confidence_score * 100):F0}%");
                sb.AppendLine($"Explanation: {pred.prediction.explanation}");
                sb.AppendLine();
            }

            // High Risk Tasks
            if (advisory.high_risk_tasks.Count > 0)
            {
                sb.AppendLine("\n═══ HIGH RISK TASKS ═══\n");
                foreach (var task in advisory.high_risk_tasks)
                {
                    sb.AppendLine($"⚠️  {task.task_name} (Risk Score: {task.risk_score}/100)");
                    sb.AppendLine($"Risk Factors:");
                    foreach (var factor in task.risk_factors)
                    {
                        sb.AppendLine($"  • {factor}");
                    }
                    sb.AppendLine();
                }
            }

            txtAdvisory.Text = sb.ToString();
        }

        private void InitializeComponent()
        {
            this.lblSummary = new System.Windows.Forms.Label();
            this.txtAdvisory = new System.Windows.Forms.TextBox();
            this.btnClose = new System.Windows.Forms.Button();
            this.SuspendLayout();

            // lblSummary
            this.lblSummary.AutoSize = true;
            this.lblSummary.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold);
            this.lblSummary.Location = new System.Drawing.Point(12, 12);
            this.lblSummary.Name = "lblSummary";
            this.lblSummary.Size = new System.Drawing.Size(200, 15);
            this.lblSummary.TabIndex = 0;
            this.lblSummary.Text = "ML Advisory Summary";

            // txtAdvisory
            this.txtAdvisory.Font = new System.Drawing.Font("Consolas", 9F);
            this.txtAdvisory.Location = new System.Drawing.Point(12, 40);
            this.txtAdvisory.Multiline = true;
            this.txtAdvisory.Name = "txtAdvisory";
            this.txtAdvisory.ReadOnly = true;
            this.txtAdvisory.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtAdvisory.Size = new System.Drawing.Size(760, 450);
            this.txtAdvisory.TabIndex = 1;

            // btnClose
            this.btnClose.Location = new System.Drawing.Point(697, 496);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(75, 23);
            this.btnClose.TabIndex = 2;
            this.btnClose.Text = "Close";
            this.btnClose.UseVisualStyleBackColor = true;
            this.btnClose.Click += new System.EventHandler(this.btnClose_Click);

            // MLAdvisoryForm
            this.ClientSize = new System.Drawing.Size(784, 531);
            this.Controls.Add(this.btnClose);
            this.Controls.Add(this.txtAdvisory);
            this.Controls.Add(this.lblSummary);
            this.Name = "MLAdvisoryForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Ilana PM - ML Advisory";
            this.ResumeLayout(false);
            this.PerformLayout();
        }

        private Label lblSummary;
        private TextBox txtAdvisory;
        private Button btnClose;

        private void btnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }
    }
}
```

---

## Step 3: Create SettingsForm

**File:** `IlanaPM.AddIn\SettingsForm.cs`

### In Visual Studio:
1. Right-click `IlanaPM.AddIn` project
2. Add → New Item → Windows Form
3. Name: `SettingsForm.cs`
4. Click Add

### Copy this code to SettingsForm.cs:

```csharp
using System;
using System.Windows.Forms;

namespace IlanaPM.AddIn
{
    public partial class SettingsForm : Form
    {
        public SettingsForm()
        {
            InitializeComponent();
            LoadSettings();
        }

        private void LoadSettings()
        {
            // Load from user settings
            txtApiUrl.Text = Properties.Settings.Default.ApiBaseUrl ?? "https://ilanapm.azurewebsites.net";
            txtWebhookUrl.Text = Properties.Settings.Default.TeamsWebhookUrl ?? "";
            chkAutoUpdate.Checked = Properties.Settings.Default.AutoUpdateEnabled;
        }

        private void btnSave_Click(object sender, EventArgs e)
        {
            // Save settings
            Properties.Settings.Default.ApiBaseUrl = txtApiUrl.Text;
            Properties.Settings.Default.TeamsWebhookUrl = txtWebhookUrl.Text;
            Properties.Settings.Default.AutoUpdateEnabled = chkAutoUpdate.Checked;
            Properties.Settings.Default.Save();

            MessageBox.Show("Settings saved successfully!", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
            this.Close();
        }

        private void btnCancel_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void btnTestConnection_Click(object sender, EventArgs e)
        {
            try
            {
                var client = new System.Net.Http.HttpClient();
                var response = client.GetAsync(txtApiUrl.Text + "/api/v1/health").Result;

                if (response.IsSuccessStatusCode)
                {
                    MessageBox.Show("Connection successful!", "Test Connection", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                else
                {
                    MessageBox.Show($"Connection failed: {response.StatusCode}", "Test Connection", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Connection error: {ex.Message}", "Test Connection", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void InitializeComponent()
        {
            this.lblApiUrl = new System.Windows.Forms.Label();
            this.txtApiUrl = new System.Windows.Forms.TextBox();
            this.btnTestConnection = new System.Windows.Forms.Button();
            this.lblWebhookUrl = new System.Windows.Forms.Label();
            this.txtWebhookUrl = new System.Windows.Forms.TextBox();
            this.chkAutoUpdate = new System.Windows.Forms.CheckBox();
            this.btnSave = new System.Windows.Forms.Button();
            this.btnCancel = new System.Windows.Forms.Button();
            this.SuspendLayout();

            // lblApiUrl
            this.lblApiUrl.AutoSize = true;
            this.lblApiUrl.Location = new System.Drawing.Point(20, 20);
            this.lblApiUrl.Name = "lblApiUrl";
            this.lblApiUrl.Size = new System.Drawing.Size(100, 15);
            this.lblApiUrl.TabIndex = 0;
            this.lblApiUrl.Text = "API Base URL:";

            // txtApiUrl
            this.txtApiUrl.Location = new System.Drawing.Point(20, 40);
            this.txtApiUrl.Name = "txtApiUrl";
            this.txtApiUrl.Size = new System.Drawing.Size(400, 23);
            this.txtApiUrl.TabIndex = 1;

            // btnTestConnection
            this.btnTestConnection.Location = new System.Drawing.Point(430, 40);
            this.btnTestConnection.Name = "btnTestConnection";
            this.btnTestConnection.Size = new System.Drawing.Size(100, 23);
            this.btnTestConnection.TabIndex = 2;
            this.btnTestConnection.Text = "Test Connection";
            this.btnTestConnection.UseVisualStyleBackColor = true;
            this.btnTestConnection.Click += new System.EventHandler(this.btnTestConnection_Click);

            // lblWebhookUrl
            this.lblWebhookUrl.AutoSize = true;
            this.lblWebhookUrl.Location = new System.Drawing.Point(20, 80);
            this.lblWebhookUrl.Name = "lblWebhookUrl";
            this.lblWebhookUrl.Size = new System.Drawing.Size(150, 15);
            this.lblWebhookUrl.TabIndex = 3;
            this.lblWebhookUrl.Text = "Teams Webhook URL:";

            // txtWebhookUrl
            this.txtWebhookUrl.Location = new System.Drawing.Point(20, 100);
            this.txtWebhookUrl.Name = "txtWebhookUrl";
            this.txtWebhookUrl.Size = new System.Drawing.Size(510, 23);
            this.txtWebhookUrl.TabIndex = 4;

            // chkAutoUpdate
            this.chkAutoUpdate.AutoSize = true;
            this.chkAutoUpdate.Location = new System.Drawing.Point(20, 140);
            this.chkAutoUpdate.Name = "chkAutoUpdate";
            this.chkAutoUpdate.Size = new System.Drawing.Size(200, 19);
            this.chkAutoUpdate.TabIndex = 5;
            this.chkAutoUpdate.Text = "Enable automatic update checks";
            this.chkAutoUpdate.UseVisualStyleBackColor = true;

            // btnSave
            this.btnSave.Location = new System.Drawing.Point(374, 180);
            this.btnSave.Name = "btnSave";
            this.btnSave.Size = new System.Drawing.Size(75, 23);
            this.btnSave.TabIndex = 6;
            this.btnSave.Text = "Save";
            this.btnSave.UseVisualStyleBackColor = true;
            this.btnSave.Click += new System.EventHandler(this.btnSave_Click);

            // btnCancel
            this.btnCancel.Location = new System.Drawing.Point(455, 180);
            this.btnCancel.Name = "btnCancel";
            this.btnCancel.Size = new System.Drawing.Size(75, 23);
            this.btnCancel.TabIndex = 7;
            this.btnCancel.Text = "Cancel";
            this.btnCancel.UseVisualStyleBackColor = true;
            this.btnCancel.Click += new System.EventHandler(this.btnCancel_Click);

            // SettingsForm
            this.ClientSize = new System.Drawing.Size(550, 220);
            this.Controls.Add(this.btnCancel);
            this.Controls.Add(this.btnSave);
            this.Controls.Add(this.chkAutoUpdate);
            this.Controls.Add(this.txtWebhookUrl);
            this.Controls.Add(this.lblWebhookUrl);
            this.Controls.Add(this.btnTestConnection);
            this.Controls.Add(this.txtApiUrl);
            this.Controls.Add(this.lblApiUrl);
            this.Name = "SettingsForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Ilana PM - Settings";
            this.ResumeLayout(false);
            this.PerformLayout();
        }

        private Label lblApiUrl;
        private TextBox txtApiUrl;
        private Button btnTestConnection;
        private Label lblWebhookUrl;
        private TextBox txtWebhookUrl;
        private CheckBox chkAutoUpdate;
        private Button btnSave;
        private Button btnCancel;
    }
}
```

---

## Step 4: Add User Settings

### In Visual Studio:
1. Right-click `IlanaPM.AddIn` project
2. Add → New Item → Search for "Settings File"
3. Name: `Settings.settings`
4. Click Add

### Add these settings in the designer:
| Name | Type | Scope | Value |
|------|------|-------|-------|
| ApiBaseUrl | string | User | https://ilanapm.azurewebsites.net |
| TeamsWebhookUrl | string | User | (empty) |
| AutoUpdateEnabled | bool | User | True |

---

## Step 5: Update IlanaPMRibbon.cs

### Add 4 New Button Handlers:

```csharp
// 1. ML Advisory Button
private async void btnMLAdvisory_Click(object sender, RibbonControlEventArgs e)
{
    System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

    try
    {
        var extractor = new Services.ProjectDataExtractor();
        var timeline = extractor.ExtractTimeline(Globals.ThisAddIn.Application);

        var apiClient = new Services.ApiClient();
        var advisory = await apiClient.GetTimelineAdvisoryAsync(timeline);

        // Write ML results back to custom fields
        var writer = new Services.ProjectDataWriter();
        foreach (var pred in advisory.duration_predictions)
        {
            writer.WriteMLAdvisory(Globals.ThisAddIn.Application, pred.task_id, pred.prediction, null);
        }
        foreach (var risk in advisory.risk_scores)
        {
            writer.WriteMLAdvisory(Globals.ThisAddIn.Application, risk.task_id, null, risk.risk);
        }

        // Show ML Advisory form
        MLAdvisoryForm advisoryForm = new MLAdvisoryForm();
        advisoryForm.DisplayAdvisory(advisory);
        advisoryForm.ShowDialog();
    }
    catch (Exception ex)
    {
        MessageBox.Show($"Error: {ex.Message}", "ML Advisory Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}

// 2. Export to Teams Button
private async void btnExportTeams_Click(object sender, RibbonControlEventArgs e)
{
    try
    {
        // Prompt for Teams webhook URL
        string webhookUrl = PromptForWebhookUrl();
        if (string.IsNullOrEmpty(webhookUrl))
            return;

        // Get current validation results
        var extractor = new Services.ProjectDataExtractor();
        var timeline = extractor.ExtractTimeline(Globals.ThisAddIn.Application);

        var apiClient = new Services.ApiClient();
        var result = await apiClient.ValidateTimelineAsync(timeline);

        // Build notification
        var notification = new Models.TeamsNotificationRequest
        {
            webhook_url = webhookUrl,
            study_name = timeline.study_name,
            validation_summary = new Models.ValidationSummary
            {
                status = result.status,
                error_count = result.error_count,
                warning_count = result.warning_count,
                total_tasks = result.total_tasks_analyzed
            },
            high_risk_tasks = new List<Models.HighRiskTaskSummary>()
        };

        // Add high-risk tasks
        foreach (var issue in result.issues)
        {
            if (issue.severity == "error" && !string.IsNullOrEmpty(issue.task_id))
            {
                var task = timeline.tasks.Find(t => t.id == issue.task_id);
                if (task != null)
                {
                    notification.high_risk_tasks.Add(new Models.HighRiskTaskSummary
                    {
                        name = task.name,
                        risk_score = 90
                    });
                }
            }
        }

        // Send notification
        bool success = await apiClient.SendTeamsNotificationAsync(notification);

        if (success)
        {
            MessageBox.Show("Validation summary sent to Teams!", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        else
        {
            MessageBox.Show("Failed to send to Teams. Check webhook URL.", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }
    catch (Exception ex)
    {
        MessageBox.Show($"Error: {ex.Message}", "Teams Export Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}

private string PromptForWebhookUrl()
{
    using (var form = new Form())
    {
        form.Text = "Teams Webhook URL";
        form.Width = 500;
        form.Height = 150;
        form.StartPosition = FormStartPosition.CenterScreen;

        var label = new Label { Text = "Enter Teams Incoming Webhook URL:", Left = 20, Top = 20, Width = 400 };
        var textBox = new TextBox { Left = 20, Top = 50, Width = 440 };
        var btnOk = new Button { Text = "OK", Left = 300, Top = 80, Width = 75, DialogResult = DialogResult.OK };
        var btnCancel = new Button { Text = "Cancel", Left = 385, Top = 80, Width = 75, DialogResult = DialogResult.Cancel };

        form.Controls.Add(label);
        form.Controls.Add(textBox);
        form.Controls.Add(btnOk);
        form.Controls.Add(btnCancel);
        form.AcceptButton = btnOk;
        form.CancelButton = btnCancel;

        return form.ShowDialog() == DialogResult.OK ? textBox.Text : null;
    }
}

// 3. View Report Button
private void btnViewReport_Click(object sender, RibbonControlEventArgs e)
{
    try
    {
        // Show menu to select view
        using (var form = new Form())
        {
            form.Text = "Select View";
            form.Width = 300;
            form.Height = 250;
            form.StartPosition = FormStartPosition.CenterScreen;

            var label = new Label { Text = "Choose a report view:", Left = 20, Top = 20, Width = 240 };

            var btnValidation = new Button { Text = "Validation Summary", Left = 20, Top = 50, Width = 240 };
            btnValidation.Click += (s, args) => {
                var viewManager = new Services.ViewManager();
                viewManager.CreateValidationSummaryView(Globals.ThisAddIn.Application);
                form.Close();
            };

            var btnRisk = new Button { Text = "Risk Dashboard", Left = 20, Top = 85, Width = 240 };
            btnRisk.Click += (s, args) => {
                var viewManager = new Services.ViewManager();
                viewManager.CreateRiskDashboardView(Globals.ThisAddIn.Application);
                form.Close();
            };

            var btnExecutive = new Button { Text = "Executive Summary", Left = 20, Top = 120, Width = 240 };
            btnExecutive.Click += (s, args) => {
                var viewManager = new Services.ViewManager();
                viewManager.CreateExecutiveSummaryView(Globals.ThisAddIn.Application);
                form.Close();
            };

            var btnChecklist = new Button { Text = "Checklist Completion", Left = 20, Top = 155, Width = 240 };
            btnChecklist.Click += (s, args) => {
                var viewManager = new Services.ViewManager();
                viewManager.CreateChecklistCompletionView(Globals.ThisAddIn.Application);
                form.Close();
            };

            form.Controls.Add(label);
            form.Controls.Add(btnValidation);
            form.Controls.Add(btnRisk);
            form.Controls.Add(btnExecutive);
            form.Controls.Add(btnChecklist);

            form.ShowDialog();
        }
    }
    catch (Exception ex)
    {
        MessageBox.Show($"Error: {ex.Message}", "View Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}

// 4. Settings Button
private void btnSettings_Click(object sender, RibbonControlEventArgs e)
{
    var settingsForm = new SettingsForm();
    settingsForm.ShowDialog();
}
```

### Update Existing Validation Button to Include Write-Back:

```csharp
private async void btnValidate_Click(object sender, RibbonControlEventArgs e)
{
    System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12;

    try
    {
        var extractor = new Services.ProjectDataExtractor();
        var timeline = extractor.ExtractTimeline(Globals.ThisAddIn.Application);

        var apiClient = new Services.ApiClient();
        var result = await apiClient.ValidateTimelineAsync(timeline);

        // NEW: Write back to MS Project
        var writer = new Services.ProjectDataWriter();
        writer.WriteValidationResults(Globals.ThisAddIn.Application, result);

        // Show results form
        ValidationResultsForm resultsForm = new ValidationResultsForm();
        resultsForm.DisplayResults(result);
        resultsForm.ShowDialog();
    }
    catch (Exception ex)
    {
        MessageBox.Show($"Error: {ex.Message}", "Ilana PM Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}
```

---

## Step 6: Build and Test

### Build Steps:
1. Build → Clean Solution
2. Build → Rebuild Solution
3. Check for errors in Error List
4. Resolve any missing references

### Test Checklist:

#### 1. Custom Fields Test
- [ ] Open MS Project
- [ ] Open a project file
- [ ] Go to View → Tables → More Tables
- [ ] Check that custom fields exist: Regulatory Authority, Study Phase, etc.

#### 2. Validation Test
- [ ] Click "Validate Timeline" button
- [ ] Verify validation results display
- [ ] Check task notes for issue details
- [ ] Verify Risk Score custom field populated
- [ ] Verify high-risk tasks are marked

#### 3. ML Advisory Test
- [ ] Click "ML Advisory" button
- [ ] Verify ML predictions display
- [ ] Check that ML Predicted Duration field populated
- [ ] Check that ML Confidence % field populated
- [ ] Verify task notes include ML explanations

#### 4. Teams Export Test
- [ ] Get a Teams incoming webhook URL
- [ ] Click "Export to Teams" button
- [ ] Enter webhook URL
- [ ] Check Teams channel for notification
- [ ] Verify Adaptive Card displays correctly

#### 5. View Report Test
- [ ] Click "View Report" button
- [ ] Select "Validation Summary"
- [ ] Verify view shows correct columns
- [ ] Repeat for all 4 views

#### 6. Settings Test
- [ ] Click "Settings" button
- [ ] Modify API URL
- [ ] Click "Test Connection"
- [ ] Verify connection successful
- [ ] Click "Save"
- [ ] Reopen Settings to verify persistence

---

## Step 7: Troubleshooting

### Common Issues:

**Missing References:**
- Right-click References → Add Reference
- Verify: Microsoft.Office.Interop.MSProject, System.Net.Http, Newtonsoft.Json

**Custom Field Errors:**
- Ensure MS Project has an active project open
- Check that field names don't conflict with existing fields

**API Connection Errors:**
- Verify backend is running: https://ilanapm.azurewebsites.net/api/v1/health
- Check TLS 1.2 is enabled (already in code)
- Verify firewall allows HTTPS outbound

**Form Designer Issues:**
- If form doesn't display, try: View → Designer
- Rebuild solution if controls are missing

---

## Step 8: Commit Changes

After successful testing:

```powershell
git add .
git commit -m "Complete Phase 3 desktop add-in implementation

- Added custom field creation (10 fields)
- Implemented data write-back service
- Added ML advisory integration
- Added Teams webhook integration
- Created 4 custom views
- Added settings UI
- Updated ribbon with all 5 buttons

All SOW Section 3.2 requirements now met."

git push origin main
```

---

## Next Steps After Integration

1. Internal testing (1 week of daily use)
2. Bug fixes and polish
3. Create MSI installer
4. User documentation
5. Pilot distribution (3-5 users)

---

## Support

**Documentation:**
- Implementation Status: See IMPLEMENTATION_STATUS.md
- Plan File: ~/.claude/plans/eager-sauteeing-sifakis.md
- API Docs: https://ilanapm.azurewebsites.net/docs

**Questions?**
- Review this guide thoroughly before starting
- Check Error List in Visual Studio for specific errors
- Test incrementally after each major addition
