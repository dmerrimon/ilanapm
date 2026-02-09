'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import { apiClient } from '@/lib/api-client';

interface CalibrationResult {
  org_id: string;
  project_name: string;
  tasks_extracted: number;
  tasks_normalized: number;
  benchmarks_generated: number;
  patterns_detected: PatternDetection[];
  org_benchmarks: OrgBenchmark[];
  quality_metrics: QualityMetrics;
  metadata: Record<string, any>;
}

interface PatternDetection {
  pattern_type: string;
  category: string;
  description: string;
  confidence: number;
  sample_size: number;
}

interface OrgBenchmark {
  ontology_task_id: string;
  task_name: string;
  category: string;
  median_days: number;
  p25_days: number;
  p75_days: number;
  sample_size: number;
  confidence: number;
}

interface QualityMetrics {
  normalization_rate: number;
  high_confidence_rate: number;
  benchmarks_created: number;
  avg_sample_size: number;
  data_quality: string;
}

interface CalibrationHistory {
  calibration_id: string;
  project_name: string;
  tasks_extracted: number;
  benchmarks_generated: number;
  created_at: string;
}

export default function CalibrationPage() {
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState('');
  const [calibrationResult, setCalibrationResult] = useState<CalibrationResult | null>(null);
  const [calibrationHistory, setCalibrationHistory] = useState<CalibrationHistory[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Load calibration history on mount
  useEffect(() => {
    loadCalibrationHistory();
  }, []);

  const loadCalibrationHistory = async () => {
    try {
      const orgId = localStorage.getItem('org_id') || '';
      const response = await apiClient.get(`/api/v1/calibration/results?org_id=${orgId}`);

      if (response.data?.results) {
        setCalibrationHistory(response.data.results);
      }
    } catch (error) {
      console.error('Failed to load calibration history:', error);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (file) {
      // Validate file type
      const validExtensions = ['.mpp', '.xml'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));

      if (!validExtensions.includes(fileExtension)) {
        setErrorMessage('Invalid file type. Please upload a .mpp or .xml file.');
        setSelectedFile(null);
        return;
      }

      setSelectedFile(file);
      setErrorMessage('');
      setCalibrationResult(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setErrorMessage('Please select a file to upload');
      return;
    }

    setUploadStatus('uploading');
    setUploadProgress(0);
    setErrorMessage('');

    try {
      const orgId = localStorage.getItem('org_id') || '';

      // Read file as bytes
      const fileReader = new FileReader();

      fileReader.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = (event.loaded / event.total) * 50; // First 50% for reading
          setUploadProgress(progress);
        }
      };

      fileReader.onload = async (event) => {
        try {
          setUploadStatus('processing');
          setUploadProgress(50);

          const fileContent = event.target?.result as ArrayBuffer;
          const bytes = new Uint8Array(fileContent);

          // Upload to API
          const response = await apiClient.post('/api/v1/calibration/upload', {
            org_id: orgId,
            file_content: Array.from(bytes),
            project_metadata: {
              phase: null,
              therapeutic_area: null,
              country: null
            }
          });

          setUploadProgress(100);
          setUploadStatus('success');
          setCalibrationResult(response.data);

          // Reload history
          await loadCalibrationHistory();

        } catch (error: any) {
          console.error('Upload failed:', error);
          setUploadStatus('error');
          setErrorMessage(error.response?.data?.detail || 'Failed to process file. Please try again.');
        }
      };

      fileReader.onerror = () => {
        setUploadStatus('error');
        setErrorMessage('Failed to read file. Please try again.');
      };

      fileReader.readAsArrayBuffer(selectedFile);

    } catch (error: any) {
      console.error('Upload error:', error);
      setUploadStatus('error');
      setErrorMessage(error.message || 'An unexpected error occurred');
    }
  };

  const getQualityBadge = (quality: string) => {
    const colors = {
      'High': 'bg-green-100 text-green-800',
      'Medium': 'bg-amber-100 text-amber-800',
      'Low': 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded ${colors[quality as keyof typeof colors] || colors.Medium}`}>
        {quality}
      </span>
    );
  };

  const getConfidenceBadge = (confidence: number) => {
    let colorClass = '';
    let label = '';

    if (confidence >= 0.8) {
      colorClass = 'bg-green-100 text-green-800';
      label = 'High';
    } else if (confidence >= 0.5) {
      colorClass = 'bg-amber-100 text-amber-800';
      label = 'Medium';
    } else {
      colorClass = 'bg-red-100 text-red-800';
      label = 'Low';
    }

    return (
      <span className={`px-2 py-1 text-xs font-medium rounded ${colorClass}`}>
        {label} ({Math.round(confidence * 100)}%)
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl mb-2 text-black">Calibration Center</h1>
          <p className="text-gray-600">
            Upload historical timelines to generate organization-specific benchmarks
          </p>
        </div>

        {/* Info Banner */}
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <div className="text-blue-600 text-xl">ℹ️</div>
            <div className="flex-1">
              <h3 className="font-medium text-blue-900 mb-1">How Calibration Works</h3>
              <p className="text-sm text-blue-800">
                Upload 5-10 historical MS Project timelines to generate organization-specific benchmarks.
                Your data is blended with industry benchmarks (70% org, 30% industry) for improved accuracy.
              </p>
            </div>
          </div>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-medium text-black mb-4">Upload Historical Timeline</h2>

          {uploadStatus === 'idle' && (
            <div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select MS Project File (.mpp or .xml)
                </label>
                <input
                  type="file"
                  accept=".mpp,.xml"
                  onChange={handleFileSelect}
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded file:border-0
                    file:text-sm file:font-medium
                    file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100
                    cursor-pointer"
                />
              </div>

              {selectedFile && (
                <div className="mb-4 p-3 bg-gray-50 rounded">
                  <p className="text-sm text-gray-700">
                    <strong>Selected:</strong> {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
                  </p>
                </div>
              )}

              {errorMessage && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
                  <p className="text-sm text-red-800">{errorMessage}</p>
                </div>
              )}

              <button
                onClick={handleUpload}
                disabled={!selectedFile}
                className={`px-6 py-2 rounded font-medium ${
                  selectedFile
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                }`}
              >
                Upload & Process
              </button>
            </div>
          )}

          {(uploadStatus === 'uploading' || uploadStatus === 'processing') && (
            <div>
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    {uploadStatus === 'uploading' ? 'Uploading file...' : 'Processing timeline...'}
                  </span>
                  <span className="text-sm text-gray-500">{Math.round(uploadProgress)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>

              <p className="text-sm text-gray-600">
                {uploadStatus === 'uploading'
                  ? 'Uploading your timeline file...'
                  : 'Analyzing tasks, normalizing to ontology, and generating benchmarks...'}
              </p>
            </div>
          )}

          {uploadStatus === 'success' && calibrationResult && (
            <div>
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-green-600 text-xl">✓</span>
                  <span className="font-medium text-green-900">Calibration Complete!</span>
                </div>
                <p className="text-sm text-green-800">
                  Successfully processed {calibrationResult.project_name}
                </p>
              </div>

              <button
                onClick={() => {
                  setUploadStatus('idle');
                  setSelectedFile(null);
                  setCalibrationResult(null);
                  setUploadProgress(0);
                }}
                className="px-6 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700"
              >
                Upload Another Timeline
              </button>
            </div>
          )}

          {uploadStatus === 'error' && (
            <div>
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-red-600 text-xl">✕</span>
                  <span className="font-medium text-red-900">Processing Failed</span>
                </div>
                <p className="text-sm text-red-800">{errorMessage}</p>
              </div>

              <button
                onClick={() => {
                  setUploadStatus('idle');
                  setErrorMessage('');
                }}
                className="px-6 py-2 bg-blue-600 text-white rounded font-medium hover:bg-blue-700"
              >
                Try Again
              </button>
            </div>
          )}
        </div>

        {/* Calibration Results */}
        {calibrationResult && (
          <div className="space-y-6">
            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <div className="text-gray-500 text-sm mb-1">Tasks Extracted</div>
                <div className="text-2xl font-light text-black">{calibrationResult.tasks_extracted}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <div className="text-gray-500 text-sm mb-1">Tasks Normalized</div>
                <div className="text-2xl font-light text-green-600">{calibrationResult.tasks_normalized}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <div className="text-gray-500 text-sm mb-1">Benchmarks Generated</div>
                <div className="text-2xl font-light text-blue-600">{calibrationResult.benchmarks_generated}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <div className="text-gray-500 text-sm mb-1">Data Quality</div>
                <div className="text-2xl font-light">
                  {getQualityBadge(calibrationResult.quality_metrics.data_quality)}
                </div>
              </div>
            </div>

            {/* Quality Metrics */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-black mb-4">Quality Metrics</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-500 mb-1">Normalization Rate</div>
                  <div className="text-xl text-black">{calibrationResult.quality_metrics.normalization_rate}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 mb-1">High Confidence Rate</div>
                  <div className="text-xl text-black">{calibrationResult.quality_metrics.high_confidence_rate}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 mb-1">Average Sample Size</div>
                  <div className="text-xl text-black">{calibrationResult.quality_metrics.avg_sample_size}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500 mb-1">Benchmarks Created</div>
                  <div className="text-xl text-black">{calibrationResult.quality_metrics.benchmarks_created}</div>
                </div>
              </div>
            </div>

            {/* Pattern Detection */}
            {calibrationResult.patterns_detected.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-medium text-black mb-4">Detected Patterns</h3>
                <div className="space-y-3">
                  {calibrationResult.patterns_detected.map((pattern, index) => (
                    <div key={index} className="border border-gray-200 rounded p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-medium text-black">{pattern.category}</div>
                        {getConfidenceBadge(pattern.confidence)}
                      </div>
                      <p className="text-sm text-gray-600">{pattern.description}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        Based on {pattern.sample_size} samples
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Organization Benchmarks */}
            {calibrationResult.org_benchmarks.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-6">
                  <h3 className="text-lg font-medium text-black mb-4">Generated Organization Benchmarks</h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Task Name</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Category</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Median Days</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Range (P25-P75)</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Samples</th>
                        <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Confidence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {calibrationResult.org_benchmarks.map((benchmark, index) => (
                        <tr key={index} className="border-t border-gray-100 hover:bg-gray-50">
                          <td className="py-4 px-4 text-black font-medium">{benchmark.task_name}</td>
                          <td className="py-4 px-4">
                            <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded">
                              {benchmark.category}
                            </span>
                          </td>
                          <td className="py-4 px-4 text-black font-medium">{benchmark.median_days} days</td>
                          <td className="py-4 px-4 text-gray-600">
                            {benchmark.p25_days}-{benchmark.p75_days} days
                          </td>
                          <td className="py-4 px-4 text-gray-600">{benchmark.sample_size}</td>
                          <td className="py-4 px-4">
                            {getConfidenceBadge(benchmark.confidence)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Calibration History */}
        {calibrationHistory.length > 0 && !calibrationResult && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-6">
              <h3 className="text-lg font-medium text-black mb-4">Calibration History</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Project Name</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Tasks Extracted</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Benchmarks Generated</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Upload Date</th>
                  </tr>
                </thead>
                <tbody>
                  {calibrationHistory.map((item) => (
                    <tr key={item.calibration_id} className="border-t border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4 text-black font-medium">{item.project_name}</td>
                      <td className="py-4 px-4 text-gray-600">{item.tasks_extracted}</td>
                      <td className="py-4 px-4 text-gray-600">{item.benchmarks_generated}</td>
                      <td className="py-4 px-4 text-gray-600">
                        {new Date(item.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Empty State */}
        {calibrationHistory.length === 0 && !calibrationResult && uploadStatus === 'idle' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <div className="text-gray-400 text-5xl mb-4">📊</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Calibration Data Yet</h3>
            <p className="text-gray-600 mb-4">
              Upload your first historical timeline to start building organization-specific benchmarks
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
