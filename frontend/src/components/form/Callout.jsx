import { AlertTriangle, CheckCircle2, Info } from 'lucide-react'

const VARIANTS = {
  success: { icon: CheckCircle2, classes: 'border-emerald-200 bg-emerald-50 text-emerald-800' },
  info: { icon: Info, classes: 'border-slate-200 bg-slate-50 text-slate-700' },
  warning: { icon: AlertTriangle, classes: 'border-amber-200 bg-amber-50 text-amber-800' },
}

export default function Callout({ variant = 'info', children }) {
  const { icon: Icon, classes } = VARIANTS[variant]

  return (
    <div className={`flex items-start gap-2 rounded-lg border px-3.5 py-2.5 text-sm ${classes}`}>
      <Icon className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
      <div className="leading-relaxed">{children}</div>
    </div>
  )
}
