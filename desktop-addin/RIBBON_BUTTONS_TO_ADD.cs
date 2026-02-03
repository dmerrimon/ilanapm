// ============================================================================
// ADD THESE 4 BUTTON HANDLERS TO IlanaPMRibbon.cs
// ============================================================================
// Also add at top of file: using System.Collections.Generic;
// ============================================================================

// 1. ML ADVISORY BUTTON
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
    catch (System.Exception ex)
    {
        MessageBox.Show("Error: " + ex.Message, "ML Advisory Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}

// 2. EXPORT TO TEAMS BUTTON
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
            high_risk_tasks = new System.Collections.Generic.List<Models.HighRiskTaskSummary>()
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
    catch (System.Exception ex)
    {
        MessageBox.Show("Error: " + ex.Message, "Teams Export Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}

// Helper method for Teams webhook URL prompt
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

// 3. VIEW REPORT BUTTON
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
    catch (System.Exception ex)
    {
        MessageBox.Show("Error: " + ex.Message, "View Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}

// 4. SETTINGS BUTTON
private void btnSettings_Click(object sender, RibbonControlEventArgs e)
{
    var settingsForm = new SettingsForm();
    settingsForm.ShowDialog();
}
