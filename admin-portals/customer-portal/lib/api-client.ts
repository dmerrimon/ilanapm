/**
 * API Client for Customer Portal
 * Handles all communication with FastAPI backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Make authenticated API request
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAccessToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_BASE}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new APIError(
        errorData.detail || `HTTP ${response.status}`,
        response.status,
        errorData
      );
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new APIError('Network error', 0, error);
  }
}

/**
 * Generic API client for making requests
 */
export const apiClient = {
  get: <T = any>(endpoint: string) => apiRequest<T>(endpoint, { method: 'GET' }),
  post: <T = any>(endpoint: string, data?: any) => {
    // Handle FormData differently (don't set Content-Type, let browser set it with boundary)
    if (data instanceof FormData) {
      const token = getAccessToken();
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      return apiRequest<T>(endpoint, {
        method: 'POST',
        body: data,
        headers,
      });
    }
    return apiRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },
  put: <T = any>(endpoint: string, data?: any) => apiRequest<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  }),
  delete: <T = any>(endpoint: string) => apiRequest<T>(endpoint, { method: 'DELETE' }),
  patch: <T = any>(endpoint: string, data?: any) => apiRequest<T>(endpoint, {
    method: 'PATCH',
    body: data ? JSON.stringify(data) : undefined,
  }),
};

/**
 * Token management helpers
 */
export function setAccessToken(token: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', token);
  }
}

export function getAccessToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
}

export function clearAccessToken() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
  }
}

// ============================================================================
// Authentication
// ============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    user_id: string;
    email: string;
    first_name: string | null;
    last_name: string | null;
    role: string;
    org_id: string;
  };
}

export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await apiRequest<LoginResponse>('/portal/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });

  // Store token
  setAccessToken(response.access_token);

  return response;
}

export function logout() {
  clearAccessToken();
}

// ============================================================================
// Dashboard
// ============================================================================

export interface DashboardData {
  org_id: string;
  org_name: string;
  license_key: string;
  status: string;
  tier: string;
  seats_purchased: number;
  seats_used: number;
  seats_available: number;
  seat_rate: number | null;
  billing_cycle: string;
  mrr: number | null;
  next_billing_date: string | null;
  recent_activity: Array<{
    action: string;
    user: string;
    timestamp: string;
  }>;
  quick_stats: {
    templates_30d: number;
    feedback_30d: number;
    active_users_7d: number;
  };
}

export async function getDashboard(): Promise<DashboardData> {
  return apiRequest<DashboardData>('/portal/customer/dashboard');
}

// ============================================================================
// Users
// ============================================================================

export interface OrgUser {
  user_id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  role: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
}

export async function getUsers(): Promise<OrgUser[]> {
  return apiRequest<OrgUser[]>('/portal/customer/users');
}

export async function deactivateUser(userId: string): Promise<void> {
  return apiRequest<void>(`/portal/customer/users/${userId}`, {
    method: 'DELETE',
  });
}

// ============================================================================
// Analytics
// ============================================================================

export interface AnalyticsData {
  org_id: string;
  org_name: string;
  template_count_30d: number;
  feedback_count_30d: number;
  active_users_30d: number;
  most_used_templates: Array<{
    template_name: string;
    count: number;
  }>;
  most_active_users: Array<{
    user_name: string;
    templates_generated: number;
  }>;
}

export async function getAnalytics(): Promise<AnalyticsData> {
  return apiRequest<AnalyticsData>('/portal/customer/analytics');
}

// ============================================================================
// Admin Transfer
// ============================================================================

export interface AdminTransferRequest {
  org_id: string;
  from_user_id: string;
  to_user_email: string;
  message?: string;
}

export interface AdminTransferResponse {
  request_id: string;
  message: string;
}

export async function initiateAdminTransfer(
  request: AdminTransferRequest
): Promise<AdminTransferResponse> {
  return apiRequest<AdminTransferResponse>('/portal/customer/admin-transfer', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export interface AdminTransferAcceptRequest {
  token: string;
}

export async function acceptAdminTransfer(
  request: AdminTransferAcceptRequest
): Promise<{ message: string }> {
  return apiRequest<{ message: string }>('/portal/customer/admin-transfer/accept', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// ============================================================================
// Settings
// ============================================================================

export interface OrganizationSettings {
  org_name: string;
  billing_email: string;
  notification_preferences: {
    notify_on_new_users: boolean;
    notify_on_billing: boolean;
    notify_on_usage: boolean;
  };
}

export async function updateSettings(
  settings: Partial<OrganizationSettings>
): Promise<{ message: string }> {
  return apiRequest<{ message: string }>('/portal/customer/settings', {
    method: 'PUT',
    body: JSON.stringify(settings),
  });
}

// Note: Billing endpoints (add-seats) are stubbed in backend
// Will be implemented when Stripe integration is added

// ============================================================================
// Intelligence Layer
// ============================================================================

export interface VarianceMetrics {
  absolute_days: number;
  percentage: number;
  severity: 'acceptable' | 'warning' | 'critical';
  classification: 'on_target' | 'overestimate' | 'underestimate';
}

export interface BenchmarkData {
  task_id: string;
  task_name: string;
  category: string;
  median_days: number;
  p25_days: number;
  p75_days: number;
  typical_duration_days: number;
  source: string;
  confidence: string;
  data_quality?: string;
}

export interface VarianceSignal {
  task_id: string;
  task_name: string;
  customer_duration_days: number;
  benchmark: BenchmarkData;
  variance: VarianceMetrics;
  financial_impact_usd: number;
  explanation: string;
  recommendations?: string[];
}

export interface VarianceSummary {
  total_tasks_analyzed: number;
  tasks_with_benchmarks: number;
  benchmark_coverage_percent: number;
  warning_count: number;
  critical_count: number;
  acceptable_count: number;
  total_financial_impact_usd: number;
  avg_variance_percent: number;
  overestimate_count: number;
  underestimate_count: number;
}

export interface BenchmarkCoverage {
  tasks_matched: number;
  tasks_unmatched: number;
  coverage_percent: number;
  unmatched_task_names: string[];
  match_quality: {
    exact: number;
    fuzzy: number;
    category: number;
    special_case: number;
  };
}

export interface VarianceReport {
  tier: string;
  org_id: string;
  analysis_timestamp: string;
  variance_signals: VarianceSignal[];
  summary: VarianceSummary;
  benchmark_coverage: BenchmarkCoverage;
  configuration?: any;
}

export interface IntelligenceValidationRequest {
  timeline: {
    study_name?: string;
    primary_country?: string;
    phase?: string;
    therapeutic_area?: string;
    tasks: Array<{
      id: string;
      name: string;
      category?: string;
      duration_days: number;
      authority?: string;
    }>;
  };
  org_id: string;
  tier: string;
}

export async function validateTimeline(
  request: IntelligenceValidationRequest
): Promise<VarianceReport> {
  return apiRequest<VarianceReport>('/intelligence/validate-core', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export interface BenchmarkQuery {
  task_name?: string;
  category?: string;
  country?: string;
  authority?: string;
  phase?: string;
  therapeutic_area?: string;
  site_type?: string;
}

export async function getBenchmark(query: BenchmarkQuery): Promise<BenchmarkData> {
  return apiRequest<BenchmarkData>('/intelligence/benchmarks', {
    method: 'POST',
    body: JSON.stringify(query),
  });
}

export interface IntelligenceConfig {
  org_id: string;
  tier: string;
  variance_thresholds: {
    warning_percent: number;
    critical_percent: number;
  };
  financial_rate_per_month_usd: number;
  benchmark_source: string;
}

export async function getIntelligenceConfig(orgId: string): Promise<IntelligenceConfig> {
  return apiRequest<IntelligenceConfig>(`/intelligence/tier-config?org_id=${orgId}`);
}

export interface TaskMapping {
  mapping_id: string;
  customer_task_name: string;
  ontology_task_id: string;
  ontology_task_name: string;
  confidence: number;
  confirmed_by_user: boolean;
  created_at: string;
}

export async function getTaskMappings(orgId: string): Promise<{
  org_id: string;
  count: number;
  mappings: TaskMapping[];
}> {
  return apiRequest<any>(`/intelligence/task-mappings?org_id=${orgId}`);
}

export interface TaskNormalizationRequest {
  customer_task_name: string;
  category?: string;
}

export interface TaskMappingSuggestion {
  ontology_task_id: string;
  ontology_task_name: string;
  confidence: number;
  match_method: string;
  reasoning?: string;
}

export async function normalizeTask(
  orgId: string,
  request: TaskNormalizationRequest
): Promise<TaskMappingSuggestion[]> {
  return apiRequest<TaskMappingSuggestion[]>(
    `/intelligence/normalize-task?org_id=${orgId}`,
    {
      method: 'POST',
      body: JSON.stringify(request),
    }
  );
}

export interface ProjectProfile {
  profile_id: string;
  project_name: string;
  study_id?: string;
  therapeutic_area?: string;
  phase?: string;
  primary_country?: string;
  additional_countries?: string[];
  metadata?: any;
  created_at: string;
}

export async function getProjectProfiles(orgId: string): Promise<{
  org_id: string;
  count: number;
  profiles: ProjectProfile[];
}> {
  return apiRequest<any>(`/intelligence/project-profiles?org_id=${orgId}`);
}

export async function createProjectProfile(
  orgId: string,
  profile: Partial<ProjectProfile>
): Promise<ProjectProfile> {
  return apiRequest<ProjectProfile>(`/intelligence/project-profiles?org_id=${orgId}`, {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}

export interface MetadataInference {
  field_name: string;
  inferred_value: string;
  confidence: number;
  evidence: string[];
  inference_method: string;
}

export async function inferMetadata(timeline: any): Promise<{
  phase?: MetadataInference | string;
  therapeutic_area?: MetadataInference | string;
  primary_country?: MetadataInference | string;
  additional_countries?: MetadataInference[];
  needs_confirmation: boolean;
}> {
  return apiRequest<any>('/intelligence/infer-metadata', {
    method: 'POST',
    body: JSON.stringify({ timeline }),
  });
}
