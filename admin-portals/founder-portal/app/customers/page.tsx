'use client';

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";

interface Customer {
  org_id: string;
  org_name: string;
  seats_purchased: number;
  seats_used: number;
  seat_rate: number;
  mrr: number;
  status: string;
  created_at: string;
  admin_email: string;
}

export default function CustomersPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const customers: Customer[] = [
    {
      org_id: "org_001",
      org_name: "MedTech Solutions",
      seats_purchased: 50,
      seats_used: 42,
      seat_rate: 18.00,
      mrr: 900.00,
      status: "active",
      created_at: "2026-02-05",
      admin_email: "admin@medtech.com"
    },
    {
      org_id: "org_002",
      org_name: "HealthCare Innovations",
      seats_purchased: 25,
      seats_used: 23,
      seat_rate: 20.00,
      mrr: 500.00,
      status: "active",
      created_at: "2026-02-04",
      admin_email: "admin@healthcareinnovations.com"
    },
    {
      org_id: "org_003",
      org_name: "BioMed Research Corp",
      seats_purchased: 75,
      seats_used: 61,
      seat_rate: 16.00,
      mrr: 1200.00,
      status: "trial",
      created_at: "2026-02-03",
      admin_email: "admin@biomedresearch.com"
    },
    {
      org_id: "org_004",
      org_name: "Clinical Trials Ltd",
      seats_purchased: 100,
      seats_used: 87,
      seat_rate: 15.00,
      mrr: 1500.00,
      status: "active",
      created_at: "2026-01-28",
      admin_email: "admin@clinicaltrials.com"
    },
    {
      org_id: "org_005",
      org_name: "Regulatory Solutions Inc",
      seats_purchased: 30,
      seats_used: 12,
      seat_rate: 20.00,
      mrr: 600.00,
      status: "paused",
      created_at: "2026-01-20",
      admin_email: "admin@regsolutions.com"
    },
    {
      org_id: "org_006",
      org_name: "Device Manufacturing Co",
      seats_purchased: 60,
      seats_used: 58,
      seat_rate: 16.00,
      mrr: 960.00,
      status: "active",
      created_at: "2026-01-15",
      admin_email: "admin@devicemfg.com"
    }
  ];

  const filteredCustomers = customers.filter(customer => {
    const matchesSearch = customer.org_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         customer.admin_email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || customer.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const totalMRR = customers.reduce((sum, c) => sum + c.mrr, 0);
  const totalSeats = customers.reduce((sum, c) => sum + c.seats_purchased, 0);
  const activeCustomers = customers.filter(c => c.status === 'active').length;

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
                <Link href="/customers" className="text-black font-medium">
                  Customers
                </Link>
                <Link href="/analytics" className="text-gray-600 hover:text-black transition-colors">
                  Analytics
                </Link>
                <Link href="/licenses" className="text-gray-600 hover:text-black transition-colors">
                  Licenses
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
          <h1 className="text-4xl mb-2 text-black">All Customers</h1>
          <p className="text-black">Manage customer organizations and subscriptions</p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Customers</div>
            <div className="text-3xl font-light text-black">{customers.length}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Active Customers</div>
            <div className="text-3xl font-light text-black">{activeCustomers}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Seats</div>
            <div className="text-3xl font-light text-black">{totalSeats}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total MRR</div>
            <div className="text-3xl font-light text-black">{formatCurrency(totalMRR)}</div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex gap-4 flex-col md:flex-row">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search by organization name or email..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-black"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setStatusFilter("all")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  statusFilter === "all"
                    ? "bg-black text-white"
                    : "bg-white text-black border border-gray-300 hover:bg-gray-50"
                }`}
              >
                All
              </button>
              <button
                onClick={() => setStatusFilter("active")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  statusFilter === "active"
                    ? "bg-black text-white"
                    : "bg-white text-black border border-gray-300 hover:bg-gray-50"
                }`}
              >
                Active
              </button>
              <button
                onClick={() => setStatusFilter("trial")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  statusFilter === "trial"
                    ? "bg-black text-white"
                    : "bg-white text-black border border-gray-300 hover:bg-gray-50"
                }`}
              >
                Trial
              </button>
              <button
                onClick={() => setStatusFilter("paused")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  statusFilter === "paused"
                    ? "bg-black text-white"
                    : "bg-white text-black border border-gray-300 hover:bg-gray-50"
                }`}
              >
                Paused
              </button>
            </div>
          </div>
        </div>

        {/* Customers Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Organization
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Admin Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Seats
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    MRR
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredCustomers.map((customer) => (
                  <tr key={customer.org_id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-black font-medium">{customer.org_name}</div>
                      <div className="text-sm text-gray-600">{customer.org_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {customer.admin_email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {customer.seats_used}/{customer.seats_purchased}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {formatCurrency(customer.seat_rate)}/mo
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {formatCurrency(customer.mrr)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded ${
                        customer.status === 'active' ? 'bg-green-100 text-green-800' :
                        customer.status === 'trial' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {customer.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {new Date(customer.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link href={`/customers/${customer.org_id}`} className="text-black hover:underline text-sm">
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {filteredCustomers.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No customers found matching your search criteria.
          </div>
        )}
      </main>
    </div>
  );
}
