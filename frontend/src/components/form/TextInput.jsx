export default function TextInput({ label, labelExtra, hint, ...inputProps }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">{label}</span>
        {labelExtra}
      </span>
      <input
        {...inputProps}
        className="rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 transition-shadow duration-150 focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15 disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500"
      />
      {hint && <span className="text-xs text-slate-500">{hint}</span>}
    </label>
  )
}
