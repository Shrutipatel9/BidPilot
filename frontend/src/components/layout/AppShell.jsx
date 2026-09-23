import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { NavLink, Outlet } from 'react-router-dom'

import { selectCurrentOrgId, selectCurrentUser, setCurrentOrgId } from '../../features/auth/authSlice'
import { useListMyOrganizationsQuery } from '../../features/org/orgApi'

const NAV_ITEMS = [
  { label: 'Dashboard', to: '/', available: true },
  { label: 'Projects', to: '/projects', available: false },
  { label: 'Knowledge Base', to: '/knowledge-base', available: false },
  { label: 'Answer Library', to: '/answer-library', available: false },
  { label: 'Analytics', to: '/analytics', available: false },
  { label: 'Settings', to: '/settings/members', available: true },
]

export default function AppShell() {
  const dispatch = useDispatch()
  const currentUser = useSelector(selectCurrentUser)
  const currentOrgId = useSelector(selectCurrentOrgId)
  const { data: organizations = [] } = useListMyOrganizationsQuery()

  useEffect(() => {
    if (!currentOrgId && organizations.length > 0) {
      dispatch(setCurrentOrgId(organizations[0].id))
    }
  }, [currentOrgId, organizations, dispatch])

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 shrink-0 border-r border-gray-200 bg-gray-50 p-4 flex flex-col gap-6">
        <div className="text-lg font-semibold">BidPilot</div>

        <select
          className="w-full rounded border border-gray-300 bg-white px-2 py-1.5 text-sm"
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

        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) =>
            item.available ? (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `rounded px-3 py-2 text-sm ${isActive ? 'bg-purple-100 text-purple-900 font-medium' : 'text-gray-700 hover:bg-gray-100'}`
                }
              >
                {item.label}
              </NavLink>
            ) : (
              <span
                key={item.to}
                title="Coming in a later phase"
                className="cursor-not-allowed rounded px-3 py-2 text-sm text-gray-400"
              >
                {item.label}
              </span>
            ),
          )}
        </nav>

        <div className="mt-auto text-xs text-gray-500">{currentUser?.email}</div>
      </aside>

      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  )
}
