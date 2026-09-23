import { PROJECT_STATUS_LABELS } from '../lib/projectStatus'

const STATUS_STYLES = {
  uploaded: 'bg-slate-100 text-slate-600 ring-slate-500/10',
  questions_confirmed: 'bg-sky-50 text-sky-700 ring-sky-600/20',
  drafting: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  drafted: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
}

export default function ProjectStatusBadge({ status }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${STATUS_STYLES[status] ?? STATUS_STYLES.uploaded}`}
    >
      {PROJECT_STATUS_LABELS[status] ?? status}
    </span>
  )
}
