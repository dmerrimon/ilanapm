// ============================================================================
// ADD THIS METHOD TO Services/ProjectDataWriter.cs
// ============================================================================
// Add this after the existing WriteValidationResults() method
// ============================================================================

public void WriteMLAdvisory(Application projectApp, string taskId, Models.DurationPrediction prediction, Models.RiskScore riskScore)
{
    if (projectApp.ActiveProject == null)
        throw new System.Exception("No active project found.");

    Project activeProject = projectApp.ActiveProject;
    var task = FindTaskById(activeProject, taskId);

    if (task != null)
    {
        try
        {
            // Write duration prediction
            if (prediction != null)
            {
                string durationRange = string.Format("{0}-{1} days",
                    prediction.confidence_interval.lower,
                    prediction.confidence_interval.upper);
                SetTaskText(task, PjCustomField.pjCustomTaskText6, durationRange);
                SetTaskNumber(task, PjCustomField.pjCustomTaskNumber3, (int)(prediction.confidence_score * 100));

                string note = string.Format("ML Duration Prediction: {0}\r\n\r\n", prediction.explanation);
                AppendTaskNote(task, note);
            }

            // Write risk score
            if (riskScore != null)
            {
                SetTaskNumber(task, PjCustomField.pjCustomTaskNumber2, riskScore.risk_score);

                string riskFactors = string.Join("\r\n- ", riskScore.risk_factors);
                string note = string.Format("Risk Analysis [{0}]:\r\n- {1}\r\n\r\n",
                    riskScore.risk_level.ToUpper(), riskFactors);
                AppendTaskNote(task, note);
            }
        }
        catch (System.Exception ex)
        {
            System.Diagnostics.Debug.WriteLine("Error writing ML advisory: " + ex.Message);
        }
    }
}
