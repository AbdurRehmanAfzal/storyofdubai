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
      <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center text-sm text-green-800">
        You are subscribed. Weekly Dubai intelligence in your inbox.
      </div>
    )
  }

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-5 my-8">
      <p className="font-medium text-gray-900 mb-1">Dubai Intelligence Weekly</p>
      <p className="text-sm text-gray-500 mb-3">
        Weekly rankings, new openings, and market insights for {context}.
      </p>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          required
          className="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400"
        />
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium bg-gray-900 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          Subscribe
        </button>
      </form>
    </div>
  )
}
