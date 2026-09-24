import { useEffect } from 'react'
import {
  BarChart3,
  Building2,
  FolderKanban,
  LayoutDashboard,
  Library,
  LogOut,
  Settings,
  Sparkles,
} from 'lucide-react'
import { useDispatch, useSelector } from 'react-redux'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import Logo from '../Logo'
import { logout, selectCurrentOrgId, selectCurrentUser, setCurrentOrgId } from '../../features/auth/authSlice'
import { useListMyOrganizationsQuery } from '../../features/org/orgApi'
import { initialsFor } from '../../lib/initials'

const NAV_ITEMS = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard, available: true },
  { label: 'Projects', to: '/projects', icon: FolderKanban, available: true },
  { label: 'Knowledge Base', to: '/knowledge-base', icon: Sparkles, available: true },
  { label: 'Answer Library', to: '/answer-library', icon: Library, available: false },
  { label: 'Analytics', to: '/analytics', icon: BarChart3, available: false },
  { label: 'Settings', to: '/settings/members', icon: Settings, available: true },
]

export default function AppShell() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const currentUser = useSelector(selectCurrentUser)
  const currentOrgId = useSelector(selectCurrentOrgId)
  const { data: organizations = [] } = useListMyOrganizationsQuery()

  useEffect(() => {
    if (organizations.length === 0) return
    // Also re-validates currentOrgId against the actual list, not just "is it set" — a
    // persisted org id that no longer belongs to this user (stale session, removed from the
    // org, etc.) must not silently keep pointing at an org they can't access.
    const isCurrentOrgValid = organizations.some((org) => org.id === currentOrgId)
    if (!isCurrentOrgValid) {
      dispatch(setCurrentOrgId(organizations[0].id))
    }
  }, [currentOrgId, organizations, dispatch])

  function handleLogout() {
    dispatch(logout())
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-white">
        <div className="flex h-16 items-center border-b border-slate-100 px-5">
          <Logo />
        </div>

        <div className="border-b border-slate-100 p-3">
          <label className="relative block">
            <Building2
              className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-400"
              aria-hidden="true"
            />
            <select
              className="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-8 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 focus:border-brand-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-brand-500/15"
              value={currentOrgId ?? ''}
              onChange={(e) => dispatch(setCurrentOrgId(e.target.value))}
            >
              {organizations.length === 0 && <option value="">No organizations yet</option>}
              {organizations.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <nav className="flex flex-1 flex-col gap-0.5 p-3">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon
            if (!item.available) {
              return (
                <span
                  key={item.to}
                  title="Coming in a later phase"
                  className="flex cursor-not-allowed items-center justify-between rounded-lg px-3 py-2 text-sm text-slate-400"
                >
                  <span className="flex items-center gap-2.5">
                    <Icon className="size-4" aria-hidden="true" />
                    {item.label}
                  </span>
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-slate-400">
                    Soon
                  </span>
                </span>
              )
            }
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-brand-50 text-brand-700'
                      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                  }`
                }
              >
                <Icon className="size-4" aria-hidden="true" />
                {item.label}
              </NavLink>
            )
          })}
        </nav>

        <div className="flex items-center gap-3 border-t border-slate-100 p-3">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700">
            {initialsFor(currentUser)}
          </span>
          <span className="min-w-0 flex-1 truncate text-sm text-slate-700">{currentUser?.email}</span>
          <button
            type="button"
            onClick={handleLogout}
            title="Log out"
            className="flex size-8 shrink-0 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700"
          >
            <LogOut className="size-4" aria-hidden="true" />
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto p-8">
        <Outlet />
      </main>
    </div>
  )
}
