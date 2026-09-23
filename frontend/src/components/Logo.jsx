import { FileCheck2 } from 'lucide-react'

export default function Logo({ light = false }) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`flex size-7 items-center justify-center rounded-md ${light ? 'bg-white/15' : 'bg-brand-600'}`}
      >
        <FileCheck2 className={`size-4 ${light ? 'text-white' : 'text-white'}`} aria-hidden="true" />
      </span>
      <span className={`text-base font-semibold tracking-tight ${light ? 'text-white' : 'text-slate-900'}`}>
        BidPilot
      </span>
    </div>
  )
}
