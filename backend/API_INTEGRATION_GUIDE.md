# Seleen Intelligence API - Integration Guide

**Version:** 1.0
**Last Updated:** 2026-02-13

This guide provides comprehensive examples for integrating with the Seleen Intelligence API.

---

## Table of Contents

1. [Authentication](#authentication)
2. [Base URL](#base-url)
3. [API Endpoints Overview](#api-endpoints-overview)
4. [Integration Examples](#integration-examples)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Webhooks](#webhooks)
8. [SDKs](#sdks)

---

## Authentication

All API requests require authentication using an API key or JWT token.

**API Key Header:**
```
Authorization: Bearer YOUR_API_KEY
```

**Example:**
```bash
curl -H "Authorization: Bearer sk_live_abc123xyz" \
     https://api.seleen.io/v1/dashboard/leadership?org_id=org_123
```

---

## Base URL

**Production:** `https://api.seleen.io/v1`
**Staging:** `https://api-staging.seleen.io/v1`
**Local Development:** `http://localhost:8000/v1`

---

## API Endpoints Overview

### Dashboard Endpoints
- `GET /dashboard/leadership` - Get Leadership Dashboard
- `GET /dashboard/study/{project_id}` - Get study detail
- `POST /dashboard/refresh` - Refresh health snapshots
- `GET /dashboard/portfolio/summary` - Get portfolio summary
- `GET /dashboard/portfolio/health` - Get comprehensive portfolio health
- `GET /dashboard/portfolio/patterns` - Get cross-study patterns
- `GET /dashboard/portfolio/systemic-issues` - Get systemic issues
- `POST /dashboard/portfolio/refresh` - Refresh portfolio intelligence

### Escalation Endpoints
- `POST /escalations/{escalation_id}/acknowledge` - Acknowledge escalation
- `POST /escalations/{escalation_id}/resolve` - Resolve escalation

### Account Management Endpoints
- `GET /account/trackers/available` - List available trackers
- `POST /account/trackers/upload-sample` - Upload sample tracker
- `POST /account/trackers/save-mapping` - Save column mappings
- `GET /account/trackers/{tracker_type}/mapping` - Get column mappings
- `GET /account/trackers/{tracker_type}/template` - Download template
- `GET /account/organization` - Get org settings

### Notification Endpoints
- `GET /notifications` - List user notifications
- `GET /notifications/{notification_id}` - Get notification details
- `POST /notifications/{notification_id}/mark-read` - Mark as read
- `POST /notifications/mark-all-read` - Mark all as read
- `GET /notifications/preferences` - Get notification preferences
- `POST /notifications/preferences` - Update notification preferences
- `GET /notifications/stats` - Get notification statistics

---

## Integration Examples

### 1. Python Integration

#### Get Leadership Dashboard

```python
import requests

API_KEY = "sk_live_abc123xyz"
BASE_URL = "https://api.seleen.io/v1"

def get_leadership_dashboard(org_id: str):
    """Get Leadership Dashboard for organization"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    params = {
        "org_id": org_id,
        "status_filter": "warning,critical",  # Optional filter
        "sort_by": "health_score_asc",
        "use_cache": True
    }

    response = requests.get(
        f"{BASE_URL}/dashboard/leadership",
        headers=headers,
        params=params
    )

    response.raise_for_status()
    return response.json()


# Usage
dashboard = get_leadership_dashboard("org_123")

print(f"Total Studies: {dashboard['total_studies']}")
print(f"Critical Count: {dashboard['critical_count']}")
print(f"Total Escalations: {dashboard['total_active_escalations']}")

for study in dashboard['studies']:
    print(f"\n{study['project_name']}")
    print(f"  Health Score: {study['health_score']}")
    print(f"  Status: {study['health_status']}")
    print(f"  Escalations: {study['director_escalations_count']} Director, {study['vp_escalations_count']} VP")
```

#### Upload Tracker (via API)

```python
def upload_tracker(org_id: str, project_id: str, tracker_type: str, file_path: str):
    """Upload tracker file for processing"""
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    params = {
        "org_id": org_id,
        "project_id": project_id,
        "tracker_type": tracker_type
    }

    files = {
        "file": open(file_path, "rb")
    }

    response = requests.post(
        f"{BASE_URL}/trackers/upload",
        headers=headers,
        params=params,
        files=files
    )

    response.raise_for_status()
    return response.json()


# Usage
result = upload_tracker(
    org_id="org_123",
    project_id="STUDY-001",
    tracker_type="risk_log",
    file_path="/path/to/Risk_Log_Jan2026.xlsx"
)

print(f"Rows Processed: {result['rows_processed']}")
print(f"Signals Extracted: {result['signals_extracted']}")
print(f"Escalations Detected: {result['escalations_detected']}")
print(f"Study Health: {result['health_score']} ({result['health_status']})")
```

#### Get Portfolio Health

```python
def get_portfolio_health(org_id: str):
    """Get comprehensive portfolio health analysis"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    params = {
        "org_id": org_id,
        "timeframe_days": 30
    }

    response = requests.get(
        f"{BASE_URL}/dashboard/portfolio/health",
        headers=headers,
        params=params
    )

    response.raise_for_status()
    return response.json()


# Usage
portfolio = get_portfolio_health("org_123")

print(f"Total Studies: {portfolio['total_studies']}")
print(f"Average Health Score: {portfolio['average_health_score']}")
print(f"Health Distribution:")
print(f"  Healthy: {portfolio['healthy_count']}")
print(f"  Warning: {portfolio['warning_count']}")
print(f"  Critical: {portfolio['critical_count']}")
print(f"\nTrends:")
print(f"  Improving: {portfolio['improving_count']}")
print(f"  Declining: {portfolio['declining_count']}")
print(f"  Stable: {portfolio['stable_count']}")
print(f"\nFinancial Impact:")
print(f"  Total Delay Days: {portfolio['estimated_total_delay_days']}")
print(f"  Cost Impact: ${portfolio['estimated_total_cost_impact']:,.0f}")

if portfolio['studies_needing_immediate_attention']:
    print(f"\n⚠️  IMMEDIATE ATTENTION NEEDED:")
    for study_id in portfolio['studies_needing_immediate_attention']:
        print(f"    - {study_id}")
```

#### Detect Cross-Study Patterns

```python
def get_cross_study_patterns(org_id: str, severity: str = None):
    """Get cross-study patterns"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    params = {"org_id": org_id}
    if severity:
        params["severity"] = severity

    response = requests.get(
        f"{BASE_URL}/dashboard/portfolio/patterns",
        headers=headers,
        params=params
    )

    response.raise_for_status()
    return response.json()


# Usage
patterns = get_cross_study_patterns("org_123", severity="high")

print(f"Total Patterns: {patterns['total_patterns']}")
print(f"Critical Patterns: {patterns['critical_patterns']}")
print(f"High Patterns: {patterns['high_patterns']}")

for pattern in patterns['patterns']:
    print(f"\n{pattern['pattern_name']} ({pattern['severity'].upper()})")
    print(f"  Type: {pattern['pattern_type']}")
    print(f"  Affected Studies: {', '.join(pattern['affected_studies'])}")
    print(f"  Confidence: {pattern['confidence_score']:.0%}")
    print(f"  Impact: {pattern['portfolio_impact']}")
    print(f"  Action: {pattern['recommended_action']}")
```

---

### 2. JavaScript/TypeScript Integration

```typescript
// api-client.ts
import axios, { AxiosInstance } from 'axios';

class SeleeenAPIClient {
  private client: AxiosInstance;

  constructor(apiKey: string, baseURL: string = 'https://api.seleen.io/v1') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
  }

  async getLeadershipDashboard(orgId: string, options?: {
    statusFilter?: string;
    sortBy?: string;
    useCache?: boolean;
  }) {
    const response = await this.client.get('/dashboard/leadership', {
      params: {
        org_id: orgId,
        status_filter: options?.statusFilter,
        sort_by: options?.sortBy || 'health_score_asc',
        use_cache: options?.useCache !== false
      }
    });
    return response.data;
  }

  async getStudyDetail(projectId: string, orgId: string) {
    const response = await this.client.get(`/dashboard/study/${projectId}`, {
      params: { org_id: orgId }
    });
    return response.data;
  }

  async getPortfolioHealth(orgId: string, timeframeDays: number = 30) {
    const response = await this.client.get('/dashboard/portfolio/health', {
      params: {
        org_id: orgId,
        timeframe_days: timeframeDays
      }
    });
    return response.data;
  }

  async acknowledgeEscalation(escalationId: string, acknowledgedBy: string) {
    const response = await this.client.post(
      `/escalations/${escalationId}/acknowledge`,
      null,
      { params: { acknowledged_by: acknowledgedBy } }
    );
    return response.data;
  }

  async resolveEscalation(
    escalationId: string,
    resolutionNotes: string,
    interventionTaken?: string
  ) {
    const response = await this.client.post(
      `/escalations/${escalationId}/resolve`,
      null,
      {
        params: {
          resolution_notes: resolutionNotes,
          intervention_taken: interventionTaken
        }
      }
    );
    return response.data;
  }

  async refreshPortfolioIntelligence(orgId: string) {
    const response = await this.client.post('/dashboard/portfolio/refresh', null, {
      params: { org_id: orgId }
    });
    return response.data;
  }
}

// Usage
const client = new SeleeenAPIClient('sk_live_abc123xyz');

// Get dashboard
const dashboard = await client.getLeadershipDashboard('org_123', {
  statusFilter: 'warning,critical',
  sortBy: 'health_score_asc'
});

console.log(`Total Studies: ${dashboard.total_studies}`);
console.log(`Critical Count: ${dashboard.critical_count}`);

// Acknowledge escalation
await client.acknowledgeEscalation('esc_123', 'user_456');

// Get portfolio health
const portfolio = await client.getPortfolioHealth('org_123');
console.log(`Average Health Score: ${portfolio.average_health_score}`);
```

---

### 3. C# Integration (for MS Project Add-in)

```csharp
using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class SeleeenAPIClient
{
    private readonly HttpClient _httpClient;
    private readonly string _apiKey;
    private readonly string _baseUrl;

    public SeleeenAPIClient(string apiKey, string baseUrl = "https://api.seleen.io/v1")
    {
        _apiKey = apiKey;
        _baseUrl = baseUrl;
        _httpClient = new HttpClient
        {
            BaseAddress = new Uri(baseUrl)
        };
        _httpClient.DefaultRequestHeaders.Authorization =
            new AuthenticationHeaderValue("Bearer", apiKey);
    }

    public async Task<LeadershipDashboard> GetLeadershipDashboard(
        string orgId,
        string statusFilter = null,
        string sortBy = "health_score_asc"
    )
    {
        var query = $"?org_id={orgId}&sort_by={sortBy}";
        if (!string.IsNullOrEmpty(statusFilter))
        {
            query += $"&status_filter={statusFilter}";
        }

        var response = await _httpClient.GetAsync($"/dashboard/leadership{query}");
        response.EnsureSuccessStatusCode();

        var json = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<LeadershipDashboard>(json);
    }

    public async Task<TrackerUploadResult> UploadTracker(
        string orgId,
        string projectId,
        string trackerType,
        byte[] fileBytes,
        string fileName
    )
    {
        using (var content = new MultipartFormDataContent())
        {
            var fileContent = new ByteArrayContent(fileBytes);
            fileContent.Headers.ContentType = MediaTypeHeaderValue.Parse("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
            content.Add(fileContent, "file", fileName);

            var response = await _httpClient.PostAsync(
                $"/trackers/upload?org_id={orgId}&project_id={projectId}&tracker_type={trackerType}",
                content
            );

            response.EnsureSuccessStatusCode();

            var json = await response.Content.ReadAsStringAsync();
            return JsonConvert.DeserializeObject<TrackerUploadResult>(json);
        }
    }

    public async Task<PortfolioHealth> GetPortfolioHealth(string orgId, int timeframeDays = 30)
    {
        var response = await _httpClient.GetAsync(
            $"/dashboard/portfolio/health?org_id={orgId}&timeframe_days={timeframeDays}"
        );

        response.EnsureSuccessStatusCode();

        var json = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<PortfolioHealth>(json);
    }
}

// Usage in MS Project Add-in
var client = new SeleeenAPIClient("sk_live_abc123xyz");

// Upload tracker from MS Project
var fileBytes = File.ReadAllBytes(@"C:\Users\Jane\Risk_Log.xlsx");
var result = await client.UploadTracker(
    orgId: "org_123",
    projectId: "STUDY-001",
    trackerType: "risk_log",
    fileBytes: fileBytes,
    fileName: "Risk_Log.xlsx"
);

MessageBox.Show(
    $"✅ {result.RowsProcessed} rows processed\n" +
    $"⚠️ {result.EscalationsDetected} escalations detected\n" +
    $"🎯 Study health: {result.HealthScore} ({result.HealthStatus})"
);
```

---

### 4. REST API Examples (curl)

#### Get Leadership Dashboard
```bash
curl -X GET "https://api.seleen.io/v1/dashboard/leadership?org_id=org_123&status_filter=warning,critical" \
  -H "Authorization: Bearer sk_live_abc123xyz" \
  -H "Content-Type: application/json"
```

#### Get Portfolio Health
```bash
curl -X GET "https://api.seleen.io/v1/dashboard/portfolio/health?org_id=org_123&timeframe_days=30" \
  -H "Authorization: Bearer sk_live_abc123xyz"
```

#### Acknowledge Escalation
```bash
curl -X POST "https://api.seleen.io/v1/escalations/esc_123/acknowledge?acknowledged_by=user_456" \
  -H "Authorization: Bearer sk_live_abc123xyz"
```

#### Refresh Portfolio Intelligence
```bash
curl -X POST "https://api.seleen.io/v1/dashboard/portfolio/refresh?org_id=org_123" \
  -H "Authorization: Bearer sk_live_abc123xyz"
```

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400
}
```

### HTTP Status Codes

- **200 OK** - Success
- **201 Created** - Resource created
- **400 Bad Request** - Invalid parameters
- **401 Unauthorized** - Invalid or missing API key
- **403 Forbidden** - Insufficient permissions
- **404 Not Found** - Resource not found
- **429 Too Many Requests** - Rate limit exceeded
- **500 Internal Server Error** - Server error

### Error Handling Example (Python)

```python
import requests
from requests.exceptions import HTTPError

try:
    response = requests.get(
        f"{BASE_URL}/dashboard/leadership",
        headers={"Authorization": f"Bearer {API_KEY}"},
        params={"org_id": "org_123"}
    )
    response.raise_for_status()
    dashboard = response.json()

except HTTPError as e:
    if e.response.status_code == 401:
        print("Invalid API key")
    elif e.response.status_code == 404:
        print("Organization not found")
    elif e.response.status_code == 429:
        print("Rate limit exceeded, retry after delay")
    else:
        print(f"HTTP error: {e.response.status_code}")
        print(f"Details: {e.response.json().get('detail')}")

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

---

## Rate Limiting

**Rate Limits:**
- **100 requests per minute** per API key
- **10,000 requests per day** per API key

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1613520000
```

**Handling Rate Limits:**

```python
import time

def make_api_request_with_retry(url, headers, params, max_retries=3):
    """Make API request with automatic retry on rate limit"""
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 429:
            # Rate limited, wait and retry
            retry_after = int(response.headers.get('Retry-After', 60))
            print(f"Rate limited, waiting {retry_after} seconds...")
            time.sleep(retry_after)
            continue

        response.raise_for_status()
        return response.json()

    raise Exception("Max retries exceeded")
```

---

## Webhooks

Seleen can send webhooks for real-time notifications of events.

### Supported Events

- `escalation.created` - New escalation created
- `escalation.acknowledged` - Escalation acknowledged
- `escalation.resolved` - Escalation resolved
- `health.critical` - Study health becomes critical
- `pattern.detected` - Cross-study pattern detected
- `systemic_issue.detected` - Systemic issue detected

### Webhook Payload

```json
{
  "event": "escalation.created",
  "timestamp": "2026-02-13T10:30:00Z",
  "org_id": "org_123",
  "data": {
    "escalation_id": "esc_123",
    "project_id": "STUDY-001",
    "escalation_level": "director",
    "priority": 7,
    "escalation_reason": "High priority risk detected"
  }
}
```

### Webhook Verification

Webhooks include an `X-Seleen-Signature` header for verification:

```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, webhook_secret: str) -> bool:
    """Verify webhook signature"""
    expected_signature = hmac.new(
        webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)
```

---

## SDKs

### Official SDKs

- **Python SDK:** `pip install seleen-python`
- **JavaScript/TypeScript SDK:** `npm install @seleen/sdk`
- **C# SDK:** `Install-Package Seleen.SDK`

### Python SDK Example

```python
from seleen import SeleeenClient

client = SeleeenClient(api_key="sk_live_abc123xyz")

# Get dashboard
dashboard = client.dashboard.get_leadership(org_id="org_123")

# Get portfolio health
portfolio = client.portfolio.get_health(org_id="org_123")

# Upload tracker
result = client.trackers.upload(
    org_id="org_123",
    project_id="STUDY-001",
    tracker_type="risk_log",
    file_path="/path/to/Risk_Log.xlsx"
)
```

---

## Support

**Documentation:** https://docs.seleen.io
**API Reference:** https://api.seleen.io/docs
**Support Email:** api-support@seleen.io
**Community:** https://community.seleen.io

---

**End of API Integration Guide**
