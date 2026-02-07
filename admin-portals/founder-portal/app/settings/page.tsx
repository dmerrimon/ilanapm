'use client';

import { useState, useEffect } from "react";
import Header from "@/components/Header";
import { apiClient } from "@/lib/api-client";

export default function SettingsPage() {
  const [freshbooksConnected, setFreshbooksConnected] = useState(false);
  const [freshbooksAccountId, setFreshbooksAccountId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [oauthError, setOauthError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const checkFreshBooksConnection = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/auth/freshbooks/status?org_id=founder-org');
      setFreshbooksConnected(response.connected);
      setFreshbooksAccountId(response.account_id);
    } catch (error) {
      console.error('Failed to check FreshBooks status:', error);
      setFreshbooksConnected(false);
    } finally {
      setLoading(false);
    }
  };

  const connectToFreshBooks = () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    window.location.href = `${apiUrl}/auth/freshbooks/authorize?org_id=founder-org`;
  };

  const disconnectFreshBooks = async () => {
    if (!confirm('Are you sure you want to disconnect FreshBooks? Customers will no longer be able to view their invoices.')) {
      return;
    }

    try {
      await apiClient.post('/auth/freshbooks/disconnect?org_id=founder-org');
      setFreshbooksConnected(false);
      setFreshbooksAccountId(null);
      setSuccessMessage('FreshBooks disconnected successfully');
    } catch (error) {
      console.error('Failed to disconnect FreshBooks:', error);
      alert('Failed to disconnect FreshBooks. Please try again.');
    }
  };

  useEffect(() => {
    // Check for OAuth callback success parameter
    const urlParams = new URLSearchParams(window.location.search);
    const freshbooksConnectedParam = urlParams.get('freshbooks_connected');
    const errorParam = urlParams.get('error');

    // Check connection status
    checkFreshBooksConnection();

    // Show success/error messages
    if (freshbooksConnectedParam === 'true') {
      setSuccessMessage('FreshBooks connected successfully! Customer invoices are now available.');
      // Clear the query parameter from URL
      window.history.replaceState({}, '', '/settings');
    }

    if (errorParam) {
      const message = urlParams.get('message') || 'Failed to connect to FreshBooks';
      console.error('FreshBooks connection error:', errorParam, message);
      setOauthError(`FreshBooks connection failed: ${message}`);
      // Clear the query parameters from URL
      window.history.replaceState({}, '', '/settings');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-black">Settings</h1>
          <p className="text-black">Manage integrations and system settings.</p>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">✓</span>
                <p className="text-green-800">{successMessage}</p>
              </div>
              <button
                onClick={() => setSuccessMessage(null)}
                className="text-green-600 hover:text-green-800"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* OAuth Error Banner */}
        {oauthError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-medium text-red-900 mb-2">Connection Error</h3>
                <p className="text-red-800">{oauthError}</p>
              </div>
              <button
                onClick={() => setOauthError(null)}
                className="text-red-600 hover:text-red-800"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Integrations Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl text-black">Integrations</h2>
          </div>

          {/* FreshBooks Integration */}
          <div className="p-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-3xl">📊</span>
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-black mb-2">FreshBooks</h3>
                  <p className="text-gray-600 mb-4">
                    Connect your FreshBooks account to automatically sync customer invoices to their portals.
                  </p>

                  {loading ? (
                    <div className="text-gray-500">Checking connection status...</div>
                  ) : freshbooksConnected ? (
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-green-600 text-lg">✓</span>
                        <span className="text-green-600 font-medium">Connected</span>
                        {freshbooksAccountId && (
                          <span className="text-gray-500 text-sm">
                            (Account: {freshbooksAccountId})
                          </span>
                        )}
                      </div>
                      <button
                        onClick={disconnectFreshBooks}
                        className="px-4 py-2 border border-red-300 text-red-600 rounded hover:bg-red-50 transition-colors"
                      >
                        Disconnect
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={connectToFreshBooks}
                      className="px-6 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors"
                    >
                      Connect FreshBooks
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Info Box */}
          {freshbooksConnected && (
            <div className="px-6 pb-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-blue-900 mb-2">How it works</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Invoices are synced from your FreshBooks account</li>
                  <li>• Customers see only their own invoices in their portal</li>
                  <li>• Invoice PDFs are downloaded directly from FreshBooks</li>
                  <li>• No customer action required - it just works!</li>
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Future Integrations Placeholder */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mt-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl text-black">Coming Soon</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 border border-gray-200 rounded-lg opacity-50">
                <div className="text-3xl mb-2">💳</div>
                <div className="text-black font-medium mb-1">Stripe</div>
                <div className="text-sm text-gray-600">Payment processing</div>
              </div>
              <div className="text-center p-6 border border-gray-200 rounded-lg opacity-50">
                <div className="text-3xl mb-2">📧</div>
                <div className="text-black font-medium mb-1">SendGrid</div>
                <div className="text-sm text-gray-600">Email notifications</div>
              </div>
              <div className="text-center p-6 border border-gray-200 rounded-lg opacity-50">
                <div className="text-3xl mb-2">🔔</div>
                <div className="text-black font-medium mb-1">Slack</div>
                <div className="text-sm text-gray-600">Team notifications</div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
