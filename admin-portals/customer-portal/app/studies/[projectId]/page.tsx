'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import { apiClient } from '@/lib/api-client';

// ============================================================================
// Types
// ============================================================================

interface Signal {
  signal_id: string;
  signal_type: string;
  signal_category: string | null;
  signal_source: string;
  signal_description: string;
  priority: number;
  status: 'open' | 'acknowledged' | 'resolved';
  date_identified: string;
  escalation_level: string | null;
  created_at: string;
}

interface Escalation {
  escalation_id: string;
  trigger_type: string;
  escalation_level: 'director' | 'vp';
  escalation_reason: string;
  priority: number;
  status: 'open' | 'acknowledged' | 'resolved';
  intervention_recommended: string;
  created_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
}

interface TrackerUpload {
  upload_id: string;
  tracker_type: string;
  uploaded_by: string;
  upload_timestamp: string;
  original_filename: string;
  rows_parsed: number;
  signals_extracted: number;
  parse_status: string;
}

interface HealthSnapshot {
  snapshot_id: string;
  overall_health_score: number;
  health_status: string;
  timeline_score: number | null;
  risk_score: number | null;
  tmf_score: number | null;
  enrollment_score: number | null;
  budget_score: number | null;
  vendor_score: number | null;
  active_escalations_count: number;
  director_escalations_count: number;
  vp_escalations_count: number;
  snapshot_date: string;
  created_at: string;
}

// ============================================================================
// Main Component
// ============================================================================

export default function StudyDetailPage() {
  const params = useParams();
  const projectId = params.projectId as string;

  // Mock org_id - in production, get from auth context
  const orgId = 'demo_org_001';

  // State
  const [signals, setSignals] = useState<Signal[]>([]);
  const [escalations, setEscalations] = useState<Escalation[]>([]);
  const [uploads, setUploads] = useState<TrackerUpload[]>([]);
  const [healthHistory, setHealthHistory] = useState<HealthSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'signals' | 'escalations' | 'uploads' | 'health'>(
    'signals'
  );

  // Filters
  const [signalStatusFilter, setSignalStatusFilter] = useState<string>('all');
  const [escalationLevelFilter, setEscalationLevelFilter] = useState<string>('all');

  // Action states
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Load data on mount
  useEffect(() => {
    fetchAllData();
  }, [projectId]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all data in parallel
      const [signalsRes, escalationsRes, uploadsRes, healthRes] = await Promise.all([
        apiClient.get<{ signals: Signal[] }>(
          `/signals?org_id=${orgId}&project_id=${projectId}&limit=100`
        ),
        apiClient.get<{ escalations: Escalation[] }>(
          `/escalations?org_id=${orgId}&project_id=${projectId}&limit=100`
        ),
        apiClient.get<{ uploads: TrackerUpload[] }>(
          `/trackers/uploads?org_id=${orgId}&project_id=${projectId}&limit=50`
        ),
        apiClient.get<{ snapshots: HealthSnapshot[] }>(
          `/health/history?org_id=${orgId}&project_id=${projectId}&limit=30`
        ),
      ]);

      setSignals(signalsRes.signals || []);
      setEscalations(escalationsRes.escalations || []);
      setUploads(uploadsRes.uploads || []);
      setHealthHistory(healthRes.snapshots || []);
    } catch (err: any) {
      console.error('Failed to fetch project data:', err);
      setError(err.message || 'Failed to load project data');
    } finally {
      setLoading(false);
    }
  };

  // Signal action handlers
  const handleSignalStatusUpdate = async (signalId: string, newStatus: string) => {
    try {
      setActionLoading(signalId);
      setSuccessMessage(null);
      setError(null);

      await apiClient.patch(
        `/signals/${signalId}/status?org_id=${orgId}&status=${newStatus}&updated_by=current_user`
      );

      // Update local state
      setSignals((prev) =>
        prev.map((s) =>
          s.signal_id === signalId ? { ...s, status: newStatus as Signal['status'] } : s
        )
      );

      setSuccessMessage(`Signal ${newStatus} successfully`);
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Failed to update signal:', err);
      setError(err.message || 'Failed to update signal');
    } finally {
      setActionLoading(null);
    }
  };

  // Escalation action handlers
  const handleEscalationAcknowledge = async (escalationId: string) => {
    try {
      setActionLoading(escalationId);
      setSuccessMessage(null);
      setError(null);

      await apiClient.patch(
        `/escalations/${escalationId}/acknowledge?org_id=${orgId}&acknowledged_by=current_user&notes=Acknowledged from portal`
      );

      // Update local state
      setEscalations((prev) =>
        prev.map((e) =>
          e.escalation_id === escalationId
            ? { ...e, status: 'acknowledged' as Escalation['status'], acknowledged_at: new Date().toISOString() }
            : e
        )
      );

      setSuccessMessage('Escalation acknowledged successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Failed to acknowledge escalation:', err);
      setError(err.message || 'Failed to acknowledge escalation');
    } finally {
      setActionLoading(null);
    }
  };

  const handleEscalationResolve = async (escalationId: string) => {
    const notes = prompt('Enter resolution notes:');
    if (!notes) return;

    try {
      setActionLoading(escalationId);
      setSuccessMessage(null);
      setError(null);

      await apiClient.patch(
        `/escalations/${escalationId}/resolve?org_id=${orgId}&resolved_by=current_user&resolution_notes=${encodeURIComponent(notes)}`
      );

      // Update local state
      setEscalations((prev) =>
        prev.map((e) =>
          e.escalation_id === escalationId
            ? { ...e, status: 'resolved' as Escalation['status'], resolved_at: new Date().toISOString() }
            : e
        )
      );

      setSuccessMessage('Escalation resolved successfully');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err: any) {
      console.error('Failed to resolve escalation:', err);
      setError(err.message || 'Failed to resolve escalation');
    } finally {
      setActionLoading(null);
    }
  };

  // Filter signals
  const filteredSignals = signals.filter((signal) => {
    if (signalStatusFilter !== 'all' && signal.status !== signalStatusFilter) {
      return false;
    }
    return true;
  });

  // Filter escalations
  const filteredEscalations = escalations.filter((escalation) => {
    if (
      escalationLevelFilter !== 'all' &&
      escalation.escalation_level !== escalationLevelFilter
    ) {
      return false;
    }
    return true;
  });

  // Get latest health snapshot
  const latestHealth = healthHistory.length > 0 ? healthHistory[0] : null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <div className="mb-4">
          <Link href="/studies" className="text-gray-600 hover:text-black">
            ← Back to Dashboard
          </Link>
        </div>

        {/* Header Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">{projectId}</h1>
          <p className="text-gray-600">Detailed project health and signal tracking</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            {error}
          </div>
        )}

        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
            {successMessage}
          </div>
        )}

        {/* Health Summary */}
        {latestHealth && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Current Health Status</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <HealthMetric
                label="Overall Health"
                value={latestHealth.overall_health_score.toFixed(1)}
                status={latestHealth.health_status}
              />
              <HealthMetric
                label="Timeline Score"
                value={latestHealth.timeline_score?.toFixed(1) || 'N/A'}
              />
              <HealthMetric
                label="Risk Score"
                value={latestHealth.risk_score?.toFixed(1) || 'N/A'}
              />
              <HealthMetric label="TMF Score" value={latestHealth.tmf_score?.toFixed(1) || 'N/A'} />
              <HealthMetric
                label="Enrollment Score"
                value={latestHealth.enrollment_score?.toFixed(1) || 'N/A'}
              />
              <HealthMetric
                label="Budget Score"
                value={latestHealth.budget_score?.toFixed(1) || 'N/A'}
              />
              <HealthMetric
                label="Vendor Score"
                value={latestHealth.vendor_score?.toFixed(1) || 'N/A'}
              />
              <HealthMetric
                label="Active Escalations"
                value={latestHealth.active_escalations_count.toString()}
                highlight={latestHealth.active_escalations_count > 0}
              />
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8">
              <TabButton
                label="Signals"
                count={signals.length}
                isActive={activeTab === 'signals'}
                onClick={() => setActiveTab('signals')}
              />
              <TabButton
                label="Escalations"
                count={escalations.length}
                isActive={activeTab === 'escalations'}
                onClick={() => setActiveTab('escalations')}
              />
              <TabButton
                label="Tracker Uploads"
                count={uploads.length}
                isActive={activeTab === 'uploads'}
                onClick={() => setActiveTab('uploads')}
              />
              <TabButton
                label="Health History"
                count={healthHistory.length}
                isActive={activeTab === 'health'}
                onClick={() => setActiveTab('health')}
              />
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-gray-600">Loading project data...</div>
          </div>
        ) : (
          <>
            {/* Signals Tab */}
            {activeTab === 'signals' && (
              <div>
                {/* Filter */}
                <div className="mb-4">
                  <select
                    value={signalStatusFilter}
                    onChange={(e) => setSignalStatusFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                  >
                    <option value="all">All Statuses</option>
                    <option value="open">Open</option>
                    <option value="acknowledged">Acknowledged</option>
                    <option value="resolved">Resolved</option>
                  </select>
                </div>

                {/* Signals Table */}
                {filteredSignals.length === 0 ? (
                  <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                    <p className="text-gray-600">No signals found for this project</p>
                  </div>
                ) : (
                  <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gray-50 border-b border-gray-200">
                          <tr>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Type
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Description
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Priority
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Status
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Escalation
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Date
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Actions
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {filteredSignals.map((signal) => (
                            <tr
                              key={signal.signal_id}
                              className="border-b border-gray-200 hover:bg-gray-50"
                            >
                              <td className="px-6 py-4 text-sm text-gray-900">
                                {signal.signal_type}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {signal.signal_description}
                              </td>
                              <td className="px-6 py-4 text-sm">
                                <PriorityBadge priority={signal.priority} />
                              </td>
                              <td className="px-6 py-4 text-sm">
                                <StatusBadge status={signal.status} />
                              </td>
                              <td className="px-6 py-4 text-sm">
                                {signal.escalation_level ? (
                                  <EscalationBadge level={signal.escalation_level} />
                                ) : (
                                  <span className="text-gray-400">None</span>
                                )}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {new Date(signal.date_identified).toLocaleDateString()}
                              </td>
                              <td className="px-6 py-4 text-sm">
                                <div className="flex gap-2">
                                  {signal.status === 'open' && (
                                    <>
                                      <button
                                        onClick={() =>
                                          handleSignalStatusUpdate(signal.signal_id, 'acknowledged')
                                        }
                                        disabled={actionLoading === signal.signal_id}
                                        className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-50"
                                      >
                                        {actionLoading === signal.signal_id
                                          ? 'Processing...'
                                          : 'Acknowledge'}
                                      </button>
                                      <button
                                        onClick={() =>
                                          handleSignalStatusUpdate(signal.signal_id, 'resolved')
                                        }
                                        disabled={actionLoading === signal.signal_id}
                                        className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 disabled:opacity-50"
                                      >
                                        {actionLoading === signal.signal_id
                                          ? 'Processing...'
                                          : 'Resolve'}
                                      </button>
                                    </>
                                  )}
                                  {signal.status === 'acknowledged' && (
                                    <button
                                      onClick={() =>
                                        handleSignalStatusUpdate(signal.signal_id, 'resolved')
                                      }
                                      disabled={actionLoading === signal.signal_id}
                                      className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 disabled:opacity-50"
                                    >
                                      {actionLoading === signal.signal_id
                                        ? 'Processing...'
                                        : 'Resolve'}
                                    </button>
                                  )}
                                  {signal.status === 'resolved' && (
                                    <span className="text-gray-400 text-xs">Resolved</span>
                                  )}
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Escalations Tab */}
            {activeTab === 'escalations' && (
              <div>
                {/* Filter */}
                <div className="mb-4">
                  <select
                    value={escalationLevelFilter}
                    onChange={(e) => setEscalationLevelFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                  >
                    <option value="all">All Levels</option>
                    <option value="director">Director</option>
                    <option value="vp">VP</option>
                  </select>
                </div>

                {/* Escalations Table */}
                {filteredEscalations.length === 0 ? (
                  <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                    <p className="text-gray-600">No escalations found for this project</p>
                  </div>
                ) : (
                  <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gray-50 border-b border-gray-200">
                          <tr>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Level
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Reason
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Priority
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Status
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Intervention
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Date
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Actions
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {filteredEscalations.map((escalation) => (
                            <tr
                              key={escalation.escalation_id}
                              className="border-b border-gray-200 hover:bg-gray-50"
                            >
                              <td className="px-6 py-4 text-sm">
                                <EscalationBadge level={escalation.escalation_level} />
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {escalation.escalation_reason}
                              </td>
                              <td className="px-6 py-4 text-sm">
                                <PriorityBadge priority={escalation.priority} />
                              </td>
                              <td className="px-6 py-4 text-sm">
                                <StatusBadge status={escalation.status} />
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {escalation.intervention_recommended}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {new Date(escalation.created_at).toLocaleDateString()}
                              </td>
                              <td className="px-6 py-4 text-sm">
                                <div className="flex gap-2">
                                  {escalation.status === 'open' && (
                                    <>
                                      <button
                                        onClick={() =>
                                          handleEscalationAcknowledge(escalation.escalation_id)
                                        }
                                        disabled={actionLoading === escalation.escalation_id}
                                        className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700 disabled:opacity-50"
                                      >
                                        {actionLoading === escalation.escalation_id
                                          ? 'Processing...'
                                          : 'Acknowledge'}
                                      </button>
                                      <button
                                        onClick={() =>
                                          handleEscalationResolve(escalation.escalation_id)
                                        }
                                        disabled={actionLoading === escalation.escalation_id}
                                        className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 disabled:opacity-50"
                                      >
                                        {actionLoading === escalation.escalation_id
                                          ? 'Processing...'
                                          : 'Resolve'}
                                      </button>
                                    </>
                                  )}
                                  {escalation.status === 'acknowledged' && (
                                    <button
                                      onClick={() =>
                                        handleEscalationResolve(escalation.escalation_id)
                                      }
                                      disabled={actionLoading === escalation.escalation_id}
                                      className="px-3 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 disabled:opacity-50"
                                    >
                                      {actionLoading === escalation.escalation_id
                                        ? 'Processing...'
                                        : 'Resolve'}
                                    </button>
                                  )}
                                  {escalation.status === 'resolved' && (
                                    <span className="text-gray-400 text-xs">Resolved</span>
                                  )}
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Uploads Tab */}
            {activeTab === 'uploads' && (
              <div>
                {uploads.length === 0 ? (
                  <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                    <p className="text-gray-600">No tracker uploads found for this project</p>
                  </div>
                ) : (
                  <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gray-50 border-b border-gray-200">
                          <tr>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              File Name
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Tracker Type
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Uploaded By
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Rows Parsed
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Signals
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Status
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Date
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {uploads.map((upload) => (
                            <tr
                              key={upload.upload_id}
                              className="border-b border-gray-200 hover:bg-gray-50"
                            >
                              <td className="px-6 py-4 text-sm text-gray-900">
                                {upload.original_filename}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {upload.tracker_type}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {upload.uploaded_by}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {upload.rows_parsed}
                              </td>
                              <td className="px-6 py-4 text-sm">
                                {upload.signals_extracted > 0 ? (
                                  <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded font-medium">
                                    {upload.signals_extracted}
                                  </span>
                                ) : (
                                  <span className="text-gray-400">0</span>
                                )}
                              </td>
                              <td className="px-6 py-4 text-sm">
                                <span
                                  className={`px-2 py-1 rounded text-xs font-medium ${
                                    upload.parse_status === 'success'
                                      ? 'bg-green-100 text-green-800'
                                      : 'bg-red-100 text-red-800'
                                  }`}
                                >
                                  {upload.parse_status}
                                </span>
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {new Date(upload.upload_timestamp).toLocaleDateString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Health History Tab */}
            {activeTab === 'health' && (
              <div>
                {healthHistory.length === 0 ? (
                  <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                    <p className="text-gray-600">No health history found for this project</p>
                  </div>
                ) : (
                  <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="bg-gray-50 border-b border-gray-200">
                          <tr>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Date
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Overall Score
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Status
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Timeline
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Risk
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              TMF
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Enrollment
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Budget
                            </th>
                            <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                              Vendor
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {healthHistory.map((snapshot) => (
                            <tr
                              key={snapshot.snapshot_id}
                              className="border-b border-gray-200 hover:bg-gray-50"
                            >
                              <td className="px-6 py-4 text-sm text-gray-900">
                                {new Date(snapshot.snapshot_date).toLocaleDateString()}
                              </td>
                              <td className="px-6 py-4 text-sm font-semibold">
                                {snapshot.overall_health_score.toFixed(1)}
                              </td>
                              <td className="px-6 py-4 text-sm">
                                <span
                                  className={`px-2 py-1 rounded text-xs font-medium ${
                                    snapshot.health_status === 'healthy'
                                      ? 'bg-green-100 text-green-800'
                                      : snapshot.health_status === 'warning'
                                      ? 'bg-yellow-100 text-yellow-800'
                                      : 'bg-red-100 text-red-800'
                                  }`}
                                >
                                  {snapshot.health_status}
                                </span>
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {snapshot.timeline_score?.toFixed(1) || 'N/A'}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {snapshot.risk_score?.toFixed(1) || 'N/A'}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {snapshot.tmf_score?.toFixed(1) || 'N/A'}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {snapshot.enrollment_score?.toFixed(1) || 'N/A'}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {snapshot.budget_score?.toFixed(1) || 'N/A'}
                              </td>
                              <td className="px-6 py-4 text-sm text-gray-600">
                                {snapshot.vendor_score?.toFixed(1) || 'N/A'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

// ============================================================================
// Sub-Components
// ============================================================================

function HealthMetric({
  label,
  value,
  status,
  highlight,
}: {
  label: string;
  value: string;
  status?: string;
  highlight?: boolean;
}) {
  return (
    <div>
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className={`text-2xl font-bold ${highlight ? 'text-red-600' : ''}`}>
        {value}
        {status && (
          <span
            className={`ml-2 text-xs font-medium ${
              status === 'healthy'
                ? 'text-green-600'
                : status === 'warning'
                ? 'text-yellow-600'
                : 'text-red-600'
            }`}
          >
            ({status})
          </span>
        )}
      </div>
    </div>
  );
}

function TabButton({
  label,
  count,
  isActive,
  onClick,
}: {
  label: string;
  count: number;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
        isActive
          ? 'border-black text-black'
          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
      }`}
    >
      {label}{' '}
      <span
        className={`ml-2 px-2 py-1 rounded text-xs ${
          isActive ? 'bg-black text-white' : 'bg-gray-200 text-gray-600'
        }`}
      >
        {count}
      </span>
    </button>
  );
}

function PriorityBadge({ priority }: { priority: number }) {
  const getColor = (p: number) => {
    if (p >= 9) return { bg: 'bg-red-100', text: 'text-red-800' };
    if (p >= 6) return { bg: 'bg-yellow-100', text: 'text-yellow-800' };
    return { bg: 'bg-gray-100', text: 'text-gray-600' };
  };

  const color = getColor(priority);

  return (
    <span className={`px-2 py-1 ${color.bg} ${color.text} rounded text-xs font-medium`}>
      P{priority}
    </span>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, { bg: string; text: string }> = {
    open: { bg: 'bg-blue-100', text: 'text-blue-800' },
    acknowledged: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
    resolved: { bg: 'bg-green-100', text: 'text-green-800' },
  };

  const style = styles[status] || { bg: 'bg-gray-100', text: 'text-gray-600' };

  return (
    <span className={`px-2 py-1 ${style.bg} ${style.text} rounded text-xs font-medium capitalize`}>
      {status}
    </span>
  );
}

function EscalationBadge({ level }: { level: string }) {
  const styles: Record<string, { bg: string; text: string; label: string }> = {
    director: { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Director' },
    vp: { bg: 'bg-red-100', text: 'text-red-800', label: 'VP' },
  };

  const style = styles[level] || { bg: 'bg-gray-100', text: 'text-gray-600', label: level };

  return (
    <span className={`px-2 py-1 ${style.bg} ${style.text} rounded text-xs font-medium`}>
      {style.label}
    </span>
  );
}
