import { GetStaticPaths, GetStaticProps } from 'next'
import Link from 'next/link'
import Layout from '@/components/Layout'
import ScoreBadge from '@/components/ScoreBadge'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import EmailCapture from '@/components/EmailCapture'
import { getPropertyPaths, getProperties, getProperty } from '@/lib/api'
import { buildBreadcrumbSchema } from '@/lib/seo'
import { PropertyListItem } from '@/lib/types'

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'

const priceRangeLabel: Record<string, string> = {
  'under-50k': 'Under AED 50,000',
  '50k-100k': 'AED 50,000–100,000',
  '100k-200k': 'AED 100,000–200,000',
  '200k-plus': 'Above AED 200,000',
}

interface Props {
  property: PropertyListItem
  area: string
  bedrooms: number
  priceRange: string
}

export default function PropertyDetailPage({
  property,
  area,
  bedrooms,
  priceRange,
}: Props) {
  const priceLabel = priceRangeLabel[priceRange] || priceRange
  const canonical = `${SITE_URL}/apartments/${area.toLowerCase().replace(/ /g, '-')}/${bedrooms}-bedroom/${priceRange}/${property.slug}/`

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: 'Apartments', url: `${SITE_URL}/apartments/` },
    { name: area, url: `${SITE_URL}/apartments/${area.toLowerCase().replace(/ /g, '-')}/` },
    {
      name: `${bedrooms}-Bedroom ${priceLabel}`,
      url: `${SITE_URL}/apartments/${area.toLowerCase().replace(/ /g, '-')}/${bedrooms}-bedroom/${priceRange}/`,
    },
    { name: property.title, url: canonical },
  ])

  const priceInThousands = (property.price_aed / 1000).toFixed(0)

  return (
    <Layout
      title={`${property.title} - AED ${priceInThousands}k in ${area} | Story of Dubai`}
      description={`${property.title} in ${area}, Dubai. Price: AED ${property.price_aed.toLocaleString()}. ${property.bedrooms} bedrooms. Ranked #${property.composite_score.toFixed(0)}.`}
      canonical={canonical}
      jsonLd={[breadcrumbSchema]}
    >
      <BreadcrumbNav
        crumbs={[
          { name: 'Apartments', href: '/apartments/' },
          { name: area, href: `/apartments/${area.toLowerCase().replace(/ /g, '-')}/` },
          {
            name: `${bedrooms}BR ${priceLabel}`,
            href: `/apartments/${area.toLowerCase().replace(/ /g, '-')}/${bedrooms}-bedroom/${priceRange}/`,
          },
          { name: property.title, href: canonical },
        ]}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main content */}
        <div className="lg:col-span-2">
          <div className="flex items-start justify-between gap-4 mb-6">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900 mb-1">
                {property.title}
              </h1>
              <p className="text-gray-600">
                {property.bedrooms} bedroom{property.bedrooms !== 1 ? 's' : ''} in{' '}
                {area}
              </p>
            </div>
            <ScoreBadge score={property.composite_score} size="lg" />
          </div>

          {/* Price highlight */}
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl p-6 mb-6 border border-blue-200">
            <p className="text-sm text-blue-600 font-medium mb-1">Asking Price</p>
            <p className="text-3xl font-bold text-gray-900">
              AED {property.price_aed.toLocaleString()}
            </p>
            <p className="text-sm text-gray-600 mt-2">
              {property.size_sqft && (
                <>
                  {property.size_sqft.toLocaleString()} sqft •{' '}
                </>
              )}
              {property.bathrooms && (
                <>
                  {property.bathrooms} bath{property.bathrooms !== 1 ? 's' : ''} •{' '}
                </>
              )}
              {property.property_type || 'Property'}
            </p>
          </div>

          {/* Key details grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-xl font-semibold text-gray-900">
                {property.bedrooms}
              </div>
              <div className="text-xs text-gray-500 mt-0.5">Bedrooms</div>
            </div>
            {property.bathrooms && (
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <div className="text-xl font-semibold text-gray-900">
                  {property.bathrooms}
                </div>
                <div className="text-xs text-gray-500 mt-0.5">Bathrooms</div>
              </div>
            )}
            {property.size_sqft && (
              <div className="bg-gray-50 rounded-lg p-3 text-center">
                <div className="text-xl font-semibold text-gray-900">
                  {(property.size_sqft / 1000).toFixed(1)}k
                </div>
                <div className="text-xs text-gray-500 mt-0.5">Sqft</div>
              </div>
            )}
          </div>

          {/* Affiliate CTA */}
          {property.affiliate_url && (
            <a
              href={property.affiliate_url}
              target="_blank"
              rel="noopener noreferrer sponsored"
              className="inline-block w-full text-center bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 rounded-xl transition-colors mb-6"
            >
              View on PropertyFinder →
            </a>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {property.developer && (
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-xs font-medium text-gray-500 mb-1">Developer</p>
              <p className="text-sm font-medium text-gray-900">
                {property.developer.name}
              </p>
            </div>
          )}

          {property.property_type && (
            <div className="bg-gray-50 rounded-xl p-4">
              <p className="text-xs font-medium text-gray-500 mb-1">Type</p>
              <p className="text-sm text-gray-900">{property.property_type}</p>
            </div>
          )}

          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-xs font-medium text-gray-500 mb-2">Area</p>
            <Link
              href={`/apartments/${area.toLowerCase().replace(/ /g, '-')}/`}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              More apartments in {area} →
            </Link>
          </div>

          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-xs font-medium text-gray-500 mb-2">Price Range</p>
            <Link
              href={`/apartments/${area.toLowerCase().replace(/ /g, '-')}/${bedrooms}-bedroom/${priceRange}/`}
              className="text-sm text-blue-600 hover:text-blue-700"
            >
              Other {bedrooms}BR in this range →
            </Link>
          </div>
        </div>
      </div>

      <EmailCapture context={`${bedrooms}-bedroom apartments in ${area}`} />
    </Layout>
  )
}

export const getStaticPaths: GetStaticPaths = async () => {
  try {
    const pathsRes = await getPropertyPaths()
    const allPaths: {
      params: { area: string; bedrooms: string; price: string; slug: string }
    }[] = []

    await Promise.all(
      (pathsRes.data || []).map(async ({ area_slug, bedrooms, price_bucket }) => {
        const propsRes = await getProperties(area_slug)
        ;(propsRes.data || [])
          .filter(
            (p) =>
              p.bedrooms === bedrooms && p.price_bucket === price_bucket
          )
          .forEach((prop) => {
            allPaths.push({
              params: {
                area: area_slug,
                bedrooms: bedrooms.toString(),
                price: price_bucket,
                slug: prop.slug,
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
    const slug = params?.slug as string
    const res = await getProperty(slug)

    if (!res.data) return { notFound: true }

    return {
      props: {
        property: res.data,
        area: (params?.area as string)
          .split('-')
          .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
          .join(' '),
        bedrooms: parseInt(params?.bedrooms as string),
        priceRange: params?.price as string,
      },
      revalidate: 43200, // 12 hours
    }
  } catch {
    return { notFound: true }
  }
}
