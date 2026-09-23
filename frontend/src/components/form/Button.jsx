import { Loader2 } from 'lucide-react'

const VARIANTS = {
  primary:
    'bg-brand-600 text-white shadow-sm shadow-brand-600/20 hover:bg-brand-700 focus-visible:ring-brand-500/40',
  secondary:
    'bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 focus-visible:ring-slate-400/40',
  ghost: 'bg-transparent text-slate-600 hover:bg-slate-100 focus-visible:ring-slate-400/40',
}

// `as` lets this render as a different element (e.g. React Router's `Link`) while keeping one
// visual definition for every button-shaped control in the app — a plain <a> or <Link> styled
// ad hoc elsewhere would drift from this the moment either one changes.
export default function Button({
  as: Component = 'button',
  children,
  disabled,
  loading,
  variant = 'primary',
  className = '',
  ...rest
}) {
  const isButtonElement = Component === 'button'

  return (
    <Component
      {...rest}
      {...(isButtonElement ? { disabled: disabled || loading, type: rest.type ?? 'button' } : {})}
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors duration-150 focus-visible:outline-none focus-visible:ring-4 disabled:cursor-not-allowed disabled:opacity-50 ${VARIANTS[variant]} ${className}`}
    >
      {loading && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
      {children}
    </Component>
  )
}
