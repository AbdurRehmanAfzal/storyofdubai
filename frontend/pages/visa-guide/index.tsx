import { GetStaticProps } from 'next'
import Link from 'next/link'
import Layout from '@/components/Layout'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import { getNationalities } from '@/lib/api'
import { buildBreadcrumbSchema } from '@/lib/seo'

interface Nationality {
  id: string
  slug: string
  name: string
  iso_code: string
}

interface Props {
  nationalities: Nationality[]
}

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'

export default function VisaGuidePage({ nationalities }: Props) {
  const canonical = `${SITE_URL}/visa-guide/`

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: 'Visa Guides', url: canonical },
  ])

  return (
    <Layout
      title="UAE Visa Guides by Nationality | Story of Dubai"
      description="Complete visa guides for UAE. Tourist, employment, investor, and residence visas organized by nationality."
      canonical={canonical}
      jsonLd={[breadcrumbSchema]}
    >
      <BreadcrumbNav
        crumbs={[{ name: 'Visa Guides', href: '/visa-guide/' }]}
      />

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-3xl font-luxury font-semibold text-b1-darker mb-2">
          UAE Visa Guides
        </h1>
        <p className="text-b1-dark leading-relaxed max-w-2xl">
          Complete step-by-step visa guides for UAE residency, organized by
          nationality. Find requirements, costs, and processing times.
        </p>
      </div>

      {/* Browse by nationality */}
      <section>
        <h2 className="text-lg font-luxury font-medium text-b1-darker mb-4">
          Browse by Nationality
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {nationalities.map((nationality) => (
            <Link
              key={nationality.slug}
              href={`/visa-guide/${nationality.slug}/`}
              className="group p-4 border border-b1-light rounded-xs hover:border-b1-light hover:shadow-sm transition-all bg-white"
            >
              <div className="font-luxury font-medium text-b1-darker group-hover:text-b1-gold transition-colors">
                {nationality.name}
              </div>
              <div className="text-sm text-b1-dark mt-1">
                {nationality.iso_code}
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
    const res = await getNationalities()
    return {
      props: {
        nationalities: res.data || [],
      },
      revalidate: 86400, // ISR: rebuild every 24 hours
    }
  } catch {
    return { notFound: true }
  }
}
