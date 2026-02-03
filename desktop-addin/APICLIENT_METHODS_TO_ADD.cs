// ============================================================================
// ADD THESE 4 METHODS TO Services/ApiClient.cs
// ============================================================================
// Add these after the existing ValidateTimelineAsync() method
// ============================================================================

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
