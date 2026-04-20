import Head from 'next/head'
import Link from 'next/link'
import { ReactNode } from 'react'

interface LayoutProps {
  children: ReactNode
  title: string
  description: string
  canonical: string
  jsonLd?: object | object[]
}

export default function Layout({
  children,
  title,
  description,
  canonical,
  jsonLd,
}: LayoutProps) {
  const schemas = jsonLd ? (Array.isArray(jsonLd) ? jsonLd : [jsonLd]) : []

  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content={description} />
        <link rel="canonical" href={canonical} />
        <meta property="og:title" content={title} />
        <meta property="og:description" content={description} />
        <meta property="og:url" content={canonical} />
        <meta property="og:site_name" content="Story of Dubai" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        {schemas.map((schema, i) => (
          <script
            key={i}
            type="application/ld+json"
            dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
          />
        ))}
      </Head>

      <div className="min-h-screen bg-white">
        {/* Header */}
        <header className="border-b border-gray-100 sticky top-0 bg-white z-50">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <Link href="/" className="font-semibold text-lg text-gray-900">
              Story of Dubai
            </Link>
            <nav className="hidden md:flex items-center gap-6 text-sm text-gray-600">
              <Link href="/restaurants" className="hover:text-gray-900">
                Restaurants
              </Link>
              <Link href="/apartments" className="hover:text-gray-900">
                Properties
              </Link>
              <Link href="/visa-guide" className="hover:text-gray-900">
                Visa Guide
              </Link>
              <Link href="/companies" className="hover:text-gray-900">
                Companies
              </Link>
            </nav>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>

        {/* Footer */}
        <footer className="border-t border-gray-100 mt-16 py-8">
          <div className="max-w-6xl mx-auto px-4 text-sm text-gray-500 text-center">
            <p>© {new Date().getFullYear()} Story of Dubai. Data updated daily.</p>
          </div>
        </footer>
      </div>
    </>
  )
}
