/**
 * Insights Panel Component
 * Displays AI-generated insights and recommendations from variance analysis
 */

export interface Insight {
  id: string;
  category: string;
  message: string;
  severity?: 'info' | 'warning' | 'success';
}

interface InsightsPanelProps {
  insights: Insight[];
  title?: string;
}

export default function InsightsPanel({
  insights,
  title = "💡 Key Insights"
}: InsightsPanelProps) {
  const getSeverityStyles = (severity?: string) => {
    switch (severity) {
      case 'warning':
        return 'bg-amber-50 border-amber-200 text-amber-900';
      case 'success':
        return 'bg-green-50 border-green-200 text-green-900';
      default:
        return 'bg-blue-50 border-blue-200 text-blue-900';
    }
  };

  const getBulletColor = (severity?: string) => {
    switch (severity) {
      case 'warning':
        return 'text-amber-600';
      case 'success':
        return 'text-green-600';
      default:
        return 'text-blue-600';
    }
  };

  if (insights.length === 0) {
    return null;
  }

  return (
    <div className={`border rounded-lg p-6 ${getSeverityStyles()}`}>
      <h3 className="text-lg font-medium mb-4">{title}</h3>
      <ul className="space-y-3">
        {insights.map((insight) => (
          <li key={insight.id} className="flex items-start gap-3">
            <span className={`mt-0.5 font-bold ${getBulletColor(insight.severity)}`}>
              •
            </span>
            <span>
              <strong>{insight.category}:</strong> {insight.message}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
