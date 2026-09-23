import { FolderKanban, UserPlus } from 'lucide-react'
import { useSelector } from 'react-redux'
import { Link } from 'react-router-dom'

import Button from '../components/form/Button'
import { selectCurrentOrgId } from '../features/auth/authSlice'
import { useListMyOrganizationsQuery } from '../features/org/orgApi'

export default function DashboardPage() {
  const currentOrgId = useSelector(selectCurrentOrgId)
  const { data: organizations = [], isLoading } = useListMyOrganizationsQuery()

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-slate-400">Loading…</div>
    )
  }

  if (organizations.length === 0) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center">
        <div className="flex max-w-md flex-col items-center text-center">
          <span className="mb-5 flex size-14 items-center justify-center rounded-2xl bg-brand-50">
            <FolderKanban className="size-7 text-brand-600" aria-hidden="true" />
          </span>
          <h1 className="text-xl font-semibold text-slate-900">Welcome to BidPilot</h1>
          <p className="mt-2 text-sm leading-relaxed text-slate-500">
            Create an organization to start uploading questionnaires and knowledge base documents
            for your team.
          </p>
          <Button as={Link} to="/create-organization" className="mt-6">
            Create your organization
          </Button>
        </div>
      </div>
    )
  }

  const currentOrg = organizations.find((o) => o.id === currentOrgId) ?? organizations[0]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">{currentOrg?.name}</h1>
        <p className="mt-1 text-sm text-slate-500">Here's what's happening with your workspace.</p>
      </div>

      <div className="flex min-h-[50vh] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white">
        <div className="flex max-w-sm flex-col items-center text-center">
          <span className="mb-5 flex size-14 items-center justify-center rounded-2xl bg-brand-50">
            <FolderKanban className="size-7 text-brand-600" aria-hidden="true" />
          </span>
          <h2 className="text-base font-semibold text-slate-900">No projects yet</h2>
          <p className="mt-2 text-sm leading-relaxed text-slate-500">
            Questionnaire drafting lands in Phase 1. In the meantime, get your workspace ready by
            inviting your team.
          </p>
          <Button as={Link} to="/settings/members" variant="secondary" className="mt-6">
            <UserPlus className="size-4" aria-hidden="true" />
            Invite a teammate
          </Button>
        </div>
      </div>
    </div>
  )
}
