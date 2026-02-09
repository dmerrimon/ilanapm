/**
 * Benchmark Coverage Chart Component
 * Displays benchmark coverage percentages by task category
 */

export interface CategoryCoverage {
  category: string;
  coverage_percent: number;
  tasks_matched: number;
  tasks_total: number;
}

interface BenchmarkCoverageChartProps {
  data: CategoryCoverage[];
  title?: string;
}

export default function BenchmarkCoverageChart({
  data,
  title = "Benchmark Coverage by Category"
}: BenchmarkCoverageChartProps) {
  const getCoverageColor = (percent: number) => {
    if (percent >= 80) return 'bg-green-600';
    if (percent >= 60) return 'bg-amber-600';
    return 'bg-red-600';
  };

  const getCoverageLabel = (percent: number) => {
    if (percent >= 80) return 'text-green-900 bg-green-50 border-green-200';
    if (percent >= 60) return 'text-amber-900 bg-amber-50 border-amber-200';
    return 'text-red-900 bg-red-50 border-red-200';
  };

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl mb-6 text-black">{title}</h2>
        <div className="text-center py-12 text-gray-500">
          No coverage data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl text-black">{title}</h2>
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-600"></div>
            <span className="text-gray-600">Good (≥80%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-amber-600"></div>
            <span className="text-gray-600">Fair (60-79%)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-600"></div>
            <span className="text-gray-600">Poor (&lt;60%)</span>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {data.map((item, index) => (
          <div key={index}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex-1">
                <span className="text-black font-medium">{item.category}</span>
                <span className="ml-3 text-sm text-gray-500">
                  ({item.tasks_matched}/{item.tasks_total} tasks)
                </span>
              </div>
              <div className={`px-3 py-1 text-sm font-medium rounded border ${getCoverageLabel(item.coverage_percent)}`}>
                {item.coverage_percent.toFixed(0)}% coverage
              </div>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-3">
              <div
                className={`${getCoverageColor(item.coverage_percent)} rounded-full h-3 transition-all duration-500`}
                style={{ width: `${item.coverage_percent}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
