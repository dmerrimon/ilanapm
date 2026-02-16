'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import { apiClient } from '@/lib/api-client';

// ============================================================================
// Types
// ============================================================================

interface TrackerDefinition {
  tracker_type: string;
  tracker_name: string;
  required_fields: string[];
  optional_fields: string[];
  is_configured: boolean;
}

interface ColumnMapping {
  [orgColumn: string]: string; // org column → seleen field
}

interface SampleFileResponse {
  detected_columns: string[];
  suggested_mappings: ColumnMapping;
  required_fields: string[];
  unmapped_required: string[];
  sample_data: Record<string, any>[];
}

// ============================================================================
// Main Component
// ============================================================================

export default function TrackerConfigPage() {
  // Mock org_id - in production, get from auth context
  const orgId = 'demo_org_001';

  // State
  const [trackerDefinitions, setTrackerDefinitions] = useState<TrackerDefinition[]>([]);
  const [selectedTracker, setSelectedTracker] = useState<TrackerDefinition | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [detectedColumns, setDetectedColumns] = useState<string[]>([]);
  const [columnMappings, setColumnMappings] = useState<ColumnMapping>({});
  const [previewData, setPreviewData] = useState<Record<string, any>[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Load tracker definitions on mount
  useEffect(() => {
    fetchTrackerDefinitions();
  }, []);

  const fetchTrackerDefinitions = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/account/trackers/available?org_id=${orgId}`);
      setTrackerDefinitions(response.trackers || []);
    } catch (err: any) {
      console.error('Failed to fetch tracker definitions:', err);
      // Use mock data for development
      setTrackerDefinitions(getMockTrackerDefinitions());
    } finally {
      setLoading(false);
    }
  };

  const handleTrackerSelect = (tracker: TrackerDefinition) => {
    setSelectedTracker(tracker);
    setUploadedFile(null);
    setDetectedColumns([]);
    setColumnMappings({});
    setPreviewData([]);
    setError(null);
    setSuccessMessage(null);
  };

  const handleFileUpload = async (file: File) => {
    if (!selectedTracker) {
      setError('Please select a tracker type first');
      return;
    }

    setUploadedFile(file);
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post<SampleFileResponse>(
        `/account/trackers/upload-sample?org_id=${orgId}&tracker_type=${selectedTracker.tracker_type}`,
        formData
      );

      setDetectedColumns(response.detected_columns);
      setColumnMappings(response.suggested_mappings);
      setPreviewData(response.sample_data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to process file');
    } finally {
      setLoading(false);
    }
  };

  const handleMappingChange = (orgColumn: string, seleenField: string) => {
    setColumnMappings((prev) => ({
      ...prev,
      [orgColumn]: seleenField,
    }));
  };

  const handleSaveMapping = async () => {
    if (!selectedTracker) return;

    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      await apiClient.post('/account/trackers/save-mapping?created_by=admin_user', {
        org_id: orgId,
        tracker_type: selectedTracker.tracker_type,
        column_mappings: columnMappings,
      });

      setSuccessMessage(
        `✅ Column mapping saved! CPMs can now upload ${selectedTracker.tracker_name} files via MS Project add-in.`
      );

      // Refresh tracker definitions to update is_configured status
      await fetchTrackerDefinitions();
    } catch (err: any) {
      setError(err.message || 'Failed to save mapping');
    } finally {
      setLoading(false);
    }
  };

  const getUnmappedRequired = () => {
    if (!selectedTracker) return [];
    const mapped = new Set(Object.values(columnMappings));
    return selectedTracker.required_fields.filter((f) => !mapped.has(f));
  };

  const canSave = () => {
    return (
      selectedTracker &&
      detectedColumns.length > 0 &&
      getUnmappedRequired().length === 0
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Tracker Configuration</h1>
        <p className="text-gray-600 mb-8">
          Configure column mappings for your organization's tracker files. Once configured,
          CPMs can upload trackers via the MS Project add-in.
        </p>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
            {error}
          </div>
        )}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800">
            {successMessage}
          </div>
        )}

        {/* Step 1: Select Tracker Type */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-4">1. Select Tracker Type</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {trackerDefinitions.map((tracker) => (
              <TrackerCard
                key={tracker.tracker_type}
                tracker={tracker}
                isSelected={selectedTracker?.tracker_type === tracker.tracker_type}
                onClick={() => handleTrackerSelect(tracker)}
              />
            ))}
          </div>
        </section>

        {selectedTracker && (
          <>
            {/* Step 2: Upload Sample */}
            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">2. Upload Sample File</h2>
              <FileUploadZone
                onFileSelect={handleFileUpload}
                selectedFile={uploadedFile}
                loading={loading}
              />
            </section>

            {/* Step 3: Map Columns */}
            {detectedColumns.length > 0 && (
              <section className="mb-8">
                <h2 className="text-xl font-semibold mb-4">3. Map Your Columns</h2>
                <ColumnMappingInterface
                  detectedColumns={detectedColumns}
                  requiredFields={selectedTracker.required_fields}
                  optionalFields={selectedTracker.optional_fields}
                  mappings={columnMappings}
                  onChange={handleMappingChange}
                />
                {getUnmappedRequired().length > 0 && (
                  <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg text-amber-800">
                    <strong>Missing Required Fields:</strong>{' '}
                    {getUnmappedRequired().join(', ')}
                  </div>
                )}
              </section>
            )}

            {/* Step 4: Preview */}
            {previewData.length > 0 && (
              <section className="mb-8">
                <h2 className="text-xl font-semibold mb-4">4. Preview Mapped Data</h2>
                <DataPreviewTable data={previewData} mappings={columnMappings} />
              </section>
            )}

            {/* Step 5: Actions */}
            {detectedColumns.length > 0 && (
              <section className="flex gap-4">
                <button
                  onClick={handleSaveMapping}
                  disabled={!canSave() || loading}
                  className={`px-6 py-2 rounded font-medium ${
                    canSave() && !loading
                      ? 'bg-black text-white hover:bg-gray-800'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {loading ? 'Saving...' : 'Save Mapping'}
                </button>
                <button
                  onClick={() => {
                    setUploadedFile(null);
                    setDetectedColumns([]);
                    setColumnMappings({});
                    setPreviewData([]);
                  }}
                  className="px-6 py-2 border border-gray-300 rounded font-medium hover:bg-gray-50"
                >
                  Upload New Sample
                </button>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}

// ============================================================================
// Sub-Components
// ============================================================================

function TrackerCard({
  tracker,
  isSelected,
  onClick,
}: {
  tracker: TrackerDefinition;
  isSelected: boolean;
  onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      className={`p-6 rounded-lg border-2 cursor-pointer transition-all ${
        isSelected
          ? 'border-black bg-gray-50'
          : 'border-gray-200 hover:border-gray-400'
      }`}
    >
      <h3 className="font-semibold text-lg mb-2">{tracker.tracker_name}</h3>
      <div className="flex items-center gap-2 mb-3">
        {tracker.is_configured ? (
          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
            ✓ Configured
          </span>
        ) : (
          <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded">
            Not Configured
          </span>
        )}
      </div>
      <p className="text-sm text-gray-600">
        {tracker.required_fields.length} required fields
      </p>
    </div>
  );
}

function FileUploadZone({
  onFileSelect,
  selectedFile,
  loading,
}: {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  loading: boolean;
}) {
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv'))) {
      onFileSelect(file);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => e.preventDefault()}
      className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors"
    >
      {selectedFile ? (
        <div>
          <p className="text-lg font-medium mb-2">✓ {selectedFile.name}</p>
          <p className="text-sm text-gray-600">
            {(selectedFile.size / 1024).toFixed(1)} KB
          </p>
          {loading && <p className="text-sm text-gray-600 mt-2">Processing file...</p>}
        </div>
      ) : (
        <>
          <p className="text-lg font-medium mb-2">
            Drag & drop your tracker file here
          </p>
          <p className="text-sm text-gray-600 mb-4">or</p>
          <label className="px-4 py-2 bg-black text-white rounded cursor-pointer hover:bg-gray-800 inline-block">
            Browse Files
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleFileInput}
              className="hidden"
            />
          </label>
          <p className="text-xs text-gray-500 mt-4">
            Supports Excel (.xlsx, .xls) and CSV (.csv) files
          </p>
        </>
      )}
    </div>
  );
}

function ColumnMappingInterface({
  detectedColumns,
  requiredFields,
  optionalFields,
  mappings,
  onChange,
}: {
  detectedColumns: string[];
  requiredFields: string[];
  optionalFields: string[];
  mappings: ColumnMapping;
  onChange: (orgColumn: string, seleenField: string) => void;
}) {
  const allFields = [...requiredFields, ...optionalFields];

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Your Columns */}
        <div>
          <h3 className="font-semibold mb-4">Your Columns</h3>
          <div className="space-y-3">
            {detectedColumns.map((orgCol) => (
              <div key={orgCol} className="flex items-center gap-3">
                <div className="flex-1 px-3 py-2 bg-gray-50 rounded border border-gray-200">
                  {orgCol}
                </div>
                <span className="text-gray-400">→</span>
              </div>
            ))}
          </div>
        </div>

        {/* Seleen Fields */}
        <div>
          <h3 className="font-semibold mb-4">Seleen Fields</h3>
          <div className="space-y-3">
            {detectedColumns.map((orgCol) => (
              <div key={orgCol}>
                <select
                  value={mappings[orgCol] || ''}
                  onChange={(e) => onChange(orgCol, e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-black"
                >
                  <option value="">-- Skip Column --</option>
                  <optgroup label="Required Fields">
                    {requiredFields.map((field) => (
                      <option key={field} value={field}>
                        {field} *
                      </option>
                    ))}
                  </optgroup>
                  <optgroup label="Optional Fields">
                    {optionalFields.map((field) => (
                      <option key={field} value={field}>
                        {field}
                      </option>
                    ))}
                  </optgroup>
                </select>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function DataPreviewTable({
  data,
  mappings,
}: {
  data: Record<string, any>[];
  mappings: ColumnMapping;
}) {
  const mappedFields = Object.values(mappings).filter((f) => f !== '');

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {mappedFields.map((field) => (
                <th
                  key={field}
                  className="px-4 py-3 text-left text-sm font-semibold text-gray-700"
                >
                  {field}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.slice(0, 5).map((row, idx) => (
              <tr key={idx} className="border-b border-gray-200">
                {mappedFields.map((field) => {
                  // Find org column that maps to this field
                  const orgCol = Object.keys(mappings).find(
                    (col) => mappings[col] === field
                  );
                  const value = orgCol ? row[orgCol] : '';
                  return (
                    <td key={field} className="px-4 py-3 text-sm text-gray-800">
                      {String(value || '')}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-4 py-3 bg-gray-50 text-xs text-gray-600">
        Showing first 5 rows of preview data
      </div>
    </div>
  );
}

// ============================================================================
// Mock Data (for development)
// ============================================================================

function getMockTrackerDefinitions(): TrackerDefinition[] {
  return [
    {
      tracker_type: 'risk_log',
      tracker_name: 'Risk Log',
      required_fields: ['risk_number', 'category', 'risk_detail', 'priority', 'status'],
      optional_fields: ['impact', 'probability', 'mitigation_plan', 'owner'],
      is_configured: false,
    },
    {
      tracker_type: 'tmf_completeness',
      tracker_name: 'TMF Completeness',
      required_fields: ['artifact_number', 'artifact_name', 'status'],
      optional_fields: ['completion_pct', 'responsible_party'],
      is_configured: true,
    },
    {
      tracker_type: 'budget',
      tracker_name: 'Budget Tracker',
      required_fields: ['category', 'budgeted_amount', 'actual_spent'],
      optional_fields: ['variance_pct'],
      is_configured: false,
    },
    {
      tracker_type: 'vendor',
      tracker_name: 'Vendor Tracker',
      required_fields: ['vendor_name', 'deliverable', 'status', 'due_date'],
      optional_fields: ['actual_date'],
      is_configured: false,
    },
  ];
}
