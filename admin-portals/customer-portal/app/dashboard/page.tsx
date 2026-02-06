'use client';

import Image from "next/image";
import Link from "next/link";

export default function DashboardPage() {
  // TODO: Fetch actual data from FastAPI backend
  const orgData = {
    org_name: "Demo Organization",
    license_key: "SELEEN-****-****-XXXX",
    status: "active",
    tier: "standard",
    seats_purchased: 50,
    seats_used: 23,
    seats_available: 27,
    seat_rate: 18.00,
    billing_cycle: "monthly",
    mrr: 414.00,
    next_billing_date: "2026-03-06",
  };

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
                <Link href="/dashboard" className="text-black font-medium">
                  Dashboard
                </Link>
                <Link href="/users" className="text-gray-600 hover:text-black transition-colors">
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
            <p className="text-xl font-mono">{orgData.license_key}</p>
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
            <p className="text-sm opacity-70 mb-1">Monthly Cost</p>
            <p className="text-2xl">${orgData.mrr.toFixed(2)}</p>
            <p className="text-xs opacity-50 mt-2">
              ${orgData.seat_rate.toFixed(2)}/seat/month
            </p>
          </div>
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
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

        {/* Recent Activity */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl mb-4">Recent Activity</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div>
                <p className="text-sm">User activated</p>
                <p className="text-xs opacity-50">john.doe@example.com</p>
              </div>
              <p className="text-xs opacity-50">2 hours ago</p>
            </div>
            <div className="flex items-center justify-between py-3 border-b border-gray-100">
              <div>
                <p className="text-sm">Template generated</p>
                <p className="text-xs opacity-50">Full Study Timeline - Uganda</p>
              </div>
              <p className="text-xs opacity-50">5 hours ago</p>
            </div>
            <div className="flex items-center justify-between py-3">
              <div>
                <p className="text-sm">Billing updated</p>
                <p className="text-xs opacity-50">Payment method changed</p>
              </div>
              <p className="text-xs opacity-50">1 day ago</p>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg mb-2">Templates Generated</h3>
            <p className="text-3xl mb-1">127</p>
            <p className="text-xs opacity-50">Last 30 days</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg mb-2">Feedback Submitted</h3>
            <p className="text-3xl mb-1">43</p>
            <p className="text-xs opacity-50">Last 30 days</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg mb-2">Active Users</h3>
            <p className="text-3xl mb-1">18</p>
            <p className="text-xs opacity-50">Last 7 days</p>
          </div>
        </div>

        {/* Billing Info */}
        <div className="mt-8 bg-blue-50 border border-blue-200 p-6 rounded-lg">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg mb-2">Next Billing Date</h3>
              <p className="text-sm opacity-70">
                Your next payment of <strong>${orgData.mrr.toFixed(2)}</strong> will be processed on{" "}
                <strong>{orgData.next_billing_date}</strong>
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
      </main>
    </div>
  );
}
