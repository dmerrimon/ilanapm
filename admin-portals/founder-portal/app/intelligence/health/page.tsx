'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import { apiClient } from '@/lib/api-client';

interface IntelligenceHealthMetrics {
  total_variance_analyses: number;
  total_calibration_uploads: number;
  avg_benchmark_coverage: number;
  total_org_benchmarks: number;
  calibrated_tier_orgs: number;
  enterprise_tier_orgs: number;
}

interface CalibrationActivity {
  org_id: string;
  org_name: string;
  uploads_count: number;
  benchmarks_generated: number;
  last_upload: string;
  data_quality: string;
}

interface ModelPerformance {
  component: string;
  accuracy: number;
  predictions_count: number;
  avg_confidence: number;
  status: string;
}

interface EnterpriseMetrics {
  total_portfolio_analyses: number;
  avg_portfolio_health_score: number;
  total_resource_collisions_detected: number;
  critical_collisions: number;
  portfolio_forecasts_generated: number;
  avg_forecast_confidence: number;
}

interface PortfolioActivity {
  org_id: string;
  org_name: string;
  active_studies: number;
  portfolio_health_score: number;
  resource_collisions: number;
  last_forecast: string;
}

export default function IntelligenceHealthPage() {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');
  const [metrics, setMetrics] = useState<IntelligenceHealthMetrics>({
    total_variance_analyses: 1247,
    total_calibration_uploads: 342,
    avg_benchmark_coverage: 82,
    total_org_benchmarks: 1856,
    calibrated_tier_orgs: 23,
    enterprise_tier_orgs: 8
  });

  const [calibrationActivity, setCalibrationActivity] = useState<CalibrationActivity[]>([
    {
      org_id: 'org_001',
      org_name: 'BioTech Innovations',
      uploads_count: 12,
      benchmarks_generated: 48,
      last_upload: '2024-02-08',
      data_quality: 'High'
    },
    {
      org_id: 'org_002',
      org_name: 'MedPharm Solutions',
      uploads_count: 8,
      benchmarks_generated: 34,
      last_upload: '2024-02-07',
      data_quality: 'High'
    },
    {
      org_id: 'org_003',
      org_name: 'Clinical Research Corp',
      uploads_count: 15,
      benchmarks_generated: 62,
      last_upload: '2024-02-06',
      data_quality: 'Medium'
    },
    {
      org_id: 'org_004',
      org_name: 'Global Therapeutics',
      uploads_count: 5,
      benchmarks_generated: 22,
      last_upload: '2024-02-05',
      data_quality: 'High'
    },
    {
      org_id: 'org_005',
      org_name: 'Precision Medicine Inc',
      uploads_count: 3,
      benchmarks_generated: 14,
      last_upload: '2024-02-03',
      data_quality: 'Medium'
    }
  ]);

  const [modelPerformance, setModelPerformance] = useState<ModelPerformance[]>([
    {
      component: 'Variance Detection',
      accuracy: 94.2,
      predictions_count: 12458,
      avg_confidence: 0.87,
      status: 'Healthy'
    },
    {
      component: 'Task Normalization',
      accuracy: 89.6,
      predictions_count: 8923,
      avg_confidence: 0.82,
      status: 'Healthy'
    },
    {
      component: 'Metadata Inference',
      accuracy: 91.3,
      predictions_count: 5647,
      avg_confidence: 0.79,
      status: 'Healthy'
    },
    {
      component: 'Benchmark Blending',
      accuracy: 96.8,
      predictions_count: 3421,
      avg_confidence: 0.92,
      status: 'Healthy'
    },
    {
      component: 'Confidence Scoring',
      accuracy: 88.5,
      predictions_count: 7834,
      avg_confidence: 0.76,
      status: 'Warning'
    }
  ]);

  const [enterpriseMetrics, setEnterpriseMetrics] = useState<EnterpriseMetrics>({
    total_portfolio_analyses: 287,
    avg_portfolio_health_score: 76.3,
    total_resource_collisions_detected: 142,
    critical_collisions: 18,
    portfolio_forecasts_generated: 456,
    avg_forecast_confidence: 81.7
  });

  const [portfolioActivity, setPortfolioActivity] = useState<PortfolioActivity[]>([
    {
      org_id: 'org_ent_001',
      org_name: 'GlobalPharma International',
      active_studies: 12,
      portfolio_health_score: 82.4,
      resource_collisions: 5,
      last_forecast: '2024-02-08'
    },
    {
      org_id: 'org_ent_002',
      org_name: 'BioScience Ventures',
      active_studies: 8,
      portfolio_health_score: 78.2,
      resource_collisions: 3,
      last_forecast: '2024-02-07'
    },
    {
      org_id: 'org_ent_003',
      org_name: 'Therapeutic Innovations Corp',
      active_studies: 15,
      portfolio_health_score: 71.5,
      resource_collisions: 8,
      last_forecast: '2024-02-07'
    },
    {
      org_id: 'org_ent_004',
      org_name: 'Clinical Excellence Partners',
      active_studies: 6,
      portfolio_health_score: 85.1,
      resource_collisions: 2,
      last_forecast: '2024-02-06'
    },
    {
      org_id: 'org_ent_005',
      org_name: 'MedTech Research Alliance',
      active_studies: 10,
      portfolio_health_score: 73.9,
      resource_collisions: 6,
      last_forecast: '2024-02-05'
    }
  ]);

  const getQualityBadge = (quality: string) => {
    const colors = {
      'High': 'bg-green-100 text-green-800',
      'Medium': 'bg-amber-100 text-amber-800',
      'Low': 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded ${colors[quality as keyof typeof colors] || colors.Medium}`}>
        {quality}
      </span>
    );
  };

  const getStatusBadge = (status: string) => {
    const colors = {
      'Healthy': 'bg-green-100 text-green-800',
      'Warning': 'bg-amber-100 text-amber-800',
      'Critical': 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded ${colors[status as keyof typeof colors] || colors.Healthy}`}>
        {status}
      </span>
    );
  };

  const getAccuracyColor = (accuracy: number) => {
    if (accuracy >= 90) return 'text-green-600';
    if (accuracy >= 80) return 'text-amber-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl mb-2 text-black">Intelligence Health Dashboard</h1>
              <p className="text-gray-600">
                Monitor system-wide intelligence performance, calibration activity, and model metrics
              </p>
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
        </div>

        {/* System-Wide Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Variance Analyses</div>
            <div className="text-2xl font-light text-black">{metrics.total_variance_analyses.toLocaleString()}</div>
            <div className="text-sm text-green-600 mt-2">↑ 18% from last period</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Calibration Uploads</div>
            <div className="text-2xl font-light text-black">{metrics.total_calibration_uploads}</div>
            <div className="text-sm text-green-600 mt-2">↑ 24% from last period</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Avg Coverage</div>
            <div className="text-2xl font-light text-black">{metrics.avg_benchmark_coverage}%</div>
            <div className="text-sm text-green-600 mt-2">↑ 5% improvement</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Org Benchmarks</div>
            <div className="text-2xl font-light text-black">{metrics.total_org_benchmarks.toLocaleString()}</div>
            <div className="text-sm text-gray-600 mt-2">Across all orgs</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Calibrated Tier</div>
            <div className="text-2xl font-light text-blue-600">{metrics.calibrated_tier_orgs}</div>
            <div className="text-sm text-gray-600 mt-2">Organizations</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Enterprise Tier</div>
            <div className="text-2xl font-light text-purple-600">{metrics.enterprise_tier_orgs}</div>
            <div className="text-sm text-gray-600 mt-2">Organizations</div>
          </div>
        </div>

        {/* Model Performance */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden mb-8">
          <div className="p-6">
            <h2 className="text-xl font-medium text-black mb-4">Intelligence Component Performance</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Component</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Accuracy</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Predictions</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Avg Confidence</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody>
                {modelPerformance.map((model) => (
                  <tr key={model.component} className="border-t border-gray-100 hover:bg-gray-50">
                    <td className="py-4 px-4 text-black font-medium">{model.component}</td>
                    <td className="py-4 px-4">
                      <span className={`font-medium ${getAccuracyColor(model.accuracy)}`}>
                        {model.accuracy}%
                      </span>
                    </td>
                    <td className="py-4 px-4 text-gray-600">{model.predictions_count.toLocaleString()}</td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-100 rounded-full h-2">
                          <div
                            className="bg-blue-600 rounded-full h-2"
                            style={{ width: `${model.avg_confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-600">{Math.round(model.avg_confidence * 100)}%</span>
                      </div>
                    </td>
                    <td className="py-4 px-4">{getStatusBadge(model.status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Calibration Activity by Organization */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden mb-8">
          <div className="p-6">
            <h2 className="text-xl font-medium text-black mb-4">Recent Calibration Activity</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Organization</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Uploads</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Benchmarks Generated</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Last Upload</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Data Quality</th>
                </tr>
              </thead>
              <tbody>
                {calibrationActivity.map((activity) => (
                  <tr key={activity.org_id} className="border-t border-gray-100 hover:bg-gray-50">
                    <td className="py-4 px-4 text-black font-medium">{activity.org_name}</td>
                    <td className="py-4 px-4 text-gray-600">{activity.uploads_count}</td>
                    <td className="py-4 px-4 text-gray-600">{activity.benchmarks_generated}</td>
                    <td className="py-4 px-4 text-gray-600">
                      {new Date(activity.last_upload).toLocaleDateString()}
                    </td>
                    <td className="py-4 px-4">{getQualityBadge(activity.data_quality)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* System Health Insights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Calibration Adoption */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-black mb-4">Calibration Adoption Rate</h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600">Calibrated Tier Orgs</span>
                  <span className="text-black font-medium">74% active</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-3">
                  <div className="bg-green-600 rounded-full h-3" style={{ width: '74%' }} />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600">Enterprise Tier Orgs</span>
                  <span className="text-black font-medium">88% active</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-3">
                  <div className="bg-green-600 rounded-full h-3" style={{ width: '88%' }} />
                </div>
              </div>
              <div className="mt-4 p-3 bg-blue-50 rounded">
                <p className="text-sm text-blue-900">
                  <strong>Insight:</strong> Calibration adoption is strong. 81% of eligible orgs have uploaded at least 3 timelines.
                </p>
              </div>
            </div>
          </div>

          {/* Data Quality Distribution */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-black mb-4">Data Quality Distribution</h3>
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600">High Quality</span>
                  <span className="text-black font-medium">68%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-3">
                  <div className="bg-green-600 rounded-full h-3" style={{ width: '68%' }} />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600">Medium Quality</span>
                  <span className="text-black font-medium">27%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-3">
                  <div className="bg-amber-600 rounded-full h-3" style={{ width: '27%' }} />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600">Low Quality</span>
                  <span className="text-black font-medium">5%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-3">
                  <div className="bg-red-600 rounded-full h-3" style={{ width: '5%' }} />
                </div>
              </div>
              <div className="mt-4 p-3 bg-green-50 rounded">
                <p className="text-sm text-green-900">
                  <strong>Status:</strong> Data quality is excellent. 95% of calibration data meets quality thresholds.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Enterprise Tier Metrics Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-medium text-black mb-6 pb-2 border-b-2 border-purple-600">
            Enterprise Tier Analytics
          </h2>

          {/* Enterprise Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
            <div className="bg-gradient-to-br from-purple-50 to-white p-4 rounded-lg shadow-sm border border-purple-200">
              <div className="text-purple-600 text-sm mb-1">Portfolio Analyses</div>
              <div className="text-2xl font-light text-black">{enterpriseMetrics.total_portfolio_analyses}</div>
              <div className="text-sm text-green-600 mt-2">↑ 32% growth</div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-white p-4 rounded-lg shadow-sm border border-purple-200">
              <div className="text-purple-600 text-sm mb-1">Avg Health Score</div>
              <div className="text-2xl font-light text-black">{enterpriseMetrics.avg_portfolio_health_score}</div>
              <div className="text-sm text-green-600 mt-2">↑ 3.2 points</div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-white p-4 rounded-lg shadow-sm border border-purple-200">
              <div className="text-purple-600 text-sm mb-1">Collisions Detected</div>
              <div className="text-2xl font-light text-black">{enterpriseMetrics.total_resource_collisions_detected}</div>
              <div className="text-sm text-gray-600 mt-2">Total detected</div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-white p-4 rounded-lg shadow-sm border border-purple-200">
              <div className="text-purple-600 text-sm mb-1">Critical Collisions</div>
              <div className="text-2xl font-light text-red-600">{enterpriseMetrics.critical_collisions}</div>
              <div className="text-sm text-gray-600 mt-2">Need attention</div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-white p-4 rounded-lg shadow-sm border border-purple-200">
              <div className="text-purple-600 text-sm mb-1">Forecasts Generated</div>
              <div className="text-2xl font-light text-black">{enterpriseMetrics.portfolio_forecasts_generated}</div>
              <div className="text-sm text-green-600 mt-2">↑ 28% usage</div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-white p-4 rounded-lg shadow-sm border border-purple-200">
              <div className="text-purple-600 text-sm mb-1">Forecast Confidence</div>
              <div className="text-2xl font-light text-black">{enterpriseMetrics.avg_forecast_confidence}%</div>
              <div className="text-sm text-green-600 mt-2">High accuracy</div>
            </div>
          </div>

          {/* Portfolio Activity Table */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden mb-6">
            <div className="p-6">
              <h3 className="text-xl font-medium text-black mb-4">Enterprise Portfolio Activity</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Organization</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Active Studies</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Portfolio Health</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Resource Collisions</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Last Forecast</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolioActivity.map((activity) => (
                    <tr key={activity.org_id} className="border-t border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4 text-black font-medium">{activity.org_name}</td>
                      <td className="py-4 px-4 text-gray-600">{activity.active_studies}</td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <span className={`font-medium ${
                            activity.portfolio_health_score >= 80 ? 'text-green-600' :
                            activity.portfolio_health_score >= 70 ? 'text-amber-600' : 'text-red-600'
                          }`}>
                            {activity.portfolio_health_score}
                          </span>
                          <div className="w-24 bg-gray-100 rounded-full h-2">
                            <div
                              className={`rounded-full h-2 ${
                                activity.portfolio_health_score >= 80 ? 'bg-green-600' :
                                activity.portfolio_health_score >= 70 ? 'bg-amber-600' : 'bg-red-600'
                              }`}
                              style={{ width: `${activity.portfolio_health_score}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`font-medium ${
                          activity.resource_collisions >= 5 ? 'text-red-600' :
                          activity.resource_collisions >= 3 ? 'text-amber-600' : 'text-gray-600'
                        }`}>
                          {activity.resource_collisions}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-600">
                        {new Date(activity.last_forecast).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Enterprise Insights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Portfolio Health Distribution */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h4 className="text-lg font-medium text-black mb-4">Portfolio Health Distribution</h4>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600">Excellent (80+)</span>
                    <span className="text-black font-medium">25%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-green-600 rounded-full h-3" style={{ width: '25%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600">Good (70-79)</span>
                    <span className="text-black font-medium">50%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-blue-600 rounded-full h-3" style={{ width: '50%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600">Needs Attention (&lt;70)</span>
                    <span className="text-black font-medium">25%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-amber-600 rounded-full h-3" style={{ width: '25%' }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Resource Collision Severity */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h4 className="text-lg font-medium text-black mb-4">Collision Severity Breakdown</h4>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600">Critical (&gt;100% util)</span>
                    <span className="text-red-600 font-medium">13%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-red-600 rounded-full h-3" style={{ width: '13%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600">Warning (80-100%)</span>
                    <span className="text-amber-600 font-medium">32%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-amber-600 rounded-full h-3" style={{ width: '32%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600">Info (&lt;80%)</span>
                    <span className="text-blue-600 font-medium">55%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-blue-600 rounded-full h-3" style={{ width: '55%' }} />
                  </div>
                </div>
              </div>
            </div>

            {/* Forecasting Adoption */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h4 className="text-lg font-medium text-black mb-4">Forecasting Feature Adoption</h4>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600">Daily Active Users</span>
                    <span className="text-black font-medium">92%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-green-600 rounded-full h-3" style={{ width: '92%' }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-600">Weekly Forecasts</span>
                    <span className="text-black font-medium">87%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-3">
                    <div className="bg-green-600 rounded-full h-3" style={{ width: '87%' }} />
                  </div>
                </div>
                <div className="mt-4 p-3 bg-purple-50 rounded">
                  <p className="text-sm text-purple-900">
                    <strong>Insight:</strong> Enterprise features showing excellent adoption. Forecast confidence improving month-over-month.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* System Alerts */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <div className="text-amber-600 text-xl">⚠️</div>
            <div className="flex-1">
              <h3 className="font-medium text-amber-900 mb-2">System Alerts</h3>
              <ul className="space-y-2 text-sm text-amber-900">
                <li className="flex items-start gap-2">
                  <span className="text-amber-600 mt-0.5">•</span>
                  <span><strong>Confidence Scoring:</strong> Accuracy below 90% threshold (88.5%). Consider model retraining.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-amber-600 mt-0.5">•</span>
                  <span><strong>BioTech Innovations:</strong> No calibration uploads in 7 days. Check engagement.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-600 mt-0.5">•</span>
                  <span><strong>Therapeutic Innovations Corp:</strong> 8 resource collisions detected, including 2 critical. Recommend immediate portfolio review.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
