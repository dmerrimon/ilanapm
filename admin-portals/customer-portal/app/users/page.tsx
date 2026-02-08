'use client';

import { useState, useEffect } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import { apiClient } from "@/lib/api-client";

interface User {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
  active_devices: number;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showDeactivateModal, setShowDeactivateModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [deactivating, setDeactivating] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await apiClient.get('/portal/customer/users');
      setUsers(response.users);
    } catch (err: any) {
      setError(err.message || "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivate = (user: User) => {
    setSelectedUser(user);
    setShowDeactivateModal(true);
  };

  const confirmDeactivate = async () => {
    if (!selectedUser) return;

    setDeactivating(true);
    try {
      await apiClient.delete(`/portal/customer/users/${selectedUser.user_id}`);

      // Refresh the user list
      await fetchUsers();

      setShowDeactivateModal(false);
      setSelectedUser(null);
    } catch (err: any) {
      setError(err.message || "Failed to deactivate user");
    } finally {
      setDeactivating(false);
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

  const activeUsers = users.filter(u => u.is_active).length;
  const inactiveUsers = users.filter(u => !u.is_active).length;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-black">User Management</h1>
          <p className="text-black">Manage user access and seat assignments for your organization.</p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Active Users</div>
            <div className="text-3xl font-light text-black">{activeUsers}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Inactive Users</div>
            <div className="text-3xl font-light text-black">{inactiveUsers}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Users</div>
            <div className="text-3xl font-light text-black">{users.length}</div>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-xl text-black">All Users</h2>
            <Link
              href="/devices"
              className="text-sm text-blue-600 hover:text-blue-800 hover:underline"
            >
              View Active Devices →
            </Link>
          </div>

          {loading ? (
            <div className="px-6 py-12 text-center text-gray-500">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black mx-auto mb-4"></div>
              Loading users...
            </div>
          ) : users.length === 0 ? (
            <div className="px-6 py-12 text-center text-gray-500">
              <p>No users found.</p>
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
                      Email
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
                <tbody className="divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.user_id} className={!user.is_active ? 'bg-gray-50' : ''}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-black">{user.first_name} {user.last_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-black">{user.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded ${
                          user.role === 'admin'
                            ? 'bg-black text-white'
                            : 'bg-gray-200 text-black'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {user.active_devices > 0 ? (
                          <span className="text-black font-medium">
                            {user.active_devices} {user.active_devices === 1 ? 'device' : 'devices'}
                          </span>
                        ) : (
                          <span className="text-gray-400">None</span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-black">
                        {formatDate(user.last_login)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded ${
                          user.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {user.is_active && user.role !== 'admin' ? (
                          <button
                            onClick={() => handleDeactivate(user)}
                            disabled={deactivating}
                            className="text-red-600 hover:text-red-800 text-sm hover:underline disabled:opacity-50"
                          >
                            Deactivate
                          </button>
                        ) : user.role === 'admin' ? (
                          <span className="text-gray-400 text-sm">Admin</span>
                        ) : (
                          <span className="text-gray-400 text-sm">N/A</span>
                        )}
                      </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          )}
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-black text-sm">
            <strong>Note:</strong> Deactivating a user will free up their seat and revoke their access to Seleen.
            You can reassign this seat to a new user from the dashboard.
          </p>
        </div>
      </main>

      {/* Deactivate Confirmation Modal */}
      {showDeactivateModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl mb-4 text-black">Deactivate User</h3>
            <p className="mb-6 text-black">
              Are you sure you want to deactivate <strong>{selectedUser.first_name} {selectedUser.last_name}</strong>?
              They will immediately lose access to Seleen, and their seat will become available for reassignment.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowDeactivateModal(false);
                  setSelectedUser(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors text-black"
              >
                Cancel
              </button>
              <button
                onClick={confirmDeactivate}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                Deactivate User
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
