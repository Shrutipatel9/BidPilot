import { ROLE_LABELS } from '../lib/roles'

const ROLE_STYLES = {
  owner: 'bg-brand-50 text-brand-700 ring-brand-600/20',
  admin: 'bg-violet-50 text-violet-700 ring-violet-600/20',
  knowledge_manager: 'bg-sky-50 text-sky-700 ring-sky-600/20',
  responder: 'bg-slate-100 text-slate-600 ring-slate-500/10',
  reviewer: 'bg-slate-100 text-slate-600 ring-slate-500/10',
  viewer: 'bg-slate-100 text-slate-600 ring-slate-500/10',
}

export default function RoleBadge({ role }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${ROLE_STYLES[role] ?? ROLE_STYLES.viewer}`}
    >
      {ROLE_LABELS[role] ?? role}
    </span>
  )
}
