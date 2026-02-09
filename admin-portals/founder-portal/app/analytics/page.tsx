'use client';

import { useState, useRef } from "react";
import Header from "@/components/Header";
import { exportMultipleSectionsToCSV, generateFilename } from "@/lib/export-utils";
import { exportSystemAnalyticsPDF } from "@/lib/pdf-export-utils";

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  // Refs for capturing chart elements
  const dailyUsageRef = useRef<HTMLDivElement>(null);
  const mlPerformanceRef = useRef<HTMLDivElement>(null);
  const apiEndpointsRef = useRef<HTMLDivElement>(null);

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

  // Core Tier Intelligence Metrics (Mock data)
  const intelligenceMetrics = {
    total_core_customers: 8,
    variance_detections_30d: 247,
    avg_high_variance_tasks: 5.2,
    avg_financial_impact: 487000,
    adoption_funnel: {
      total_customers: 8,
      used_feature: 7,
      viewed_portal: 5,
      upgraded: 0
    },
    top_variance_categories: [
      { category: "Site Contract Execution", count: 42 },
      { category: "Ethics Committee Approval", count: 38 },
      { category: "IND/CTA Submission", count: 35 },
      { category: "Patient Enrollment", count: 29 },
      { category: "Site Initiation Visit", count: 24 }
    ]
  };

  const handleExportCSV = () => {
    const sections = [
      {
        title: 'System Metrics Overview',
        data: [{
          metric: 'Total Templates',
          value: systemMetrics.total_templates,
          time_range: timeRange
        }, {
          metric: 'Avg Response Time (seconds)',
          value: systemMetrics.avg_response_time,
          time_range: timeRange
        }, {
          metric: 'API Requests',
          value: systemMetrics.api_requests,
          time_range: timeRange
        }, {
          metric: 'ML Accuracy (%)',
          value: systemMetrics.ml_accuracy,
          time_range: timeRange
        }, {
          metric: 'Total Users',
          value: systemMetrics.total_users,
          time_range: timeRange
        }, {
          metric: 'Active Organizations',
          value: systemMetrics.active_organizations,
          time_range: timeRange
        }]
      },
      {
        title: 'Daily Platform Usage',
        data: dailyUsage
      },
      {
        title: 'ML Model Performance',
        data: mlPerformance
      },
      {
        title: 'Top API Endpoints',
        data: apiEndpoints
      }
    ];

    const filename = generateFilename(`system-analytics-${timeRange}`);
    exportMultipleSectionsToCSV(sections, filename);
  };

  const handleExportPDF = async () => {
    await exportSystemAnalyticsPDF({
      timeRange,
      systemMetrics,
      chartElements: {
        dailyUsage: dailyUsageRef.current,
        mlPerformance: mlPerformanceRef.current,
        apiEndpoints: apiEndpointsRef.current
      },
      tableData: {
        dailyUsage,
        mlPerformance,
        apiEndpoints
      }
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

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
        <div ref={dailyUsageRef} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
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
          <div ref={mlPerformanceRef} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
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
          <div ref={apiEndpointsRef} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
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
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
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

        {/* Core Tier Intelligence Usage */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl text-black">Core Tier Intelligence Usage</h2>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-medium rounded-full">
              Last 30 Days
            </span>
          </div>

          {/* Key Metrics Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div>
              <div className="text-gray-500 text-sm mb-1">Core Customers</div>
              <div className="text-3xl font-light text-black">{intelligenceMetrics.total_core_customers}</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Variance Detections</div>
              <div className="text-3xl font-light text-black">{intelligenceMetrics.variance_detections_30d}</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Avg High-Variance Tasks</div>
              <div className="text-3xl font-light text-black">{intelligenceMetrics.avg_high_variance_tasks}</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Avg Financial Impact</div>
              <div className="text-3xl font-light text-black">
                ${(intelligenceMetrics.avg_financial_impact / 1000).toFixed(0)}K
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Adoption Funnel */}
            <div>
              <h3 className="text-base font-medium text-black mb-4">Adoption Funnel</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-black">Total Core Customers</span>
                    <span className="text-black font-medium">{intelligenceMetrics.adoption_funnel.total_customers}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-8">
                    <div
                      className="bg-blue-600 rounded-full h-8 flex items-center justify-center text-white text-sm font-medium"
                      style={{ width: '100%' }}
                    >
                      100%
                    </div>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-black">Used Intelligence Feature</span>
                    <span className="text-black font-medium">{intelligenceMetrics.adoption_funnel.used_feature}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-8">
                    <div
                      className="bg-blue-600 rounded-full h-8 flex items-center justify-center text-white text-sm font-medium"
                      style={{ width: `${(intelligenceMetrics.adoption_funnel.used_feature / intelligenceMetrics.adoption_funnel.total_customers) * 100}%` }}
                    >
                      {Math.round((intelligenceMetrics.adoption_funnel.used_feature / intelligenceMetrics.adoption_funnel.total_customers) * 100)}%
                    </div>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-black">Viewed Intelligence Portal</span>
                    <span className="text-black font-medium">{intelligenceMetrics.adoption_funnel.viewed_portal}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-8">
                    <div
                      className="bg-blue-600 rounded-full h-8 flex items-center justify-center text-white text-sm font-medium"
                      style={{ width: `${(intelligenceMetrics.adoption_funnel.viewed_portal / intelligenceMetrics.adoption_funnel.total_customers) * 100}%` }}
                    >
                      {Math.round((intelligenceMetrics.adoption_funnel.viewed_portal / intelligenceMetrics.adoption_funnel.total_customers) * 100)}%
                    </div>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-black">Upgraded to Calibrated</span>
                    <span className="text-black font-medium">{intelligenceMetrics.adoption_funnel.upgraded}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-8">
                    <div
                      className="bg-green-600 rounded-full h-8 flex items-center justify-center text-white text-sm font-medium"
                      style={{ width: intelligenceMetrics.adoption_funnel.upgraded > 0 ? `${(intelligenceMetrics.adoption_funnel.upgraded / intelligenceMetrics.adoption_funnel.total_customers) * 100}%` : '10%', minWidth: '10%' }}
                    >
                      {intelligenceMetrics.adoption_funnel.upgraded > 0 ? `${Math.round((intelligenceMetrics.adoption_funnel.upgraded / intelligenceMetrics.adoption_funnel.total_customers) * 100)}%` : '0%'}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  <strong>Conversion Rate:</strong> {Math.round((intelligenceMetrics.adoption_funnel.viewed_portal / intelligenceMetrics.adoption_funnel.used_feature) * 100)}% of users view portal after using feature
                </div>
              </div>
            </div>

            {/* Top Variance Categories */}
            <div>
              <h3 className="text-base font-medium text-black mb-4">Most Common High-Variance Categories</h3>
              <div className="space-y-3">
                {intelligenceMetrics.top_variance_categories.map((item, index) => (
                  <div key={item.category} className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-sm font-medium text-black">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="text-sm text-black mb-1">{item.category}</div>
                      <div className="w-full bg-gray-100 rounded-full h-2">
                        <div
                          className="bg-amber-600 rounded-full h-2"
                          style={{ width: `${(item.count / intelligenceMetrics.top_variance_categories[0].count) * 100}%` }}
                        />
                      </div>
                    </div>
                    <div className="text-sm font-medium text-black">{item.count}</div>
                  </div>
                ))}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="text-sm text-gray-600">
                  Total high-variance detections across all categories: {intelligenceMetrics.top_variance_categories.reduce((sum, item) => sum + item.count, 0)}
                </div>
              </div>
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
              <button
                onClick={handleExportCSV}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors text-black"
              >
                Export CSV
              </button>
              <button
                onClick={handleExportPDF}
                className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors"
              >
                Export PDF Report
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
