'use client';

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";

interface User {
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([
    {
      user_id: "usr_001",
      email: "john.doe@example.com",
      first_name: "John",
      last_name: "Doe",
      role: "admin",
      is_active: true,
      last_login: "2026-02-06T10:30:00Z",
      created_at: "2025-12-01T09:00:00Z"
    },
    {
      user_id: "usr_002",
      email: "jane.smith@example.com",
      first_name: "Jane",
      last_name: "Smith",
      role: "user",
      is_active: true,
      last_login: "2026-02-05T14:20:00Z",
      created_at: "2025-12-02T10:30:00Z"
    },
    {
      user_id: "usr_003",
      email: "bob.johnson@example.com",
      first_name: "Bob",
      last_name: "Johnson",
      role: "user",
      is_active: true,
      last_login: "2026-02-04T16:45:00Z",
      created_at: "2025-12-03T11:15:00Z"
    },
    {
      user_id: "usr_004",
      email: "alice.williams@example.com",
      first_name: "Alice",
      last_name: "Williams",
      role: "user",
      is_active: false,
      last_login: "2026-01-15T09:20:00Z",
      created_at: "2025-12-01T14:00:00Z"
    }
  ]);

  const [showDeactivateModal, setShowDeactivateModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  const handleDeactivate = (user: User) => {
    setSelectedUser(user);
    setShowDeactivateModal(true);
  };

  const confirmDeactivate = async () => {
    if (!selectedUser) return;

    // TODO: Call API to deactivate user
    // await fetch(`/api/v1/portal/customer/users/${selectedUser.user_id}`, { method: 'DELETE' })

    setUsers(users.map(u =>
      u.user_id === selectedUser.user_id
        ? { ...u, is_active: false }
        : u
    ));

    setShowDeactivateModal(false);
    setSelectedUser(null);
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
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <Link href="/dashboard">
                <Image
                  src="/logo.png"
                  alt="Seleen Logo"
                  width={120}
                  height={32}
                  priority
                />
              </Link>
              <nav className="flex gap-6">
                <Link href="/dashboard" className="text-gray-600 hover:text-black transition-colors">
                  Dashboard
                </Link>
                <Link href="/users" className="text-black font-medium">
                  Users
                </Link>
                <Link href="/billing" className="text-gray-600 hover:text-black transition-colors">
                  Billing
                </Link>
                <Link href="/analytics" className="text-gray-600 hover:text-black transition-colors">
                  Analytics
                </Link>
                <Link href="/settings" className="text-gray-600 hover:text-black transition-colors">
                  Settings
                </Link>
              </nav>
            </div>
            <button className="px-4 py-2 text-gray-600 hover:text-black transition-colors">
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-black">User Management</h1>
          <p className="text-black">Manage user access and seat assignments for your organization.</p>
        </div>

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
            <div className="text-gray-500 text-sm mb-1">Total Seats</div>
            <div className="text-3xl font-light text-black">50</div>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl text-black">All Users</h2>
          </div>
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
                      {user.is_active && user.role !== 'admin' && (
                        <button
                          onClick={() => handleDeactivate(user)}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          Deactivate
                        </button>
                      )}
                      {user.role === 'admin' && (
                        <span className="text-gray-400 text-sm">Admin</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
