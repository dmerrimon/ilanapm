'use client';

import { useState, useEffect } from "react";
import Link from "next/link";
import Header from "@/components/Header";
import { apiClient } from "@/lib/api-client";

interface DashboardData {
  org_name: string;
  license_key: string | null;
  status: string;
  tier: string;
  seats_purchased: number;
  seats_used: number;
  seats_available: number;
  active_devices: number;
  active_users: number;
  seat_rate: number | null;
  billing_cycle: string;
  mrr: number | null;
  next_billing_date: string | null;
  subscription_end: string;
}

export default function DashboardPage() {
  const [orgData, setOrgData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await apiClient.get('/portal/customer/dashboard');
      setOrgData(response);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
              <p className="text-gray-600">Loading dashboard...</p>
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error || !orgData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
            {error || "Failed to load dashboard data"}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl mb-2">Dashboard</h1>
          <p className="text-sm opacity-70">
            Overview of your Seleen organization
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm opacity-70 mb-1">Organization</p>
            <p className="text-2xl">{orgData.org_name}</p>
            <p className="text-xs opacity-50 mt-2">Status: {orgData.status}</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm opacity-70 mb-1">License Key</p>
            <p className="text-xl font-mono">{orgData.license_key || "N/A"}</p>
            <p className="text-xs opacity-50 mt-2">Tier: {orgData.tier}</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm opacity-70 mb-1">Seats</p>
            <p className="text-2xl">
              {orgData.seats_used} / {orgData.seats_purchased}
            </p>
            <p className="text-xs opacity-50 mt-2">
              {orgData.seats_available} available
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <p className="text-sm opacity-70 mb-1">Active Devices</p>
            <p className="text-2xl">{orgData.active_devices}</p>
            <p className="text-xs opacity-50 mt-2">
              {orgData.active_users} active users
            </p>
          </div>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Link
            href="/users"
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
          >
            <h3 className="text-xl mb-2">Manage Users</h3>
            <p className="text-sm opacity-70 mb-4">
              Add or remove users, reassign seats, and manage permissions
            </p>
            <div className="text-sm hover:underline">View users →</div>
          </Link>

          <Link
            href="/devices"
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
          >
            <h3 className="text-xl mb-2">Active Devices</h3>
            <p className="text-sm opacity-70 mb-4">
              View and manage device activations across your organization
            </p>
            <div className="text-sm hover:underline">View devices →</div>
          </Link>

          <Link
            href="/billing"
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
          >
            <h3 className="text-xl mb-2">Billing & Invoices</h3>
            <p className="text-sm opacity-70 mb-4">
              Update payment methods, view invoices, and add more seats
            </p>
            <div className="text-sm hover:underline">Manage billing →</div>
          </Link>

          <Link
            href="/analytics"
            className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
          >
            <h3 className="text-xl mb-2">Usage Analytics</h3>
            <p className="text-sm opacity-70 mb-4">
              Track template generation, feedback, and team activity
            </p>
            <div className="text-sm hover:underline">View analytics →</div>
          </Link>
        </div>

        {/* Subscription Info */}
        {orgData.next_billing_date && orgData.mrr && (
          <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg mb-2">Next Billing Date</h3>
                <p className="text-sm opacity-70">
                  Your next payment of <strong>${orgData.mrr.toFixed(2)}</strong> will be processed on{" "}
                  <strong>{new Date(orgData.next_billing_date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}</strong>
                </p>
              </div>
              <Link
                href="/billing"
                className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors text-sm"
              >
                Update Payment
              </Link>
            </div>
          </div>
        )}

        {/* Subscription End Warning */}
        {orgData.subscription_end && (
          <div className="mt-6 bg-gray-50 border border-gray-200 p-6 rounded-lg">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg mb-2">Subscription Status</h3>
                <p className="text-sm opacity-70">
                  Your subscription is valid until{" "}
                  <strong>{new Date(orgData.subscription_end).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}</strong>
                </p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
