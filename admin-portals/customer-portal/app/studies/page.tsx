'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Header from '@/components/Header';
import { apiClient } from '@/lib/api-client';

// ============================================================================
// Types
// ============================================================================

interface Project {
  project_id: string;
  upload_count: number;
  signal_count: number;
  escalation_count: number;
  last_upload: string;
  health_score: number | null;
  health_status: 'healthy' | 'warning' | 'critical' | 'unknown';
}

interface ProjectsResponse {
  projects: Project[];
  total: number;
}

// ============================================================================
// Main Component
// ============================================================================

export default function StudyDashboardPage() {
  // Mock org_id - in production, get from auth context
  const orgId = 'demo_org_001';

  // State
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Load projects on mount
  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.get<ProjectsResponse>(
        `/projects?org_id=${orgId}`
      );
      setProjects(response.projects || []);
    } catch (err: any) {
      console.error('Failed to fetch projects:', err);
      setError(err.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  // Filter projects
  const filteredProjects = projects.filter((project) => {
    // Search filter
    if (searchQuery && !project.project_id.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }

    // Status filter
    if (statusFilter !== 'all' && project.health_status !== statusFilter) {
      return false;
    }

    return true;
  });

  // Calculate summary stats
  const totalSignals = projects.reduce((sum, p) => sum + p.signal_count, 0);
  const totalEscalations = projects.reduce((sum, p) => sum + p.escalation_count, 0);
  const criticalProjects = projects.filter((p) => p.health_status === 'critical').length;
  const warningProjects = projects.filter((p) => p.health_status === 'warning').length;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Study Dashboard</h1>
          <p className="text-gray-600">
            Monitor health scores, signals, and escalations across all your clinical trials
          </p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <SummaryCard
            label="Total Projects"
            value={projects.length}
            iconBg="bg-blue-100"
            iconColor="text-blue-600"
            icon="📊"
          />
          <SummaryCard
            label="Active Signals"
            value={totalSignals}
            iconBg="bg-yellow-100"
            iconColor="text-yellow-600"
            icon="⚠️"
          />
          <SummaryCard
            label="Open Escalations"
            value={totalEscalations}
            iconBg="bg-red-100"
            iconColor="text-red-600"
            icon="🚨"
          />
          <SummaryCard
            label="Critical Projects"
            value={criticalProjects}
            iconBg="bg-red-100"
            iconColor="text-red-600"
            icon="🔴"
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            {error}
          </div>
        )}

        {/* Filters */}
        <div className="mb-6 flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
            />
          </div>
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
            >
              <option value="all">All Statuses</option>
              <option value="healthy">Healthy</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
              <option value="unknown">Unknown</option>
            </select>
          </div>
        </div>

        {/* Projects Table */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-gray-600">Loading projects...</div>
          </div>
        ) : filteredProjects.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
            <p className="text-gray-600 mb-4">
              {searchQuery || statusFilter !== 'all'
                ? 'No projects match your filters'
                : 'No projects found. Upload a tracker to get started.'}
            </p>
            {!searchQuery && statusFilter === 'all' && (
              <Link
                href="/settings/tracker-config"
                className="inline-block px-6 py-2 bg-black text-white rounded hover:bg-gray-800"
              >
                Configure Trackers
              </Link>
            )}
          </div>
        ) : (
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                      Project ID
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                      Health Score
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                      Signals
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                      Escalations
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                      Uploads
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                      Last Upload
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProjects.map((project) => (
                    <tr
                      key={project.project_id}
                      className="border-b border-gray-200 hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        {project.project_id}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        {project.health_score !== null ? (
                          <span className="font-semibold">
                            {project.health_score.toFixed(1)}
                          </span>
                        ) : (
                          <span className="text-gray-400">N/A</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <HealthStatusBadge status={project.health_status} />
                      </td>
                      <td className="px-6 py-4 text-sm">
                        {project.signal_count > 0 ? (
                          <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded font-medium">
                            {project.signal_count}
                          </span>
                        ) : (
                          <span className="text-gray-400">0</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        {project.escalation_count > 0 ? (
                          <span className="px-2 py-1 bg-red-100 text-red-800 rounded font-medium">
                            {project.escalation_count}
                          </span>
                        ) : (
                          <span className="text-gray-400">0</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {project.upload_count}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {project.last_upload
                          ? new Date(project.last_upload).toLocaleDateString()
                          : 'N/A'}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <Link
                          href={`/studies/${project.project_id}`}
                          className="text-black hover:underline font-medium"
                        >
                          View Details →
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Results Summary */}
        {!loading && filteredProjects.length > 0 && (
          <div className="mt-4 text-sm text-gray-600">
            Showing {filteredProjects.length} of {projects.length} projects
          </div>
        )}
      </main>
    </div>
  );
}

// ============================================================================
// Sub-Components
// ============================================================================

function SummaryCard({
  label,
  value,
  iconBg,
  iconColor,
  icon,
}: {
  label: string;
  value: number;
  iconBg: string;
  iconColor: string;
  icon: string;
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-center justify-between mb-2">
        <div className={`w-10 h-10 ${iconBg} rounded-lg flex items-center justify-center`}>
          <span className={`text-xl ${iconColor}`}>{icon}</span>
        </div>
      </div>
      <div className="text-3xl font-bold mb-1">{value}</div>
      <div className="text-sm text-gray-600">{label}</div>
    </div>
  );
}

function HealthStatusBadge({ status }: { status: string }) {
  const styles: Record<string, { bg: string; text: string; label: string }> = {
    healthy: { bg: 'bg-green-100', text: 'text-green-800', label: 'Healthy' },
    warning: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Warning' },
    critical: { bg: 'bg-red-100', text: 'text-red-800', label: 'Critical' },
    unknown: { bg: 'bg-gray-100', text: 'text-gray-600', label: 'Unknown' },
  };

  const style = styles[status] || styles.unknown;

  return (
    <span className={`px-2 py-1 ${style.bg} ${style.text} rounded text-xs font-medium`}>
      {style.label}
    </span>
  );
}
