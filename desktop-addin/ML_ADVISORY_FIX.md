# ML Advisory Fix - Complete Implementation

## Problem
The `TimelineAdvisory` model doesn't match the backend API response structure.

## Backend Returns (from `/api/v1/advisory/timeline`):
```json
{
    "study_name": "Study Name",
    "phase": "Phase II",
    "authority": "FDA",
    "duration_predictions": {
        "predictions": [
            {
                "task_id": "1",
                "task_name": "Task Name",
                "current_duration": 30,
                "prediction": {
                    "predicted_duration_days": 45,
                    "confidence_interval": { "lower": 30, "upper": 60 },
                    "confidence_score": 0.85,
                    "explanation": "...",
                    "comparable_tasks": [...],
                    "model_version": "heuristic-v1"
                }
            }
        ],
        "average_confidence": 0.72,
        "total_tasks": 10,
        "model_version": "heuristic-v1"
    },
    "risk_analysis": {
        "risk_scores": [
            {
                "task_id": "1",
                "task_name": "Task Name",
                "risk": {
                    "risk_score": 65,
                    "risk_level": "high",
                    "risk_factors": ["..."],
                    "mitigation_suggestions": ["..."]
                }
            }
        ],
        "high_risk_tasks": [
            {
                "task_id": "1",
                "task_name": "Task Name",
                "risk_score": 65,
                "risk_factors": ["..."]
            }
        ],
        "average_risk": 42,
        "high_risk_count": 3
    },
    "summary_statistics": {...},
    "recommendations": ["..."]
}
```

## Solution

### Step 1: Update MLModels.cs

Replace the entire content of `desktop-addin/IlanaPM.AddIn/Models/MLModels.cs` with:

```csharp
using System.Collections.Generic;

namespace IlanaPM.AddIn.Models
{
    // Duration prediction for a single task
    public class DurationPrediction
    {
        public int predicted_duration_days { get; set; }
        public ConfidenceInterval confidence_interval { get; set; }
        public double confidence_score { get; set; }
        public string explanation { get; set; }
        public List<ComparableTask> comparable_tasks { get; set; }
        public string model_version { get; set; }
    }

    public class ConfidenceInterval
    {
        public int lower { get; set; }
        public int upper { get; set; }
    }

    public class ComparableTask
    {
        public string name { get; set; }
        public int typical_duration { get; set; }
        public string authority { get; set; }
    }

    // Risk score for a single task
    public class RiskScore
    {
        public int risk_score { get; set; }
        public string risk_level { get; set; }
        public List<string> risk_factors { get; set; }
        public List<string> mitigation_suggestions { get; set; }
        public string model_version { get; set; }
    }

    // Duration predictions wrapper (matches backend "duration_predictions" structure)
    public class DurationPredictionsWrapper
    {
        public List<TaskDurationPrediction> predictions { get; set; }
        public double average_confidence { get; set; }
        public int total_tasks { get; set; }
        public string model_version { get; set; }
    }

    // Risk analysis wrapper (matches backend "risk_analysis" structure)
    public class RiskAnalysisWrapper
    {
        public List<TaskRiskScore> risk_scores { get; set; }
        public List<HighRiskTask> high_risk_tasks { get; set; }
        public double average_risk { get; set; }
        public int high_risk_count { get; set; }
    }

    // Task with duration prediction
    public class TaskDurationPrediction
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public int current_duration { get; set; }
        public DurationPrediction prediction { get; set; }
    }

    // Task with risk score
    public class TaskRiskScore
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public RiskScore risk { get; set; }
    }

    // High risk task summary
    public class HighRiskTask
    {
        public string task_id { get; set; }
        public string task_name { get; set; }
        public int risk_score { get; set; }
        public List<string> risk_factors { get; set; }
    }

    // Summary statistics
    public class SummaryStatistics
    {
        public int total_tasks { get; set; }
        public double avg_predicted_duration { get; set; }
        public double avg_risk_score { get; set; }
        public int critical_risk_count { get; set; }
        public int high_risk_count { get; set; }
        public int medium_risk_count { get; set; }
        public int aggressive_duration_count { get; set; }
        public double avg_prediction_confidence { get; set; }
    }

    // COMPLETE timeline advisory response (matches backend exactly)
    public class TimelineAdvisory
    {
        public string study_name { get; set; }
        public string phase { get; set; }
        public string authority { get; set; }
        public DurationPredictionsWrapper duration_predictions { get; set; }
        public RiskAnalysisWrapper risk_analysis { get; set; }
        public SummaryStatistics summary_statistics { get; set; }
        public List<string> recommendations { get; set; }
        public string model_version { get; set; }
    }
}
```

### Step 2: Update IlanaPMRibbon.cs - ML Advisory Button

Replace the `btnMLAdvisory_Click` method (around line 81) with:

```csharp
// ML ADVISORY BUTTON
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

        // Write duration predictions
        if (advisory.duration_predictions != null && advisory.duration_predictions.predictions != null)
        {
            foreach (var pred in advisory.duration_predictions.predictions)
            {
                writer.WriteMLAdvisory(
                    Globals.ThisAddIn.Application,
                    pred.task_id,
                    pred.prediction,
                    null
                );
            }
        }

        // Write risk scores
        if (advisory.risk_analysis != null && advisory.risk_analysis.risk_scores != null)
        {
            foreach (var risk in advisory.risk_analysis.risk_scores)
            {
                writer.WriteMLAdvisory(
                    Globals.ThisAddIn.Application,
                    risk.task_id,
                    null,
                    risk.risk
                );
            }
        }

        // Show ML Advisory form
        MLAdvisoryForm advisoryForm = new MLAdvisoryForm();
        advisoryForm.DisplayAdvisory(advisory);
        advisoryForm.ShowDialog();
    }
    catch (System.Exception ex)
    {
        string detailedError = "Error: " + ex.Message;
        if (ex.InnerException != null)
        {
            detailedError = detailedError + "\n\nInner: " + ex.InnerException.Message;
        }
        MessageBox.Show(detailedError, "ML Advisory Error",
            MessageBoxButtons.OK, MessageBoxIcon.Error);
    }
}
```

### Step 3: Update MLAdvisoryForm.cs - Display Method

Replace the `DisplayAdvisory` method in `MLAdvisoryForm.cs` with:

```csharp
public void DisplayAdvisory(Models.TimelineAdvisory advisory)
{
    int predictionCount = advisory.duration_predictions?.predictions?.Count ?? 0;
    int highRiskCount = advisory.risk_analysis?.high_risk_tasks?.Count ?? 0;

    lblSummary.Text = string.Format("Analyzed {0} tasks | High Risk Tasks: {1}",
        predictionCount,
        highRiskCount);

    var sb = new System.Text.StringBuilder();

    // Summary Statistics
    if (advisory.summary_statistics != null)
    {
        sb.AppendLine("═══ SUMMARY ═══" + Environment.NewLine);
        sb.AppendLine(string.Format("Total Tasks: {0}", advisory.summary_statistics.total_tasks));
        sb.AppendLine(string.Format("Avg Predicted Duration: {0} days", advisory.summary_statistics.avg_predicted_duration));
        sb.AppendLine(string.Format("Avg Risk Score: {0}/100", advisory.summary_statistics.avg_risk_score));
        sb.AppendLine(string.Format("High Risk Tasks: {0}", advisory.summary_statistics.high_risk_count));
        sb.AppendLine(string.Format("Critical Risk Tasks: {0}", advisory.summary_statistics.critical_risk_count));
        sb.AppendLine(string.Format("Aggressive Durations: {0}", advisory.summary_statistics.aggressive_duration_count));
        sb.AppendLine();
    }

    // Recommendations
    if (advisory.recommendations != null && advisory.recommendations.Count > 0)
    {
        sb.AppendLine("═══ RECOMMENDATIONS ═══" + Environment.NewLine);
        foreach (var rec in advisory.recommendations)
        {
            sb.AppendLine("• " + rec);
        }
        sb.AppendLine();
    }

    // Duration Predictions
    if (advisory.duration_predictions != null && advisory.duration_predictions.predictions != null)
    {
        sb.AppendLine("═══ DURATION PREDICTIONS ═══" + Environment.NewLine);
        foreach (var pred in advisory.duration_predictions.predictions)
        {
            sb.AppendLine(string.Format("Task: {0}", pred.task_name));
            sb.AppendLine(string.Format("  Current: {0} days", pred.current_duration));
            sb.AppendLine(string.Format("  Predicted: {0} days", pred.prediction.predicted_duration_days));
            sb.AppendLine(string.Format("  Range: {0}-{1} days",
                pred.prediction.confidence_interval.lower,
                pred.prediction.confidence_interval.upper));
            sb.AppendLine(string.Format("  Confidence: {0:F0}%", pred.prediction.confidence_score * 100));
            sb.AppendLine(string.Format("  {0}", pred.prediction.explanation));
            sb.AppendLine();
        }
    }

    // High Risk Tasks
    if (advisory.risk_analysis != null && advisory.risk_analysis.high_risk_tasks != null && advisory.risk_analysis.high_risk_tasks.Count > 0)
    {
        sb.AppendLine("═══ HIGH RISK TASKS ═══" + Environment.NewLine);
        foreach (var task in advisory.risk_analysis.high_risk_tasks)
        {
            sb.AppendLine(string.Format("⚠️  {0} (Risk Score: {1}/100)", task.task_name, task.risk_score));
            sb.AppendLine("  Risk Factors:");
            foreach (var factor in task.risk_factors)
            {
                sb.AppendLine(string.Format("    • {0}", factor));
            }
            sb.AppendLine();
        }
    }

    txtAdvisory.Text = sb.ToString();
}
```

## Testing

1. Build the solution
2. Run MS Project with the add-in
3. Open a project
4. Click "ML Advisory" button
5. Should see:
   - API call to backend
   - Custom fields updated with predictions
   - MLAdvisoryForm showing full advisory with recommendations

## Expected Result

Instead of seeing "ML Advisory feature is being configured..." message, you'll see:
- Complete analysis of all tasks
- Duration predictions for each task
- Risk scores and factors
- Timeline-wide recommendations
- All data written to custom fields in MS Project
