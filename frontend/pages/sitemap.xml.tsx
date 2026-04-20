import { GetServerSideProps } from 'next'
import {
  getVenueAreaPaths,
  getPropertyPaths,
  getVisaGuidePaths,
} from '@/lib/api'

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com'

interface SitemapUrl {
  loc: string
  priority: string
  changefreq: string
}

function generateSiteMap(urls: SitemapUrl[]): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>${SITE_URL}/</loc>
    <priority>1.0</priority>
    <changefreq>daily</changefreq>
  </url>
${urls
  .map(
    (u) => `  <url>
    <loc>${u.loc}</loc>
    <priority>${u.priority}</priority>
    <changefreq>${u.changefreq}</changefreq>
  </url>`
  )
  .join('\n')}
</urlset>`
}

export default function Sitemap() {
  return null
}

export const getServerSideProps: GetServerSideProps = async ({ res }) => {
  const [venueAreaRes, propertyRes, visaRes] = await Promise.allSettled([
    getVenueAreaPaths(),
    getPropertyPaths(),
    getVisaGuidePaths(),
  ])

  const urls: SitemapUrl[] = []

  // Venue area hub pages
  if (venueAreaRes.status === 'fulfilled' && venueAreaRes.value.data) {
    for (const { category_slug, area_slug } of venueAreaRes.value.data) {
      urls.push({
        loc: `${SITE_URL}/${category_slug}/${area_slug}/`,
        priority: '0.8',
        changefreq: 'daily',
      })
    }
  }

  // Property filter pages
  if (propertyRes.status === 'fulfilled' && propertyRes.value.data) {
    for (const { area_slug, bedrooms, price_bucket } of propertyRes.value.data) {
      urls.push({
        loc: `${SITE_URL}/apartments/${area_slug}/${bedrooms}-bedroom/${price_bucket}/`,
        priority: '0.8',
        changefreq: 'twice a week',
      })
    }
  }

  // Visa guide pages
  if (visaRes.status === 'fulfilled' && visaRes.value.data) {
    for (const { nationality_slug, visa_type_slug } of visaRes.value.data) {
      urls.push({
        loc: `${SITE_URL}/visa-guide/${nationality_slug}/${visa_type_slug}/`,
        priority: '0.7',
        changefreq: 'weekly',
      })
    }
  }

  const sitemap = generateSiteMap(urls)

  res.setHeader('Content-Type', 'text/xml')
  res.setHeader(
    'Cache-Control',
    'public, s-maxage=86400, stale-while-revalidate'
  )
  res.write(sitemap)
  res.end()

  return { props: {} }
}
