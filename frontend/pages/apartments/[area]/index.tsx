import { GetStaticPaths, GetStaticProps } from 'next'
import Link from 'next/link'
import Layout from '@/components/Layout'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import { getAreas, getProperties } from '@/lib/api'
import { buildBreadcrumbSchema } from '@/lib/seo'

interface Props {
  area: {
    slug: string
    name: string
  }
  priceBuckets: string[]
  bedroomCounts: number[]
}

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'

export default function ApartmentsAreaPage({
  area,
  priceBuckets,
  bedroomCounts,
}: Props) {
  const canonical = `${SITE_URL}/apartments/${area.slug}/`

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: 'Apartments', url: `${SITE_URL}/apartments/` },
    { name: area.name, url: canonical },
  ])

  return (
    <Layout
      title={`${area.name} Apartments | Rentals & Sales | Story of Dubai`}
      description={`Browse apartments for rent and sale in ${area.name}, Dubai. Filter by bedrooms and price range.`}
      canonical={canonical}
      jsonLd={[breadcrumbSchema]}
    >
      <BreadcrumbNav
        crumbs={[
          { name: 'Apartments', href: '/apartments/' },
          { name: area.name, href: `/apartments/${area.slug}/` },
        ]}
      />

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-3xl font-luxury font-semibold text-b1-darker mb-2">
          Apartments in {area.name}
        </h1>
        <p className="text-b1-dark leading-relaxed max-w-2xl">
          Browse available apartments for rent and sale in {area.name}. Filter
          by number of bedrooms and price range to find your ideal property.
        </p>
      </div>

      {/* Filter by bedrooms */}
      <section className="mb-12">
        <h2 className="text-lg font-luxury font-medium text-b1-darker mb-4">
          By Bedroom Count
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {bedroomCounts.map((bedrooms) => (
            <Link
              key={bedrooms}
              href={`/apartments/${area.slug}/${bedrooms}/under-50k/`}
              className="group p-4 border border-b1-light rounded-xs hover:border-b1-light hover:shadow-sm transition-all bg-white"
            >
              <div className="font-luxury font-medium text-b1-darker group-hover:text-b1-gold transition-colors">
                {bedrooms} Bedroom{bedrooms !== 1 ? 's' : ''}
              </div>
              <p className="text-sm text-b1-dark mt-1">View properties</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Filter by price */}
      <section className="mb-12">
        <h2 className="text-lg font-luxury font-medium text-b1-darker mb-4">
          By Price Range
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {priceBuckets.map((bucket) => (
            <Link
              key={bucket}
              href={`/apartments/${area.slug}/1/${bucket}/`}
              className="group p-4 border border-b1-light rounded-xs hover:border-b1-light hover:shadow-sm transition-all bg-white"
            >
              <div className="font-luxury font-medium text-b1-darker group-hover:text-b1-gold transition-colors">
                {bucket}
              </div>
              <p className="text-sm text-b1-dark mt-1">
                1+ bedrooms in this range
              </p>
            </Link>
          ))}
        </div>
      </section>
    </Layout>
  )
}

export const getStaticPaths: GetStaticPaths = async () => {
  try {
    const res = await getAreas()
    const paths = (res.data || []).map((area) => ({
      params: { area: area.slug },
    }))
    return { paths, fallback: 'blocking' }
  } catch {
    return { paths: [], fallback: 'blocking' }
  }
}

export const getStaticProps: GetStaticProps<Props> = async ({ params }) => {
  const areaSlug = params?.area as string

  try {
    const [areasRes, propertiesRes] = await Promise.all([
      getAreas(),
      getProperties(areaSlug),
    ])

    const area = areasRes.data?.find((a) => a.slug === areaSlug)
    if (!area) return { notFound: true }

    // Extract unique bedroom counts from properties
    const properties = propertiesRes.data || []
    const bedroomSet = new Set<number>()

    properties.forEach((prop) => {
      if (prop.bedrooms) bedroomSet.add(prop.bedrooms)
    })

    // Default bedroom counts if none exist
    const bedroomCounts = Array.from(bedroomSet).sort((a, b) => a - b)
    if (bedroomCounts.length === 0) {
      bedroomCounts.push(1, 2, 3, 4, 5)
    }

    // Default price buckets
    const priceBuckets = [
      'under-50k',
      '50k-100k',
      '100k-150k',
      '150k-200k',
      '200k-300k',
      'above-300k',
    ]

    return {
      props: {
        area: {
          slug: area.slug,
          name: area.name,
        },
        priceBuckets,
        bedroomCounts,
      },
      revalidate: 86400, // ISR: rebuild every 24 hours
    }
  } catch {
    return { notFound: true }
  }
}
