import { GetStaticProps } from 'next'
import Link from 'next/link'
import Layout from '@/components/Layout'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import { getAreas } from '@/lib/api'
import { buildBreadcrumbSchema } from '@/lib/seo'
import { Area } from '@/lib/types'

interface Props {
  areas: Area[]
}

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'

export default function ApartmentsPage({ areas }: Props) {
  const canonical = `${SITE_URL}/apartments/`

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: 'Apartments', url: canonical },
  ])

  return (
    <Layout
      title="Apartments in Dubai | Rentals & Sales | Story of Dubai"
      description="Browse apartments and properties for rent and sale in Dubai. Ranked by price, area, and quality."
      canonical={canonical}
      jsonLd={[breadcrumbSchema]}
    >
      <BreadcrumbNav
        crumbs={[{ name: 'Apartments', href: '/apartments/' }]}
      />

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-3xl font-luxury font-semibold text-b1-darker mb-2">
          Apartments in Dubai
        </h1>
        <p className="text-b1-dark leading-relaxed max-w-2xl">
          Browse apartments and properties for rent and sale across Dubai
          neighborhoods, ranked by price, amenities, and community.
        </p>
      </div>

      {/* Browse by area */}
      <section>
        <h2 className="text-lg font-luxury font-medium text-b1-darker mb-4">
          Browse by Area
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {areas.map((area) => (
            <Link
              key={area.slug}
              href={`/apartments/${area.slug}/`}
              className="group p-4 border border-b1-light rounded-xs hover:border-b1-light hover:shadow-sm transition-all bg-white"
            >
              <div className="font-luxury font-medium text-b1-darker group-hover:text-b1-gold transition-colors">
                {area.name}
              </div>
              {area.description && (
                <p className="text-sm text-b1-dark mt-1 line-clamp-2">
                  {area.description}
                </p>
              )}
            </Link>
          ))}
        </div>
      </section>
    </Layout>
  )
}

export const getStaticProps: GetStaticProps<Props> = async () => {
  try {
    const areasRes = await getAreas()
    return {
      props: {
        areas: areasRes.data || [],
      },
      revalidate: 86400, // ISR: rebuild every 24 hours
    }
  } catch {
    return { notFound: true }
  }
}
