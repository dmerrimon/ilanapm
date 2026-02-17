'use client';

import { useState, useEffect } from "react";
import Header from "@/components/Header";
import { apiClient } from "@/lib/api-client";
import Link from "next/link";

interface User {
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

interface OrgFilter {
  org_id: string;
  org_name: string;
  user_count: number;
}

export default function UsersManagementPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedOrg, setSelectedOrg] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all"); // 'all', 'active', 'inactive'

  // Modals
  const [showToggleModal, setShowToggleModal] = useState(false);
  const [showResetModal, setShowResetModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Stats
  const [totalUsers, setTotalUsers] = useState(0);
  const [activeUsers, setActiveUsers] = useState(0);
  const [inactiveUsers, setInactiveUsers] = useState(0);

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    // Apply client-side filters
    let filtered = users;

    if (selectedOrg !== "all") {
      filtered = filtered.filter(u => u.org_id === selectedOrg);
    }

    if (statusFilter === "active") {
      filtered = filtered.filter(u => u.is_active);
    } else if (statusFilter === "inactive") {
      filtered = filtered.filter(u => !u.is_active);
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(u =>
        u.email.toLowerCase().includes(query) ||
        u.first_name?.toLowerCase().includes(query) ||
        u.last_name?.toLowerCase().includes(query) ||
        u.org_name.toLowerCase().includes(query)
      );
    }

    setFilteredUsers(filtered);
  }, [users, selectedOrg, statusFilter, searchQuery]);

  const fetchUsers = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await apiClient.get('/portal/founder/users?limit=1000');
      setUsers(response.users);
      setFilteredUsers(response.users);
      setTotalUsers(response.total_count || response.users.length);

      // Calculate stats
      const active = response.users.filter((u: User) => u.is_active).length;
      setActiveUsers(active);
      setInactiveUsers(response.users.length - active);
    } catch (err: any) {
      setError(err.message || "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = (user: User) => {
    setSelectedUser(user);
    setShowToggleModal(true);
  };

  const confirmToggleActive = async () => {
    if (!selectedUser) return;

    setActionLoading(true);
    setError("");
    setSuccessMessage("");

    try {
      const response = await apiClient.patch(
        `/portal/founder/users/${selectedUser.user_id}/toggle-active`
      );

      setSuccessMessage(response.message);
      setShowToggleModal(false);
      setSelectedUser(null);

      // Refresh users list
      await fetchUsers();
    } catch (err: any) {
      setError(err.message || "Failed to toggle user status");
    } finally {
      setActionLoading(false);
    }
  };

  const handleResetPassword = (user: User) => {
    setSelectedUser(user);
    setShowResetModal(true);
  };

  const confirmResetPassword = async () => {
    if (!selectedUser) return;

    setActionLoading(true);
    setError("");
    setSuccessMessage("");

    try {
      const response = await apiClient.post(
        `/portal/founder/users/${selectedUser.user_id}/reset-password`
      );

      setSuccessMessage(response.message);
      setShowResetModal(false);
      setSelectedUser(null);
    } catch (err: any) {
      setError(err.message || "Failed to send reset email");
    } finally {
      setActionLoading(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never";
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getRelativeTime = (dateString: string | null) => {
    if (!dateString) return "Never";
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo ago`;
    return `${Math.floor(diffDays / 365)}y ago`;
  };

  // Get unique organizations for filter dropdown
  const organizations = Array.from(
    new Map(users.map(u => [u.org_id, { org_id: u.org_id, org_name: u.org_name }])).values()
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-black">User Management</h1>
          <p className="text-black">Manage users across all organizations from a single dashboard.</p>
        </div>

        {/* Success/Error Messages */}
        {successMessage && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded flex justify-between items-center">
            <span>{successMessage}</span>
            <button onClick={() => setSuccessMessage("")} className="text-green-600 hover:text-green-800">
              ✕
            </button>
          </div>
        )}

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded flex justify-between items-center">
            <span>{error}</span>
            <button onClick={() => setError("")} className="text-red-600 hover:text-red-800">
              ✕
            </button>
          </div>
        )}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Users</div>
            <div className="text-3xl font-light text-black">{totalUsers}</div>
            <div className="text-xs text-gray-400 mt-1">All organizations</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Active Users</div>
            <div className="text-3xl font-light text-green-600">{activeUsers}</div>
            <div className="text-xs text-gray-400 mt-1">Can access system</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Inactive Users</div>
            <div className="text-3xl font-light text-gray-600">{inactiveUsers}</div>
            <div className="text-xs text-gray-400 mt-1">Deactivated accounts</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Organizations</div>
            <div className="text-3xl font-light text-black">{organizations.length}</div>
            <div className="text-xs text-gray-400 mt-1">With users</div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-black mb-2">Search Users</label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Email, name, or organization..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-black"
              />
            </div>

            {/* Organization Filter */}
            <div>
              <label className="block text-sm font-medium text-black mb-2">Organization</label>
              <select
                value={selectedOrg}
                onChange={(e) => setSelectedOrg(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-black"
              >
                <option value="all">All Organizations ({totalUsers})</option>
                {organizations.map((org) => (
                  <option key={org.org_id} value={org.org_id}>
                    {org.org_name}
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-black mb-2">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-black"
              >
                <option value="all">All ({totalUsers})</option>
                <option value="active">Active ({activeUsers})</option>
                <option value="inactive">Inactive ({inactiveUsers})</option>
              </select>
            </div>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-xl text-black">
              Users ({filteredUsers.length})
            </h2>
            <button
              onClick={fetchUsers}
              disabled={loading}
              className="px-4 py-2 bg-gray-100 text-black rounded hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              {loading ? "Loading..." : "Refresh"}
            </button>
          </div>

          {loading ? (
            <div className="px-6 py-12 text-center text-gray-500">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black mx-auto mb-4"></div>
              Loading users...
            </div>
          ) : filteredUsers.length === 0 ? (
            <div className="px-6 py-12 text-center text-gray-500">
              <p>No users found matching your filters.</p>
              <button
                onClick={() => {
                  setSearchQuery("");
                  setSelectedOrg("all");
                  setStatusFilter("all");
                }}
                className="mt-4 text-black hover:underline"
              >
                Clear filters
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      Organization
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      Devices
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      Last Login
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredUsers.map((user) => (
                    <tr key={user.user_id} className={!user.is_active ? "opacity-60" : ""}>
                      <td className="px-6 py-4">
                        <div className="text-sm text-black font-medium">
                          {user.first_name && user.last_name
                            ? `${user.first_name} ${user.last_name}`
                            : user.email}
                        </div>
                        <div className="text-xs text-gray-500">{user.email}</div>
                        <div className="text-xs text-gray-400 mt-1">
                          Joined {formatDate(user.created_at)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link
                          href={`/customers/${user.org_id}`}
                          className="text-sm text-black hover:underline"
                        >
                          {user.org_name}
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs rounded ${
                            user.role === 'admin' || user.role === 'super_admin'
                              ? 'bg-black text-white'
                              : 'bg-gray-200 text-black'
                          }`}
                        >
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-black">
                        {user.device_count > 0 ? (
                          <Link
                            href={`/devices?org_id=${user.org_id}`}
                            className="hover:underline"
                          >
                            {user.device_count} device{user.device_count !== 1 ? 's' : ''}
                          </Link>
                        ) : (
                          <span className="text-gray-400">No devices</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-black">
                        {getRelativeTime(user.last_login)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {user.is_active ? (
                          <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            Active
                          </span>
                        ) : (
                          <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                            Inactive
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-3">
                          <button
                            onClick={() => handleToggleActive(user)}
                            className={`${
                              user.is_active
                                ? 'text-red-600 hover:text-red-900'
                                : 'text-green-600 hover:text-green-900'
                            } hover:underline`}
                            title={user.is_active ? 'Deactivate user' : 'Activate user'}
                          >
                            {user.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                          <button
                            onClick={() => handleResetPassword(user)}
                            className="text-blue-600 hover:text-blue-900 hover:underline"
                            title="Send password reset email"
                          >
                            Reset Password
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-black text-sm">
            <strong>Support Functions:</strong> As a super admin, you can manage users across all organizations. Deactivating a user will also deactivate all their devices and free up seats. Password reset will send an email with a secure reset link. All actions are logged in the audit trail.
          </p>
        </div>
      </main>

      {/* Toggle Active Modal */}
      {showToggleModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-xl font-semibold text-black mb-4">
              {selectedUser.is_active ? 'Deactivate User?' : 'Activate User?'}
            </h3>
            <p className="text-gray-700 mb-4">
              {selectedUser.is_active
                ? 'Are you sure you want to deactivate this user? This will deactivate all their devices and free up seats.'
                : 'Are you sure you want to activate this user? They will be able to log in and activate devices.'}
            </p>
            <div className="bg-gray-50 p-4 rounded mb-6 space-y-2">
              <div className="text-sm">
                <span className="text-gray-600">Name:</span>{" "}
                <span className="text-black font-medium">
                  {selectedUser.first_name} {selectedUser.last_name}
                </span>
              </div>
              <div className="text-sm">
                <span className="text-gray-600">Email:</span>{" "}
                <span className="text-black">{selectedUser.email}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-600">Organization:</span>{" "}
                <span className="text-black">{selectedUser.org_name}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-600">Active Devices:</span>{" "}
                <span className="text-black">{selectedUser.device_count}</span>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowToggleModal(false);
                  setSelectedUser(null);
                }}
                disabled={actionLoading}
                className="flex-1 px-4 py-2 border border-gray-300 rounded text-black hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmToggleActive}
                disabled={actionLoading}
                className={`flex-1 px-4 py-2 rounded transition-colors disabled:opacity-50 ${
                  selectedUser.is_active
                    ? 'bg-red-600 text-white hover:bg-red-700'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {actionLoading
                  ? 'Processing...'
                  : selectedUser.is_active
                  ? 'Deactivate User'
                  : 'Activate User'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reset Password Modal */}
      {showResetModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-xl font-semibold text-black mb-4">Reset Password?</h3>
            <p className="text-gray-700 mb-4">
              This will send a password reset email to the user with a secure reset link that expires in 1 hour.
            </p>
            <div className="bg-gray-50 p-4 rounded mb-6 space-y-2">
              <div className="text-sm">
                <span className="text-gray-600">Name:</span>{" "}
                <span className="text-black font-medium">
                  {selectedUser.first_name} {selectedUser.last_name}
                </span>
              </div>
              <div className="text-sm">
                <span className="text-gray-600">Email:</span>{" "}
                <span className="text-black">{selectedUser.email}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-600">Organization:</span>{" "}
                <span className="text-black">{selectedUser.org_name}</span>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-6">
              The user will receive an email with instructions to reset their password. This action will be logged in the audit trail.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowResetModal(false);
                  setSelectedUser(null);
                }}
                disabled={actionLoading}
                className="flex-1 px-4 py-2 border border-gray-300 rounded text-black hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmResetPassword}
                disabled={actionLoading}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                {actionLoading ? 'Sending...' : 'Send Reset Email'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
