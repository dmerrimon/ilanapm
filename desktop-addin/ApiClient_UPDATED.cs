using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace IlanaPM.AddIn.Services
{
    public class ApiClient
    {
        private static readonly HttpClient httpClient = new HttpClient();
        private const string API_BASE_URL = "https://ilanapm.azurewebsites.net";

        public async Task<Models.ValidationResult> ValidateTimelineAsync(Models.Timeline timeline)
        {
            string jsonContent = JsonConvert.SerializeObject(timeline);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL +
"/api/v1/validate", content);
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            Models.ValidationResult result =
JsonConvert.DeserializeObject<Models.ValidationResult>(responseBody);
            return result;
        }

        public async Task<Models.TimelineAdvisory> GetTimelineAdvisoryAsync(Models.Timeline timeline)
        {
            string jsonContent = JsonConvert.SerializeObject(timeline);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/advisory/timeline", content);
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.TimelineAdvisory>(responseBody);
        }

        public async Task<Models.DurationPrediction> GetDurationPredictionAsync(Models.Task task)
        {
            string jsonContent = JsonConvert.SerializeObject(task);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/advisory/duration", content);
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.DurationPrediction>(responseBody);
        }

        public async Task<Models.RiskScore> GetRiskScoreAsync(Models.Task task)
        {
            string jsonContent = JsonConvert.SerializeObject(task);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/advisory/risk", content);
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.RiskScore>(responseBody);
        }

        public async Task<bool> SendTeamsNotificationAsync(Models.TeamsNotificationRequest notification)
        {
            string jsonContent = JsonConvert.SerializeObject(notification);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/teams/notify", content);
            return response.IsSuccessStatusCode;
        }

        // ============================================================================
        // NEW METHODS FOR FEEDBACK, AUTO-FIX, AND CRITICAL PATH (Phase 2)
        // ============================================================================

        /// <summary>
        /// Submit task completion feedback to backend for ML learning
        /// Endpoint: POST /api/v1/feedback/task-completion
        /// </summary>
        /// <param name="feedback">Feedback data with predicted and actual durations</param>
        /// <returns>Response indicating if feedback was recorded successfully</returns>
        public async Task<Models.TaskFeedbackResponse> SubmitTaskFeedbackAsync(Models.TaskFeedback feedback)
        {
            try
            {
                // Serialize feedback object to JSON
                string jsonContent = JsonConvert.SerializeObject(feedback);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                // POST to backend
                HttpResponseMessage response = await httpClient.PostAsync(
                    API_BASE_URL + "/api/v1/feedback/task-completion",
                    content
                );

                // Check for HTTP errors
                response.EnsureSuccessStatusCode();

                // Parse response
                string responseBody = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<Models.TaskFeedbackResponse>(responseBody);
            }
            catch (HttpRequestException ex)
            {
                throw new Exception($"Failed to submit feedback: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Submit bulk task completion feedback
        /// Endpoint: POST /api/v1/feedback/task-completions
        /// </summary>
        /// <param name="feedbackList">List of feedback items to submit in batch</param>
        /// <returns>Response with count of recorded feedback items</returns>
        public async Task<Models.TaskFeedbackResponse> SubmitBulkFeedbackAsync(List<Models.TaskFeedback> feedbackList)
        {
            try
            {
                // Serialize list of feedback objects to JSON array
                string jsonContent = JsonConvert.SerializeObject(feedbackList);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                // POST to bulk endpoint
                HttpResponseMessage response = await httpClient.PostAsync(
                    API_BASE_URL + "/api/v1/feedback/task-completions",
                    content
                );

                response.EnsureSuccessStatusCode();

                string responseBody = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<Models.TaskFeedbackResponse>(responseBody);
            }
            catch (HttpRequestException ex)
            {
                throw new Exception($"Failed to submit bulk feedback: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Auto-fix timeline validation errors
        /// Endpoint: POST /api/v1/validate/autofix
        /// Fixes: self-dependencies, invalid references, duration bounds, invalid percentages
        /// </summary>
        /// <param name="timeline">Current timeline with validation errors</param>
        /// <returns>Result with list of fixes applied and corrected timeline</returns>
        public async Task<Models.AutoFixResult> AutoFixTimelineAsync(Models.Timeline timeline)
        {
            try
            {
                string jsonContent = JsonConvert.SerializeObject(timeline);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                HttpResponseMessage response = await httpClient.PostAsync(
                    API_BASE_URL + "/api/v1/validate/autofix",
                    content
                );

                response.EnsureSuccessStatusCode();

                string responseBody = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<Models.AutoFixResult>(responseBody);
            }
            catch (HttpRequestException ex)
            {
                throw new Exception($"Failed to auto-fix timeline: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Get critical path for timeline using CPM algorithm
        /// Endpoint: POST /api/v1/analytics/critical-path
        /// </summary>
        /// <param name="timeline">Timeline with tasks and dependencies</param>
        /// <returns>Critical path result with task IDs, durations, and slack calculations</returns>
        public async Task<Models.CriticalPathResult> GetCriticalPathAsync(Models.Timeline timeline)
        {
            try
            {
                string jsonContent = JsonConvert.SerializeObject(timeline);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                HttpResponseMessage response = await httpClient.PostAsync(
                    API_BASE_URL + "/api/v1/analytics/critical-path",
                    content
                );

                response.EnsureSuccessStatusCode();

                string responseBody = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<Models.CriticalPathResult>(responseBody);
            }
            catch (HttpRequestException ex)
            {
                throw new Exception($"Failed to get critical path: {ex.Message}", ex);
            }
        }
    }
}
