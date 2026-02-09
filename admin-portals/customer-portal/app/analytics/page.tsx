'use client';

import { useState, useRef } from "react";
import Header from "@/components/Header";
import { exportMultipleSectionsToCSV, generateFilename } from "@/lib/export-utils";
import { exportUsageAnalyticsPDF } from "@/lib/pdf-export-utils";

// Tab types
type AnalyticsTab = 'usage' | 'intelligence';

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
  const [activeTab, setActiveTab] = useState<AnalyticsTab>('usage');
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
            <h1 className="text-4xl mb-2 text-black">Analytics</h1>
            <p className="text-black">Track usage, intelligence performance, and system insights.</p>
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

        {/* Tab Navigation */}
        <div className="mb-8 border-b border-gray-200">
          <div className="flex gap-8">
            <button
              onClick={() => setActiveTab('usage')}
              className={`pb-4 px-1 border-b-2 font-medium transition-colors ${
                activeTab === 'usage'
                  ? 'border-black text-black'
                  : 'border-transparent text-gray-500 hover:text-black hover:border-gray-300'
              }`}
            >
              Usage Analytics
            </button>
            <button
              onClick={() => setActiveTab('intelligence')}
              className={`pb-4 px-1 border-b-2 font-medium transition-colors relative ${
                activeTab === 'intelligence'
                  ? 'border-black text-black'
                  : 'border-transparent text-gray-500 hover:text-black hover:border-gray-300'
              }`}
            >
              Intelligence Analytics
              <span className="ml-2 px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full">NEW</span>
            </button>
          </div>
        </div>

        {/* Usage Analytics Tab Content */}
        {activeTab === 'usage' && (
          <>
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
          </>
        )}

        {/* Intelligence Analytics Tab Content */}
        {activeTab === 'intelligence' && (
          <div>
            {/* Intelligence Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="text-gray-500 text-sm mb-1">Variance Analyses</div>
                <div className="text-3xl font-light text-black">247</div>
                <div className="text-sm text-green-600 mt-2">↑ 18% from last period</div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="text-gray-500 text-sm mb-1">Avg Benchmark Coverage</div>
                <div className="text-3xl font-light text-black">78%</div>
                <div className="text-sm text-green-600 mt-2">↑ 5% improvement</div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="text-gray-500 text-sm mb-1">Total Financial Impact</div>
                <div className="text-3xl font-light text-black">$2.4M</div>
                <div className="text-sm text-gray-600 mt-2">Potential savings identified</div>
              </div>
            </div>

            {/* High Variance Tasks */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
              <h2 className="text-xl mb-6 text-black">High Variance Tasks</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Task Name</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Your Duration</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Benchmark</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Variance</th>
                      <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Severity</th>
                      <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Financial Impact</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4 text-black">Site Contract Negotiation</td>
                      <td className="py-4 px-4 text-black">90 days</td>
                      <td className="py-4 px-4 text-gray-600">280 days</td>
                      <td className="py-4 px-4">
                        <span className="text-red-600 font-medium">-67.9%</span>
                        <span className="ml-2 text-sm text-gray-500">(underestimate)</span>
                      </td>
                      <td className="py-4 px-4">
                        <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                          Critical
                        </span>
                      </td>
                      <td className="py-4 px-4 text-right text-red-600 font-medium">-$4.6M</td>
                    </tr>
                    <tr className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4 text-black">Patient Enrollment</td>
                      <td className="py-4 px-4 text-black">180 days</td>
                      <td className="py-4 px-4 text-gray-600">365 days</td>
                      <td className="py-4 px-4">
                        <span className="text-red-600 font-medium">-50.7%</span>
                        <span className="ml-2 text-sm text-gray-500">(underestimate)</span>
                      </td>
                      <td className="py-4 px-4">
                        <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                          Critical
                        </span>
                      </td>
                      <td className="py-4 px-4 text-right text-red-600 font-medium">-$4.5M</td>
                    </tr>
                    <tr className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4 text-black">Ethics Committee Review</td>
                      <td className="py-4 px-4 text-black">60 days</td>
                      <td className="py-4 px-4 text-gray-600">45 days</td>
                      <td className="py-4 px-4">
                        <span className="text-amber-600 font-medium">+33.3%</span>
                        <span className="ml-2 text-sm text-gray-500">(overestimate)</span>
                      </td>
                      <td className="py-4 px-4">
                        <span className="px-2 py-1 text-xs font-medium bg-amber-100 text-amber-800 rounded">
                          Warning
                        </span>
                      </td>
                      <td className="py-4 px-4 text-right text-green-600 font-medium">+$366K</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Benchmark Coverage by Category */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
              <h2 className="text-xl mb-6 text-black">Benchmark Coverage by Category</h2>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-black">Regulatory Submissions</span>
                    <span className="text-black font-medium">95% coverage</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-green-600 rounded-full h-3" style={{ width: '95%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-black">Ethics Approvals</span>
                    <span className="text-black font-medium">82% coverage</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-green-600 rounded-full h-3" style={{ width: '82%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-black">Site Contracting</span>
                    <span className="text-black font-medium">76% coverage</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-amber-600 rounded-full h-3" style={{ width: '76%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-black">Patient Enrollment</span>
                    <span className="text-black font-medium">68% coverage</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-amber-600 rounded-full h-3" style={{ width: '68%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-black">Clinical Procedures</span>
                    <span className="text-black font-medium">54% coverage</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-red-600 rounded-full h-3" style={{ width: '54%' }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Intelligence Insights */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-blue-900 mb-4">💡 Key Insights</h3>
              <ul className="space-y-3 text-blue-900">
                <li className="flex items-start gap-3">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span><strong>Site contracting</strong> consistently underestimated by 50-70%. Consider adding 6-9 months to initial estimates.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span><strong>Patient enrollment</strong> times vary widely by therapeutic area. Oncology studies averaging 12 months vs 6 months for cardiovascular.</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-blue-600 mt-0.5">•</span>
                  <span><strong>Regulatory review</strong> timelines are highly accurate (within 10% of benchmarks). Your planning here is solid.</span>
                </li>
              </ul>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
