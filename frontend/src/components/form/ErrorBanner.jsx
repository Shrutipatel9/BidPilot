export default function ErrorBanner({ error }) {
  if (!error) return null

  const message = error.data?.detail ?? 'Something went wrong. Please try again.'

  return (
    <div className="rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-700">
      {typeof message === 'string' ? message : JSON.stringify(message)}
    </div>
  )
}
