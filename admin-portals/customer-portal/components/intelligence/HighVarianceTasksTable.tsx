/**
 * High Variance Tasks Table Component
 * Displays tasks with significant variances from industry benchmarks
 */

export interface VarianceTask {
  task_name: string;
  customer_duration_days: number;
  benchmark_duration_days: number;
  variance_percent: number;
  variance_classification: 'overestimate' | 'underestimate' | 'on_target';
  severity: 'critical' | 'warning' | 'acceptable';
  financial_impact_usd: number;
  source?: string;
}

interface HighVarianceTasksTableProps {
  tasks: VarianceTask[];
  title?: string;
  maxRows?: number;
}

export default function HighVarianceTasksTable({
  tasks,
  title = "High Variance Tasks",
  maxRows
}: HighVarianceTasksTableProps) {
  const displayTasks = maxRows ? tasks.slice(0, maxRows) : tasks;

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'critical':
        return (
          <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
            Critical
          </span>
        );
      case 'warning':
        return (
          <span className="px-2 py-1 text-xs font-medium bg-amber-100 text-amber-800 rounded">
            Warning
          </span>
        );
      default:
        return (
          <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">
            Acceptable
          </span>
        );
    }
  };

  const formatFinancialImpact = (amount: number) => {
    const absAmount = Math.abs(amount);
    const formatted = absAmount >= 1000000
      ? `$${(absAmount / 1000000).toFixed(1)}M`
      : absAmount >= 1000
      ? `$${(absAmount / 1000).toFixed(0)}K`
      : `$${absAmount.toFixed(0)}`;

    return amount < 0 ? `-${formatted}` : `+${formatted}`;
  };

  const getVarianceColor = (classification: string) => {
    switch (classification) {
      case 'underestimate':
        return 'text-red-600';
      case 'overestimate':
        return 'text-green-600';
      default:
        return 'text-gray-600';
    }
  };

  const getFinancialImpactColor = (amount: number) => {
    return amount < 0 ? 'text-red-600' : 'text-green-600';
  };

  if (tasks.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl mb-6 text-black">{title}</h2>
        <div className="text-center py-12 text-gray-500">
          No variance data available. Run a timeline analysis to see results.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h2 className="text-xl mb-6 text-black">{title}</h2>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Task Name</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Your Duration</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Benchmark</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Variance</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-500">Severity</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-gray-500">Financial Impact</th>
            </tr>
          </thead>
          <tbody>
            {displayTasks.map((task, index) => (
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-4 px-4 text-black">{task.task_name}</td>
                <td className="py-4 px-4 text-black">{task.customer_duration_days} days</td>
                <td className="py-4 px-4 text-gray-600">{task.benchmark_duration_days} days</td>
                <td className="py-4 px-4">
                  <span className={`font-medium ${getVarianceColor(task.variance_classification)}`}>
                    {task.variance_percent > 0 ? '+' : ''}{task.variance_percent.toFixed(1)}%
                  </span>
                  <span className="ml-2 text-sm text-gray-500">
                    ({task.variance_classification})
                  </span>
                </td>
                <td className="py-4 px-4">{getSeverityBadge(task.severity)}</td>
                <td className={`py-4 px-4 text-right font-medium ${getFinancialImpactColor(task.financial_impact_usd)}`}>
                  {formatFinancialImpact(task.financial_impact_usd)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {maxRows && tasks.length > maxRows && (
        <div className="mt-4 text-center text-sm text-gray-500">
          Showing {maxRows} of {tasks.length} high-variance tasks
        </div>
      )}
    </div>
  );
}
