/**
 * Variance Summary Card Component
 * Displays key variance metrics with trend indicators
 */

interface VarianceSummaryCardProps {
  title: string;
  value: string | number;
  trend?: {
    value: string;
    direction: 'up' | 'down' | 'neutral';
    label: string;
  };
  className?: string;
}

export default function VarianceSummaryCard({
  title,
  value,
  trend,
  className = ''
}: VarianceSummaryCardProps) {
  const getTrendColor = () => {
    if (!trend) return '';
    switch (trend.direction) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    switch (trend.direction) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      default:
        return '→';
    }
  };

  return (
    <div className={`bg-white p-6 rounded-lg shadow-sm border border-gray-200 ${className}`}>
      <div className="text-gray-500 text-sm mb-1">{title}</div>
      <div className="text-3xl font-light text-black">{value}</div>
      {trend && (
        <div className={`text-sm mt-2 ${getTrendColor()}`}>
          {getTrendIcon()} {trend.value} {trend.label}
        </div>
      )}
    </div>
  );
}
