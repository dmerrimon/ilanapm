'use client';

import { useState, useEffect } from "react";
import Header from "@/components/Header";
import { apiClient } from "@/lib/api-client";

interface Activation {
  activation_id: string;
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  device_id: string;
  device_name: string;
  is_active: boolean;
  activated_at: string;
  deactivated_at: string | null;
  last_api_call: string | null;
  api_call_count: number;
  ms_project_version: string;
  addin_version: string;
}

export default function DevicesPage() {
  const [activations, setActivations] = useState<Activation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeCount, setActiveCount] = useState(0);
  const [inactiveCount, setInactiveCount] = useState(0);
  const [showDeactivateModal, setShowDeactivateModal] = useState(false);
  const [selectedActivation, setSelectedActivation] = useState<Activation | null>(null);
  const [deactivating, setDeactivating] = useState(false);

  useEffect(() => {
    fetchActivations();
  }, []);

  const fetchActivations = async () => {
    setLoading(true);
    setError("");
    try {
      const response = await apiClient.get('/portal/customer/activations');
      setActivations(response.activations);
      setActiveCount(response.active_count);
      setInactiveCount(response.inactive_count);
    } catch (err: any) {
      setError(err.message || "Failed to load devices");
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivate = (activation: Activation) => {
    setSelectedActivation(activation);
    setShowDeactivateModal(true);
  };

  const confirmDeactivate = async () => {
    if (!selectedActivation) return;

    setDeactivating(true);
    try {
      await apiClient.delete(`/portal/customer/activations/${selectedActivation.activation_id}`);

      // Refresh the list
      await fetchActivations();

      setShowDeactivateModal(false);
      setSelectedActivation(null);
    } catch (err: any) {
      setError(err.message || "Failed to deactivate device");
    } finally {
      setDeactivating(false);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never";
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getRelativeTime = (dateString: string | null) => {
    if (!dateString) return "Never";
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return formatDate(dateString);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-black">Active Devices</h1>
          <p className="text-black">Manage device activations and seat usage across your organization.</p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Active Devices</div>
            <div className="text-3xl font-light text-black">{activeCount}</div>
            <div className="text-xs text-gray-400 mt-1">Currently using seats</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Inactive Devices</div>
            <div className="text-3xl font-light text-black">{inactiveCount}</div>
            <div className="text-xs text-gray-400 mt-1">Previously deactivated</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Activations</div>
            <div className="text-3xl font-light text-black">{activations.length}</div>
            <div className="text-xs text-gray-400 mt-1">All time</div>
          </div>
        </div>

        {/* Devices Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-xl text-black">All Devices</h2>
            <button
              onClick={fetchActivations}
              disabled={loading}
              className="px-4 py-2 bg-gray-100 text-black rounded hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              {loading ? "Loading..." : "Refresh"}
            </button>
          </div>

          {loading ? (
            <div className="px-6 py-12 text-center text-gray-500">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-black mx-auto mb-4"></div>
              Loading devices...
            </div>
          ) : activations.length === 0 ? (
            <div className="px-6 py-12 text-center text-gray-500">
              <p>No device activations found.</p>
              <p className="text-sm mt-2">Users will appear here once they activate the desktop add-in.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      Device
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      Version
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      Last Activity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      API Calls
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {activations.map((activation) => (
                    <tr key={activation.activation_id} className={!activation.is_active ? "opacity-50" : ""}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-black">
                          {activation.first_name} {activation.last_name}
                        </div>
                        <div className="text-xs text-gray-500">{activation.email}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-black">
                          {activation.device_name || "Unknown Device"}
                        </div>
                        <div className="text-xs text-gray-500 font-mono">
                          {activation.device_id.substring(0, 12)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-black">
                          MS Project {activation.ms_project_version || "N/A"}
                        </div>
                        {activation.addin_version && (
                          <div className="text-xs text-gray-500">
                            Add-in v{activation.addin_version}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-black">
                          {getRelativeTime(activation.last_api_call)}
                        </div>
                        <div className="text-xs text-gray-500">
                          Activated {formatDate(activation.activated_at)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-black">
                        {activation.api_call_count.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {activation.is_active ? (
                          <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            Active
                          </span>
                        ) : (
                          <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                            Inactive
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        {activation.is_active ? (
                          <button
                            onClick={() => handleDeactivate(activation)}
                            className="text-red-600 hover:text-red-900 hover:underline"
                          >
                            Deactivate
                          </button>
                        ) : (
                          <span className="text-gray-400">N/A</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* Deactivation Confirmation Modal */}
      {showDeactivateModal && selectedActivation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-xl font-semibold text-black mb-4">
              Deactivate Device?
            </h3>
            <p className="text-gray-700 mb-4">
              Are you sure you want to deactivate this device?
            </p>
            <div className="bg-gray-50 p-4 rounded mb-6 space-y-2">
              <div className="text-sm">
                <span className="text-gray-600">User:</span>{" "}
                <span className="text-black font-medium">
                  {selectedActivation.first_name} {selectedActivation.last_name}
                </span>
              </div>
              <div className="text-sm">
                <span className="text-gray-600">Device:</span>{" "}
                <span className="text-black font-medium">
                  {selectedActivation.device_name || "Unknown Device"}
                </span>
              </div>
              <div className="text-sm">
                <span className="text-gray-600">Last Activity:</span>{" "}
                <span className="text-black">
                  {getRelativeTime(selectedActivation.last_api_call)}
                </span>
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-6">
              This will free up one seat. The user will need to re-activate on this device to use the add-in again.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowDeactivateModal(false);
                  setSelectedActivation(null);
                }}
                disabled={deactivating}
                className="flex-1 px-4 py-2 border border-gray-300 rounded text-black hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmDeactivate}
                disabled={deactivating}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {deactivating ? "Deactivating..." : "Deactivate Device"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
