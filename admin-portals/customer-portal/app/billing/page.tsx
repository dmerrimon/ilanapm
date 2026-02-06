'use client';

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";

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
  const [invoices] = useState<Invoice[]>([
    {
      invoice_id: "inv_001",
      invoice_number: "INV-2026-001",
      date: "2026-01-01",
      amount: 414.00,
      status: "paid",
      period_start: "2026-01-01",
      period_end: "2026-01-31"
    },
    {
      invoice_id: "inv_002",
      invoice_number: "INV-2025-012",
      date: "2025-12-01",
      amount: 414.00,
      status: "paid",
      period_start: "2025-12-01",
      period_end: "2025-12-31"
    },
    {
      invoice_id: "inv_003",
      invoice_number: "INV-2025-011",
      date: "2025-11-01",
      amount: 414.00,
      status: "paid",
      period_start: "2025-11-01",
      period_end: "2025-11-30"
    }
  ]);

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
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-8">
              <Link href="/dashboard">
                <Image
                  src="/logo.png"
                  alt="Seleen Logo"
                  width={120}
                  height={32}
                  priority
                />
              </Link>
              <nav className="flex gap-6">
                <Link href="/dashboard" className="text-gray-600 hover:text-black transition-colors">
                  Dashboard
                </Link>
                <Link href="/users" className="text-gray-600 hover:text-black transition-colors">
                  Users
                </Link>
                <Link href="/billing" className="text-black font-medium">
                  Billing
                </Link>
                <Link href="/analytics" className="text-gray-600 hover:text-black transition-colors">
                  Analytics
                </Link>
                <Link href="/settings" className="text-gray-600 hover:text-black transition-colors">
                  Settings
                </Link>
              </nav>
            </div>
            <button className="px-4 py-2 text-gray-600 hover:text-black transition-colors">
              Sign Out
            </button>
          </div>
        </div>
      </header>

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

        {/* Invoices */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mt-8">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl text-black">Invoice History</h2>
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
                {invoices.map((invoice) => (
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
                      <span className="px-2 py-1 text-xs rounded bg-green-100 text-green-800">
                        {invoice.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button className="text-black hover:underline text-sm">
                        Download PDF
                      </button>
                    </td>
                  </tr>
                ))}
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
