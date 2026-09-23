import { ShieldCheck } from 'lucide-react'

import Logo from '../Logo'

export default function AuthCard({ title, subtitle, children }) {
  return (
    <div className="flex min-h-screen bg-white">
      <div className="relative hidden w-1/2 flex-col justify-between overflow-hidden bg-gradient-to-br from-brand-700 via-brand-600 to-brand-900 p-12 text-white lg:flex">
        <div
          className="pointer-events-none absolute inset-0 opacity-[0.15]"
          style={{
            backgroundImage:
              'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.6) 1px, transparent 0)',
            backgroundSize: '28px 28px',
          }}
          aria-hidden="true"
        />

        <div className="relative z-10">
          <Logo light />
        </div>

        <div className="relative z-10 max-w-md">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-brand-100 ring-1 ring-white/20">
            <ShieldCheck className="size-3.5" aria-hidden="true" />
            Cited answers, reviewed before they ship
          </div>
          <h2 className="text-3xl font-semibold leading-tight text-balance">
            Answer RFPs and security questionnaires in minutes, not weeks.
          </h2>
          <p className="mt-4 text-sm leading-relaxed text-brand-100/90">
            BidPilot drafts grounded, cited answers from your knowledge base and routes anything
            uncertain to your team — so nothing goes out the door unreviewed.
          </p>
        </div>

        <div className="relative z-10 text-xs text-brand-200/70">
          © {new Date().getFullYear()} BidPilot
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center px-6 py-12 sm:px-10">
        <div className="w-full max-w-sm">
          <div className="mb-8 lg:hidden">
            <Logo />
          </div>

          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">{title}</h1>
          {subtitle && <p className="mt-1.5 text-sm text-slate-500">{subtitle}</p>}

          <div className="mt-8 flex flex-col gap-5">{children}</div>
        </div>
      </div>
    </div>
  )
}
