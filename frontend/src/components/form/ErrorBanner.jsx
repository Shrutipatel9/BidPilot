import { AlertCircle } from 'lucide-react'

export default function ErrorBanner({ error }) {
  if (!error) return null

  const message = error.data?.detail ?? 'Something went wrong. Please try again.'

  return (
    <div className="flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 px-3.5 py-2.5 text-sm text-rose-700">
      <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
      <span>{typeof message === 'string' ? message : JSON.stringify(message)}</span>
    </div>
  )
}
