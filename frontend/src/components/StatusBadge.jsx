import { ANSWER_STATUS_LABELS } from '../lib/answerStatus'

const STATUS_STYLES = {
  not_started: 'bg-slate-100 text-slate-600 ring-slate-500/10',
  ai_drafted: 'bg-sky-50 text-sky-700 ring-sky-600/20',
  needs_review: 'bg-rose-50 text-rose-700 ring-rose-600/20',
  in_review: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  approved: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  rejected: 'bg-slate-200 text-slate-500 ring-slate-500/10 line-through',
}

export default function StatusBadge({ status }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${STATUS_STYLES[status] ?? STATUS_STYLES.not_started}`}
    >
      {ANSWER_STATUS_LABELS[status] ?? status}
    </span>
  )
}
