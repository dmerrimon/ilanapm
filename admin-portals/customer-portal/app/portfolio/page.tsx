'use client';

import React, { useState, useEffect } from 'react';
import Header from '@/components/Header';
import { apiClient } from '@/lib/api-client';

interface PortfolioAnalytics {
  org_id: string;
  portfolio_health_score: number;
  total_studies: number;
  study_distribution: {
    by_status: Record<string, number>;
    by_phase: Record<string, number>;
    active_studies: number;
    completed_studies: number;
    planned_studies: number;
  };
  risk_distribution: {
    critical_studies: number;
    warning_studies: number;
    healthy_studies: number;
    critical_rate: number;
    warning_rate: number;
    healthy_rate: number;
  };
  systemic_patterns: Array<{
    pattern_type: string;
    category: string;
    avg_variance_percent: number;
    affected_studies: number;
    consistency_rate: number;
    severity: string;
    description: string;
  }>;
  financial_metrics: {
    total_impact_usd: number;
    at_risk_usd: number;
    potential_savings_usd: number;
    avg_impact_per_study: number;
  };
  capacity_utilization: {
    capacity_used: number;
    max_capacity: number;
    utilization_rate: number;
    status: string;
    available_capacity: number;
  };
  common_bottlenecks: Array<{
    category: string;
    affected_studies: number;
    avg_variance_percent: number;
    severity: string;
  }>;
  benchmark_performance: {
    avg_coverage: number;
    tasks_with_org_benchmarks: number;
    total_variance_analyses: number;
    benchmark_maturity: string;
  };
  timestamp: string;
}

interface ResourceCollision {
  org_id: string;
  collisions: Array<{
    resource_id: string;
    resource_name: string;
    resource_type: string;
    conflicting_studies: Array<{
      study_id: string;
      study_name: string;
      start_date: string;
      end_date: string;
      utilization: number;
    }>;
    overlap_start: string;
    overlap_end: string;
    overlap_days: number;
    severity: string;
    total_utilization: number;
    recommendations: string[];
  }>;
  summary: {
    total_collisions: number;
    critical_collisions: number;
    warning_collisions: number;
    info_collisions: number;
    affected_resources: number;
    affected_studies: number;
    total_resources_tracked: number;
    collision_rate: number;
    collisions_by_type: Record<string, number>;
  };
  recommendations: string[];
  timestamp: string;
}

interface PortfolioForecast {
  org_id: string;
  forecast_start: string;
  forecast_end: string;
  horizon_days: number;
  milestones: Array<{
    study_id: string;
    study_name: string;
    milestone_type: string;
    projected_date: string;
    days_from_now: number;
    probability_on_time: number;
    confidence: string;
  }>;
  resource_forecast: {
    site_activations_needed: number;
    estimated_sites_required: number;
    enrollment_starts: number;
    estimated_patients_needed: number;
    data_management_events: number;
    peak_activity_period: {
      period: string;
      start_date: string;
      end_date: string;
      milestone_count: number;
    };
    resource_pressure_points: Array<{
      date: string;
      concurrent_milestones: number;
      studies_affected: number;
      severity: string;
    }>;
  };
  capacity_forecast: {
    current_capacity_fte: number;
    projected_peak_capacity_fte: number;
    capacity_increase_needed: number;
    capacity_utilization: number;
    recommendation: string;
  };
  risk_forecast: Array<{
    risk_type: string;
    severity: string;
    description: string;
    impact: string;
    mitigation: string;
  }>;
  confidence: {
    overall_confidence: number;
    level: string;
    factors: {
      org_benchmarks_available: boolean;
      historical_data_available: boolean;
      sample_size: number;
    };
  };
  timestamp: string;
}

export default function PortfolioDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<PortfolioAnalytics | null>(null);
  const [collisions, setCollisions] = useState<ResourceCollision | null>(null);
  const [forecast, setForecast] = useState<PortfolioForecast | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'collisions' | 'forecast' | 'patterns'>('overview');

  const orgId = 'org_001'; // TODO: Get from auth context

  const loadPortfolioData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all portfolio data in parallel
      const [analyticsRes, collisionsRes, forecastRes] = await Promise.all([
        apiClient.get(`/api/v1/intelligence/portfolio/analytics?org_id=${orgId}`),
        apiClient.get(`/api/v1/intelligence/portfolio/collisions?org_id=${orgId}`),
        apiClient.get(`/api/v1/intelligence/portfolio/forecast?org_id=${orgId}&horizon_days=90`)
      ]);

      setAnalytics(analyticsRes.data);
      setCollisions(collisionsRes.data);
      setForecast(forecastRes.data);
    } catch (err: any) {
      console.error('Error loading portfolio data:', err);
      setError(err.response?.data?.detail || 'Failed to load portfolio data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPortfolioData();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadPortfolioData();
    setRefreshing(false);
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSeverityBadge = (severity: string) => {
    const colors = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      warning: 'bg-yellow-100 text-yellow-800',
      medium: 'bg-blue-100 text-blue-800',
      low: 'bg-green-100 text-green-800',
      info: 'bg-gray-100 text-gray-800'
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded ${colors[severity as keyof typeof colors] || colors.info}`}>
        {severity}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
            <p className="text-gray-600">Loading portfolio data...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h3 className="text-red-800 font-medium mb-2">Error</h3>
            <p className="text-red-600">{error}</p>
            <button
              onClick={loadPortfolioData}
              className="mt-4 px-4 py-2 bg-black text-white rounded hover:bg-gray-800"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!analytics || !collisions || !forecast) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <p className="text-blue-800">No portfolio data available.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl mb-2 text-black">Portfolio Intelligence</h1>
            <p className="text-gray-600">
              Comprehensive view of your clinical trial portfolio
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 disabled:opacity-50 flex items-center gap-2"
          >
            <span className={refreshing ? 'animate-spin' : ''}>↻</span>
            Refresh
          </button>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Health Score */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-gray-500 text-sm mb-2">Portfolio Health</div>
            <div className={`text-3xl font-light ${getHealthScoreColor(analytics.portfolio_health_score)}`}>
              {analytics.portfolio_health_score.toFixed(1)}
            </div>
            <p className="text-xs text-gray-500 mt-1">out of 100</p>
          </div>

          {/* Active Studies */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-gray-500 text-sm mb-2">Active Studies</div>
            <div className="text-3xl font-light text-black">
              {analytics.study_distribution.active_studies}
            </div>
            <p className="text-xs text-gray-500 mt-1">of {analytics.total_studies} total</p>
          </div>

          {/* Financial Impact */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-gray-500 text-sm mb-2">Financial Impact</div>
            <div className="text-2xl font-light text-black">
              ${(analytics.financial_metrics.total_impact_usd / 1000000).toFixed(2)}M
            </div>
            <p className="text-xs text-gray-500 mt-1">total portfolio impact</p>
          </div>

          {/* Resource Collisions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="text-gray-500 text-sm mb-2">Resource Collisions</div>
            <div className="text-3xl font-light text-black">
              {collisions.summary.total_collisions}
            </div>
            <p className="text-xs text-red-500 mt-1">
              {collisions.summary.critical_collisions} critical
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="flex gap-2 border-b border-gray-200">
            {(['overview', 'collisions', 'forecast', 'patterns'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 font-medium capitalize ${
                  activeTab === tab
                    ? 'border-b-2 border-black text-black'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Portfolio Recommendations */}
            {collisions.recommendations.length > 0 && (
              <div className={`border rounded-lg p-6 ${
                collisions.summary.critical_collisions > 0
                  ? 'bg-red-50 border-red-200'
                  : 'bg-blue-50 border-blue-200'
              }`}>
                <h3 className="font-medium mb-3">Portfolio Recommendations</h3>
                <ul className="list-disc list-inside space-y-1">
                  {collisions.recommendations.map((rec, idx) => (
                    <li key={idx}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Common Bottlenecks */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-xl font-medium text-black mb-4">Common Bottlenecks</h3>
              <div className="space-y-4">
                {analytics.common_bottlenecks.map((bottleneck, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900">{bottleneck.category}</h4>
                      <p className="text-sm text-gray-600">
                        Affects {bottleneck.affected_studies} studies • Avg variance: {bottleneck.avg_variance_percent.toFixed(1)}%
                      </p>
                    </div>
                    {getSeverityBadge(bottleneck.severity)}
                  </div>
                ))}
                {analytics.common_bottlenecks.length === 0 && (
                  <p className="text-center text-gray-500 py-4">No common bottlenecks detected</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Resource Collisions Tab */}
        {activeTab === 'collisions' && (
          <div className="space-y-6">
            {/* Collision Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="text-gray-500 text-sm mb-1">Critical Collisions</div>
                <div className="text-2xl font-light text-red-600">{collisions.summary.critical_collisions}</div>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="text-gray-500 text-sm mb-1">Warning Collisions</div>
                <div className="text-2xl font-light text-yellow-600">{collisions.summary.warning_collisions}</div>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="text-gray-500 text-sm mb-1">Collision Rate</div>
                <div className="text-2xl font-light text-gray-900">{collisions.summary.collision_rate.toFixed(1)}%</div>
              </div>
            </div>

            {/* Collision Details */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-xl font-medium text-black mb-4">Resource Collision Details</h3>
              <div className="space-y-6">
                {collisions.collisions.map((collision, idx) => (
                  <div key={idx} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h4 className="font-semibold text-gray-900">{collision.resource_name}</h4>
                        <p className="text-sm text-gray-600">
                          {collision.resource_type} • {collision.overlap_days} days overlap
                        </p>
                      </div>
                      {getSeverityBadge(collision.severity)}
                    </div>

                    <div className="mb-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">Conflicting Studies:</p>
                      <div className="space-y-2">
                        {collision.conflicting_studies.map((study, studyIdx) => (
                          <div key={studyIdx} className="text-sm bg-gray-50 p-2 rounded">
                            <span className="font-medium">{study.study_name}</span>
                            <span className="text-gray-600 ml-2">
                              ({new Date(study.start_date).toLocaleDateString()} - {new Date(study.end_date).toLocaleDateString()})
                            </span>
                            <span className="text-gray-600 ml-2">Utilization: {study.utilization}%</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="mb-2">
                      <p className="text-sm font-medium text-gray-700">Total Utilization: {collision.total_utilization.toFixed(1)}%</p>
                    </div>

                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Recommendations:</p>
                      <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                        {collision.recommendations.map((rec, recIdx) => (
                          <li key={recIdx}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
                {collisions.collisions.length === 0 && (
                  <div className="text-center py-8">
                    <p className="text-gray-600">No resource collisions detected</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Forecast Tab */}
        {activeTab === 'forecast' && (
          <div className="space-y-6">
            {/* Forecast Confidence */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h4 className="font-medium text-blue-900 mb-2">
                Forecast Confidence: {forecast.confidence.overall_confidence.toFixed(1)}% ({forecast.confidence.level})
              </h4>
              <p className="text-sm text-blue-800">
                Based on {forecast.confidence.factors.sample_size} studies
                {forecast.confidence.factors.org_benchmarks_available && ', organization benchmarks available'}
                {forecast.confidence.factors.historical_data_available && ', historical performance data available'}
              </p>
            </div>

            {/* Risk Forecast */}
            {forecast.risk_forecast.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-xl font-medium text-black mb-4">Forecasted Risks</h3>
                <div className="space-y-4">
                  {forecast.risk_forecast.map((risk, idx) => (
                    <div key={idx} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-semibold text-gray-900">{risk.risk_type.replace(/_/g, ' ').toUpperCase()}</h4>
                        {getSeverityBadge(risk.severity)}
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{risk.description}</p>
                      <p className="text-sm text-gray-600 mb-2"><strong>Impact:</strong> {risk.impact}</p>
                      <p className="text-sm text-blue-600"><strong>Mitigation:</strong> {risk.mitigation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Upcoming Milestones */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-xl font-medium text-black mb-4">Upcoming Milestones (Next {forecast.horizon_days} Days)</h3>
              <div className="space-y-2">
                {forecast.milestones.slice(0, 10).map((milestone, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 border rounded">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{milestone.study_name}</p>
                      <p className="text-sm text-gray-600">
                        {milestone.milestone_type.replace(/_/g, ' ')} • {milestone.days_from_now} days from now
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        {new Date(milestone.projected_date).toLocaleDateString()}
                      </p>
                      <p className="text-xs text-gray-600">
                        {(milestone.probability_on_time * 100).toFixed(0)}% on-time probability
                      </p>
                    </div>
                  </div>
                ))}
                {forecast.milestones.length === 0 && (
                  <p className="text-center text-gray-500 py-4">No milestones projected in this period</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Systemic Patterns Tab */}
        {activeTab === 'patterns' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-xl font-medium text-black mb-4">Systemic Patterns Across Portfolio</h3>
              <div className="space-y-4">
                {analytics.systemic_patterns.map((pattern, idx) => (
                  <div key={idx} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{pattern.category}</h4>
                        <p className="text-sm text-gray-600 mt-1">{pattern.description}</p>
                      </div>
                      {getSeverityBadge(pattern.severity)}
                    </div>
                    <div className="grid grid-cols-3 gap-4 mt-3 text-sm">
                      <div>
                        <span className="text-gray-600">Affected Studies:</span>
                        <span className="font-semibold ml-2">{pattern.affected_studies}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Avg Variance:</span>
                        <span className="font-semibold ml-2">{pattern.avg_variance_percent.toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Consistency:</span>
                        <span className="font-semibold ml-2">{pattern.consistency_rate.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
                {analytics.systemic_patterns.length === 0 && (
                  <div className="text-center py-8">
                    <p className="text-gray-600">No systemic patterns detected</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
