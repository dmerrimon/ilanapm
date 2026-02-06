'use client';

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  const systemMetrics = {
    total_templates: 24567,
    avg_response_time: 2.1,
    api_requests: 156789,
    ml_accuracy: 94.2,
    total_users: 312,
    active_organizations: 12
  };

  const mlPerformance = [
    { metric: "FDA 510(k) Accuracy", value: 96.5, trend: "up" },
    { metric: "CE Mark Accuracy", value: 94.8, trend: "up" },
    { metric: "Risk Assessment Accuracy", value: 92.3, trend: "stable" },
    { metric: "Clinical Evaluation Accuracy", value: 95.1, trend: "up" },
  ];

  const apiEndpoints = [
    { endpoint: "/api/v1/templates/generate", calls: 45623, avg_time: 2.1, errors: 23 },
    { endpoint: "/api/v1/feedback/submit", calls: 12456, avg_time: 0.8, errors: 5 },
    { endpoint: "/api/v1/auth/login", calls: 8934, avg_time: 0.5, errors: 12 },
    { endpoint: "/api/v1/portal/customer/dashboard", calls: 6234, avg_time: 1.2, errors: 3 },
  ];

  const dailyUsage = [
    { date: "Feb 1", templates: 842, users: 145 },
    { date: "Feb 2", templates: 798, users: 138 },
    { date: "Feb 3", templates: 965, users: 162 },
    { date: "Feb 4", templates: 887, users: 151 },
    { date: "Feb 5", templates: 1024, users: 178 },
    { date: "Feb 6", templates: 953, users: 167 },
  ];

  const maxTemplates = Math.max(...dailyUsage.map(d => d.templates));
  const maxUsers = Math.max(...dailyUsage.map(d => d.users));

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
                <Link href="/customers" className="text-gray-600 hover:text-black transition-colors">
                  Customers
                </Link>
                <Link href="/analytics" className="text-black font-medium">
                  Analytics
                </Link>
                <Link href="/licenses" className="text-gray-600 hover:text-black transition-colors">
                  Licenses
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
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl mb-2 text-black">System Analytics</h1>
            <p className="text-black">Platform-wide performance and usage metrics</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setTimeRange('7d')}
              className={`px-4 py-2 rounded transition-colors ${
                timeRange === '7d'
                  ? 'bg-black text-white'
                  : 'bg-white text-black border border-gray-300 hover:bg-gray-50'
              }`}
            >
              7 Days
            </button>
            <button
              onClick={() => setTimeRange('30d')}
              className={`px-4 py-2 rounded transition-colors ${
                timeRange === '30d'
                  ? 'bg-black text-white'
                  : 'bg-white text-black border border-gray-300 hover:bg-gray-50'
              }`}
            >
              30 Days
            </button>
            <button
              onClick={() => setTimeRange('90d')}
              className={`px-4 py-2 rounded transition-colors ${
                timeRange === '90d'
                  ? 'bg-black text-white'
                  : 'bg-white text-black border border-gray-300 hover:bg-gray-50'
              }`}
            >
              90 Days
            </button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Templates Generated</div>
            <div className="text-3xl font-light text-black">{systemMetrics.total_templates.toLocaleString()}</div>
            <div className="text-sm text-green-600 mt-2">↑ 18% from last period</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Active Users</div>
            <div className="text-3xl font-light text-black">{systemMetrics.total_users}</div>
            <div className="text-sm text-green-600 mt-2">↑ 12% from last period</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Avg Response Time</div>
            <div className="text-3xl font-light text-black">{systemMetrics.avg_response_time}s</div>
            <div className="text-sm text-green-600 mt-2">↓ 8% faster</div>
          </div>
        </div>

        {/* Daily Usage Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl mb-6 text-black">Daily Platform Usage</h2>
          <div className="space-y-4">
            {dailyUsage.map((day) => (
              <div key={day.date}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-black w-16">{day.date}</span>
                  <div className="flex-1 ml-4">
                    <div className="text-xs text-gray-600 mb-1">
                      Templates: {day.templates} • Users: {day.users}
                    </div>
                    <div className="flex gap-2">
                      <div className="flex-1 bg-gray-100 rounded-full h-6 relative">
                        <div
                          className="bg-black rounded-full h-6 flex items-center justify-end pr-2"
                          style={{ width: `${(day.templates / maxTemplates) * 100}%` }}
                        >
                          <span className="text-white text-xs font-medium">{day.templates}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* ML Performance */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl mb-6 text-black">ML Model Performance</h2>
            <div className="space-y-4">
              {mlPerformance.map((item) => (
                <div key={item.metric}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-black text-sm">{item.metric}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-black font-medium">{item.value}%</span>
                      <span className={`text-xs ${
                        item.trend === 'up' ? 'text-green-600' :
                        item.trend === 'down' ? 'text-red-600' :
                        'text-gray-600'
                      }`}>
                        {item.trend === 'up' ? '↑' : item.trend === 'down' ? '↓' : '→'}
                      </span>
                    </div>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-black rounded-full h-2"
                      style={{ width: `${item.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="text-sm text-gray-600 mb-1">Overall ML Accuracy</div>
              <div className="text-3xl font-light text-black">{systemMetrics.ml_accuracy}%</div>
            </div>
          </div>

          {/* API Endpoints */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl mb-6 text-black">Top API Endpoints</h2>
            <div className="space-y-3">
              {apiEndpoints.map((endpoint) => (
                <div key={endpoint.endpoint} className="p-3 bg-gray-50 rounded">
                  <div className="text-black font-mono text-xs mb-2">{endpoint.endpoint}</div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <div className="text-gray-600 text-xs">Calls</div>
                      <div className="text-black font-medium">{endpoint.calls.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-gray-600 text-xs">Avg Time</div>
                      <div className="text-black font-medium">{endpoint.avg_time}s</div>
                    </div>
                    <div>
                      <div className="text-gray-600 text-xs">Errors</div>
                      <div className={`font-medium ${endpoint.errors > 10 ? 'text-red-600' : 'text-green-600'}`}>
                        {endpoint.errors}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* System Health */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl mb-6 text-black">System Health Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <div className="text-gray-500 text-sm mb-1">API Requests (30d)</div>
              <div className="text-2xl font-light text-black">{systemMetrics.api_requests.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Active Organizations</div>
              <div className="text-2xl font-light text-black">{systemMetrics.active_organizations}</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Error Rate</div>
              <div className="text-2xl font-light text-green-600">0.03%</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Uptime</div>
              <div className="text-2xl font-light text-green-600">99.8%</div>
            </div>
          </div>
        </div>

        {/* Export Options */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg text-black mb-1">Export System Analytics</h3>
              <p className="text-black text-sm">Download comprehensive analytics report</p>
            </div>
            <div className="flex gap-3">
              <button className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors text-black">
                Export CSV
              </button>
              <button className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors">
                Export PDF Report
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
