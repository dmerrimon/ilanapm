'use client';

import { useState, useEffect, useCallback } from "react";
import Header from "@/components/Header";
import { apiClient } from "@/lib/api-client";

interface Invoice {
  invoice_id: string;
  invoice_number: string;
  date: string;
  amount: number;
  status: string;
  period_start: string;
  period_end: string;
  pdf_url?: string;
}

interface PaymentMethod {
  id: string;
  type: string;
  last4: string;
  brand: string;
  exp_month: number;
  exp_year: number;
  is_default: boolean;
}

export default function BillingPage() {
  // FreshBooks state
  const [freshbooksConnected, setFreshbooksConnected] = useState(false);
  const [freshbooksAccountId, setFreshbooksAccountId] = useState<string | null>(null);
  const [loadingInvoices, setLoadingInvoices] = useState(false);
  const [invoicesError, setInvoicesError] = useState<string | null>(null);

  const [invoices, setInvoices] = useState<Invoice[]>([]);

  const [paymentMethods] = useState<PaymentMethod[]>([
    {
      id: "pm_001",
      type: "card",
      last4: "4242",
      brand: "Visa",
      exp_month: 12,
      exp_year: 2027,
      is_default: true
    }
  ]);

  const [showAddSeatsModal, setShowAddSeatsModal] = useState(false);
  const [seatsToAdd, setSeatsToAdd] = useState(10);
  const [billingCycle] = useState("monthly");

  // Function definitions (must come before useEffect hooks that use them)
  const checkFreshBooksConnection = async () => {
    try {
      const response = await apiClient.get('/auth/freshbooks/status?org_id=placeholder-org-id');
      setFreshbooksConnected(response.connected);
      setFreshbooksAccountId(response.account_id);
    } catch (error) {
      console.error('Failed to check FreshBooks status:', error);
      setFreshbooksConnected(false);
    }
  };

  const fetchInvoices = useCallback(async () => {
    setLoadingInvoices(true);
    setInvoicesError(null);
    try {
      const response = await apiClient.get('/portal/customer/billing/invoices?org_id=placeholder-org-id&per_page=15');
      setInvoices(response.invoices || []);
    } catch (error: any) {
      console.error('Failed to fetch invoices:', error);
      setInvoicesError(error.message || 'Failed to load invoices');
    } finally {
      setLoadingInvoices(false);
    }
  }, []);

  const connectToFreshBooks = () => {
    // Redirect to OAuth authorization
    const orgId = 'placeholder-org-id'; // TODO: Get from user context
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    window.location.href = `${apiUrl}/auth/freshbooks/authorize?org_id=${orgId}`;
  };

  const handleDownloadInvoice = async (invoiceId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
      const url = `${apiUrl}/portal/customer/billing/invoices/${invoiceId}/pdf?org_id=placeholder-org-id`;

      // Download PDF directly from backend
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('Failed to download invoice PDF');
      }

      // Get the PDF blob
      const blob = await response.blob();

      // Create a download link
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `invoice-${invoiceId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error('Failed to download invoice:', error);
      alert('Failed to download invoice PDF. Please try again.');
    }
  };

  // Check FreshBooks connection status on mount and after OAuth callback
  useEffect(() => {
    // Check for OAuth callback success parameter
    const urlParams = new URLSearchParams(window.location.search);
    const freshbooksConnectedParam = urlParams.get('freshbooks_connected');
    const errorParam = urlParams.get('error');

    // Check connection status
    checkFreshBooksConnection();

    // Show success/error messages
    if (freshbooksConnectedParam === 'true') {
      // Clear the query parameter from URL
      window.history.replaceState({}, '', '/billing');
    }

    if (errorParam) {
      const message = urlParams.get('message') || 'Failed to connect to FreshBooks';
      console.error('FreshBooks connection error:', errorParam, message);
      alert(`FreshBooks connection failed: ${message}`);
      // Clear the query parameters from URL
      window.history.replaceState({}, '', '/billing');
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetch invoices when FreshBooks is connected
  useEffect(() => {
    if (freshbooksConnected) {
      fetchInvoices();
    }
  }, [freshbooksConnected, fetchInvoices]);

  const currentPlan = {
    seats_purchased: 50,
    seats_used: 23,
    seat_rate: 18.00,
    mrr: 414.00,
    next_billing_date: "2026-03-01"
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const calculateNewTotal = () => {
    const newSeats = currentPlan.seats_purchased + seatsToAdd;
    let rate = 20;

    if (newSeats >= 100) rate = 15;
    else if (newSeats >= 51) rate = 16;
    else if (newSeats >= 26) rate = 18;

    return newSeats * rate;
  };

  const handleAddSeats = async () => {
    // TODO: Call Stripe checkout API
    // const response = await fetch('/api/v1/portal/customer/billing/add-seats', {
    //   method: 'POST',
    //   body: JSON.stringify({ additional_seats: seatsToAdd })
    // });

    console.log(`Adding ${seatsToAdd} seats`);
    setShowAddSeatsModal(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-black">Billing & Subscription</h1>
          <p className="text-black">Manage your subscription, invoices, and payment methods.</p>
        </div>

        {/* Current Plan Overview */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-2xl mb-2 text-black">Current Plan</h2>
              <p className="text-black">Standard Plan - {billingCycle === 'monthly' ? 'Monthly' : 'Annual'} Billing</p>
            </div>
            <button
              onClick={() => setShowAddSeatsModal(true)}
              className="px-6 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors"
            >
              Add Seats
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <div className="text-gray-500 text-sm mb-1">Total Seats</div>
              <div className="text-2xl font-light text-black">{currentPlan.seats_purchased}</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Seats Used</div>
              <div className="text-2xl font-light text-black">{currentPlan.seats_used}</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Rate per Seat</div>
              <div className="text-2xl font-light text-black">{formatCurrency(currentPlan.seat_rate)}/mo</div>
            </div>
            <div>
              <div className="text-gray-500 text-sm mb-1">Monthly Total</div>
              <div className="text-2xl font-light text-black">{formatCurrency(currentPlan.mrr)}</div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-black font-medium">Next Billing Date</div>
                <div className="text-black">{formatDate(currentPlan.next_billing_date)}</div>
              </div>
              <div className="text-right">
                <div className="text-black font-medium">Amount Due</div>
                <div className="text-2xl text-black">{formatCurrency(currentPlan.mrr)}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Payment Methods */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl text-black">Payment Methods</h2>
              <button className="text-sm text-black hover:underline">
                Add New
              </button>
            </div>
            <div className="p-6">
              {paymentMethods.map((method) => (
                <div
                  key={method.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-8 bg-gray-100 rounded flex items-center justify-center">
                      <span className="text-xs font-medium text-black">{method.brand}</span>
                    </div>
                    <div>
                      <div className="text-black">•••• {method.last4}</div>
                      <div className="text-sm text-gray-600">
                        Expires {method.exp_month}/{method.exp_year}
                      </div>
                    </div>
                  </div>
                  {method.is_default && (
                    <span className="px-2 py-1 bg-black text-white text-xs rounded">
                      Default
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl text-black">Subscription Management</h2>
            </div>
            <div className="p-6 space-y-4">
              <button className="w-full px-4 py-3 border border-gray-200 rounded hover:bg-gray-50 transition-colors text-left">
                <div className="text-black font-medium">Switch to Annual Billing</div>
                <div className="text-sm text-gray-600">Save 17% with annual payment</div>
              </button>
              <button className="w-full px-4 py-3 border border-gray-200 rounded hover:bg-gray-50 transition-colors text-left">
                <div className="text-black font-medium">Pause Subscription</div>
                <div className="text-sm text-gray-600">Temporarily pause your subscription</div>
              </button>
              <button className="w-full px-4 py-3 border border-red-200 rounded hover:bg-red-50 transition-colors text-left">
                <div className="text-red-600 font-medium">Cancel Subscription</div>
                <div className="text-sm text-gray-600">End your Seleen subscription</div>
              </button>
            </div>
          </div>
        </div>

        {/* FreshBooks Connection Banner */}
        {!freshbooksConnected && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-medium text-blue-900 mb-2">Connect to FreshBooks</h3>
                <p className="text-blue-800 mb-4">
                  Connect your FreshBooks account to view and download your invoices directly from here.
                </p>
                <button
                  onClick={connectToFreshBooks}
                  className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                >
                  Connect FreshBooks
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Invoices */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mt-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-xl text-black">Invoice History</h2>
              {freshbooksConnected && freshbooksAccountId && (
                <span className="text-sm text-green-600">
                  ✓ Connected to FreshBooks
                </span>
              )}
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Invoice
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Billing Period
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {loadingInvoices ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                      Loading invoices...
                    </td>
                  </tr>
                ) : invoicesError ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center">
                      <div className="text-red-600 mb-2">Failed to load invoices</div>
                      <div className="text-sm text-gray-500">{invoicesError}</div>
                      <button
                        onClick={fetchInvoices}
                        className="mt-4 px-4 py-2 bg-black text-white rounded hover:bg-gray-800"
                      >
                        Retry
                      </button>
                    </td>
                  </tr>
                ) : !freshbooksConnected ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                      Connect to FreshBooks to view your invoices
                    </td>
                  </tr>
                ) : invoices.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                      No invoices found
                    </td>
                  </tr>
                ) : (
                  invoices.map((invoice) => (
                    <tr key={invoice.invoice_id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-black font-medium">{invoice.invoice_number}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-black">
                        {formatDate(invoice.date)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-black">
                        {formatDate(invoice.period_start)} - {formatDate(invoice.period_end)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-black">
                        {formatCurrency(invoice.amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded ${
                          invoice.status === 'paid' ? 'bg-green-100 text-green-800' :
                          invoice.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          invoice.status === 'overdue' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {invoice.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => handleDownloadInvoice(invoice.invoice_id)}
                          className="text-black hover:underline text-sm"
                        >
                          Download PDF
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Add Seats Modal */}
      {showAddSeatsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl mb-4 text-black">Add Seats</h3>
            <p className="mb-6 text-black">
              How many additional seats would you like to purchase?
            </p>

            <div className="mb-6">
              <label className="block text-sm font-medium text-black mb-2">
                Number of Seats
              </label>
              <input
                type="number"
                min="1"
                value={seatsToAdd}
                onChange={(e) => setSeatsToAdd(parseInt(e.target.value) || 1)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black text-black"
              />
            </div>

            <div className="bg-gray-50 p-4 rounded mb-6">
              <div className="flex justify-between mb-2">
                <span className="text-black">Current Seats:</span>
                <span className="font-medium text-black">{currentPlan.seats_purchased}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span className="text-black">Additional Seats:</span>
                <span className="font-medium text-black">+{seatsToAdd}</span>
              </div>
              <div className="flex justify-between pt-2 border-t border-gray-200">
                <span className="font-medium text-black">New Total:</span>
                <span className="font-medium text-black">{currentPlan.seats_purchased + seatsToAdd} seats</span>
              </div>
              <div className="flex justify-between mt-4 pt-2 border-t border-gray-200">
                <span className="font-medium text-black">New Monthly Cost:</span>
                <span className="text-xl font-medium text-black">{formatCurrency(calculateNewTotal())}</span>
              </div>
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowAddSeatsModal(false)}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors text-black"
              >
                Cancel
              </button>
              <button
                onClick={handleAddSeats}
                className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors"
              >
                Proceed to Checkout
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
