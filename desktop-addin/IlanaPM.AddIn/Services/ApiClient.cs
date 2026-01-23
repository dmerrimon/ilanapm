using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace IlanaPM.AddIn.Services
{
    public class ApiClient
    {
        private static readonly HttpClient httpClient = new HttpClient();
        private const string API_BASE_URL = "https://ilanapm.onrender.com";

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

        public async Task<Models.AutoFixResult> AutoFixTimelineAsync(Models.Timeline timeline)
        {
            string jsonContent = JsonConvert.SerializeObject(timeline);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/validate/autofix", content);
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.AutoFixResult>(responseBody);
        }

        public async Task<Models.CriticalPathResult> GetCriticalPathAsync(Models.Timeline timeline)
        {
            string jsonContent = JsonConvert.SerializeObject(timeline);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/analytics/critical-path", content);
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.CriticalPathResult>(responseBody);
        }

        public async Task<Models.BaselineComparisonResult> CompareToBaselineAsync(Models.Timeline current, Models.Timeline baseline)
        {
            var request = new Models.BaselineComparisonRequest { current = current, baseline = baseline };
            string jsonContent = JsonConvert.SerializeObject(request);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/analytics/baseline-comparison", content);
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.BaselineComparisonResult>(responseBody);
        }

        public async Task<Models.CountriesResponse> GetCountriesAsync()
        {
            HttpResponseMessage response = await httpClient.GetAsync(API_BASE_URL + "/api/v1/templates/countries");
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.CountriesResponse>(responseBody);
        }

        /// <summary>
        /// Get comprehensive country data for Multi-Country Calculator
        /// Returns detailed workflow information, complexity, authorities, and pathways
        /// </summary>
        public async Task<System.Collections.Generic.List<Models.CountrySummary>> GetCountriesDetailedAsync()
        {
            HttpResponseMessage response = await httpClient.GetAsync(API_BASE_URL + "/api/v1/config/countries");
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<System.Collections.Generic.List<Models.CountrySummary>>(responseBody);
        }

        public async Task<Models.Timeline> GenerateTemplateAsync(Models.TemplateRequest request)
        {
            string jsonContent = JsonConvert.SerializeObject(request);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/templates/generate", content);
            response.EnsureSuccessStatusCode();
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.Timeline>(responseBody);
        }
    }
}