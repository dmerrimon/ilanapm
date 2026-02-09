'use client';

import { useState } from 'react';
import Header from '@/components/Header';

type SortField = 'task_name' | 'category' | 'median_days';
type SortDirection = 'asc' | 'desc';

interface Benchmark {
  task_id: string;
  task_name: string;
  category: string;
  median_days: number;
  p25_days: number;
  p75_days: number;
  source: string;
  confidence: string;
  country?: string;
}

export default function IntelligencePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [countryFilter, setCountryFilter] = useState('all');
  const [sourceFilter, setSourceFilter] = useState('all');
  const [sortField, setSortField] = useState<SortField>('category');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  // Mock benchmark data from ontology
  const benchmarks: Benchmark[] = [
    {
      task_id: 'ont_001',
      task_name: 'IND/CTA Submission & Review',
      category: 'Regulatory',
      median_days: 45,
      p25_days: 30,
      p75_days: 60,
      source: 'WCG Clintrax',
      confidence: 'High',
      country: 'United States'
    },
    {
      task_id: 'ont_002',
      task_name: 'Ethics Committee Approval',
      category: 'Regulatory',
      median_days: 60,
      p25_days: 45,
      p75_days: 90,
      source: 'Emmes CRO',
      confidence: 'High',
      country: 'Global'
    },
    {
      task_id: 'ont_003',
      task_name: 'Site Contract Execution',
      category: 'Site Management',
      median_days: 90,
      p25_days: 60,
      p75_days: 120,
      source: 'Tufts CSDD',
      confidence: 'Medium',
      country: 'Global'
    },
    {
      task_id: 'ont_004',
      task_name: 'Patient Enrollment',
      category: 'Clinical Operations',
      median_days: 180,
      p25_days: 120,
      p75_days: 270,
      source: 'CenterWatch',
      confidence: 'Medium',
      country: 'Global'
    },
    {
      task_id: 'ont_005',
      task_name: 'Site Initiation Visit',
      category: 'Site Management',
      median_days: 30,
      p25_days: 21,
      p75_days: 45,
      source: 'WCG Clintrax',
      confidence: 'High',
      country: 'Global'
    },
    {
      task_id: 'ont_006',
      task_name: 'Database Lock',
      category: 'Data Management',
      median_days: 45,
      p25_days: 30,
      p75_days: 60,
      source: 'Emmes CRO',
      confidence: 'High',
      country: 'Global'
    },
    {
      task_id: 'ont_007',
      task_name: 'Final Study Report',
      category: 'Closeout',
      median_days: 90,
      p25_days: 60,
      p75_days: 120,
      source: 'Tufts CSDD',
      confidence: 'Medium',
      country: 'Global'
    },
    {
      task_id: 'ont_008',
      task_name: 'FDA 510(k) Submission',
      category: 'Regulatory',
      median_days: 90,
      p25_days: 60,
      p75_days: 180,
      source: 'WCG Clintrax',
      confidence: 'Medium',
      country: 'United States'
    },
    {
      task_id: 'ont_009',
      task_name: 'CE Mark Technical Documentation',
      category: 'Regulatory',
      median_days: 60,
      p25_days: 45,
      p75_days: 90,
      source: 'Emmes CRO',
      confidence: 'High',
      country: 'European Union'
    },
    {
      task_id: 'ont_010',
      task_name: 'Clinical Study Report (CSR)',
      category: 'Data Management',
      median_days: 120,
      p25_days: 90,
      p75_days: 180,
      source: 'Tufts CSDD',
      confidence: 'High',
      country: 'Global'
    },
  ];

  const categories = ['all', ...Array.from(new Set(benchmarks.map(b => b.category)))];
  const countries = ['all', ...Array.from(new Set(benchmarks.map(b => b.country || 'Global')))];
  const sources = ['all', ...Array.from(new Set(benchmarks.map(b => b.source)))];

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredBenchmarks = benchmarks
    .filter((benchmark) => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (
          !benchmark.task_name.toLowerCase().includes(query) &&
          !benchmark.category.toLowerCase().includes(query)
        ) {
          return false;
        }
      }

      // Category filter
      if (categoryFilter !== 'all' && benchmark.category !== categoryFilter) {
        return false;
      }

      // Country filter
      if (countryFilter !== 'all' && (benchmark.country || 'Global') !== countryFilter) {
        return false;
      }

      // Source filter
      if (sourceFilter !== 'all' && benchmark.source !== sourceFilter) {
        return false;
      }

      return true;
    })
    .sort((a, b) => {
      let aVal: any;
      let bVal: any;

      if (sortField === 'task_name') {
        aVal = a.task_name;
        bVal = b.task_name;
      } else if (sortField === 'category') {
        aVal = a.category;
        bVal = b.category;
      } else if (sortField === 'median_days') {
        aVal = a.median_days;
        bVal = b.median_days;
      }

      if (typeof aVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
    });

  const getConfidenceBadge = (confidence: string) => {
    const colors = {
      'High': 'bg-green-100 text-green-800',
      'Medium': 'bg-amber-100 text-amber-800',
      'Low': 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded ${colors[confidence as keyof typeof colors] || colors.Medium}`}>
        {confidence}
      </span>
    );
  };

  const stats = {
    total: benchmarks.length,
    high_confidence: benchmarks.filter(b => b.confidence === 'High').length,
    medium_confidence: benchmarks.filter(b => b.confidence === 'Medium').length,
    low_confidence: benchmarks.filter(b => b.confidence === 'Low').length,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl mb-2 text-black">Industry Benchmarks</h1>
              <p className="text-gray-600">
                Browse and manage benchmark data from industry research sources
              </p>
            </div>
            <button
              disabled
              className="px-4 py-2 bg-gray-200 text-gray-500 rounded cursor-not-allowed"
              title="Edit functionality available in Calibrated tier"
            >
              + Add Benchmark
            </button>
          </div>
        </div>

        {/* Info Banner */}
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="text-blue-600 text-xl">ℹ️</div>
            <div className="flex-1">
              <h3 className="font-medium text-blue-900 mb-1">Read-Only View</h3>
              <p className="text-sm text-blue-800">
                This view shows industry benchmarks from our research partners (WCG, Emmes, Tufts CSDD, CenterWatch).
                Benchmark editing and custom data uploads will be available in future releases.
              </p>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Total Benchmarks</div>
            <div className="text-2xl font-light text-black">{stats.total}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">High Confidence</div>
            <div className="text-2xl font-light text-green-600">{stats.high_confidence}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Medium Confidence</div>
            <div className="text-2xl font-light text-amber-600">{stats.medium_confidence}</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
            <div className="text-gray-500 text-sm mb-1">Low Confidence</div>
            <div className="text-2xl font-light text-red-600">{stats.low_confidence}</div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <input
              type="text"
              placeholder="Search task name or category..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category === 'all' ? 'All Categories' : category}
                </option>
              ))}
            </select>

            {/* Country Filter */}
            <select
              value={countryFilter}
              onChange={(e) => setCountryFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {countries.map((country) => (
                <option key={country} value={country}>
                  {country === 'all' ? 'All Countries' : country}
                </option>
              ))}
            </select>

            {/* Source Filter */}
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {sources.map((source) => (
                <option key={source} value={source}>
                  {source === 'all' ? 'All Sources' : source}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Benchmarks Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {filteredBenchmarks.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <p className="text-lg mb-2">No benchmarks found</p>
              <p className="text-sm">Try adjusting your filters</p>
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
                      Task Name {sortField === 'task_name' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                    <th
                      onClick={() => handleSort('category')}
                      className="text-left py-3 px-4 text-sm font-medium text-gray-500 cursor-pointer hover:bg-gray-100"
                    >
                      Category {sortField === 'category' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                    <th
                      onClick={() => handleSort('median_days')}
                      className="text-left py-3 px-4 text-sm font-medium text-gray-500 cursor-pointer hover:bg-gray-100"
                    >
                      Median Duration {sortField === 'median_days' && (sortDirection === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Range (P25-P75)
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Source
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Confidence
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">
                      Country
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredBenchmarks.map((benchmark) => (
                    <tr key={benchmark.task_id} className="border-t border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4 text-black font-medium">
                        {benchmark.task_name}
                      </td>
                      <td className="py-4 px-4">
                        <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded">
                          {benchmark.category}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-black font-medium">
                        {benchmark.median_days} days
                      </td>
                      <td className="py-4 px-4 text-gray-600">
                        {benchmark.p25_days}-{benchmark.p75_days} days
                      </td>
                      <td className="py-4 px-4 text-gray-600 text-sm">
                        {benchmark.source}
                      </td>
                      <td className="py-4 px-4">
                        {getConfidenceBadge(benchmark.confidence)}
                      </td>
                      <td className="py-4 px-4 text-gray-600 text-sm">
                        {benchmark.country || 'Global'}
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
          <h3 className="text-lg font-medium text-black mb-4">About Industry Benchmarks</h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-black mb-2">Data Sources</h4>
              <ul className="space-y-1">
                <li>• <strong>WCG Clintrax:</strong> Regulatory timeline data from 500+ trials</li>
                <li>• <strong>Emmes CRO:</strong> Site management and ethics approval benchmarks</li>
                <li>• <strong>Tufts CSDD:</strong> Academic research on clinical development timelines</li>
                <li>• <strong>CenterWatch:</strong> Patient enrollment and retention data</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-black mb-2">Confidence Levels</h4>
              <ul className="space-y-1">
                <li>• <strong>High:</strong> Based on 50+ data points with recent validation</li>
                <li>• <strong>Medium:</strong> Based on 20-49 data points or older research</li>
                <li>• <strong>Low:</strong> Based on &lt;20 data points or extrapolated estimates</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
