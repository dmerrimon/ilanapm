'use client';

import { useState } from "react";
import Header from "@/components/Header";

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl mb-2 text-black">Intelligence Analytics</h1>
            <p className="text-black">Track timeline variance detection, benchmark coverage, and optimization insights.</p>
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
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 relative">
            <div className="absolute top-3 right-3">
              <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                Coming Soon
              </span>
            </div>
            <div className="text-gray-400 text-sm mb-1">Financial Impact Analysis</div>
            <div className="text-3xl font-light text-gray-300">--</div>
            <div className="text-sm text-gray-400 mt-2">Feature in development</div>
          </div>
        </div>

        {/* High Variance Tasks */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl mb-6 text-black">High Variance Tasks</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-black">Task Name</th>
                  <th className="text-left py-3 px-4 text-black">Your Duration</th>
                  <th className="text-left py-3 px-4 text-black">Benchmark</th>
                  <th className="text-left py-3 px-4 text-black">Variance</th>
                  <th className="text-left py-3 px-4 text-black">Impact</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-gray-100">
                  <td className="py-4 px-4 text-black">IRB/EC Review & Approval</td>
                  <td className="py-4 px-4 text-black">65 days</td>
                  <td className="py-4 px-4 text-gray-600">45 days</td>
                  <td className="py-4 px-4">
                    <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm">+44%</span>
                  </td>
                  <td className="py-4 px-4 text-black">High</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-4 px-4 text-black">Site Identification & Feasibility</td>
                  <td className="py-4 px-4 text-black">38 days</td>
                  <td className="py-4 px-4 text-gray-600">30 days</td>
                  <td className="py-4 px-4">
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">+27%</span>
                  </td>
                  <td className="py-4 px-4 text-black">Medium</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-4 px-4 text-black">Budget Negotiation</td>
                  <td className="py-4 px-4 text-black">23 days</td>
                  <td className="py-4 px-4 text-gray-600">21 days</td>
                  <td className="py-4 px-4">
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">+10%</span>
                  </td>
                  <td className="py-4 px-4 text-black">Low</td>
                </tr>
                <tr className="border-b border-gray-100">
                  <td className="py-4 px-4 text-black">CDA/NDA Execution</td>
                  <td className="py-4 px-4 text-black">48 days</td>
                  <td className="py-4 px-4 text-gray-600">35 days</td>
                  <td className="py-4 px-4">
                    <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm">+37%</span>
                  </td>
                  <td className="py-4 px-4 text-black">High</td>
                </tr>
                <tr>
                  <td className="py-4 px-4 text-black">Site Activation Visit</td>
                  <td className="py-4 px-4 text-black">18 days</td>
                  <td className="py-4 px-4 text-gray-600">14 days</td>
                  <td className="py-4 px-4">
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">+29%</span>
                  </td>
                  <td className="py-4 px-4 text-black">Medium</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Variance by Category */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl mb-6 text-black">Variance by Task Category</h2>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-black">Regulatory & Ethics</span>
                <span className="text-red-600 font-medium">+35% avg variance</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div className="bg-red-500 rounded-full h-3" style={{ width: '70%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-black">Site Setup & Activation</span>
                <span className="text-yellow-600 font-medium">+22% avg variance</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div className="bg-yellow-500 rounded-full h-3" style={{ width: '44%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-black">Budget & Contracts</span>
                <span className="text-yellow-600 font-medium">+18% avg variance</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div className="bg-yellow-500 rounded-full h-3" style={{ width: '36%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-black">Study Startup Documentation</span>
                <span className="text-green-600 font-medium">+8% avg variance</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div className="bg-green-500 rounded-full h-3" style={{ width: '16%' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Benchmark Coverage */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-xl mb-6 text-black">Benchmark Coverage by Country</h2>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-black">United States (FDA)</span>
                <span className="text-black font-medium">95% coverage</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div className="bg-black rounded-full h-3" style={{ width: '95%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-black">European Union (EMA)</span>
                <span className="text-black font-medium">88% coverage</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div className="bg-black rounded-full h-3" style={{ width: '88%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-black">United Kingdom (MHRA)</span>
                <span className="text-black font-medium">82% coverage</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div className="bg-black rounded-full h-3" style={{ width: '82%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-black">Canada (Health Canada)</span>
                <span className="text-black font-medium">75% coverage</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div className="bg-black rounded-full h-3" style={{ width: '75%' }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-black">Australia (TGA)</span>
                <span className="text-black font-medium">68% coverage</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-3">
                <div className="bg-black rounded-full h-3" style={{ width: '68%' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Advisory Engagement */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl mb-6 text-black">ML Advisory Engagement</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4">
              <div className="text-4xl font-light text-black mb-2">127</div>
              <div className="text-gray-600 text-sm">Advisory Requests</div>
            </div>
            <div className="text-center p-4">
              <div className="text-4xl font-light text-black mb-2">89%</div>
              <div className="text-gray-600 text-sm">Recommendations Accepted</div>
            </div>
            <div className="text-center p-4">
              <div className="text-4xl font-light text-black mb-2">12.3</div>
              <div className="text-gray-600 text-sm">Avg Days Saved per Timeline</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
