import { useParams } from 'react-router-dom'
import { useSelector } from 'react-redux'

import ProjectStatusBadge from '../components/ProjectStatusBadge'
import { selectCurrentOrgId } from '../features/auth/authSlice'
import { useGetProjectQuery } from '../features/project/projectApi'

export default function ProjectDetailPage() {
  const { projectId } = useParams()
  const orgId = useSelector(selectCurrentOrgId)
  const { data: project, isLoading } = useGetProjectQuery({ orgId, projectId }, { skip: !orgId })

  if (isLoading || !project) {
    return <p className="text-sm text-slate-400">Loading…</p>
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">{project.name}</h1>
          <p className="mt-1 text-sm text-slate-500">
            {project.buyer || 'No buyer specified'}
            {project.due_date && ` · Due ${project.due_date}`}
          </p>
        </div>
        <ProjectStatusBadge status={project.status} />
      </div>

      <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
        Question parsing and drafting land in the next sub-phases.
      </div>
    </div>
  )
}
