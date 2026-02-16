'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import { getTaskMappings, TaskMapping } from '@/lib/api-client';

type ConfidenceFilter = 'all' | 'high' | 'medium' | 'low';
type ConfidenceLevel = 'high' | 'medium' | 'low';
type SortField = 'task_name' | 'confidence' | 'confirmed';
type SortDirection = 'asc' | 'desc';

export default function TaskMappingPage() {
  const [mappings, setMappings] = useState<TaskMapping[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [confidenceFilter, setConfidenceFilter] = useState<ConfidenceFilter>('all');
  const [sortField, setSortField] = useState<SortField>('confidence');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock org_id - in production, get from auth context
  const orgId = 'demo_org_001';
  const tier = 'core'; // Mock tier - get from auth context

  useEffect(() => {
    loadTaskMappings();
  }, []);

  const loadTaskMappings = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getTaskMappings(orgId);
      setMappings(response.mappings || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load task mappings');
      // Use mock data for development
      setMappings(getMockMappings());
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceLabel = (confidence: number): ConfidenceLevel => {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.6) return 'medium';
    return 'low';
  };

  const getConfidenceBadge = (confidence: number) => {
    const label = getConfidenceLabel(confidence);
    const colors = {
      high: 'bg-green-100 text-green-800',
      medium: 'bg-amber-100 text-amber-800',
      low: 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded ${colors[label]}`}>
        {(confidence * 100).toFixed(0)}% {label}
      </span>
    );
  };

  const filteredMappings = mappings
    .filter((mapping) => {
      // Confidence filter
      if (confidenceFilter !== 'all') {
        const label = getConfidenceLabel(mapping.confidence);
        if (label !== confidenceFilter) return false;
      }

      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          mapping.customer_task_name.toLowerCase().includes(query) ||
          mapping.ontology_task_name.toLowerCase().includes(query)
        );
      }

      return true;
    })
    .sort((a, b) => {
      let aVal: any;
      let bVal: any;

      if (sortField === 'task_name') {
        aVal = a.customer_task_name;
        bVal = b.customer_task_name;
      } else if (sortField === 'confirmed') {
        aVal = a.confirmed_by_user ? 1 : 0;
        bVal = b.confirmed_by_user ? 1 : 0;
      } else if (sortField === 'confidence') {
        aVal = a.confidence;
        bVal = b.confidence;
      }

      if (typeof aVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
    });

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const stats = {
    total: mappings.length,
    confirmed: mappings.filter((m) => m.confirmed_by_user).length,
    high: mappings.filter((m) => getConfidenceLabel(m.confidence) === 'high').length,
    medium: mappings.filter((m) => getConfidenceLabel(m.confidence) === 'medium').length,
    low: mappings.filter((m) => getConfidenceLabel(m.confidence) === 'low').length,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl mb-2 text-black">Task Mapping</h1>
              <p className="text-gray-600">
                Manage how your task names map to our industry-standard ontology
              </p>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Mappings</div>
            <div className="text-2xl font-light text-black">{stats.total}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Confirmed</div>
            <div className="text-2xl font-light text-black">{stats.confirmed}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">High Confidence</div>
            <div className="text-2xl font-light text-green-600">{stats.high}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Medium</div>
            <div className="text-2xl font-light text-amber-600">{stats.medium}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Low</div>
            <div className="text-2xl font-light text-red-600">{stats.low}</div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search task names..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Confidence Filter */}
            <div className="flex gap-2">
              <button
                onClick={() => setConfidenceFilter('all')}
                className={`px-4 py-2 rounded transition-colors ${
                  confidenceFilter === 'all'
                    ? 'bg-black text-white'
                    : 'bg-white text-black border border-gray-300 hover:bg-gray-50'
                }`}
              >
                All ({stats.total})
              </button>
              <button
                onClick={() => setConfidenceFilter('high')}
                className={`px-4 py-2 rounded transition-colors ${
                  confidenceFilter === 'high'
                    ? 'bg-green-600 text-white'
                    : 'bg-white text-black border border-gray-300 hover:bg-gray-50'
                }`}
              >
                High ({stats.high})
              </button>
              <button
                onClick={() => setConfidenceFilter('medium')}
                className={`px-4 py-2 rounded transition-colors ${
                  confidenceFilter === 'medium'
                    ? 'bg-amber-600 text-white'
                    : 'bg-white text-black border border-gray-300 hover:bg-gray-50'
                }`}
              >
                Medium ({stats.medium})
              </button>
              <button
                onClick={() => setConfidenceFilter('low')}
                className={`px-4 py-2 rounded transition-colors ${
                  confidenceFilter === 'low'
                    ? 'bg-red-600 text-white'
                    : 'bg-white text-black border border-gray-300 hover:bg-gray-50'
                }`}
              >
                Low ({stats.low})
              </button>
            </div>
          </div>
        </div>

        {/* Mappings Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-gray-500">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mb-4"></div>
              <p>Loading task mappings...</p>
            </div>
          ) : error ? (
            <div className="p-12 text-center text-red-600">
              <p className="mb-2">Error: {error}</p>
              <button
                onClick={loadTaskMappings}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Retry
              </button>
            </div>
          ) : filteredMappings.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <p className="text-lg mb-2">No task mappings found</p>
              <p className="text-sm">
                {searchQuery || confidenceFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Task mappings will appear here after running variance detection'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th
                      onClick={() => handleSort('task_name')}
                      className="text-left py-3 px-4 text-sm font-medium text-gray-500 cursor-pointer hover:bg-gray-100"
                    >
                      Your Task Name {sortField === 'task_name' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Mapped To (Ontology)
                    </th>
                    <th
                      onClick={() => handleSort('confidence')}
                      className="text-left py-3 px-4 text-sm font-medium text-gray-500 cursor-pointer hover:bg-gray-100"
                    >
                      Confidence {sortField === 'confidence' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                    <th
                      onClick={() => handleSort('confirmed')}
                      className="text-left py-3 px-4 text-sm font-medium text-gray-500 cursor-pointer hover:bg-gray-100"
                    >
                      Status {sortField === 'confirmed' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Created
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredMappings.map((mapping) => (
                    <tr key={mapping.mapping_id} className="border-t border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4 text-black font-medium">
                        {mapping.customer_task_name}
                      </td>
                      <td className="py-4 px-4 text-gray-600">
                        {mapping.ontology_task_name}
                      </td>
                      <td className="py-4 px-4">
                        {getConfidenceBadge(mapping.confidence)}
                      </td>
                      <td className="py-4 px-4">
                        {mapping.confirmed_by_user ? (
                          <span className="flex items-center gap-2 text-green-600">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            Confirmed
                          </span>
                        ) : (
                          <span className="text-gray-500">Auto-learned</span>
                        )}
                      </td>
                      <td className="py-4 px-4 text-sm text-gray-500">
                        {new Date(mapping.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-4 px-4 text-right">
                        <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                          Edit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Help Section */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-black mb-4">How Task Mapping Works</h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-black mb-2">Automatic Learning</h4>
              <p>
                When you run variance detection, our system automatically matches your task names to our
                industry-standard ontology using fuzzy matching and keyword analysis. High-confidence matches
                (≥80%) are applied automatically.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-black mb-2">Confidence Levels</h4>
              <ul className="space-y-1">
                <li><span className="text-green-600">●</span> <strong>High (≥80%):</strong> Very accurate match</li>
                <li><span className="text-amber-600">●</span> <strong>Medium (60-79%):</strong> Probable match</li>
                <li><span className="text-red-600">●</span> <strong>Low (&lt;60%):</strong> Uncertain match</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-black mb-2">Editing Mappings</h4>
              <p>
                Manually edit mappings, confirm suggestions, and create custom task dictionaries.
                All customers can edit and customize their task mappings.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-black mb-2">Training the System</h4>
              <p>
                Upload historical timelines via Calibration feature to train the system on your
                organization's naming conventions. Mappings improve automatically over time.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// Mock data for development
function getMockMappings(): TaskMapping[] {
  return [
    {
      mapping_id: 'map_001',
      customer_task_name: 'Site Agreement Finalization',
      ontology_task_id: 'ont_site_contract',
      ontology_task_name: 'Site Contract Execution',
      confidence: 0.95,
      confirmed_by_user: true,
      created_at: '2026-01-15T10:30:00Z',
    },
    {
      mapping_id: 'map_002',
      customer_task_name: 'IRB Review & Approval',
      ontology_task_id: 'ont_ethics_approval',
      ontology_task_name: 'Ethics Committee Approval',
      confidence: 0.88,
      confirmed_by_user: true,
      created_at: '2026-01-16T14:20:00Z',
    },
    {
      mapping_id: 'map_003',
      customer_task_name: 'Subject Recruitment',
      ontology_task_id: 'ont_enrollment',
      ontology_task_name: 'Patient Enrollment',
      confidence: 0.82,
      confirmed_by_user: false,
      created_at: '2026-01-18T09:15:00Z',
    },
    {
      mapping_id: 'map_004',
      customer_task_name: 'Regulatory Filing - FDA',
      ontology_task_id: 'ont_regulatory_submission',
      ontology_task_name: 'IND/CTA Submission & Review',
      confidence: 0.75,
      confirmed_by_user: false,
      created_at: '2026-01-20T11:45:00Z',
    },
    {
      mapping_id: 'map_005',
      customer_task_name: 'Study Startup Meeting',
      ontology_task_id: 'ont_site_activation',
      ontology_task_name: 'Site Initiation Visit',
      confidence: 0.68,
      confirmed_by_user: false,
      created_at: '2026-01-22T16:30:00Z',
    },
    {
      mapping_id: 'map_006',
      customer_task_name: 'Database Lock',
      ontology_task_id: 'ont_database_lock',
      ontology_task_name: 'Database Lock',
      confidence: 1.0,
      confirmed_by_user: true,
      created_at: '2026-01-25T08:00:00Z',
    },
    {
      mapping_id: 'map_007',
      customer_task_name: 'Contract Review',
      ontology_task_id: 'ont_site_contract',
      ontology_task_name: 'Site Contract Negotiation',
      confidence: 0.55,
      confirmed_by_user: false,
      created_at: '2026-01-28T13:20:00Z',
    },
  ];
}
