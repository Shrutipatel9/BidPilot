import { FolderKanban } from 'lucide-react'
import { useSelector } from 'react-redux'
import { Link } from 'react-router-dom'

import ProjectStatusBadge from '../components/ProjectStatusBadge'
import Button from '../components/form/Button'
import { selectCurrentOrgId } from '../features/auth/authSlice'
import { useListProjectsQuery } from '../features/project/projectApi'

export default function ProjectListPage() {
  const orgId = useSelector(selectCurrentOrgId)
  const { data: projects = [], isLoading } = useListProjectsQuery(orgId, { skip: !orgId })

  if (!orgId) {
    return <p className="text-sm text-slate-500">Create or select an organization first.</p>
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Projects</h1>
          <p className="mt-1 text-sm text-slate-500">Questionnaires and RFPs your team is working on.</p>
        </div>
        <Button as={Link} to="/projects/new">
          New project
        </Button>
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-400">Loading…</p>
      ) : projects.length === 0 ? (
        <div className="flex min-h-[40vh] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white">
          <div className="flex max-w-sm flex-col items-center text-center">
            <span className="mb-5 flex size-14 items-center justify-center rounded-2xl bg-brand-50">
              <FolderKanban className="size-7 text-brand-600" aria-hidden="true" />
            </span>
            <h2 className="text-base font-semibold text-slate-900">No projects yet</h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-500">
              Upload a questionnaire to get started with AI-drafted answers.
            </p>
            <Button as={Link} to="/projects/new" className="mt-6">
              New project
            </Button>
          </div>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <ul className="divide-y divide-slate-100">
            {projects.map((project) => (
              <li key={project.id}>
                <Link
                  to={`/projects/${project.id}`}
                  className="flex items-center justify-between gap-4 px-5 py-4 hover:bg-slate-50"
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-slate-900">{project.name}</p>
                    <p className="truncate text-xs text-slate-500">
                      {project.buyer || 'No buyer specified'}
                      {project.due_date && ` · Due ${project.due_date}`}
                    </p>
                  </div>
                  <ProjectStatusBadge status={project.status} />
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
