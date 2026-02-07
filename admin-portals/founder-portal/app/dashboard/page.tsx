'use client';

import Link from "next/link";
import Header from "@/components/Header";

export default function DashboardPage() {
  // TODO: Fetch actual data from FastAPI backend
  const systemData = {
    total_customers: 12,
    total_seats: 485,
    active_seats: 312,
    total_mrr: 8730.00,
    system_health: "healthy",
    api_uptime: 99.8,
    templates_generated_today: 234,
    active_users_today: 156
  };

  const recentCustomers = [
    { org_name: "MedTech Solutions", seats: 50, mrr: 900, status: "active", created_at: "2026-02-05" },
    { org_name: "HealthCare Innovations", seats: 25, mrr: 500, status: "active", created_at: "2026-02-04" },
    { org_name: "BioMed Research Corp", seats: 75, mrr: 1200, status: "trial", created_at: "2026-02-03" },
  ];

  const systemAlerts = [
    { type: "info", message: "Database backup completed successfully", time: "2 hours ago" },
    { type: "warning", message: "ML model response time increased by 15%", time: "5 hours ago" },
    { type: "success", message: "New customer onboarded: MedTech Solutions", time: "1 day ago" },
  ];

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-black">System Dashboard</h1>
          <p className="text-black">Monitor platform health and customer metrics</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Customers</div>
            <div className="text-3xl font-light text-black">{systemData.total_customers}</div>
            <div className="text-sm text-green-600 mt-2">↑ 3 new this month</div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Active Seats</div>
            <div className="text-3xl font-light text-black">{systemData.active_seats}/{systemData.total_seats}</div>
            <div className="text-sm text-gray-600 mt-2">{Math.round(systemData.active_seats / systemData.total_seats * 100)}% utilization</div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Monthly Recurring Revenue</div>
            <div className="text-3xl font-light text-black">{formatCurrency(systemData.total_mrr)}</div>
            <div className="text-sm text-green-600 mt-2">↑ 12% from last month</div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">System Health</div>
            <div className="text-3xl font-light text-black capitalize">{systemData.system_health}</div>
            <div className="text-sm text-gray-600 mt-2">{systemData.api_uptime}% uptime</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Today's Activity */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl mb-4 text-black">Today's Activity</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded">
                <div>
                  <div className="text-black font-medium">Templates Generated</div>
                  <div className="text-sm text-gray-600">Across all customers</div>
                </div>
                <div className="text-2xl font-light text-black">{systemData.templates_generated_today}</div>
              </div>
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded">
                <div>
                  <div className="text-black font-medium">Active Users</div>
                  <div className="text-sm text-gray-600">Currently online</div>
                </div>
                <div className="text-2xl font-light text-black">{systemData.active_users_today}</div>
              </div>
            </div>
          </div>

          {/* System Alerts */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl mb-4 text-black">System Alerts</h2>
            <div className="space-y-3">
              {systemAlerts.map((alert, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded">
                  <div className={`w-2 h-2 rounded-full mt-1.5 ${
                    alert.type === 'success' ? 'bg-green-500' :
                    alert.type === 'warning' ? 'bg-yellow-500' :
                    'bg-blue-500'
                  }`} />
                  <div className="flex-1">
                    <div className="text-black text-sm">{alert.message}</div>
                    <div className="text-xs text-gray-500 mt-1">{alert.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Customers */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-xl text-black">Recent Customers</h2>
            <Link href="/customers" className="text-sm text-black hover:underline">
              View All
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Organization
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Seats
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
                {recentCustomers.map((customer, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-black font-medium">{customer.org_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {customer.seats}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {formatCurrency(customer.mrr)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded ${
                        customer.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {customer.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {new Date(customer.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link href={`/customers/${index + 1}`} className="text-black hover:underline text-sm">
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
