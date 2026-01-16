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
    }
}