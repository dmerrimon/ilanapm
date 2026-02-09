'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import { getProjectProfiles, createProjectProfile, ProjectProfile } from '@/lib/api-client';

type SortField = 'project_name' | 'phase' | 'created_at';
type SortDirection = 'asc' | 'desc';

// Dropdown options from ontology
const PHASES = [
  'Phase I',
  'Phase I/II',
  'Phase II',
  'Phase II/III',
  'Phase III',
  'Phase IV',
  'Post-Market',
];

const THERAPEUTIC_AREAS = [
  'Oncology',
  'Cardiovascular',
  'Infectious Disease',
  'Neurology',
  'Immunology',
  'Rare Disease',
  'Respiratory',
  'Endocrinology',
  'Dermatology',
  'Gastroenterology',
  'Other',
];

const COUNTRIES = [
  'United States',
  'United Kingdom',
  'Germany',
  'France',
  'Spain',
  'Italy',
  'Canada',
  'Australia',
  'Japan',
  'China',
  'South Korea',
  'India',
  'Brazil',
  'Mexico',
  'Argentina',
  'South Africa',
  'Kenya',
  'Nigeria',
  'Ghana',
  'Tanzania',
  'Uganda',
  'Zimbabwe',
  'Zambia',
];

interface NewProfile {
  project_name: string;
  study_id: string;
  phase: string;
  therapeutic_area: string;
  primary_country: string;
  additional_countries: string[];
}

export default function ProjectsPage() {
  const [profiles, setProfiles] = useState<ProjectProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [creating, setCreating] = useState(false);

  // New profile form state
  const [newProfile, setNewProfile] = useState<NewProfile>({
    project_name: '',
    study_id: '',
    phase: '',
    therapeutic_area: '',
    primary_country: '',
    additional_countries: [],
  });

  // Mock org_id - in production, get from auth context
  const orgId = 'demo_org_001';
  const tier = 'core'; // Mock tier - get from auth context

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getProjectProfiles(orgId);
      setProfiles(response.profiles || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load project profiles');
      // Use mock data for development
      setProfiles(getMockProfiles());
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProfile = async () => {
    // Validation
    if (!newProfile.project_name.trim()) {
      alert('Project name is required');
      return;
    }
    if (!newProfile.phase) {
      alert('Phase is required');
      return;
    }
    if (!newProfile.primary_country) {
      alert('Primary country is required');
      return;
    }

    try {
      setCreating(true);
      const created = await createProjectProfile(orgId, newProfile);
      setProfiles([created, ...profiles]);
      setShowCreateModal(false);
      resetForm();
    } catch (err: any) {
      alert(err.message || 'Failed to create project profile');
    } finally {
      setCreating(false);
    }
  };

  const resetForm = () => {
    setNewProfile({
      project_name: '',
      study_id: '',
      phase: '',
      therapeutic_area: '',
      primary_country: '',
      additional_countries: [],
    });
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const filteredProfiles = profiles
    .filter((profile) => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          profile.project_name.toLowerCase().includes(query) ||
          (profile.study_id && profile.study_id.toLowerCase().includes(query)) ||
          (profile.phase && profile.phase.toLowerCase().includes(query)) ||
          (profile.therapeutic_area && profile.therapeutic_area.toLowerCase().includes(query))
        );
      }
      return true;
    })
    .sort((a, b) => {
      let aVal: any = a[sortField];
      let bVal: any = b[sortField];

      if (sortField === 'created_at') {
        aVal = new Date(a.created_at).getTime();
        bVal = new Date(b.created_at).getTime();
      }

      if (typeof aVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
    });

  const stats = {
    total: profiles.length,
    by_phase: profiles.reduce((acc, p) => {
      const phase = p.phase || 'Unknown';
      acc[phase] = (acc[phase] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl mb-2 text-black">Project Management</h1>
              <p className="text-gray-600">
                Configure project profiles to improve intelligence accuracy
              </p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors"
            >
              + New Project Profile
            </button>
          </div>
        </div>

        {/* Tier Notice */}
        {tier === 'core' && (
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="text-blue-600 text-xl">ℹ️</div>
              <div className="flex-1">
                <h3 className="font-medium text-blue-900 mb-1">Core Tier - Basic Profiles</h3>
                <p className="text-sm text-blue-800 mb-2">
                  Create basic project profiles with essential metadata. Advanced features like custom fields, bulk operations, and timeline associations require Calibrated tier or higher.
                </p>
                <button
                  onClick={() => window.location.href = '/billing'}
                  className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                >
                  Learn about Calibrated tier →
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Projects</div>
            <div className="text-2xl font-light text-black">{stats.total}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Phase I/II</div>
            <div className="text-2xl font-light text-black">
              {(stats.by_phase['Phase I'] || 0) + (stats.by_phase['Phase I/II'] || 0) + (stats.by_phase['Phase II'] || 0)}
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Phase III/IV</div>
            <div className="text-2xl font-light text-black">
              {(stats.by_phase['Phase III'] || 0) + (stats.by_phase['Phase IV'] || 0)}
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Post-Market</div>
            <div className="text-2xl font-light text-black">
              {stats.by_phase['Post-Market'] || 0}
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <input
            type="text"
            placeholder="Search by project name, study ID, phase, or therapeutic area..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Projects Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-gray-500">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mb-4"></div>
              <p>Loading project profiles...</p>
            </div>
          ) : error ? (
            <div className="p-12 text-center text-red-600">
              <p className="mb-2">Error: {error}</p>
              <button
                onClick={loadProfiles}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Retry
              </button>
            </div>
          ) : filteredProfiles.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <p className="text-lg mb-2">No project profiles found</p>
              <p className="text-sm mb-4">
                {searchQuery
                  ? 'Try adjusting your search'
                  : 'Create your first project profile to get started'}
              </p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-4 py-2 bg-black text-white rounded hover:bg-gray-800"
              >
                + New Project Profile
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th
                      onClick={() => handleSort('project_name')}
                      className="text-left py-3 px-4 text-sm font-medium text-gray-500 cursor-pointer hover:bg-gray-100"
                    >
                      Project Name {sortField === 'project_name' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Study ID
                    </th>
                    <th
                      onClick={() => handleSort('phase')}
                      className="text-left py-3 px-4 text-sm font-medium text-gray-500 cursor-pointer hover:bg-gray-100"
                    >
                      Phase {sortField === 'phase' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Therapeutic Area
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Primary Country
                    </th>
                    <th
                      onClick={() => handleSort('created_at')}
                      className="text-left py-3 px-4 text-sm font-medium text-gray-500 cursor-pointer hover:bg-gray-100"
                    >
                      Created {sortField === 'created_at' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProfiles.map((profile) => (
                    <tr key={profile.profile_id} className="border-t border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4 text-black font-medium">
                        {profile.project_name}
                      </td>
                      <td className="py-4 px-4 text-gray-600">
                        {profile.study_id || '-'}
                      </td>
                      <td className="py-4 px-4">
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                          {profile.phase || 'N/A'}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-600">
                        {profile.therapeutic_area || '-'}
                      </td>
                      <td className="py-4 px-4 text-gray-600">
                        {profile.primary_country || '-'}
                      </td>
                      <td className="py-4 px-4 text-sm text-gray-500">
                        {new Date(profile.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-4 px-4 text-right">
                        <button
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                          onClick={() => alert('Edit functionality - Calibrated tier feature')}
                        >
                          View
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
          <h3 className="text-lg font-medium text-black mb-4">Why Use Project Profiles?</h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-black mb-2">Improve Intelligence Accuracy</h4>
              <p>
                Pre-configure metadata (phase, therapeutic area, country) for your projects. When you run variance detection, this metadata is automatically applied, improving benchmark matching and variance analysis accuracy.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-black mb-2">Streamline Workflow</h4>
              <p>
                Create profiles once and reuse them for multiple timelines. No need to re-enter the same metadata every time you validate a timeline or generate a template.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-black mb-2">Core Tier Features</h4>
              <ul className="space-y-1 mt-2">
                <li>• Create basic project profiles</li>
                <li>• Essential metadata fields</li>
                <li>• Search and sort profiles</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-black mb-2">Calibrated Tier Features</h4>
              <ul className="space-y-1 mt-2">
                <li>• Edit and update profiles</li>
                <li>• Custom metadata fields</li>
                <li>• Bulk operations</li>
                <li>• Timeline associations</li>
                <li>• Template library</li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* Create Profile Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-light text-black">New Project Profile</h2>
                <button
                  onClick={() => {
                    setShowCreateModal(false);
                    resetForm();
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <form onSubmit={(e) => { e.preventDefault(); handleCreateProfile(); }}>
                {/* Project Name */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Project Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={newProfile.project_name}
                    onChange={(e) => setNewProfile({ ...newProfile, project_name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., ZENITH-301 Oncology Trial"
                    required
                  />
                </div>

                {/* Study ID */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Study ID (Optional)
                  </label>
                  <input
                    type="text"
                    value={newProfile.study_id}
                    onChange={(e) => setNewProfile({ ...newProfile, study_id: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., NCT12345678"
                  />
                </div>

                {/* Phase */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phase <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={newProfile.phase}
                    onChange={(e) => setNewProfile({ ...newProfile, phase: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Select phase...</option>
                    {PHASES.map((phase) => (
                      <option key={phase} value={phase}>{phase}</option>
                    ))}
                  </select>
                </div>

                {/* Therapeutic Area */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Therapeutic Area (Optional)
                  </label>
                  <select
                    value={newProfile.therapeutic_area}
                    onChange={(e) => setNewProfile({ ...newProfile, therapeutic_area: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select therapeutic area...</option>
                    {THERAPEUTIC_AREAS.map((area) => (
                      <option key={area} value={area}>{area}</option>
                    ))}
                  </select>
                </div>

                {/* Primary Country */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Primary Country <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={newProfile.primary_country}
                    onChange={(e) => setNewProfile({ ...newProfile, primary_country: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="">Select country...</option>
                    {COUNTRIES.map((country) => (
                      <option key={country} value={country}>{country}</option>
                    ))}
                  </select>
                </div>

                {/* Additional Countries Info */}
                <div className="mb-6 p-4 bg-gray-50 rounded border border-gray-200">
                  <p className="text-sm text-gray-600">
                    <strong>Note:</strong> Additional countries and custom fields are available in Calibrated tier.
                    <button
                      type="button"
                      onClick={() => window.location.href = '/billing'}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                    >
                      Upgrade →
                    </button>
                  </p>
                </div>

                {/* Actions */}
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      resetForm();
                    }}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                    disabled={creating}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-black text-white rounded hover:bg-gray-800 transition-colors disabled:opacity-50"
                    disabled={creating}
                  >
                    {creating ? 'Creating...' : 'Create Profile'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Mock data for development
function getMockProfiles(): ProjectProfile[] {
  return [
    {
      profile_id: 'prof_001',
      project_name: 'ZENITH-301 Oncology Trial',
      study_id: 'NCT05123456',
      therapeutic_area: 'Oncology',
      phase: 'Phase III',
      primary_country: 'United States',
      additional_countries: ['Canada', 'United Kingdom'],
      metadata: {},
      created_at: '2026-01-10T09:00:00Z',
    },
    {
      profile_id: 'prof_002',
      project_name: 'NEXUS Cardiovascular Study',
      study_id: 'NCT05234567',
      therapeutic_area: 'Cardiovascular',
      phase: 'Phase II',
      primary_country: 'Germany',
      additional_countries: ['France', 'Spain'],
      metadata: {},
      created_at: '2026-01-15T14:30:00Z',
    },
    {
      profile_id: 'prof_003',
      project_name: 'ASPIRE Rare Disease Program',
      study_id: 'NCT05345678',
      therapeutic_area: 'Rare Disease',
      phase: 'Phase I/II',
      primary_country: 'United Kingdom',
      additional_countries: ['Italy'],
      metadata: {},
      created_at: '2026-01-20T11:15:00Z',
    },
    {
      profile_id: 'prof_004',
      project_name: 'GUARDIAN Infectious Disease Trial',
      study_id: 'NCT05456789',
      therapeutic_area: 'Infectious Disease',
      phase: 'Phase III',
      primary_country: 'South Africa',
      additional_countries: ['Kenya', 'Nigeria', 'Ghana'],
      metadata: {},
      created_at: '2026-01-25T16:45:00Z',
    },
    {
      profile_id: 'prof_005',
      project_name: 'HORIZON Neurology Study',
      study_id: '',
      therapeutic_area: 'Neurology',
      phase: 'Phase II',
      primary_country: 'Japan',
      additional_countries: [],
      metadata: {},
      created_at: '2026-02-01T10:00:00Z',
    },
  ];
}
