'use client';

import { useParams } from "next/navigation";
import { useState, useEffect } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import { apiClient } from "@/lib/api-client";

interface User {
  user_id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login: string | null;
  device_count: number;
}

export default function CustomerDetailPage() {
  const params = useParams();
  const customerId = params.id;

  const [customer, setCustomer] = useState<any>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchCustomerData();
    fetchUsers();
  }, [customerId]);

  const fetchCustomerData = async () => {
    try {
      const response = await apiClient.get(`/portal/founder/customers/${customerId}`);
      setCustomer(response);
    } catch (err: any) {
      setError(err.message || "Failed to load customer data");
    }
  };

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/portal/founder/customers/${customerId}/users`);
      setUsers(response.users);
    } catch (err: any) {
      setError(err.message || "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  // Fallback data while loading or if API fails
  if (!customer) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black mx-auto mb-4"></div>
            Loading customer details...
          </div>
        </main>
      </div>
    );
  }

  const activity = [
    { action: "Template generated", user: "John Doe", timestamp: "2026-02-06 10:30 AM" },
    { action: "User activated", user: "Jane Smith", timestamp: "2026-02-06 09:15 AM" },
    { action: "Invoice paid", user: "System", timestamp: "2026-02-05 08:00 PM" },
    { action: "Template generated", user: "Bob Johnson", timestamp: "2026-02-05 03:45 PM" },
  ];

  const invoices = [
    { invoice_number: "INV-2026-002", date: "2026-02-01", amount: 900.00, status: "paid" },
    { invoice_number: "INV-2026-001", date: "2026-01-01", amount: 900.00, status: "paid" },
  ];

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <Link href="/customers" className="text-black hover:underline mb-4 inline-block">
            ← Back to Customers
          </Link>
          <h1 className="text-4xl mb-2 text-black">{customer.org_name}</h1>
          <p className="text-black">{customer.admin_email}</p>
        </div>

        {/* Customer Overview */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-2xl mb-2 text-black">Subscription Overview</h2>
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded text-sm ${
                  customer.status === 'active' ? 'bg-green-100 text-green-800' :
                  customer.status === 'trial' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {customer.status.toUpperCase()}
                </span>
                <span className="text-black">•</span>
                <span className="text-black">Created {new Date(customer.created_at).toLocaleDateString()}</span>
              </div>
            </div>
            <div className="flex gap-3">
              <button className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors text-black">
                Edit Details
              </button>
              <button className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors">
                Generate License
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <div className="text-gray-500 text-sm mb-1">Seats Purchased</div>
              <div className="text-2xl font-light text-black">{customer.seats_purchased}</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Seats Used</div>
              <div className="text-2xl font-light text-black">{customer.seats_used}</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Rate per Seat</div>
              <div className="text-2xl font-light text-black">{formatCurrency(customer.seat_rate)}/mo</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Monthly Revenue</div>
              <div className="text-2xl font-light text-black">{formatCurrency(customer.mrr)}</div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="text-sm text-gray-500 mb-1">License Key</div>
              <div className="flex items-center gap-2">
                <code className="text-black bg-gray-50 px-3 py-1 rounded font-mono text-sm">
                  {customer.license_key}
                </code>
                <button className="text-sm text-black hover:underline">Copy</button>
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500 mb-1">Next Billing Date</div>
              <div className="text-black">{new Date(customer.next_billing_date).toLocaleDateString()}</div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Users */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h2 className="text-xl text-black">Users ({users.length})</h2>
              <Link
                href={`/users?org_id=${customerId}`}
                className="text-sm text-black hover:underline"
              >
                View All →
              </Link>
            </div>
            <div className="p-6">
              {loading ? (
                <div className="text-center py-8 text-gray-500">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-black mx-auto mb-2"></div>
                  Loading users...
                </div>
              ) : users.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No users in this organization yet.
                </div>
              ) : (
                <div className="space-y-3">
                  {users.map((user) => (
                    <div key={user.user_id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <div className="flex-1">
                        <div className="text-black font-medium">
                          {user.first_name && user.last_name
                            ? `${user.first_name} ${user.last_name}`
                            : user.email}
                        </div>
                        <div className="text-sm text-gray-600">{user.email}</div>
                        <div className="text-xs text-gray-400 mt-1">
                          {user.device_count > 0 ? `${user.device_count} device${user.device_count !== 1 ? 's' : ''}` : 'No devices'}
                          {user.last_login && ` • Last login ${new Date(user.last_login).toLocaleDateString()}`}
                        </div>
                      </div>
                      <div className="text-right flex items-center gap-2">
                        <div className={`px-2 py-1 text-xs rounded ${
                          user.role === 'admin' || user.role === 'super_admin' ? 'bg-black text-white' : 'bg-gray-200 text-black'
                        }`}>
                          {user.role}
                        </div>
                        {!user.is_active && (
                          <span className="px-2 py-1 text-xs rounded bg-red-100 text-red-800">
                            Inactive
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl text-black">Recent Activity</h2>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                {activity.map((item, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded">
                    <div className="w-2 h-2 rounded-full bg-black mt-1.5" />
                    <div className="flex-1">
                      <div className="text-black text-sm">{item.action}</div>
                      <div className="text-xs text-gray-600 mt-1">
                        {item.user} • {item.timestamp}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Invoices */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl text-black">Invoice History</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Invoice Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {invoices.map((invoice, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-black font-medium">
                      {invoice.invoice_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {new Date(invoice.date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {formatCurrency(invoice.amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-800">
                        {invoice.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
