import { GetStaticPaths, GetStaticProps } from 'next'
import Link from 'next/link'
import Layout from '@/components/Layout'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import { getNationalities, getAllVisaGuides } from '@/lib/api'
import { buildBreadcrumbSchema } from '@/lib/seo'
import { VisaNationalityGuide } from '@/lib/types'

interface Props {
  nationality: {
    slug: string
    name: string
    iso_code: string
  }
  visaTypes: VisaNationalityGuide[]
}

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'

export default function NationalityVisasPage({ nationality, visaTypes }: Props) {
  const canonical = `${SITE_URL}/visa-guide/${nationality.slug}/`

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: 'Visa Guides', url: `${SITE_URL}/visa-guide/` },
    { name: nationality.name, url: canonical },
  ])

  return (
    <Layout
      title={`${nationality.name} Visa Types for Dubai/UAE | Story of Dubai`}
      description={`All visa types available for ${nationality.name} nationals in Dubai and UAE. Tourist, employment, investor, and residence visas.`}
      canonical={canonical}
      jsonLd={[breadcrumbSchema]}
    >
      <BreadcrumbNav
        crumbs={[
          { name: 'Visa Guides', href: '/visa-guide/' },
          { name: nationality.name, href: `/visa-guide/${nationality.slug}/` },
        ]}
      />

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-gray-900 mb-2">
          Visa Types for {nationality.name} Nationals
        </h1>
        <p className="text-gray-600 leading-relaxed max-w-2xl">
          Complete guides for all visa types available to {nationality.name}
          nationals in Dubai and the UAE. Browse by visa type to compare costs,
          processing times, and requirements.
        </p>
      </div>

      {/* Visa types */}
      <section>
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Available Visa Types
        </h2>
        {visaTypes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {visaTypes.map((visa) => (
              <Link
                key={visa.id}
                href={`/visa-guide/${nationality.slug}/${visa.visa_type.slug}/`}
                className="group p-5 border border-gray-100 rounded-xl hover:border-gray-200 hover:shadow-sm transition-all bg-white"
              >
                <div>
                  <h3 className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors mb-2">
                    {visa.visa_type.name}
                  </h3>
                  <div className="grid grid-cols-3 gap-3 text-sm">
                    <div>
                      <div className="text-xs text-gray-500 mb-0.5">Cost</div>
                      <div className="font-semibold text-gray-900">
                        AED {visa.visa_type.cost_aed?.toLocaleString() || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-0.5">Processing</div>
                      <div className="font-semibold text-gray-900">
                        {visa.visa_type.processing_days || 'N/A'} days
                      </div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-500 mb-0.5">Valid for</div>
                      <div className="font-semibold text-gray-900">
                        {visa.visa_type.duration_days || 'N/A'} days
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 text-center">
            <p className="text-gray-600">
              No visa guides available for {nationality.name} nationals yet.
            </p>
          </div>
        )}
      </section>
    </Layout>
  )
}

export const getStaticPaths: GetStaticPaths = async () => {
  try {
    const res = await getNationalities()
    const paths = (res.data || []).map((n) => ({
      params: { nationality: n.slug },
    }))
    return { paths, fallback: 'blocking' }
  } catch {
    return { paths: [], fallback: 'blocking' }
  }
}

export const getStaticProps: GetStaticProps<Props> = async ({ params }) => {
  const nationality_slug = params?.nationality as string

  try {
    const [nationalitiesRes, visasRes] = await Promise.all([
      getNationalities(),
      getAllVisaGuides(),
    ])

    const nationality = nationalitiesRes.data?.find(
      (n) => n.slug === nationality_slug
    )
    if (!nationality) return { notFound: true }

    // Filter visa guides for this nationality
    const visasForNationality = (visasRes.data || []).filter(
      (v) => v.nationality?.slug === nationality_slug
    )

    return {
      props: {
        nationality: {
          slug: nationality.slug,
          name: nationality.name,
          iso_code: nationality.iso_code,
        },
        visaTypes: visasForNationality,
      },
      revalidate: 86400, // ISR: rebuild every 24 hours
    }
  } catch {
    return { notFound: true }
  }
}
