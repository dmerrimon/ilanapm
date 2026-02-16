'use client';

import { useState } from "react";
import Link from "next/link";
import Header from "@/components/Header";

export default function SettingsPage() {
  const [orgName, setOrgName] = useState("Demo Organization");
  const [billingEmail, setBillingEmail] = useState("billing@example.com");
  const [notifyOnNewUsers, setNotifyOnNewUsers] = useState(true);
  const [notifyOnBilling, setNotifyOnBilling] = useState(true);
  const [notifyOnUsage, setNotifyOnUsage] = useState(false);

  const [showTransferModal, setShowTransferModal] = useState(false);
  const [transferEmail, setTransferEmail] = useState("");
  const [transferMessage, setTransferMessage] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  // Intelligence Settings
  const tier = 'core'; // Mock - get from auth context
  const [warningThreshold, setWarningThreshold] = useState(15);
  const [criticalThreshold, setCriticalThreshold] = useState(30);
  const financialRate = 733000; // Fixed for Core tier

  const currentAdmin = {
    name: "John Doe",
    email: "john.doe@example.com"
  };

  const handleSaveSettings = async () => {
    setIsSaving(true);

    // TODO: Call API to save settings
    // await fetch('/api/v1/portal/customer/settings', {
    //   method: 'PUT',
    //   body: JSON.stringify({ org_name: orgName, billing_email: billingEmail })
    // });

    setTimeout(() => {
      setIsSaving(false);
      alert("Settings saved successfully!");
    }, 1000);
  };

  const handleTransferAdmin = async () => {
    if (!transferEmail) {
      alert("Please enter an email address");
      return;
    }

    // TODO: Call API to initiate admin transfer
    // await fetch('/api/v1/portal/customer/admin-transfer', {
    //   method: 'POST',
    //   body: JSON.stringify({ to_user_email: transferEmail, message: transferMessage })
    // });

    console.log("Transferring admin to:", transferEmail);
    setShowTransferModal(false);
    setTransferEmail("");
    setTransferMessage("");
    alert("Admin transfer request sent! The new admin must accept the transfer.");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-black">Organization Settings</h1>
          <p className="text-black">Manage your organization details and preferences.</p>
        </div>

        {/* Organization Details */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl mb-6 text-black">Organization Details</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Organization Name
              </label>
              <input
                type="text"
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black text-black"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-black mb-2">
                Billing Email
              </label>
              <input
                type="email"
                value={billingEmail}
                onChange={(e) => setBillingEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black text-black"
              />
              <p className="text-sm text-gray-600 mt-1">
                Invoices and billing notifications will be sent to this email
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-black mb-2">
                License Key
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value="SELEEN-****-****-XXXX"
                  disabled
                  className="flex-1 px-3 py-2 border border-gray-300 rounded bg-gray-50 text-black"
                />
                <button className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors text-black">
                  Copy
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Notification Preferences */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl mb-6 text-black">Notification Preferences</h2>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-black font-medium">New User Activations</div>
                <div className="text-sm text-gray-600">Get notified when new users join your organization</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifyOnNewUsers}
                  onChange={(e) => setNotifyOnNewUsers(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-gray-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-black"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <div className="text-black font-medium">Billing Notifications</div>
                <div className="text-sm text-gray-600">Receive alerts about billing and payment updates</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifyOnBilling}
                  onChange={(e) => setNotifyOnBilling(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-gray-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-black"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <div className="text-black font-medium">Usage Reports</div>
                <div className="text-sm text-gray-600">Monthly summary of template generation and activity</div>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notifyOnUsage}
                  onChange={(e) => setNotifyOnUsage(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-gray-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-black"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Admin Ownership */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl mb-6 text-black">Admin Ownership</h2>

          <div className="bg-gray-50 border border-gray-200 rounded p-4 mb-4">
            <div className="text-sm text-gray-600 mb-1">Current Admin</div>
            <div className="text-black font-medium">{currentAdmin.name}</div>
            <div className="text-black">{currentAdmin.email}</div>
          </div>

          <p className="text-black mb-4">
            Transfer admin privileges to another user in your organization. The new admin will have full
            control over the organization, including billing, user management, and settings.
          </p>

          <button
            onClick={() => setShowTransferModal(true)}
            className="px-4 py-2 border border-red-300 text-red-600 rounded hover:bg-red-50 transition-colors"
          >
            Transfer Admin Ownership
          </button>
        </div>

        {/* Intelligence Settings */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl text-black">Intelligence Settings</h2>
          </div>

          {/* Variance Thresholds */}
          <div className="mb-6">
            <h3 className="text-base font-medium text-black mb-4">Variance Detection Thresholds</h3>
            <p className="text-sm text-gray-600 mb-4">
              Configure when variances from industry benchmarks trigger warnings or critical alerts.
            </p>

            {/* Warning Threshold */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-black">
                  Warning Threshold
                </label>
                <span className="px-2 py-1 bg-amber-100 text-amber-800 text-sm font-medium rounded">
                  {warningThreshold}%
                </span>
              </div>
              <input
                type="range"
                min="10"
                max="25"
                step="1"
                value={warningThreshold}
                onChange={(e) => setWarningThreshold(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-amber-600"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>10%</span>
                <span>25%</span>
              </div>
              <p className="text-xs text-gray-600 mt-2">
                Tasks with variances above this threshold will be flagged as warnings.
              </p>
            </div>

            {/* Critical Threshold */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-black">
                  Critical Threshold
                </label>
                <span className="px-2 py-1 bg-red-100 text-red-800 text-sm font-medium rounded">
                  {criticalThreshold}%
                </span>
              </div>
              <input
                type="range"
                min="25"
                max="50"
                step="5"
                value={criticalThreshold}
                onChange={(e) => setCriticalThreshold(Number(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-red-600"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>25%</span>
                <span>50%</span>
              </div>
              <p className="text-xs text-gray-600 mt-2">
                Tasks with variances above this threshold will be flagged as critical.
              </p>
            </div>
          </div>

          {/* Financial Impact Rate */}
          <div className="mb-6">
            <h3 className="text-base font-medium text-black mb-4">Financial Impact Calculation</h3>
            <p className="text-sm text-gray-600 mb-4">
              The baseline cost used to calculate financial impact of timeline delays.
            </p>

            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-black mb-1">Monthly Delay Cost</div>
                  <div className="text-xs text-gray-600">
                    Based on industry research (WCG Avoca PICAS)
                  </div>
                </div>
                <div className="text-2xl font-light text-black">
                  ${(financialRate / 1000).toFixed(0)}K/month
                </div>
              </div>
            </div>
          </div>

          {/* Feature Access */}
          <div>
            <h3 className="text-base font-medium text-black mb-4">Intelligence Features</h3>

            <div className="space-y-3">
              {/* Core Features */}
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <div className="text-sm font-medium text-black">Industry Benchmark Validation</div>
                  <div className="text-xs text-gray-600">Compare your timelines against industry standards</div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <div className="text-sm font-medium text-black">Variance Detection</div>
                  <div className="text-xs text-gray-600">Identify tasks with significant deviations</div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <div className="text-sm font-medium text-black">Financial Impact Analysis</div>
                  <div className="text-xs text-gray-600">Calculate cost implications of delays</div>
                </div>
              </div>

              {/* Additional Features */}
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <div className="text-sm font-medium text-black">Organization-Specific Benchmarks</div>
                  <div className="text-xs text-gray-600">Train system on your historical data</div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <div className="text-sm font-medium text-black">Confidence Scoring</div>
                  <div className="text-xs text-gray-600">See accuracy scores for AI predictions</div>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <div className="text-sm font-medium text-black">Portfolio Intelligence</div>
                  <div className="text-xs text-gray-600">Cross-study analytics and insights</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tracker Configuration */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl mb-4 text-black">Tracker Configuration</h2>
          <p className="text-black mb-4">
            Configure column mappings for your organization's tracker files (Risk Log, TMF, Budget, Vendor).
            Once configured, CPMs can upload trackers via the MS Project add-in.
          </p>
          <Link href="/settings/tracker-config">
            <button className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors">
              Configure Trackers →
            </button>
          </Link>
          <div className="mt-4">
            <Link href="/settings/task-mapping" className="text-sm text-gray-600 hover:text-black">
              View Task Mappings →
            </Link>
          </div>
        </div>

        {/* API Access (Future Feature) */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl mb-4 text-black">API Access</h2>
          <p className="text-black mb-4">
            API access is coming soon. You'll be able to integrate Seleen with your own systems and workflows.
          </p>
          <button
            disabled
            className="px-4 py-2 bg-gray-200 text-gray-500 rounded cursor-not-allowed"
          >
            Generate API Key (Coming Soon)
          </button>
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSaveSettings}
            disabled={isSaving}
            className="px-6 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors disabled:bg-gray-400"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </main>

      {/* Transfer Admin Modal */}
      {showTransferModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl mb-4 text-black">Transfer Admin Ownership</h3>

            <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
              <p className="text-sm text-black">
                <strong>Warning:</strong> You will lose all admin privileges once the transfer is accepted.
                Make sure you trust the new admin.
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-black mb-2">
                New Admin Email Address
              </label>
              <input
                type="email"
                value={transferEmail}
                onChange={(e) => setTransferEmail(e.target.value)}
                placeholder="newadmin@example.com"
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black text-black"
              />
              <p className="text-sm text-gray-600 mt-1">
                This user must already be a member of your organization
              </p>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-black mb-2">
                Message (Optional)
              </label>
              <textarea
                value={transferMessage}
                onChange={(e) => setTransferMessage(e.target.value)}
                rows={3}
                placeholder="Add a message for the new admin..."
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black text-black"
              />
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowTransferModal(false);
                  setTransferEmail("");
                  setTransferMessage("");
                }}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors text-black"
              >
                Cancel
              </button>
              <button
                onClick={handleTransferAdmin}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                Send Transfer Request
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
