import { useSelector } from 'react-redux'
import { Link } from 'react-router-dom'

import { selectCurrentOrgId } from '../features/auth/authSlice'
import { useListMyOrganizationsQuery } from '../features/org/orgApi'

export default function DashboardPage() {
  const currentOrgId = useSelector(selectCurrentOrgId)
  const { data: organizations = [], isLoading } = useListMyOrganizationsQuery()

  if (isLoading) {
    return <p className="text-sm text-gray-600">Loading…</p>
  }

  if (organizations.length === 0) {
    return (
      <div className="max-w-md">
        <h1 className="mb-2 text-xl font-semibold">Welcome to BidPilot</h1>
        <p className="mb-4 text-sm text-gray-600">
          Create an organization to start uploading questionnaires and knowledge base documents.
        </p>
        <Link className="text-purple-600 underline" to="/create-organization">
          Create your organization
        </Link>
      </div>
    )
  }

  const currentOrg = organizations.find((o) => o.id === currentOrgId) ?? organizations[0]

  return (
    <div>
      <h1 className="mb-2 text-xl font-semibold">{currentOrg?.name}</h1>
      <p className="text-sm text-gray-600">
        No projects yet. Questionnaire drafting lands in Phase 1 — for now, try{' '}
        <Link className="text-purple-600 underline" to="/settings/members">
          inviting a teammate
        </Link>
        .
      </p>
    </div>
  )
}
