'use client';

import { useState, useRef } from "react";
import Header from "@/components/Header";
import { exportMultipleSectionsToCSV, generateFilename } from "@/lib/export-utils";
import { exportUsageAnalyticsPDF } from "@/lib/pdf-export-utils";

interface TemplateUsage {
  template_name: string;
  count: number;
}

interface UserActivity {
  user_name: string;
  templates_generated: number;
}

interface CountryData {
  country: string;
  count: number;
}

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  // Refs for capturing chart elements
  const dailyActivityRef = useRef<HTMLDivElement>(null);
  const templateUsageRef = useRef<HTMLDivElement>(null);
  const userActivityRef = useRef<HTMLDivElement>(null);
  const countryDataRef = useRef<HTMLDivElement>(null);

  const stats = {
    templates_generated: 1247,
    feedback_submissions: 89,
    active_users: 23,
    avg_response_time: 2.3
  };

  const templateUsage: TemplateUsage[] = [
    { template_name: "FDA 510(k) Submission", count: 342 },
    { template_name: "CE Mark Technical File", count: 289 },
    { template_name: "Risk Management Plan", count: 215 },
    { template_name: "Clinical Evaluation Report", count: 178 },
    { template_name: "Design History File", count: 142 },
    { template_name: "Post-Market Surveillance", count: 81 }
  ];

  const userActivity: UserActivity[] = [
    { user_name: "John Doe", templates_generated: 134 },
    { user_name: "Jane Smith", templates_generated: 98 },
    { user_name: "Bob Johnson", templates_generated: 87 },
    { user_name: "Alice Williams", templates_generated: 76 },
    { user_name: "Charlie Brown", templates_generated: 54 }
  ];

  const countryData: CountryData[] = [
    { country: "United States (FDA)", count: 487 },
    { country: "European Union (CE)", count: 356 },
    { country: "United Kingdom (MHRA)", count: 198 },
    { country: "Canada (Health Canada)", count: 124 },
    { country: "Australia (TGA)", count: 82 }
  ];

  const dailyActivity = [
    { date: "Feb 1", count: 42 },
    { date: "Feb 2", count: 38 },
    { date: "Feb 3", count: 55 },
    { date: "Feb 4", count: 47 },
    { date: "Feb 5", count: 61 },
    { date: "Feb 6", count: 53 }
  ];

  const maxValue = Math.max(...templateUsage.map(t => t.count));
  const maxUserActivity = Math.max(...userActivity.map(u => u.templates_generated));
  const maxCountry = Math.max(...countryData.map(c => c.count));
  const maxDaily = Math.max(...dailyActivity.map(d => d.count));

  const handleExportCSV = () => {
    const sections = [
      {
        title: 'Overview Statistics',
        data: [{
          metric: 'Templates Generated',
          value: stats.templates_generated,
          time_range: timeRange
        }, {
          metric: 'Feedback Submissions',
          value: stats.feedback_submissions,
          time_range: timeRange
        }, {
          metric: 'Active Users',
          value: stats.active_users,
          time_range: timeRange
        }, {
          metric: 'Avg Response Time (seconds)',
          value: stats.avg_response_time,
          time_range: timeRange
        }]
      },
      {
        title: 'Daily Template Generation',
        data: dailyActivity
      },
      {
        title: 'Most Used Templates',
        data: templateUsage
      },
      {
        title: 'Most Active Users',
        data: userActivity
      },
      {
        title: 'Templates by Regulatory Authority',
        data: countryData
      }
    ];

    const filename = generateFilename(`usage-analytics-${timeRange}`);
    exportMultipleSectionsToCSV(sections, filename);
  };

  const handleExportPDF = async () => {
    await exportUsageAnalyticsPDF({
      timeRange,
      stats,
      chartElements: {
        dailyActivity: dailyActivityRef.current,
        templateUsage: templateUsageRef.current,
        userActivity: userActivityRef.current,
        countryData: countryDataRef.current
      },
      tableData: {
        templateUsage,
        userActivity,
        countryData,
        dailyActivity
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
            <h1 className="text-4xl mb-2 text-black">Usage Analytics</h1>
            <p className="text-black">Track template generation, user activity, and system usage.</p>
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Templates Generated</div>
            <div className="text-3xl font-light text-black">{stats.templates_generated}</div>
            <div className="text-sm text-green-600 mt-2">↑ 12% from last period</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Feedback Submissions</div>
            <div className="text-3xl font-light text-black">{stats.feedback_submissions}</div>
            <div className="text-sm text-green-600 mt-2">↑ 8% from last period</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Active Users</div>
            <div className="text-3xl font-light text-black">{stats.active_users}</div>
            <div className="text-sm text-gray-600 mt-2">→ No change</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Avg Response Time</div>
            <div className="text-3xl font-light text-black">{stats.avg_response_time}s</div>
            <div className="text-sm text-green-600 mt-2">↓ 15% faster</div>
          </div>
        </div>

        {/* Daily Activity Chart */}
        <div ref={dailyActivityRef} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl mb-6 text-black">Daily Template Generation</h2>
          <div className="space-y-3">
            {dailyActivity.map((day) => (
              <div key={day.date} className="flex items-center gap-4">
                <div className="w-16 text-sm text-black">{day.date}</div>
                <div className="flex-1 bg-gray-100 rounded-full h-8 relative">
                  <div
                    className="bg-black rounded-full h-8 flex items-center justify-end pr-3"
                    style={{ width: `${(day.count / maxDaily) * 100}%` }}
                  >
                    <span className="text-white text-sm font-medium">{day.count}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Most Used Templates */}
          <div ref={templateUsageRef} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl mb-6 text-black">Most Used Templates</h2>
            <div className="space-y-4">
              {templateUsage.map((template, index) => (
                <div key={template.template_name}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-black text-sm">{template.template_name}</span>
                    <span className="text-black font-medium">{template.count}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className="bg-black rounded-full h-2"
                      style={{ width: `${(template.count / maxValue) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Most Active Users */}
          <div ref={userActivityRef} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl mb-6 text-black">Most Active Users</h2>
            <div className="space-y-4">
              {userActivity.map((user, index) => (
                <div key={user.user_name}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                        <span className="text-black text-sm font-medium">
                          {user.user_name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <span className="text-black text-sm">{user.user_name}</span>
                    </div>
                    <span className="text-black font-medium">{user.templates_generated}</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2 ml-11">
                    <div
                      className="bg-black rounded-full h-2"
                      style={{ width: `${(user.templates_generated / maxUserActivity) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Regulatory Authority Distribution */}
        <div ref={countryDataRef} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl mb-6 text-black">Templates by Regulatory Authority</h2>
          <div className="space-y-4">
            {countryData.map((country) => (
              <div key={country.country}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-black">{country.country}</span>
                  <span className="text-black font-medium">{country.count} templates</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-3">
                  <div
                    className="bg-black rounded-full h-3"
                    style={{ width: `${(country.count / maxCountry) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Export Options */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg text-black mb-1">Export Analytics Data</h3>
              <p className="text-black text-sm">Download your usage data for custom analysis</p>
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
