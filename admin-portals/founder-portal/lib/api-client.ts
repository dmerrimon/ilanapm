/**
 * API Client for Founder Portal
 * Handles all communication with FastAPI backend for super admin operations
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
// Founder Dashboard
// ============================================================================

export interface FounderDashboardData {
  total_customers: number;
  total_seats: number;
  total_mrr: number;
  system_uptime: number;
  api_response_time_p95: number;
  db_size_mb: number;
  recent_alerts: Array<{
    type: string;
    message: string;
    timestamp: string;
  }>;
}

export async function getFounderDashboard(): Promise<FounderDashboardData> {
  return apiRequest<FounderDashboardData>('/portal/founder/dashboard');
}

// ============================================================================
// Customers
// ============================================================================

export interface Customer {
  org_id: string;
  org_name: string;
  license_key: string;
  seats_used: number;
  seats_purchased: number;
  seat_rate: number | null;
  mrr: number | null;
  status: string;
  created_at: string;
  last_active: string | null;
}

export async function getCustomers(): Promise<Customer[]> {
  return apiRequest<Customer[]>('/portal/founder/customers');
}

export interface CustomerDetails {
  org_id: string;
  org_name: string;
  admin_email: string;
  seats_purchased: number;
  seats_used: number;
  seats_available: number;
  seat_rate: number | null;
  billing_cycle: string;
  mrr: number | null;
  status: string;
  license_key: string;
  created_at: string;
  next_billing_date: string | null;
  users: Array<{
    user_id: string;
    email: string;
    first_name: string | null;
    last_name: string | null;
    role: string;
    is_active: boolean;
    last_login: string | null;
  }>;
  recent_activity: Array<{
    action: string;
    user: string;
    timestamp: string;
  }>;
}

export async function getCustomerDetails(orgId: string): Promise<CustomerDetails> {
  return apiRequest<CustomerDetails>(`/portal/founder/customers/${orgId}`);
}

// ============================================================================
// System Analytics
// ============================================================================

export interface SystemAnalytics {
  total_templates_30d: number;
  total_api_requests_30d: number;
  avg_response_time_ms: number;
  ml_accuracy_metrics: {
    fda_510k: number;
    ce_mark: number;
    risk_assessment: number;
    clinical_evaluation: number;
  };
  top_api_endpoints: Array<{
    endpoint: string;
    calls: number;
    avg_time: number;
    errors: number;
  }>;
  daily_usage: Array<{
    date: string;
    templates: number;
    users: number;
  }>;
}

export async function getSystemAnalytics(): Promise<SystemAnalytics> {
  return apiRequest<SystemAnalytics>('/portal/founder/analytics/system');
}

// ============================================================================
// License Management
// ============================================================================

export interface License {
  license_key: string;
  org_name: string;
  seats: number;
  status: string;
  created_at: string;
  expires_at: string | null;
}

export async function getLicenses(): Promise<License[]> {
  return apiRequest<License[]>('/portal/founder/licenses');
}

export interface GenerateLicenseRequest {
  org_name: string;
  admin_email: string;
  seats: number;
}

export interface GenerateLicenseResponse {
  license_key: string;
  org_id: string;
  message: string;
}

export async function generateLicense(
  request: GenerateLicenseRequest
): Promise<GenerateLicenseResponse> {
  return apiRequest<GenerateLicenseResponse>('/portal/founder/licenses/generate', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

export async function revokeLicense(licenseKey: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/portal/founder/licenses/${licenseKey}/revoke`, {
    method: 'POST',
  });
}

export async function extendLicense(
  licenseKey: string,
  months: number
): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/portal/founder/licenses/${licenseKey}/extend`, {
    method: 'POST',
    body: JSON.stringify({ months }),
  });
}

// ============================================================================
// Generic API Client Helper
// ============================================================================

export const apiClient = {
  get: <T = any>(endpoint: string) => apiRequest<T>(endpoint, { method: 'GET' }),
  post: <T = any>(endpoint: string, data?: any) => apiRequest<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  }),
  put: <T = any>(endpoint: string, data?: any) => apiRequest<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  }),
  patch: <T = any>(endpoint: string, data?: any) => apiRequest<T>(endpoint, {
    method: 'PATCH',
    body: data ? JSON.stringify(data) : undefined,
  }),
  delete: <T = any>(endpoint: string) => apiRequest<T>(endpoint, { method: 'DELETE' }),
};

// ============================================================================
// User Management (Super Admin)
// ============================================================================

export interface User {
  user_id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
  org_id: string;
  org_name: string;
  device_count: number;
}

export interface UsersResponse {
  users: User[];
  count: number;
  total_count: number;
  limit: number;
  offset: number;
}

export interface UserManagementParams {
  org_id?: string;
  search?: string;
  status?: 'active' | 'inactive';
  limit?: number;
  offset?: number;
}

export async function getAllUsers(params?: UserManagementParams): Promise<UsersResponse> {
  const queryParams = new URLSearchParams();
  if (params?.org_id) queryParams.append('org_id', params.org_id);
  if (params?.search) queryParams.append('search', params.search);
  if (params?.status) queryParams.append('status', params.status);
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());

  const query = queryParams.toString();
  return apiRequest<UsersResponse>(`/portal/founder/users${query ? `?${query}` : ''}`);
}

export async function getCustomerUsers(orgId: string): Promise<{
  org_id: string;
  org_name: string;
  users: User[];
  count: number;
}> {
  return apiRequest(`/portal/founder/customers/${orgId}/users`);
}

export async function toggleUserActive(userId: string): Promise<{
  message: string;
  user_id: string;
  email: string;
  is_active: boolean;
  devices_deactivated: number;
}> {
  return apiRequest(`/portal/founder/users/${userId}/toggle-active`, {
    method: 'PATCH',
  });
}

export async function resetUserPassword(userId: string): Promise<{
  message: string;
  user_id: string;
  email: string;
  email_sent: boolean;
  expires_at: string;
}> {
  return apiRequest(`/portal/founder/users/${userId}/reset-password`, {
    method: 'POST',
  });
}
