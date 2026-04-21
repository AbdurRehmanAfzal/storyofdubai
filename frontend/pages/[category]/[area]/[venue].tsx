import { GetStaticPaths, GetStaticProps } from 'next'
import Link from 'next/link'
import Layout from '@/components/Layout'
import ScoreBadge from '@/components/ScoreBadge'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import EmailCapture from '@/components/EmailCapture'
import {
  getVenueAreaPaths,
  getVenuesByAreaCategory,
  getVenue,
} from '@/lib/api'
import { buildBreadcrumbSchema } from '@/lib/seo'
import { VenueDetail } from '@/lib/types'

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'

interface Props {
  venue: VenueDetail
}

export default function VenuePage({ venue }: Props) {
  const canonical = `${SITE_URL}/${venue.category.slug}/${venue.area.slug}/${venue.slug}/`

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: venue.category.name, url: `${SITE_URL}/${venue.category.slug}/` },
    {
      name: venue.area.name,
      url: `${SITE_URL}/${venue.category.slug}/${venue.area.slug}/`,
    },
    { name: venue.name, url: canonical },
  ])

  const localBusinessSchema = {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    name: venue.name,
    url: canonical,
    telephone: venue.phone || undefined,
    address: venue.address
      ? {
          '@type': 'PostalAddress',
          streetAddress: venue.address,
          addressLocality: 'Dubai',
          addressCountry: 'AE',
        }
      : undefined,
    aggregateRating: venue.rating
      ? {
          '@type': 'AggregateRating',
          ratingValue: venue.rating,
          reviewCount: venue.review_count,
          bestRating: 5,
          worstRating: 1,
        }
      : undefined,
  }

  return (
    <Layout
      title={`${venue.name} — ${venue.area.name} Dubai | Story of Dubai`}
      description={
        venue.description ||
        venue.ai_summary ||
        `${venue.name} in ${venue.area.name}, Dubai. Rated ${venue.rating}/5 from ${venue.review_count} reviews.`
      }
      canonical={canonical}
      jsonLd={[localBusinessSchema, breadcrumbSchema]}
    >
      <BreadcrumbNav
        crumbs={[
          { name: venue.category.name, href: `/${venue.category.slug}/` },
          {
            name: venue.area.name,
            href: `/${venue.category.slug}/${venue.area.slug}/`,
          },
          { name: venue.name, href: canonical },
        ]}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main content */}
        <div className="lg:col-span-2">
          <div className="flex items-start justify-between gap-4 mb-4">
            <h1 className="text-2xl font-luxury font-semibold text-b1-darker">{venue.name}</h1>
            <ScoreBadge score={venue.composite_score} size="lg" />
          </div>

          {(venue.description || venue.ai_summary) && (
            <p className="text-b1-dark leading-relaxed mb-6">
              {venue.description || venue.ai_summary}
            </p>
          )}

          {/* Stats grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
            {venue.rating && (
              <div className="bg-white border border-b1-light rounded-xs p-3 text-center">
                <div className="text-xl font-semibold text-amber-500">
                  {venue.rating.toFixed(1)}
                </div>
                <div className="text-xs text-b1-dark mt-0.5">Google rating</div>
              </div>
            )}
            {venue.review_count > 0 && (
              <div className="bg-white border border-b1-light rounded-xs p-3 text-center">
                <div className="text-xl font-semibold text-b1-darker">
                  {venue.review_count.toLocaleString()}
                </div>
                <div className="text-xs text-b1-dark mt-0.5">Reviews</div>
              </div>
            )}
            {venue.price_tier && (
              <div className="bg-white border border-b1-light rounded-xs p-3 text-center">
                <div className="text-xl font-semibold text-b1-darker">
                  {'$'.repeat(venue.price_tier)}
                </div>
                <div className="text-xs text-b1-dark mt-0.5">Price range</div>
              </div>
            )}
          </div>

          {venue.affiliate_url && (
            <a
              href={venue.affiliate_url}
              target="_blank"
              rel="noopener noreferrer sponsored"
              className="inline-block w-full text-center bg-b1-gold hover:bg-b1-gold-hover text-white font-medium py-3 rounded-xs transition-colors mb-6"
            >
              Book / Reserve at {venue.name} →
            </a>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {venue.address && (
            <div className="bg-white border border-b1-light rounded-xs p-4">
              <p className="text-xs font-medium text-b1-dark mb-1">Address</p>
              <p className="text-sm text-b1-darker">{venue.address}</p>
            </div>
          )}
          {venue.phone && (
            <div className="bg-white border border-b1-light rounded-xs p-4">
              <p className="text-xs font-medium text-b1-dark mb-1">Phone</p>
              <a
                href={`tel:${venue.phone}`}
                className="text-sm text-b1-gold hover:text-b1-gold-hover transition-colors"
              >
                {venue.phone}
              </a>
            </div>
          )}
          {venue.website && (
            <div className="bg-white border border-b1-light rounded-xs p-4">
              <p className="text-xs font-medium text-b1-dark mb-1">Website</p>
              <a
                href={venue.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-b1-gold hover:text-b1-gold-hover truncate block transition-colors"
              >
                Visit website
              </a>
            </div>
          )}

          <div className="bg-white border border-b1-light rounded-xs p-4">
            <p className="text-xs font-medium text-b1-dark mb-2">Area</p>
            <Link
              href={`/${venue.category.slug}/${venue.area.slug}/`}
              className="text-sm text-b1-gold hover:text-b1-gold-hover transition-colors"
            >
              More {venue.category.name} in {venue.area.name} →
            </Link>
          </div>
        </div>
      </div>

      <EmailCapture context={`${venue.category.name} in Dubai`} />
    </Layout>
  )
}

export const getStaticPaths: GetStaticPaths = async () => {
  try {
    const pathsRes = await getVenueAreaPaths()
    const allPaths: {
      params: { category: string; area: string; venue: string }
    }[] = []

    await Promise.all(
      (pathsRes.data || []).map(async ({ category_slug, area_slug }) => {
        const venuesRes = await getVenuesByAreaCategory(area_slug, category_slug)
        ;(venuesRes.data || []).forEach((v) => {
          allPaths.push({
            params: {
              category: category_slug,
              area: area_slug,
              venue: v.slug,
            },
          })
        })
      })
    )

    return { paths: allPaths, fallback: 'blocking' }
  } catch {
    return { paths: [], fallback: 'blocking' }
  }
}

export const getStaticProps: GetStaticProps<Props> = async ({ params }) => {
  try {
    const res = await getVenue(params?.venue as string)
    if (!res.data) return { notFound: true }
    return { props: { venue: res.data }, revalidate: 86400 }
  } catch {
    return { notFound: true }
  }
}
