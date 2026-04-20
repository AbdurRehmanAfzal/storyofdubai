interface AffiliateCTAProps {
  category: string
  area: string
}

interface CTAConfig {
  text: string
  subtext: string
  color: string
}

const ctaConfig: Record<string, CTAConfig> = {
  restaurants: {
    text: 'Find a table on TheFork',
    subtext: 'Free reservations, no booking fee',
    color: 'bg-orange-50 border-orange-200 text-orange-800',
  },
  hotels: {
    text: 'Check rates on Booking.com',
    subtext: 'Best price guarantee, free cancellation',
    color: 'bg-blue-50 border-blue-200 text-blue-800',
  },
  attractions: {
    text: 'Book tickets on Viator',
    subtext: 'Skip the queue, instant confirmation',
    color: 'bg-purple-50 border-purple-200 text-purple-800',
  },
  apartments: {
    text: 'Browse listings on Bayut',
    subtext: 'Verified listings, direct agent contact',
    color: 'bg-green-50 border-green-200 text-green-800',
  },
}

export default function AffiliateCTA({ category, area }: AffiliateCTAProps) {
  const config = ctaConfig[category] || ctaConfig.attractions

  return (
    <div className={`rounded-xl border p-4 ${config.color} my-6`}>
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <p className="font-medium">
            {config.text} in {area}
          </p>
          <p className="text-sm opacity-75 mt-0.5">{config.subtext}</p>
        </div>

        <a
          href="#"
          className="text-sm font-medium px-4 py-2 bg-white rounded-lg border border-current hover:opacity-90 transition-opacity"
        >
          Browse now →
        </a>
      </div>
    </div>
  )
}
