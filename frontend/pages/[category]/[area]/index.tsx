import { GetStaticPaths, GetStaticProps } from 'next'
import Layout from '@/components/Layout'
import VenueCard from '@/components/VenueCard'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import AffiliateCTA from '@/components/AffiliateCTA'
import EmailCapture from '@/components/EmailCapture'
import {
  getVenueAreaPaths,
  getVenuesByAreaCategory,
  getArea,
  getCategories,
} from '@/lib/api'
import {
  buildVenueAreaMeta,
  buildItemListSchema,
  buildBreadcrumbSchema,
} from '@/lib/seo'
import { VenueListItem, Area, Category } from '@/lib/types'

interface Props {
  venues: VenueListItem[]
  area: Area
  category: Category
  lastUpdated: string
}

export default function VenueAreaPage({
  venues,
  area,
  category,
  lastUpdated,
}: Props) {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'
  const meta = buildVenueAreaMeta(category.name, area.name, venues.length)

  const itemListSchema = buildItemListSchema(
    meta.title,
    meta.canonical,
    venues.map((v) => ({
      name: v.name,
      url: `${siteUrl}/${category.slug}/${area.slug}/${v.slug}/`,
    }))
  )

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: category.name, url: `${siteUrl}/${category.slug}/` },
    { name: area.name, url: meta.canonical },
  ])

  return (
    <Layout
      title={meta.title}
      description={meta.description}
      canonical={meta.canonical}
      jsonLd={[itemListSchema, breadcrumbSchema]}
    >
      <BreadcrumbNav
        crumbs={[
          { name: category.name, href: `/${category.slug}/` },
          { name: area.name, href: `/${category.slug}/${area.slug}/` },
        ]}
      />

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-luxury font-semibold text-b1-darker mb-2">
          Top {category.name} in {area.name}, Dubai
        </h1>
        {area.description && (
          <p className="text-b1-dark leading-relaxed max-w-2xl">
            {area.description}
          </p>
        )}
        <p className="text-xs text-b1-light mt-3">
          {venues.length} places ranked · Last updated {lastUpdated}
        </p>
      </div>

      {/* Affiliate CTA — above the fold */}
      <AffiliateCTA category={category.slug} area={area.name} />

      {/* Ranked list */}
      {venues.length > 0 ? (
        <div className="space-y-3">
          {venues.map((venue, i) => (
            <VenueCard key={venue.id} venue={venue} rank={i + 1} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-400">
          <p>
            No {category.name.toLowerCase()} listed for {area.name} yet.
          </p>
          <p className="text-sm mt-1">Check back soon — we update daily.</p>
        </div>
      )}

      {/* Email capture — below list */}
      <EmailCapture context={`${category.name} in ${area.name}`} />

      {/* Related areas internal links */}
      <div className="mt-8 pt-8 border-t border-gray-100">
        <h2 className="text-sm font-medium text-gray-500 mb-3">
          More {category.name} guides in Dubai
        </h2>
        <div className="flex flex-wrap gap-2">
          {[
            'Dubai Marina',
            'Downtown Dubai',
            'Business Bay',
            'JBR',
            'DIFC',
            'Jumeirah',
          ].map((a) => (
            <a
              key={a}
              href={`/${category.slug}/${a
                .toLowerCase()
                .replace(/ /g, '-')}/`}
              className="text-sm text-blue-600 hover:text-blue-700 border border-blue-100 rounded-lg px-3 py-1 hover:bg-blue-50 transition-colors"
            >
              {a}
            </a>
          ))}
        </div>
      </div>
    </Layout>
  )
}

export const getStaticPaths: GetStaticPaths = async () => {
  try {
    const res = await getVenueAreaPaths()
    const paths = (res.data || []).map(({ category_slug, area_slug }) => ({
      params: { category: category_slug, area: area_slug },
    }))
    return { paths, fallback: 'blocking' }
  } catch {
    return { paths: [], fallback: 'blocking' }
  }
}

export const getStaticProps: GetStaticProps<Props> = async ({ params }) => {
  const category_slug = params?.category as string
  const area_slug = params?.area as string

  try {
    const [venuesRes, areaRes, categoriesRes] = await Promise.all([
      getVenuesByAreaCategory(area_slug, category_slug),
      getArea(area_slug),
      getCategories(),
    ])

    if (!areaRes.data) return { notFound: true }

    const category = categoriesRes.data?.find((c) => c.slug === category_slug)
    if (!category) return { notFound: true }

    return {
      props: {
        venues: venuesRes.data || [],
        area: areaRes.data,
        category,
        lastUpdated: new Date().toLocaleDateString('en-AE', {
          day: 'numeric',
          month: 'long',
          year: 'numeric',
        }),
      },
      revalidate: 86400, // ISR: rebuild every 24 hours
    }
  } catch {
    return { notFound: true }
  }
}
