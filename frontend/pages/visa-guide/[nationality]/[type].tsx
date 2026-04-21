import { GetStaticPaths, GetStaticProps } from 'next'
import Layout from '@/components/Layout'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import EmailCapture from '@/components/EmailCapture'
import { getVisaGuidePaths, getVisaGuide } from '@/lib/api'
import {
  buildBreadcrumbSchema,
  buildHowToSchema,
} from '@/lib/seo'
import { VisaNationalityGuide } from '@/lib/types'

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'

interface Props {
  guide: VisaNationalityGuide
}

function parseGuideIntoSteps(
  guide: string
): Array<{ name: string; text: string }> {
  const steps: Array<{ name: string; text: string }> = []

  // Try to split by numbered bullets (1. 2. 3.)
  const numberBulletRegex = /^\d+\.\s+(.+?)$/gm
  let match

  while ((match = numberBulletRegex.exec(guide)) !== null) {
    const stepNumber = (steps.length + 1).toString()
    steps.push({
      name: `Step ${stepNumber}`,
      text: match[1],
    })
  }

  // If no numbered bullets found, split by paragraphs
  if (steps.length === 0) {
    const paragraphs = guide
      .split('\n\n')
      .filter((p) => p.trim().length > 0)
    paragraphs.forEach((para, i) => {
      steps.push({
        name: `Step ${i + 1}`,
        text: para.trim(),
      })
    })
  }

  return steps.length > 0
    ? steps
    : [{ name: 'Overview', text: guide }]
}

export default function VisaGuidePage({ guide }: Props) {
  const canonical = `${SITE_URL}/visa-guide/${guide.nationality.slug}/${guide.visa_type.slug}/`
  const title = `${guide.nationality.name} ${guide.visa_type.name} Dubai — Cost, Requirements & Process`
  const description = `Complete guide for ${guide.nationality.name} nationals applying for a ${guide.visa_type.name} in Dubai/UAE. Cost: AED ${guide.visa_type.cost_aed.toLocaleString()}, Processing: ${guide.visa_type.processing_days} days, Valid for ${guide.visa_type.duration_days} days.`

  const steps = guide.ai_guide
    ? parseGuideIntoSteps(guide.ai_guide)
    : []

  const howToSchema = steps.length > 0 ? buildHowToSchema(
    title,
    description,
    steps
  ) : null

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: 'Visa Guides', url: `${SITE_URL}/visa-guide/` },
    { name: guide.nationality.name, url: `${SITE_URL}/visa-guide/${guide.nationality.slug}/` },
  ])

  return (
    <Layout
      title={title}
      description={description}
      canonical={canonical}
      jsonLd={howToSchema ? [breadcrumbSchema, howToSchema] : [breadcrumbSchema]}
    >
      <BreadcrumbNav
        crumbs={[
          { name: 'Visa Guides', href: '/visa-guide/' },
          { name: guide.nationality.name, href: `/visa-guide/${guide.nationality.slug}/` },
          {
            name: guide.visa_type.name,
            href: canonical,
          },
        ]}
      />

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-luxury font-semibold text-b1-darker mb-2">
          {guide.nationality.name} {guide.visa_type.name} Dubai
        </h1>
        <p className="text-b1-dark leading-relaxed max-w-2xl">
          Complete step-by-step guide for {guide.nationality.name} nationals
          applying for a {guide.visa_type.name} in Dubai and the UAE.
        </p>
      </div>

      {/* Key facts grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-8">
        <div className="bg-white border border-b1-light rounded-xs p-4">
          <div className="text-xs font-medium text-b1-gold mb-1">Cost</div>
          <div className="text-xl font-semibold text-b1-darker">
            AED {guide.visa_type.cost_aed.toLocaleString()}
          </div>
        </div>

        <div className="bg-white border border-b1-light rounded-xs p-4">
          <div className="text-xs font-medium text-b1-gold mb-1">Processing</div>
          <div className="text-xl font-semibold text-b1-darker">
            {guide.visa_type.processing_days} days
          </div>
        </div>

        <div className="bg-white border border-b1-light rounded-xs p-4">
          <div className="text-xs font-medium text-b1-gold mb-1">Valid for</div>
          <div className="text-xl font-semibold text-b1-darker">
            {guide.visa_type.duration_days} days
          </div>
        </div>
      </div>

      {/* AI-generated guide */}
      {guide.ai_guide && (
        <div className="prose prose-sm max-w-none mb-8">
          <div className="bg-white rounded-xs p-6 border border-b1-light">
            <h2 className="text-lg font-luxury font-semibold text-b1-darker mb-4">
              How to Apply
            </h2>
            <div className="space-y-4 text-b1-dark">
              {steps.map((step, i) => (
                <div key={i} className="flex gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-xs bg-b1-gold text-white flex items-center justify-center text-xs font-semibold">
                    {i + 1}
                  </div>
                  <div>
                    <p className="font-medium text-b1-darker mb-0.5">
                      {step.name}
                    </p>
                    <p className="text-sm text-b1-dark">{step.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Specific requirements if available */}
      {guide.requirements && (
        <div className="bg-white border border-b1-light rounded-xs p-6 mb-8">
          <h2 className="text-lg font-luxury font-semibold text-b1-darker mb-3">
            Additional Requirements
          </h2>
          <p className="text-b1-dark leading-relaxed whitespace-pre-wrap">
            {guide.requirements}
          </p>
        </div>
      )}

      {/* Email capture */}
      <EmailCapture context={`${guide.nationality.name} visa information`} />

      {/* Related visas */}
      <div className="mt-8 pt-8 border-t border-b1-light">
        <h2 className="text-sm font-medium text-b1-dark mb-3">
          Other visa types for {guide.nationality.name}
        </h2>
        <p className="text-sm text-b1-dark mb-4">
          Explore other visa options available for {guide.nationality.name} nationals.
        </p>
        <a
          href={`/visa-guide/${guide.nationality.slug}/`}
          className="text-sm font-medium text-b1-gold hover:text-b1-gold-hover transition-colors"
        >
          View all visa types for {guide.nationality.name} →
        </a>
      </div>
    </Layout>
  )
}

export const getStaticPaths: GetStaticPaths = async () => {
  try {
    const res = await getVisaGuidePaths()
    const paths = (res.data || []).map(({ nationality_slug: nslug, visa_type_slug: vslug }) => ({
      params: { nationality: nslug, type: vslug },
    }))
    return { paths, fallback: 'blocking' }
  } catch {
    return { paths: [], fallback: 'blocking' }
  }
}

export const getStaticProps: GetStaticProps<Props> = async ({ params }) => {
  const nationality_slug = params?.nationality as string
  const visa_type_slug = params?.type as string

  try {
    const res = await getVisaGuide(nationality_slug, visa_type_slug)
    if (!res.data) return { notFound: true }
    return {
      props: { guide: res.data },
      revalidate: 604800, // ISR: rebuild every 7 days (visa info changes less frequently)
    }
  } catch {
    return { notFound: true }
  }
}
