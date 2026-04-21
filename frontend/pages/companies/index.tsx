import { GetStaticProps } from 'next'
import Link from 'next/link'
import Layout from '@/components/Layout'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import { getSectors } from '@/lib/api'
import { buildBreadcrumbSchema } from '@/lib/seo'

interface Sector {
  id: string
  slug: string
  name: string
}

interface Props {
  sectors: Sector[]
}

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'

export default function CompaniesPage({ sectors }: Props) {
  const canonical = `${SITE_URL}/companies/`

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: 'Companies', url: canonical },
  ])

  return (
    <Layout
      title="Dubai Companies & Startups Directory | Story of Dubai"
      description="Browse Dubai companies and startups. Find businesses by sector, size, and industry."
      canonical={canonical}
      jsonLd={[breadcrumbSchema]}
    >
      <BreadcrumbNav
        crumbs={[{ name: 'Companies', href: '/companies/' }]}
      />

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-gray-900 mb-2">
          Dubai Companies & Startups
        </h1>
        <p className="text-gray-600 leading-relaxed max-w-2xl">
          Browse companies and startups in Dubai, organized by industry and
          sector. Find business information, founders, and market data.
        </p>
      </div>

      {/* Browse by sector */}
      <section>
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Browse by Sector
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sectors.map((sector) => (
            <Link
              key={sector.slug}
              href={`/companies/${sector.slug}/`}
              className="group p-4 border border-gray-100 rounded-xl hover:border-gray-200 hover:shadow-sm transition-all bg-white"
            >
              <div className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                {sector.name}
              </div>
            </Link>
          ))}
        </div>
      </section>
    </Layout>
  )
}

export const getStaticProps: GetStaticProps<Props> = async () => {
  try {
    const res = await getSectors()
    return {
      props: {
        sectors: res.data || [],
      },
      revalidate: 86400, // ISR: rebuild every 24 hours
    }
  } catch {
    return { notFound: true }
  }
}
