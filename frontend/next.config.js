/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  pageExtensions: ['ts', 'tsx'],

  // Image optimization
  images: {
    domains: ['maps.googleapis.com', 'lh3.googleusercontent.com', 'storyofdubai.com', 'api.storyofdubai.com'],
    formats: ['image/avif', 'image/webp'],
  },

  // ISR revalidation for static pages
  onDemandEntries: {
    maxInactiveAge: 60 * 1000,
    pagesBufferLength: 5,
  },

  // Environment variables exposed to browser
  env: {
    NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL || 'https://storyofdubai.com',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-XSS-Protection', value: '1; mode=block' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
    ]
  },

  // Redirects: www → non-www and API proxying
  async redirects() {
    return [
      {
        source: '/:path*',
        has: [{ type: 'host', value: 'www.storyofdubai.com' }],
        destination: 'https://storyofdubai.com/:path*',
        permanent: true,
      },
    ]
  },
};

module.exports = nextConfig;
