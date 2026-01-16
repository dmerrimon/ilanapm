using System;
using Microsoft.Office.Interop.MSProject;

namespace IlanaPM.AddIn.Services
{
    public class ViewManager
    {
        public void CreateValidationSummaryView(Application app)
        {
            try
            {
                Project project = app.ActiveProject;
                if (project == null)
                {
                    throw new Exception("No active project found.");
                }

                // Create or get view
                View view = GetOrCreateView(app, "Seleen Validation Summary");

                // Apply table with custom fields
                var table = GetOrCreateTable(app, "Seleen_Validation");
                table.TableFields.Add(app.FieldNameToFieldConstant("Name", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Task Category", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Risk Score", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Gating Status", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Is Mandatory", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Duration", PjField.pjTaskField));

                view.Table = "Seleen_Validation";
                app.ViewApply("Seleen Validation Summary");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error creating validation view: {ex.Message}");
                throw;
            }
        }

        public void CreateRiskDashboardView(Application app)
        {
            try
            {
                Project project = app.ActiveProject;
                if (project == null)
                {
                    throw new Exception("No active project found.");
                }

                View view = GetOrCreateView(app, "Seleen Risk Dashboard");

                var table = GetOrCreateTable(app, "Seleen_Risk");
                table.TableFields.Add(app.FieldNameToFieldConstant("Name", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Risk Score", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("ML Predicted Duration", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("ML Confidence %", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Task Category", PjField.pjTaskField));

                view.Table = "Seleen_Risk";

                // Apply filter for high-risk tasks only
                var filter = GetOrCreateFilter(app, "Seleen_HighRisk");
                filter.ShowInMenu = false;

                app.ViewApply("Seleen Risk Dashboard");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error creating risk view: {ex.Message}");
                throw;
            }
        }

        public void CreateExecutiveSummaryView(Application app)
        {
            try
            {
                Project project = app.ActiveProject;
                if (project == null)
                {
                    throw new Exception("No active project found.");
                }

                View view = GetOrCreateView(app, "Seleen Executive Summary");

                var table = GetOrCreateTable(app, "Seleen_Executive");
                table.TableFields.Add(app.FieldNameToFieldConstant("Name", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Start", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Finish", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Task Category", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Gating Status", PjField.pjTaskField));

                view.Table = "Seleen_Executive";

                // Show only mandatory/milestone tasks
                var filter = GetOrCreateFilter(app, "Seleen_MandatoryOnly");

                app.ViewApply("Seleen Executive Summary");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error creating executive view: {ex.Message}");
                throw;
            }
        }

        public void CreateChecklistCompletionView(Application app)
        {
            try
            {
                Project project = app.ActiveProject;
                if (project == null)
                {
                    throw new Exception("No active project found.");
                }

                View view = GetOrCreateView(app, "Seleen Checklist Completion");

                var table = GetOrCreateTable(app, "Seleen_Checklist");
                table.TableFields.Add(app.FieldNameToFieldConstant("Name", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Checklist Completion %", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("Task Category", PjField.pjTaskField));
                table.TableFields.Add(app.FieldNameToFieldConstant("% Complete", PjField.pjTaskField));

                view.Table = "Seleen_Checklist";
                app.ViewApply("Seleen Checklist Completion");
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error creating checklist view: {ex.Message}");
                throw;
            }
        }

        private View GetOrCreateView(Application app, string viewName)
        {
            try
            {
                return app.ActiveProject.Views[viewName];
            }
            catch
            {
                return app.ActiveProject.Views.Add(viewName, PjViewType.pjViewGantt, false);
            }
        }

        private Table GetOrCreateTable(Application app, string tableName)
        {
            try
            {
                return app.ActiveProject.Tables[tableName];
            }
            catch
            {
                return app.ActiveProject.Tables.Add(tableName);
            }
        }

        private Filter GetOrCreateFilter(Application app, string filterName)
        {
            try
            {
                return app.ActiveProject.Filters[filterName];
            }
            catch
            {
                return app.ActiveProject.Filters.Add(filterName);
            }
        }
    }
}
