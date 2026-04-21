import { GetStaticPaths, GetStaticProps } from 'next'
import Link from 'next/link'
import Layout from '@/components/Layout'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import { getVenueAreaPaths, getCategories, getAreas } from '@/lib/api'
import { buildBreadcrumbSchema } from '@/lib/seo'
import { Category, Area } from '@/lib/types'

interface Props {
  category: Category
  areas: Area[]
}

export default function CategoryPage({ category, areas }: Props) {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'
  const canonical = `${siteUrl}/${category.slug}/`

  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: category.name, url: canonical },
  ])

  return (
    <Layout
      title={`${category.name} in Dubai | Story of Dubai`}
      description={`Browse the best ${category.name.toLowerCase()} in Dubai, ranked by area and quality.`}
      canonical={canonical}
      jsonLd={[breadcrumbSchema]}
    >
      <BreadcrumbNav
        crumbs={[{ name: category.name, href: `/${category.slug}/` }]}
      />

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-gray-900 mb-2">
          {category.name} in Dubai
        </h1>
        <p className="text-gray-600 leading-relaxed max-w-2xl">
          Browse the best {category.name.toLowerCase()} across Dubai neighborhoods,
          ranked by ratings, reviews, and quality.
        </p>
      </div>

      {/* Browse by area */}
      <section>
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          Browse by Area
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {areas.map((area) => (
            <Link
              key={area.slug}
              href={`/${category.slug}/${area.slug}/`}
              className="group p-4 border border-gray-100 rounded-xl hover:border-gray-200 hover:shadow-sm transition-all bg-white"
            >
              <div className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                {area.name}
              </div>
              {area.description && (
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">
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

export const getStaticPaths: GetStaticPaths = async () => {
  try {
    const categoriesRes = await getCategories()
    const paths = (categoriesRes.data || []).map((c) => ({
      params: { category: c.slug },
    }))
    return { paths, fallback: 'blocking' }
  } catch {
    return { paths: [], fallback: 'blocking' }
  }
}

export const getStaticProps: GetStaticProps<Props> = async ({ params }) => {
  const category_slug = params?.category as string

  try {
    const [categoriesRes, areasRes, pathsRes] = await Promise.all([
      getCategories(),
      getAreas(),
      getVenueAreaPaths(),
    ])

    const category = categoriesRes.data?.find((c) => c.slug === category_slug)
    if (!category) return { notFound: true }

    // Get unique areas for this category
    const categoryAreaSlugs = new Set(
      (pathsRes.data || [])
        .filter((p) => p.category_slug === category_slug)
        .map((p) => p.area_slug)
    )

    const filteredAreas = (areasRes.data || []).filter((a) =>
      categoryAreaSlugs.has(a.slug)
    )

    return {
      props: {
        category,
        areas: filteredAreas,
      },
      revalidate: 86400, // ISR: rebuild every 24 hours
    }
  } catch {
    return { notFound: true }
  }
}
