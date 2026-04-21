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
    color: 'bg-b1-gold border-b1-gold text-white',
  },
  hotels: {
    text: 'Check rates on Booking.com',
    subtext: 'Best price guarantee, free cancellation',
    color: 'bg-b1-gold border-b1-gold text-white',
  },
  attractions: {
    text: 'Book tickets on Viator',
    subtext: 'Skip the queue, instant confirmation',
    color: 'bg-b1-gold border-b1-gold text-white',
  },
  apartments: {
    text: 'Browse listings on Bayut',
    subtext: 'Verified listings, direct agent contact',
    color: 'bg-b1-gold border-b1-gold text-white',
  },
}

export default function AffiliateCTA({ category, area }: AffiliateCTAProps) {
  const config = ctaConfig[category] || ctaConfig.attractions

  return (
    <div className={`rounded-xs border p-4 ${config.color} my-6`}>
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <p className="font-luxury font-medium">
            {config.text} in {area}
          </p>
          <p className="text-sm opacity-75 mt-0.5">{config.subtext}</p>
        </div>

        <a
          href="#"
          className="text-sm font-medium px-4 py-2 bg-white text-b1-gold rounded-xs border border-current hover:opacity-90 transition-opacity"
        >
          Browse now →
        </a>
      </div>
    </div>
  )
}
