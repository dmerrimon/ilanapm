# Seleen API Contract Specification

**Version:** 1.0.0  
**Base URL:** `https://api.seleen.io` (production) or `http://localhost:8000` (development)  
**Protocol:** REST over HTTPS  
**Format:** JSON

---

## Table of Contents

1. [Authentication](#authentication)
2. [Common Data Models](#common-data-models)
3. [Endpoints](#endpoints)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Versioning](#versioning)

---

## 1. Authentication

### API Key Authentication

All requests must include an API key in the `Authorization` header:

```
Authorization: Bearer <api_key>
```

**Example:**
```
Authorization: Bearer sk_live_4eC39HqLyjWDarjtT1zdp7dc
```

**Status Codes:**
- `401 Unauthorized` - Missing or invalid API key
- `403 Forbidden` - API key lacks required permissions

---

## 2. Common Data Models

### 2.1 TaskData

Represents a single task in the project timeline.

```json
{
  "id": 1,
  "name": "Protocol Development",
  "duration_days": 90,
  "start_date": "2026-01-15T00:00:00Z",
  "finish_date": "2026-04-15T00:00:00Z",
  "category": "Regulatory",
  "regulatory_authority": "FDA",
  "study_phase": "Phase III",
  "therapeutic_area": "Oncology",
  "is_mandatory": true,
  "predecessors": [],
  "custom_fields": {
    "gating_status": "Ready",
    "checklist_completion": 85,
    "risk_score": 25
  }
}
```

**Field Definitions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Yes | Unique task identifier (MS Project task ID) |
| `name` | string | Yes | Task name |
| `duration_days` | integer | Yes | Planned duration in days |
| `start_date` | ISO 8601 | No | Planned start date |
| `finish_date` | ISO 8601 | No | Planned finish date |
| `category` | enum | Yes | Task category: "Regulatory", "Operational", "Site", "Data", "Closeout" |
| `regulatory_authority` | string | No | Regulatory authority (e.g., "FDA", "EMA") |
| `study_phase` | string | No | Clinical trial phase |
| `therapeutic_area` | string | No | Therapeutic area |
| `is_mandatory` | boolean | Yes | Whether task is mandatory |
| `predecessors` | array[int] | Yes | Array of predecessor task IDs |
| `custom_fields` | object | No | Additional custom field values |

---

### 2.2 ProjectData

Represents the complete project timeline.

```json
{
  "project_name": "ABC-123 Phase III Oncology Trial",
  "project_id": "proj_abc123",
  "regulatory_authority": "FDA",
  "study_phase": "Phase III",
  "therapeutic_area": "Oncology",
  "tasks": [
    {
      "id": 1,
      "name": "Protocol Development",
      "duration_days": 90,
      ...
    },
    ...
  ],
  "metadata": {
    "created_by": "user@company.com",
    "created_at": "2026-01-15T10:00:00Z",
    "last_modified": "2026-01-15T15:30:00Z"
  }
}
```

---

### 2.3 ValidationViolation

Represents a single validation rule violation.

```json
{
  "task_id": 5,
  "task_name": "Site Initiation Visit",
  "violation_type": "RegulatoryGating",
  "severity": "Error",
  "description": "SIV cannot occur before IRB approval is complete",
  "suggested_fix": "Add dependency: Task 5 must follow Task 3 (IRB Approval)",
  "rule_id": "REG_GATE_001",
  "affected_tasks": [3, 5]
}
```

**Severity Levels:**
- `Error` - Must be fixed before timeline is valid
- `Warning` - Should be reviewed but not blocking
- `Info` - Informational suggestion

---

### 2.4 ValidationResult

Complete validation result for a timeline.

```json
{
  "is_valid": false,
  "violations": [
    {
      "task_id": 5,
      "task_name": "Site Initiation Visit",
      ...
    }
  ],
  "summary": "Found 3 errors, 5 warnings, 2 info messages",
  "error_count": 3,
  "warning_count": 5,
  "info_count": 2,
  "validated_at": "2026-01-15T16:00:00Z",
  "validation_id": "val_xyz789"
}
```

---

### 2.5 MLPrediction

Machine learning prediction for a task.

```json
{
  "duration_min": 72,
  "duration_max": 108,
  "duration_mean": 90,
  "confidence_pct": 78.5,
  "explanation": "Prediction based on 45 similar tasks. Factors: Phase III, FDA, Oncology.",
  "risk_factors": [
    "Complex protocol with multiple endpoints",
    "High regulatory scrutiny in therapeutic area"
  ],
  "comparable_tasks": [
    {
      "task_name": "Protocol Development - XYZ-456",
      "actual_duration": 95,
      "similarity_score": 0.89
    }
  ]
}
```

---

### 2.6 MLAdvisory

Complete ML advisory for a task.

```json
{
  "task_id": 1,
  "task_name": "Protocol Development",
  "prediction": {
    "duration_min": 72,
    "duration_max": 108,
    ...
  },
  "risk_score": 35.2,
  "delay_probability": 28.5,
  "recommendations": [
    "Consider adding 2 weeks buffer for regulatory review cycles",
    "Early engagement with FDA may reduce timeline risk"
  ],
  "generated_at": "2026-01-15T16:05:00Z"
}
```

---

## 3. Endpoints

### 3.1 Health Check

**Endpoint:** `GET /health`

**Description:** Check API health status

**Authentication:** None required

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-01-15T16:00:00Z"
}
```

**Status Codes:**
- `200 OK` - Service is healthy

---

### 3.2 Validate Timeline

**Endpoint:** `POST /api/v1/validate`

**Description:** Validate a clinical trial timeline against rules and regulations

**Authentication:** Required

**Request Body:**
```json
{
  "project_name": "ABC-123 Phase III Trial",
  "regulatory_authority": "FDA",
  "study_phase": "Phase III",
  "therapeutic_area": "Oncology",
  "tasks": [
    {
      "id": 1,
      "name": "Protocol Development",
      "duration_days": 90,
      "category": "Regulatory",
      ...
    },
    ...
  ]
}
```

**Response (200 OK):**
```json
{
  "is_valid": false,
  "violations": [
    {
      "task_id": 5,
      "violation_type": "RegulatoryGating",
      "severity": "Error",
      "description": "SIV cannot occur before IRB approval",
      "suggested_fix": "Add dependency: Task 5 → Task 3"
    }
  ],
  "summary": "Found 3 errors, 5 warnings",
  "error_count": 3,
  "warning_count": 5,
  "info_count": 2,
  "validated_at": "2026-01-15T16:00:00Z",
  "validation_id": "val_abc123"
}
```

**Status Codes:**
- `200 OK` - Validation completed
- `400 Bad Request` - Invalid request body
- `401 Unauthorized` - Missing/invalid API key
- `422 Unprocessable Entity` - Validation error in request data
- `500 Internal Server Error` - Server error

---

### 3.3 Get ML Advisory

**Endpoint:** `POST /api/v1/advisory`

**Description:** Get ML-based duration prediction and risk assessment for a task

**Authentication:** Required

**Request Body:**
```json
{
  "task": {
    "id": 1,
    "name": "Protocol Development",
    "duration_days": 90,
    "category": "Regulatory",
    "regulatory_authority": "FDA",
    "study_phase": "Phase III",
    "therapeutic_area": "Oncology"
  },
  "context": {
    "project_complexity": "High",
    "sponsor_experience": "Moderate",
    "prior_submissions": 2
  }
}
```

**Response (200 OK):**
```json
{
  "task_id": 1,
  "task_name": "Protocol Development",
  "prediction": {
    "duration_min": 72,
    "duration_max": 108,
    "duration_mean": 90,
    "confidence_pct": 78.5,
    "explanation": "Based on 45 similar tasks in Phase III oncology trials"
  },
  "risk_score": 35.2,
  "delay_probability": 28.5,
  "recommendations": [
    "Add 2-week buffer for regulatory review",
    "Early FDA engagement recommended"
  ],
  "generated_at": "2026-01-15T16:05:00Z"
}
```

**Status Codes:**
- `200 OK` - Advisory generated
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Missing/invalid API key
- `500 Internal Server Error` - Server error

---

### 3.4 Get Configuration

**Endpoint:** `GET /api/v1/config`

**Description:** Retrieve current configuration (authority timelines, checklists, task ontology)

**Authentication:** Required

**Query Parameters:**
- `config_type` (optional): Specific config to retrieve ("authority_timelines", "checklists", "task_ontology", "all")
- `authority` (optional): Filter by regulatory authority

**Response (200 OK):**
```json
{
  "version": "1.0",
  "updated_at": "2026-01-10T12:00:00Z",
  "authority_timelines": {
    "FDA": {
      "ind_review_days": 30,
      "irb_review_days": 45,
      "gating_sequence": [
        "protocol_development",
        "ind_submission",
        "irb_submission"
      ]
    },
    "EMA": {
      "cta_review_days": 60,
      ...
    }
  },
  "task_ontology": {
    "tasks": [
      {
        "id": "protocol_development",
        "name": "Protocol Development",
        "typical_duration_days": 90,
        ...
      }
    ]
  },
  "checklists": {
    "startup": {
      "items": [...]
    }
  }
}
```

**Status Codes:**
- `200 OK` - Configuration retrieved
- `401 Unauthorized` - Missing/invalid API key
- `404 Not Found` - Requested config type not found

---

### 3.5 Update Configuration

**Endpoint:** `PUT /api/v1/config/{config_type}`

**Description:** Update a configuration section (admin only)

**Authentication:** Required (admin API key)

**Path Parameters:**
- `config_type`: Type of config ("authority_timelines", "checklists", "task_ontology")

**Request Body:**
```json
{
  "FDA": {
    "ind_review_days": 30,
    "irb_review_days": 45,
    ...
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "config_type": "authority_timelines",
  "version": "1.1",
  "updated_at": "2026-01-15T16:10:00Z"
}
```

**Status Codes:**
- `200 OK` - Configuration updated
- `400 Bad Request` - Invalid configuration data
- `401 Unauthorized` - Missing/invalid API key
- `403 Forbidden` - Insufficient permissions
- `422 Unprocessable Entity` - Validation error

---

### 3.6 Post to Teams

**Endpoint:** `POST /api/v1/teams/notify`

**Description:** Send validation summary to Microsoft Teams channel

**Authentication:** Required

**Request Body:**
```json
{
  "project_name": "ABC-123 Phase III Trial",
  "channel_webhook_url": "https://outlook.office.com/webhook/...",
  "validation_summary": "Timeline validation completed",
  "validation_result": {
    "is_valid": false,
    "error_count": 3,
    "warning_count": 5
  },
  "risk_summary": {
    "high_risk_tasks": 2,
    "medium_risk_tasks": 8,
    "total_risk_score": 142
  },
  "include_details": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Notification sent to Teams",
  "teams_message_id": "msg_xyz789",
  "sent_at": "2026-01-15T16:15:00Z"
}
```

**Teams Message Format:**

The API will format and send an Adaptive Card to Teams with:
- Project name and validation timestamp
- Summary of errors, warnings, and info messages
- Top 5 high-risk tasks
- Link to full report (if applicable)

**Status Codes:**
- `200 OK` - Notification sent
- `400 Bad Request` - Invalid webhook URL or request
- `401 Unauthorized` - Missing/invalid API key
- `500 Internal Server Error` - Teams API error

---

### 3.7 Get Task Recommendations

**Endpoint:** `POST /api/v1/recommendations`

**Description:** Get AI-powered recommendations for timeline improvements

**Authentication:** Required

**Request Body:**
```json
{
  "project_data": {
    "project_name": "ABC-123",
    "tasks": [...]
  },
  "focus_areas": [
    "duration_optimization",
    "risk_mitigation",
    "regulatory_compliance"
  ]
}
```

**Response (200 OK):**
```json
{
  "recommendations": [
    {
      "category": "duration_optimization",
      "priority": "High",
      "description": "Tasks 12 and 13 can be parallelized to save 14 days",
      "estimated_savings_days": 14,
      "confidence": 0.85,
      "affected_tasks": [12, 13]
    },
    {
      "category": "risk_mitigation",
      "priority": "Medium",
      "description": "Add buffer to Task 5 (IRB Submission) - historical 30% delay rate",
      "recommended_buffer_days": 10,
      "confidence": 0.72,
      "affected_tasks": [5]
    }
  ],
  "summary": "Found 8 optimization opportunities saving up to 42 days",
  "generated_at": "2026-01-15T16:20:00Z"
}
```

**Status Codes:**
- `200 OK` - Recommendations generated
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Missing/invalid API key

---

### 3.8 Batch Validate

**Endpoint:** `POST /api/v1/validate/batch`

**Description:** Validate multiple timelines in a single request (useful for comparisons)

**Authentication:** Required

**Request Body:**
```json
{
  "projects": [
    {
      "project_id": "proj_001",
      "project_name": "ABC-123 Scenario A",
      "tasks": [...]
    },
    {
      "project_id": "proj_002",
      "project_name": "ABC-123 Scenario B",
      "tasks": [...]
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "project_id": "proj_001",
      "is_valid": false,
      "error_count": 3,
      "validation_id": "val_001"
    },
    {
      "project_id": "proj_002",
      "is_valid": true,
      "error_count": 0,
      "validation_id": "val_002"
    }
  ],
  "comparison": {
    "recommended_scenario": "proj_002",
    "reason": "Fewer violations and lower risk score"
  }
}
```

---

## 4. Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Timeline validation failed with 3 errors",
    "details": [
      "Task 5 violates regulatory gating rules",
      "Circular dependency detected: 3 → 5 → 3"
    ],
    "request_id": "req_abc123",
    "timestamp": "2026-01-15T16:00:00Z"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_API_KEY` | 401 | API key is missing or invalid |
| `INSUFFICIENT_PERMISSIONS` | 403 | API key lacks required permissions |
| `VALIDATION_ERROR` | 422 | Request data failed validation |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## 5. Rate Limiting

**Limits:**
- 100 requests per minute per API key
- 1000 requests per hour per API key

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705334400
```

**429 Response:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 42 seconds.",
    "retry_after": 42
  }
}
```

---

## 6. Versioning

API versioning is handled via URL path:
- Current: `/api/v1/`
- Future: `/api/v2/`

**Deprecation Policy:**
- Versions supported for minimum 12 months after new version release
- Deprecation notices sent 6 months in advance
- `Sunset` header included in deprecated version responses

---

## 7. Request/Response Examples

### Example 1: Complete Validation Flow

**Request:**
```bash
curl -X POST https://api.seleen.io/api/v1/validate \
  -H "Authorization: Bearer sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "ABC-123 Phase III",
    "regulatory_authority": "FDA",
    "study_phase": "Phase III",
    "therapeutic_area": "Oncology",
    "tasks": [
      {
        "id": 1,
        "name": "Protocol Development",
        "duration_days": 90,
        "category": "Regulatory",
        "is_mandatory": true,
        "predecessors": []
      },
      {
        "id": 2,
        "name": "IND Submission",
        "duration_days": 30,
        "category": "Regulatory",
        "is_mandatory": true,
        "predecessors": [1]
      }
    ]
  }'
```

**Response:**
```json
{
  "is_valid": true,
  "violations": [],
  "summary": "Timeline is valid with no errors",
  "error_count": 0,
  "warning_count": 0,
  "info_count": 1,
  "validated_at": "2026-01-15T16:00:00Z",
  "validation_id": "val_abc123"
}
```

### Example 2: ML Advisory Request

**Request:**
```bash
curl -X POST https://api.seleen.io/api/v1/advisory \
  -H "Authorization: Bearer sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{
    "task": {
      "id": 1,
      "name": "Protocol Development",
      "duration_days": 90,
      "category": "Regulatory",
      "regulatory_authority": "FDA",
      "study_phase": "Phase III",
      "therapeutic_area": "Oncology"
    }
  }'
```

**Response:**
```json
{
  "task_id": 1,
  "prediction": {
    "duration_min": 75,
    "duration_max": 105,
    "confidence_pct": 82.3,
    "explanation": "Based on 52 Phase III oncology protocols with FDA"
  },
  "risk_score": 28.5,
  "delay_probability": 22.0,
  "recommendations": [
    "Historical data shows 22% delay rate for this task type",
    "Consider early FDA engagement to reduce uncertainty"
  ]
}
```

---

## 8. Webhook Events (Future)

Future versions may support webhooks for asynchronous notifications:

**Planned Events:**
- `validation.completed`
- `ml_model.updated`
- `config.changed`

---

## 9. SDK Support

**Planned SDKs:**
- C# (.NET 6+) - for add-in integration
- Python 3.11+ - for backend integration
- JavaScript/TypeScript - for web integrations

---

**End of API Contract Specification**
