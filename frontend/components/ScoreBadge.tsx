interface ScoreBadgeProps {
  score: number
  size?: 'sm' | 'md' | 'lg'
}

function getScoreColor(score: number): string {
  if (score >= 80) return 'bg-green-50 text-green-800 border-green-200'
  if (score >= 60) return 'bg-blue-50 text-blue-800 border-blue-200'
  if (score >= 40) return 'bg-amber-50 text-amber-800 border-amber-200'
  return 'bg-gray-50 text-gray-700 border-gray-200'
}

function getScoreLabel(score: number): string {
  if (score >= 85) return 'Exceptional'
  if (score >= 70) return 'Very Good'
  if (score >= 55) return 'Good'
  if (score >= 40) return 'Fair'
  return 'Listed'
}

export default function ScoreBadge({ score, size = 'md' }: ScoreBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5 font-semibold',
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${getScoreColor(score)} ${sizeClasses[size]}`}
    >
      <span>{score}</span>
      <span className="opacity-60 text-xs">{getScoreLabel(score)}</span>
    </span>
  )
}
