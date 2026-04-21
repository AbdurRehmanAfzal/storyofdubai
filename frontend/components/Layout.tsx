import Head from 'next/head'
import Link from 'next/link'
import { ReactNode } from 'react'
import { DM_Sans, Playfair_Display } from 'next/font/google'

const dmSans = DM_Sans({
  subsets: ['latin'],
  variable: '--font-dm-sans',
  weight: ['400', '500', '700'],
})

const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-luxury',
  weight: ['400', '500', '700'],
})

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
    <div className={`${dmSans.variable} ${playfair.variable}`}>
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
        <header className="border-b border-b1-light sticky top-0 bg-white z-50">
          <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <Link href="/" className="font-luxury font-bold text-xl text-b1-darker">
              Story of Dubai
            </Link>
            <nav className="hidden md:flex items-center gap-6 text-sm text-b1-dark">
              <Link href="/restaurants" className="hover:text-b1-darker transition-colors">
                Restaurants
              </Link>
              <Link href="/apartments" className="hover:text-b1-darker transition-colors">
                Properties
              </Link>
              <Link href="/visa-guide" className="hover:text-b1-darker transition-colors">
                Visa Guide
              </Link>
              <Link href="/companies" className="hover:text-b1-darker transition-colors">
                Companies
              </Link>
            </nav>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-6xl mx-auto px-4 py-8">{children}</main>

        {/* Footer */}
        <footer className="border-t border-b1-light mt-16 py-8">
          <div className="max-w-6xl mx-auto px-4 text-sm text-b1-dark text-center">
            <p>© 2026 Story of Dubai. Data updated daily.</p>
          </div>
        </footer>
      </div>
    </div>
  )
}
