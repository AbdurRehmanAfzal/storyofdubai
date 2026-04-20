import Link from 'next/link'
import Layout from '@/components/Layout'
import { buildTitle, buildCanonical } from '@/lib/seo'

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'

const categories = [
  {
    name: 'Restaurants',
    slug: 'restaurants',
    icon: '🍽',
    desc: 'Top dining across every Dubai neighborhood',
  },
  {
    name: 'Hotels',
    slug: 'hotels',
    icon: '🏨',
    desc: 'Best hotels ranked by value and quality',
  },
  {
    name: 'Attractions',
    slug: 'attractions',
    icon: '🎡',
    desc: 'Must-visit experiences and activities',
  },
  {
    name: 'Apartments',
    slug: 'apartments',
    icon: '🏙',
    desc: 'Rental and sale properties by area',
  },
  {
    name: 'Visa Guide',
    slug: 'visa-guide',
    icon: '🛂',
    desc: 'UAE visa guides by nationality',
  },
  {
    name: 'Companies',
    slug: 'companies',
    icon: '🏢',
    desc: 'Dubai startup and company directory',
  },
]

const topAreas = [
  'dubai-marina',
  'downtown-dubai',
  'business-bay',
  'jumeirah-village-circle',
  'difc',
  'palm-jumeirah',
  'jumeirah',
  'dubai-hills',
  'al-barsha',
  'jbr',
]

const websiteSchema = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'Story of Dubai',
  url: SITE_URL,
  potentialAction: {
    '@type': 'SearchAction',
    target: {
      '@type': 'EntryPoint',
      urlTemplate: `${SITE_URL}/search?q={search_term_string}`,
    },
    'query-input': 'required name=search_term_string',
  },
}

export default function HomePage() {
  return (
    <Layout
      title={buildTitle(
        'Dubai Rankings, Guides & Intelligence — Story of Dubai'
      )}
      description="The definitive rankings platform for Dubai. Top restaurants, hotels, properties, visa guides, and company data — all scored and updated daily."
      canonical={buildCanonical('/')}
      jsonLd={websiteSchema}
    >
      {/* Hero */}
      <div className="text-center py-12 mb-12">
        <h1 className="text-4xl font-semibold text-gray-900 mb-4">
          The Story of Dubai
        </h1>
        <p className="text-lg text-gray-500 max-w-2xl mx-auto leading-relaxed">
          Data-ranked guides to every restaurant, hotel, property, and experience
          in Dubai. Updated daily. No ads. No bias.
        </p>
      </div>

      {/* Category grid */}
      <section className="mb-12">
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
          Explore by category
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {categories.map((cat) => (
            <Link
              key={cat.slug}
              href={`/${cat.slug}/`}
              className="group p-5 border border-gray-100 rounded-xl hover:border-gray-200 hover:shadow-sm transition-all bg-white"
            >
              <div className="text-2xl mb-2">{cat.icon}</div>
              <div className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                {cat.name}
              </div>
              <div className="text-sm text-gray-400 mt-1">{cat.desc}</div>
            </Link>
          ))}
        </div>
      </section>

      {/* Top areas */}
      <section className="mb-12">
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">
          Browse by area
        </h2>
        <div className="flex flex-wrap gap-2">
          {topAreas.map((area) => (
            <Link
              key={area}
              href={`/restaurants/${area}/`}
              className="text-sm text-gray-600 hover:text-blue-600 border border-gray-200 hover:border-blue-200 rounded-full px-4 py-1.5 transition-colors"
            >
              {area
                .split('-')
                .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                .join(' ')}
            </Link>
          ))}
        </div>
      </section>

      {/* Data stats */}
      <section className="grid grid-cols-3 gap-4 py-8 border-t border-gray-100">
        {[
          { val: '10,000+', label: 'Pages indexed' },
          { val: 'Daily', label: 'Data updates' },
          { val: '40+', label: 'Dubai areas covered' },
        ].map((stat) => (
          <div key={stat.label} className="text-center">
            <div className="text-2xl font-semibold text-gray-900">
              {stat.val}
            </div>
            <div className="text-sm text-gray-400 mt-1">{stat.label}</div>
          </div>
        ))}
      </section>
    </Layout>
  )
}
