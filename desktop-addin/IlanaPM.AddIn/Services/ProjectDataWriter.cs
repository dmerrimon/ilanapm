using System;
using Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Services
{
    public class ProjectDataWriter
    {
        public void WriteValidationResults(Application projectApp, Models.ValidationResult validationResult)
        {
            if (projectApp.ActiveProject == null)
                throw new System.Exception("No active project found.");

            Project activeProject = projectApp.ActiveProject;

            // Update each task with its validation issues                                                                                                                                                          
            foreach (var issue in validationResult.issues)
            {
                if (!string.IsNullOrEmpty(issue.task_id))
                {
                    var task = FindTaskById(activeProject, issue.task_id);
                    if (task != null)
                    {
                        try
                        {
                            // Update Risk Score based on severity                                                                                                                                                  
                            int riskScore = GetRiskScoreFromSeverity(issue.severity);
                            SetTaskNumber(task, PjCustomField.pjCustomTaskNumber2, riskScore);

                            // Update Gating Status if regulatory issue                                                                                                                                             
                            if (issue.category == "regulatory")
                            {
                                SetTaskText(task, PjCustomField.pjCustomTaskText5, "Blocked");
                            }

                            // Add note with issue details                                                                                                                                                          
                            string note = string.Format("[{0}] {1}\r\n{2}\r\nSuggested Fix: {3}\r\n\r\n",
                                issue.severity.ToUpper(),
                                issue.message,
                                issue.detail,
                                issue.suggested_fix);

                            AppendTaskNote(task, note);

                            // Highlight high-risk tasks                                                                                                                                                            
                            if (riskScore >= 70)
                            {
                                task.Marked = true;
                            }
                        }
                        catch (System.Exception ex)
                        {
                            System.Diagnostics.Debug.WriteLine("Error updating task " + task.ID + ": " + ex.Message);
                        }
                    }
                }
            }
        }

        private Task FindTaskById(Project project, string taskId)
        {
            if (int.TryParse(taskId, out int id))
            {
                foreach (Task task in project.Tasks)
                {
                    if (task != null && task.ID == id)
                        return task;
                }
            }
            return null;
        }

        private void SetTaskText(Task task, PjCustomField field, string value)
        {
            try
            {
                // Convert PjCustomField to PjField                                                                                                                                                                 
                PjField pjField = ConvertCustomFieldToPjField(field);
                task.SetField(pjField, value);
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("Error setting text field: " + ex.Message);
            }
        }

        private void SetTaskNumber(Task task, PjCustomField field, int value)
        {
            try
            {
                // Convert PjCustomField to PjField                                                                                                                                                                 
                PjField pjField = ConvertCustomFieldToPjField(field);
                task.SetField(pjField, value.ToString());
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("Error setting number field: " + ex.Message);
            }
        }

        private PjField ConvertCustomFieldToPjField(PjCustomField customField)
        {
            // Map PjCustomField to PjField                                                                                                                                                                         
            switch (customField)
            {
                case PjCustomField.pjCustomTaskText1:
                    return PjField.pjTaskText1;
                case PjCustomField.pjCustomTaskText2:
                    return PjField.pjTaskText2;
                case PjCustomField.pjCustomTaskText3:
                    return PjField.pjTaskText3;
                case PjCustomField.pjCustomTaskText4:
                    return PjField.pjTaskText4;
                case PjCustomField.pjCustomTaskText5:
                    return PjField.pjTaskText5;
                case PjCustomField.pjCustomTaskText6:
                    return PjField.pjTaskText6;
                case PjCustomField.pjCustomTaskNumber1:
                    return PjField.pjTaskNumber1;
                case PjCustomField.pjCustomTaskNumber2:
                    return PjField.pjTaskNumber2;
                case PjCustomField.pjCustomTaskNumber3:
                    return PjField.pjTaskNumber3;
                case PjCustomField.pjCustomTaskFlag1:
                    return PjField.pjTaskFlag1;
                default:
                    return PjField.pjTaskText1; // Default fallback                                                                                                                                                 
            }
        }

        private void AppendTaskNote(Task task, string note)
        {
            try
            {
                string existingNotes = task.Notes ?? "";
                task.Notes = existingNotes + note;
            }
            catch (System.Exception ex)
            {
                System.Diagnostics.Debug.WriteLine("Error appending note: " + ex.Message);
            }
        }

        private int GetRiskScoreFromSeverity(string severity)
        {
            switch (severity.ToLower())
            {
                case "error":
                    return 90;
                case "warning":
                    return 60;
                case "info":
                    return 30;
                default:
                    return 50;
            }
        }

        // ADD WriteMLAdvisory HERE (INSIDE THE CLASS, BEFORE THE CLOSING BRACE)                                                                                                                                  
        public void WriteMLAdvisory(Microsoft.Office.Interop.MSProject.Application projectApp, string taskId, Models.DurationPrediction prediction, Models.RiskScore riskScore)
        {
            if (projectApp.ActiveProject == null)
                throw new System.Exception("No active project found.");

            Microsoft.Office.Interop.MSProject.Project activeProject = projectApp.ActiveProject;
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
                        SetTaskText(task, Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskText6, durationRange);
                        SetTaskNumber(task, Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskNumber3, (int)(prediction.confidence_score * 100));

                        string note = string.Format("ML Duration Prediction: {0}" + Environment.NewLine + Environment.NewLine, prediction.explanation);
                        AppendTaskNote(task, note);
                    }

                    // Write risk score                                                                                                                                                                           
                    if (riskScore != null)
                    {
                        SetTaskNumber(task, Microsoft.Office.Interop.MSProject.PjCustomField.pjCustomTaskNumber2, riskScore.risk_score);

                        string riskFactors = string.Join(Environment.NewLine + "- ", riskScore.risk_factors);
                        string note = string.Format("Risk Analysis [{0}]:" + Environment.NewLine + "- {1}" + Environment.NewLine + Environment.NewLine,
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

    } // <-- CLASS CLOSING BRACE - WriteMLAdvisory must be ABOVE this line                                                                                                                                        
} // <-- NAMESPACE CLOSING BRACE
