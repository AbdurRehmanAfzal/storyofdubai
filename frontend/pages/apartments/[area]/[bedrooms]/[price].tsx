import { GetStaticPaths, GetStaticProps } from 'next'
import Link from 'next/link'
import Layout from '@/components/Layout'
import ScoreBadge from '@/components/ScoreBadge'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import AffiliateCTA from '@/components/AffiliateCTA'
import EmailCapture from '@/components/EmailCapture'
import { getPropertyPaths, getProperties } from '@/lib/api'
import { buildBreadcrumbSchema, buildItemListSchema } from '@/lib/seo'
import { PropertyListItem } from '@/lib/types'

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'

const priceRangeLabel: Record<string, string> = {
  'under-50k': 'Under AED 50,000',
  '50k-100k': 'AED 50,000–100,000',
  '100k-200k': 'AED 100,000–200,000',
  '200k-plus': 'Above AED 200,000',
}

interface Props {
  properties: PropertyListItem[]
  area: string
  bedrooms: number
  priceRange: string
  lastUpdated: string
}

export default function PropertyFilterPage({
  properties,
  area,
  bedrooms,
  priceRange,
  lastUpdated,
}: Props) {
  const priceLabel = priceRangeLabel[priceRange] || priceRange
  const canonical = `${SITE_URL}/apartments/${area.toLowerCase().replace(/ /g, '-')}/${bedrooms}-bedroom/${priceRange}/`
  const title = `${bedrooms}-Bedroom Apartments in ${area} ${priceLabel} | Story of Dubai`
  const description = `Browse ${bedrooms}-bedroom apartments for rent in ${area}, Dubai ${priceLabel.toLowerCase()}. Ranked by value and quality score.`

  const itemListSchema = buildItemListSchema(
    title,
    canonical,
    properties.map((p) => ({
      name: p.title,
      url: `${SITE_URL}/apartments/${area.toLowerCase().replace(/ /g, '-')}/${bedrooms}-bedroom/${priceRange}/${p.slug}/`,
    }))
  )

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: 'Apartments', url: `${SITE_URL}/apartments/` },
    { name: area, url: canonical },
  ])

  return (
    <Layout
      title={title}
      description={description}
      canonical={canonical}
      jsonLd={[itemListSchema, breadcrumbSchema]}
    >
      <BreadcrumbNav
        crumbs={[
          { name: 'Apartments', href: '/apartments/' },
          { name: area, href: `/apartments/${area.toLowerCase().replace(/ /g, '-')}/` },
          {
            name: `${bedrooms}BR ${priceLabel}`,
            href: canonical,
          },
        ]}
      />

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">
          {bedrooms}-Bedroom Apartments in {area}, Dubai
        </h1>
        <p className="text-gray-600 leading-relaxed max-w-2xl mb-3">
          {bedrooms}-bedroom apartment rentals in {area} {priceLabel.toLowerCase()}.
          Ranked by quality score, price value, and availability.
        </p>
        <p className="text-xs text-gray-400">
          {properties.length} properties ranked · Last updated {lastUpdated}
        </p>
      </div>

      {/* Affiliate CTA */}
      <AffiliateCTA category="apartments" area={area} />

      {/* Properties grid */}
      {properties.length > 0 ? (
        <div className="space-y-3">
          {properties.map((property, i) => (
            <article
              key={property.id}
              className="flex items-start gap-4 p-4 border border-gray-100 rounded-xl hover:border-gray-200 hover:shadow-sm transition-all bg-white"
            >
              {/* Rank */}
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-sm font-medium text-gray-500">
                {i + 1}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <Link
                      href={`/apartments/${area
                        .toLowerCase()
                        .replace(/ /g, '-')}/${bedrooms}-bedroom/${priceRange}/${property.slug}/`}
                      className="font-medium text-gray-900 hover:text-blue-600 transition-colors"
                    >
                      {property.title}
                    </Link>
                    <div className="flex items-center gap-2 mt-1 text-sm text-gray-500 flex-wrap">
                      <span className="font-semibold text-gray-900">
                        AED {property.price_aed.toLocaleString()}
                      </span>
                      {property.developer && (
                        <span className="text-gray-400">
                          by {property.developer.name}
                        </span>
                      )}
                      {property.size_sqft && (
                        <span className="text-gray-400">
                          {property.size_sqft.toLocaleString()} sqft
                        </span>
                      )}
                    </div>
                  </div>
                  <ScoreBadge score={property.composite_score} size="sm" />
                </div>

                {/* Affiliate CTA */}
                {property.affiliate_url && (
                  <a
                    href={property.affiliate_url}
                    target="_blank"
                    rel="noopener noreferrer sponsored"
                    className="mt-2 inline-block text-xs text-blue-600 hover:text-blue-700 border border-blue-200 rounded-lg px-3 py-1 hover:bg-blue-50 transition-colors"
                  >
                    View on Bayut →
                  </a>
                )}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <p>No {bedrooms}-bedroom apartments found in {area} {priceLabel.toLowerCase()}.</p>
          <p className="text-sm mt-1">Try different filters or check back soon.</p>
        </div>
      )}

      {/* Email capture */}
      <EmailCapture context={`${bedrooms}-bedroom apartments in ${area}`} />

      {/* Related properties links */}
      <div className="mt-8 pt-8 border-t border-gray-100">
        <h2 className="text-sm font-medium text-gray-500 mb-3">
          Other apartment options in {area}
        </h2>
        <div className="flex flex-wrap gap-2">
          {[1, 2, 3, 4, 5].map((br) => (
            <a
              key={br}
              href={`/apartments/${area.toLowerCase().replace(/ /g, '-')}/${br}-bedroom/${priceRange}/`}
              className={`text-sm border rounded-lg px-3 py-1 transition-colors ${
                br === bedrooms
                  ? 'bg-blue-50 border-blue-200 text-blue-800'
                  : 'text-blue-600 hover:text-blue-700 border-blue-100 hover:bg-blue-50'
              }`}
            >
              {br}BR
            </a>
          ))}
        </div>
      </div>
    </Layout>
  )
}

export const getStaticPaths: GetStaticPaths = async () => {
  try {
    const res = await getPropertyPaths()
    const paths = (res.data || []).map(({ area_slug, bedrooms, price_bucket }) => ({
      params: { area: area_slug, bedrooms: bedrooms.toString(), price: price_bucket },
    }))
    return { paths, fallback: 'blocking' }
  } catch {
    return { paths: [], fallback: 'blocking' }
  }
}

export const getStaticProps: GetStaticProps<Props> = async ({ params }) => {
  const area_slug = params?.area as string
  const bedrooms = parseInt(params?.bedrooms as string, 10)
  const price_bucket = params?.price as string

  try {
    const res = await getProperties(area_slug, bedrooms, price_bucket)

    return {
      props: {
        properties: res.data || [],
        area: area_slug
          .replace(/-/g, ' ')
          .split(' ')
          .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
          .join(' '),
        bedrooms,
        priceRange: price_bucket,
        lastUpdated: new Date().toLocaleDateString('en-AE', {
          day: 'numeric',
          month: 'long',
          year: 'numeric',
        }),
      },
      revalidate: 43200, // ISR: rebuild every 12 hours (prices change faster)
    }
  } catch {
    return { notFound: true }
  }
}
