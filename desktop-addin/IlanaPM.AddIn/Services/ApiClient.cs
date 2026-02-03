using System;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace IlanaPM.AddIn.Services
{
    public class ApiClient
    {
        private static readonly HttpClient httpClient;
        private const string API_BASE_URL = "https://ilanapm.onrender.com";

        /// <summary>
        /// Static constructor to configure TLS 1.2 for HTTPS connections
        /// Required for .NET Framework to connect to modern HTTPS endpoints
        /// </summary>
        static ApiClient()
        {
            // Enable TLS 1.2 (required for Render and most modern APIs)
            ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12 | SecurityProtocolType.Tls11 | SecurityProtocolType.Tls;

            // Initialize HttpClient with timeout
            httpClient = new HttpClient();
            httpClient.Timeout = TimeSpan.FromSeconds(30);

            System.Diagnostics.Debug.WriteLine("ApiClient initialized with TLS 1.2 support");
        }

        /// <summary>
        /// Add Authorization header with JWT token to HTTP client
        /// Called before each authenticated API request
        /// </summary>
        private void AddAuthorizationHeader()
        {
            string token = SecureStorage.ReadToken();
            if (!string.IsNullOrEmpty(token))
            {
                httpClient.DefaultRequestHeaders.Authorization =
                    new AuthenticationHeaderValue("Bearer", token);
                System.Diagnostics.Debug.WriteLine("Authorization header added");
            }
            else
            {
                // Clear authorization header if no token
                httpClient.DefaultRequestHeaders.Authorization = null;
                System.Diagnostics.Debug.WriteLine("No token found - Authorization header not set");
            }
        }

        /// <summary>
        /// Handle HTTP response and throw appropriate exceptions
        /// </summary>
        private async Task HandleResponseAsync(HttpResponseMessage response)
        {
            if (response.StatusCode == System.Net.HttpStatusCode.Unauthorized)
            {
                System.Diagnostics.Debug.WriteLine("401 Unauthorized - Token expired or invalid");
                // Clear invalid token
                SecureStorage.ClearToken();
                throw new Models.UnauthorizedException(
                    "Your license has expired or is invalid. Please activate your license in Settings."
                );
            }

            if (!response.IsSuccessStatusCode)
            {
                string errorBody = await response.Content.ReadAsStringAsync();
                System.Diagnostics.Debug.WriteLine($"API Error {response.StatusCode}: {errorBody}");

                // Try to parse error message from JSON
                try
                {
                    var errorObj = JsonConvert.DeserializeObject<dynamic>(errorBody);
                    string detail = errorObj?.detail?.ToString();
                    if (!string.IsNullOrEmpty(detail))
                    {
                        throw new Models.LicenseException(detail);
                    }
                }
                catch (JsonException)
                {
                    // Not JSON, use raw error body
                }

                throw new HttpRequestException(
                    $"API request failed: {response.StatusCode} - {errorBody}"
                );
            }
        }

        // ===================================================================
        // LICENSING ENDPOINTS
        // ===================================================================

        /// <summary>
        /// Activate a license key and receive JWT token
        /// No authorization header needed (this is the activation endpoint)
        /// </summary>
        public async Task<Models.ActivationResponse> ActivateLicenseAsync(Models.ActivationRequest request)
        {
            try
            {
                string jsonContent = JsonConvert.SerializeObject(request);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                HttpResponseMessage response = await httpClient.PostAsync(
                    API_BASE_URL + "/api/v1/licensing/activate",
                    content
                );

                await HandleResponseAsync(response);

                string responseBody = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<Models.ActivationResponse>(responseBody);
            }
            catch (Models.LicenseException)
            {
                throw; // Re-throw license exceptions as-is
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Activation error: {ex.Message}");
                throw new Models.LicenseException("Failed to activate license. Please check your internet connection and try again.", ex);
            }
        }

        /// <summary>
        /// Get license information for current user
        /// Requires valid JWT token
        /// </summary>
        public async Task<Models.LicenseInfo> GetLicenseInfoAsync()
        {
            try
            {
                AddAuthorizationHeader();

                HttpResponseMessage response = await httpClient.GetAsync(
                    API_BASE_URL + "/api/v1/licensing/info"
                );

                await HandleResponseAsync(response);

                string responseBody = await response.Content.ReadAsStringAsync();
                return JsonConvert.DeserializeObject<Models.LicenseInfo>(responseBody);
            }
            catch (Models.UnauthorizedException)
            {
                throw; // Re-throw unauthorized exceptions
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Get license info error: {ex.Message}");
                throw new Models.LicenseException("Failed to retrieve license information.", ex);
            }
        }

        /// <summary>
        /// Get Stripe billing portal URL for self-service subscription management
        /// Works for both Professional and Enterprise tiers
        /// </summary>
        public async Task<string> GetBillingPortalUrlAsync()
        {
            try
            {
                AddAuthorizationHeader();

                HttpResponseMessage response = await httpClient.GetAsync(
                    API_BASE_URL + "/api/v1/billing/portal-url"
                );

                await HandleResponseAsync(response);

                string responseBody = await response.Content.ReadAsStringAsync();
                var portalResponse = JsonConvert.DeserializeObject<Models.BillingPortalResponse>(responseBody);
                return portalResponse.portal_url;
            }
            catch (Models.UnauthorizedException)
            {
                throw;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Get billing portal URL error: {ex.Message}");
                throw new Models.LicenseException("Failed to generate billing portal link.", ex);
            }
        }

        // ===================================================================
        // VALIDATION & ANALYTICS ENDPOINTS (AUTHENTICATED)
        // ===================================================================

        public async Task<Models.ValidationResult> ValidateTimelineAsync(Models.Timeline timeline)
        {
            AddAuthorizationHeader(); // Add JWT token
            string jsonContent = JsonConvert.SerializeObject(timeline);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/validate", content);
            await HandleResponseAsync(response); // Handle 401 and other errors
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.ValidationResult>(responseBody);
        }

        public async Task<Models.TimelineAdvisory> GetTimelineAdvisoryAsync(Models.Timeline timeline)
        {
            AddAuthorizationHeader();
            string jsonContent = JsonConvert.SerializeObject(timeline);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/advisory/timeline", content);
            await HandleResponseAsync(response);
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.TimelineAdvisory>(responseBody);
        }

        public async Task<Models.DurationPrediction> GetDurationPredictionAsync(Models.Task task)
        {
            AddAuthorizationHeader();
            string jsonContent = JsonConvert.SerializeObject(task);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/advisory/duration", content);
            await HandleResponseAsync(response);
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.DurationPrediction>(responseBody);
        }

        public async Task<Models.RiskScore> GetRiskScoreAsync(Models.Task task)
        {
            AddAuthorizationHeader();
            string jsonContent = JsonConvert.SerializeObject(task);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/advisory/risk", content);
            await HandleResponseAsync(response);
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.RiskScore>(responseBody);
        }

        public async Task<bool> SendTeamsNotificationAsync(Models.TeamsNotificationRequest notification)
        {
            AddAuthorizationHeader();
            string jsonContent = JsonConvert.SerializeObject(notification);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/teams/notify", content);
            await HandleResponseAsync(response);
            return response.IsSuccessStatusCode;
        }

        public async Task<Models.AutoFixResult> AutoFixTimelineAsync(Models.Timeline timeline)
        {
            AddAuthorizationHeader();
            string jsonContent = JsonConvert.SerializeObject(timeline);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/validate/autofix", content);
            await HandleResponseAsync(response);
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.AutoFixResult>(responseBody);
        }

        public async Task<Models.CriticalPathResult> GetCriticalPathAsync(Models.Timeline timeline)
        {
            AddAuthorizationHeader();
            string jsonContent = JsonConvert.SerializeObject(timeline);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/analytics/critical-path", content);
            await HandleResponseAsync(response);
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.CriticalPathResult>(responseBody);
        }

        public async Task<Models.BaselineComparisonResult> CompareToBaselineAsync(Models.Timeline current, Models.Timeline baseline)
        {
            AddAuthorizationHeader();
            var request = new Models.BaselineComparisonRequest { current = current, baseline = baseline };
            string jsonContent = JsonConvert.SerializeObject(request);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/analytics/baseline-comparison", content);
            await HandleResponseAsync(response);
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.BaselineComparisonResult>(responseBody);
        }

        public async Task<System.Collections.Generic.List<Models.CountrySummary>> GetCountriesAsync()
        {
            AddAuthorizationHeader();
            HttpResponseMessage response = await httpClient.GetAsync(API_BASE_URL + "/api/v1/templates/countries");
            await HandleResponseAsync(response);
            string responseBody = await response.Content.ReadAsStringAsync();
            var countriesResponse = JsonConvert.DeserializeObject<Models.CountriesResponse>(responseBody);
            return countriesResponse.countries;
        }

        /// <summary>
        /// Get comprehensive country data for Multi-Country Calculator
        /// Returns detailed workflow information, complexity, authorities, and pathways
        /// </summary>
        public async Task<System.Collections.Generic.List<Models.CountrySummary>> GetCountriesDetailedAsync()
        {
            AddAuthorizationHeader();
            HttpResponseMessage response = await httpClient.GetAsync(API_BASE_URL + "/api/v1/config/countries");
            await HandleResponseAsync(response);
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<System.Collections.Generic.List<Models.CountrySummary>>(responseBody);
        }

        public async Task<Models.Timeline> GenerateTemplateAsync(Models.TemplateRequest request)
        {
            AddAuthorizationHeader();
            string jsonContent = JsonConvert.SerializeObject(request);
            var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");
            HttpResponseMessage response = await httpClient.PostAsync(API_BASE_URL + "/api/v1/templates/generate", content);
            await HandleResponseAsync(response);
            string responseBody = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<Models.Timeline>(responseBody);
        }

        /// <summary>
        /// Send telemetry batch to backend for ML learning
        /// Privacy-focused: User IDs are hashed, no PII collected
        /// </summary>
        public async Task SendTelemetryBatchAsync(Models.TelemetryBatch batch)
        {
            try
            {
                AddAuthorizationHeader();
                string jsonContent = JsonConvert.SerializeObject(batch);
                var content = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                HttpResponseMessage response = await httpClient.PostAsync(
                    API_BASE_URL + "/api/v1/telemetry/batch",
                    content
                );

                // Don't throw on telemetry errors - fail silently
                if (!response.IsSuccessStatusCode)
                {
                    string errorBody = await response.Content.ReadAsStringAsync();
                    System.Diagnostics.Debug.WriteLine($"Telemetry API Error {response.StatusCode}: {errorBody}");
                    // Don't throw - telemetry should never break user experience
                    return;
                }

                System.Diagnostics.Debug.WriteLine($"Telemetry batch sent successfully: {batch.events.Count} events");
            }
            catch (Exception ex)
            {
                // Fail silently - telemetry errors should not impact user
                System.Diagnostics.Debug.WriteLine($"Telemetry send error: {ex.Message}");
            }
        }
    }
}