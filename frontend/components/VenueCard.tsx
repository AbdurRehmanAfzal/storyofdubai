import Link from 'next/link'
import { VenueListItem } from '@/lib/types'
import ScoreBadge from './ScoreBadge'

interface VenueCardProps {
  venue: VenueListItem
  rank: number
}

const priceTierLabel = (tier: number | null): string => {
  if (!tier) return ''
  return '$'.repeat(tier)
}

export default function VenueCard({ venue, rank }: VenueCardProps) {
  const href = `/${venue.category.slug}/${venue.area.slug}/${venue.slug}/`

  return (
    <article className="flex items-start gap-4 p-4 border border-gray-100 rounded-xl hover:border-gray-200 hover:shadow-sm transition-all bg-white">
      {/* Rank */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-sm font-medium text-gray-500">
        {rank}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-3">
          <div>
            <Link
              href={href}
              className="font-medium text-gray-900 hover:text-blue-600 transition-colors"
            >
              {venue.name}
            </Link>
            <div className="flex items-center gap-2 mt-1 text-sm text-gray-500 flex-wrap">
              {venue.google_rating && (
                <span className="flex items-center gap-1">
                  <span className="text-amber-400">★</span>
                  {venue.google_rating.toFixed(1)}
                </span>
              )}
              {venue.review_count > 0 && (
                <span>({venue.review_count.toLocaleString()} reviews)</span>
              )}
              {venue.price_tier && (
                <span className="text-gray-400">{priceTierLabel(venue.price_tier)}</span>
              )}
            </div>
          </div>
          <ScoreBadge score={venue.composite_score} size="sm" />
        </div>

        {/* Affiliate CTA */}
        {venue.affiliate_url && (
          <a
            href={venue.affiliate_url}
            target="_blank"
            rel="noopener noreferrer sponsored"
            className="mt-2 inline-block text-xs text-blue-600 hover:text-blue-700 border border-blue-200 rounded-lg px-3 py-1 hover:bg-blue-50 transition-colors"
          >
            Book / Reserve →
          </a>
        )}
      </div>
    </article>
  )
}
