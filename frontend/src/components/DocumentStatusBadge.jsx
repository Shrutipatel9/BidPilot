import { DOCUMENT_STATUS_LABELS } from '../lib/documentStatus'

const STATUS_STYLES = {
  uploaded: 'bg-slate-100 text-slate-600 ring-slate-500/10',
  processing: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  indexed: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  failed: 'bg-rose-50 text-rose-700 ring-rose-600/20',
}

export default function DocumentStatusBadge({ status }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${STATUS_STYLES[status] ?? STATUS_STYLES.uploaded}`}
    >
      {DOCUMENT_STATUS_LABELS[status] ?? status}
    </span>
  )
}
