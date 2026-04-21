interface ScoreBadgeProps {
  score: number
  size?: 'sm' | 'md' | 'lg'
}

function getScoreColor(score: number): string {
  if (score >= 60) return 'bg-b1-gold text-white'
  return 'bg-b1-light text-b1-darker'
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
      className={`inline-flex items-center gap-1.5 rounded-xs font-medium ${getScoreColor(score)} ${sizeClasses[size]}`}
    >
      <span>{score}</span>
      <span className="opacity-70 text-xs">{getScoreLabel(score)}</span>
    </span>
  )
}
