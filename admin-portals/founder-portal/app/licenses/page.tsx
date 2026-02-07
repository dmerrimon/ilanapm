'use client';

import { useState } from "react";
import Header from "@/components/Header";

interface License {
  license_key: string;
  org_name: string;
  seats: number;
  status: string;
  created_at: string;
  expires_at: string | null;
}

export default function LicensesPage() {
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [orgName, setOrgName] = useState("");
  const [seats, setSeats] = useState(50);
  const [adminEmail, setAdminEmail] = useState("");

  const licenses: License[] = [
    {
      license_key: "SELEEN-MTCH-5024-XK7P",
      org_name: "MedTech Solutions",
      seats: 50,
      status: "active",
      created_at: "2026-02-05",
      expires_at: null
    },
    {
      license_key: "SELEEN-HLTH-2513-QR8M",
      org_name: "HealthCare Innovations",
      seats: 25,
      status: "active",
      created_at: "2026-02-04",
      expires_at: null
    },
    {
      license_key: "SELEEN-BIOM-7536-LP4N",
      org_name: "BioMed Research Corp",
      seats: 75,
      status: "trial",
      created_at: "2026-02-03",
      expires_at: "2026-08-03"
    },
    {
      license_key: "SELEEN-CLIN-9248-ZT2V",
      org_name: "Clinical Trials Ltd",
      seats: 100,
      status: "active",
      created_at: "2026-01-28",
      expires_at: null
    },
    {
      license_key: "SELEEN-REGS-4167-WK5D",
      org_name: "Regulatory Solutions Inc",
      seats: 30,
      status: "paused",
      created_at: "2026-01-20",
      expires_at: null
    },
  ];

  const handleGenerateLicense = async () => {
    if (!orgName || !adminEmail) {
      alert("Please fill in all fields");
      return;
    }

    // TODO: Call API to generate license
    // const response = await fetch('/api/v1/portal/founder/licenses/generate', {
    //   method: 'POST',
    //   body: JSON.stringify({ org_name: orgName, seats, admin_email: adminEmail })
    // });

    console.log("Generating license for:", orgName, seats, adminEmail);
    setShowGenerateModal(false);
    setOrgName("");
    setSeats(50);
    setAdminEmail("");
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert("License key copied to clipboard!");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl mb-2 text-black">License Management</h1>
            <p className="text-black">Generate and manage customer licenses</p>
          </div>
          <button
            onClick={() => setShowGenerateModal(true)}
            className="px-6 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors"
          >
            Generate New License
          </button>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Licenses</div>
            <div className="text-3xl font-light text-black">{licenses.length}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Active</div>
            <div className="text-3xl font-light text-black">
              {licenses.filter(l => l.status === 'active').length}
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Trial</div>
            <div className="text-3xl font-light text-black">
              {licenses.filter(l => l.status === 'trial').length}
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Seats</div>
            <div className="text-3xl font-light text-black">
              {licenses.reduce((sum, l) => sum + l.seats, 0)}
            </div>
          </div>
        </div>

        {/* Licenses Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl text-black">All Licenses</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    License Key
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Organization
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Seats
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Expires
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-black uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {licenses.map((license) => (
                  <tr key={license.license_key}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <code className="text-black bg-gray-50 px-2 py-1 rounded font-mono text-sm">
                          {license.license_key}
                        </code>
                        <button
                          onClick={() => copyToClipboard(license.license_key)}
                          className="text-black hover:underline text-xs"
                        >
                          Copy
                        </button>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black font-medium">
                      {license.org_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {license.seats}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded ${
                        license.status === 'active' ? 'bg-green-100 text-green-800' :
                        license.status === 'trial' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {license.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {new Date(license.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-black">
                      {license.expires_at ? new Date(license.expires_at).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button className="text-black hover:underline text-sm mr-3">
                        Revoke
                      </button>
                      <button className="text-black hover:underline text-sm">
                        Extend
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-black text-sm">
            <strong>Note:</strong> License keys are automatically generated using a secure algorithm.
            Each key is unique and tied to the organization. Trial licenses expire after 6 months by default.
          </p>
        </div>
      </main>

      {/* Generate License Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl mb-4 text-black">Generate New License</h3>

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Organization Name
                </label>
                <input
                  type="text"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  placeholder="Acme Medical Devices Inc"
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black text-black"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Admin Email
                </label>
                <input
                  type="email"
                  value={adminEmail}
                  onChange={(e) => setAdminEmail(e.target.value)}
                  placeholder="admin@acmemedical.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black text-black"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-black mb-2">
                  Number of Seats
                </label>
                <input
                  type="number"
                  min="1"
                  value={seats}
                  onChange={(e) => setSeats(parseInt(e.target.value) || 1)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black text-black"
                />
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded mb-6">
              <div className="text-sm text-black mb-2">
                <strong>Preview:</strong>
              </div>
              <div className="text-sm text-black">
                Organization: <strong>{orgName || "Not set"}</strong>
              </div>
              <div className="text-sm text-black">
                Seats: <strong>{seats}</strong>
              </div>
              <div className="text-sm text-black">
                Admin: <strong>{adminEmail || "Not set"}</strong>
              </div>
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowGenerateModal(false);
                  setOrgName("");
                  setSeats(50);
                  setAdminEmail("");
                }}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors text-black"
              >
                Cancel
              </button>
              <button
                onClick={handleGenerateLicense}
                className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors"
              >
                Generate License
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
