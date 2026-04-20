import Head from 'next/head'
import { buildTitle, buildCanonical } from '@/lib/seo'

export default function Home() {
  const title = buildTitle('Restaurants, Properties & Visa Guides in Dubai')
  const description =
    'Explore the best restaurants, apartments, and visa information in Dubai. Ranked by quality, rating, and value.'
  const canonical = buildCanonical('/')

  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:type" content="website" />
        <meta property="og:url" content={canonical} />
        <link rel="canonical" href={canonical} />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
        <div className="container mx-auto px-4 py-16 sm:py-24">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Story of Dubai
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
              Discover the best restaurants, apartments, and visa guides in Dubai.
              Ranked by quality, ratings, and value.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mt-12">
              <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition">
                <h2 className="text-2xl font-bold text-gray-900 mb-3">
                  🍽️ Restaurants
                </h2>
                <p className="text-gray-600 mb-4">
                  Find the best dining spots across Dubai neighborhoods
                </p>
                <a
                  href="/restaurants/downtown"
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Explore →
                </a>
              </div>

              <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition">
                <h2 className="text-2xl font-bold text-gray-900 mb-3">
                  🏢 Properties
                </h2>
                <p className="text-gray-600 mb-4">
                  Browse apartments and villas in Dubai
                </p>
                <a
                  href="/apartments/marina"
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Explore →
                </a>
              </div>

              <div className="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition">
                <h2 className="text-2xl font-bold text-gray-900 mb-3">
                  📋 Visa Guides
                </h2>
                <p className="text-gray-600 mb-4">
                  Complete visa information for all nationalities
                </p>
                <a
                  href="/visa-guide"
                  className="text-blue-600 hover:text-blue-800 font-medium"
                >
                  Explore →
                </a>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  )
}
