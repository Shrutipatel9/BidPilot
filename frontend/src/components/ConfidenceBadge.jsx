function confidenceStyle(confidence) {
  if (confidence >= 80) return 'bg-emerald-50 text-emerald-700 ring-emerald-600/20'
  if (confidence >= 50) return 'bg-amber-50 text-amber-700 ring-amber-600/20'
  return 'bg-rose-50 text-rose-700 ring-rose-600/20'
}

export default function ConfidenceBadge({ confidence }) {
  if (confidence === null || confidence === undefined) {
    return <span className="text-xs text-slate-400">—</span>
  }

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${confidenceStyle(confidence)}`}
    >
      {confidence}% confidence
    </span>
  )
}
