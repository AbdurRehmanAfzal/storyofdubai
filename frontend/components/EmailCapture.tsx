import { useState } from 'react'

interface EmailCaptureProps {
  context: string
}

export default function EmailCapture({ context }: EmailCaptureProps) {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Connect to Beehiiv API in Phase 4
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="bg-b1-gold border border-b1-gold rounded-xs p-4 text-center text-sm text-white">
        You are subscribed. Weekly Dubai intelligence in your inbox.
      </div>
    )
  }

  return (
    <div className="bg-white border border-b1-light rounded-xs p-5 my-8">
      <p className="font-luxury font-medium text-b1-darker mb-1">Dubai Intelligence Weekly</p>
      <p className="text-sm text-b1-dark mb-3">
        Weekly rankings, new openings, and market insights for {context}.
      </p>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          required
          className="flex-1 px-3 py-2 text-sm border border-b1-light rounded-xs focus:outline-none focus:border-b1-darker focus:ring-1 focus:ring-b1-darker"
        />
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium bg-b1-gold text-white rounded-xs hover:bg-b1-gold-hover transition-colors"
        >
          Subscribe
        </button>
      </form>
    </div>
  )
}
