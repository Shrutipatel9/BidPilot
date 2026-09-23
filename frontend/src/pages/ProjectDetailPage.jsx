import { useState } from 'react'
import { FileSearch } from 'lucide-react'
import { useSelector } from 'react-redux'
import { useParams } from 'react-router-dom'

import ProjectStatusBadge from '../components/ProjectStatusBadge'
import Button from '../components/form/Button'
import ErrorBanner from '../components/form/ErrorBanner'
import { selectCurrentOrgId } from '../features/auth/authSlice'
import {
  useConfirmQuestionsMutation,
  useGetProjectQuery,
  useListQuestionsQuery,
  useParseProjectMutation,
  useUpdateQuestionMutation,
} from '../features/project/projectApi'
import { QUESTION_TYPE_LABELS } from '../lib/questionTypes'

const QUESTION_TYPES = Object.keys(QUESTION_TYPE_LABELS)

function QuestionRow({ orgId, projectId, question }) {
  const [updateQuestion] = useUpdateQuestionMutation()

  return (
    <tr className="border-b border-slate-100 last:border-0">
      <td className="py-2.5 pr-4 align-top">
        <textarea
          defaultValue={question.text}
          rows={2}
          onBlur={(e) => {
            if (e.target.value !== question.text) {
              updateQuestion({ orgId, projectId, questionId: question.id, text: e.target.value })
            }
          }}
          className="w-full resize-none rounded-lg border border-slate-200 px-2.5 py-1.5 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15"
        />
      </td>
      <td className="w-44 py-2.5 align-top">
        <select
          value={question.type}
          onChange={(e) => updateQuestion({ orgId, projectId, questionId: question.id, type: e.target.value })}
          className="w-full rounded-lg border border-slate-200 px-2 py-1.5 text-sm text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15"
        >
          {QUESTION_TYPES.map((type) => (
            <option key={type} value={type}>
              {QUESTION_TYPE_LABELS[type]}
            </option>
          ))}
        </select>
      </td>
      <td className="w-40 py-2.5 align-top text-sm text-slate-500">{question.section || '—'}</td>
    </tr>
  )
}

export default function ProjectDetailPage() {
  const { projectId } = useParams()
  const orgId = useSelector(selectCurrentOrgId)
  const { data: project, isLoading: projectLoading } = useGetProjectQuery({ orgId, projectId }, { skip: !orgId })
  const { data: questions = [], isLoading: questionsLoading } = useListQuestionsQuery(
    { orgId, projectId },
    { skip: !orgId },
  )
  const [parseProject, { isLoading: parsing, error: parseError }] = useParseProjectMutation()
  const [confirmQuestions, { isLoading: confirming, error: confirmError }] = useConfirmQuestionsMutation()
  const [confirmed, setConfirmed] = useState(false)

  if (projectLoading || !project) {
    return <p className="text-sm text-slate-400">Loading…</p>
  }

  const isUnparsed = project.status === 'uploaded' && questions.length === 0
  const isMappingReview = project.status === 'uploaded' && questions.length > 0
  const isPastMapping = project.status !== 'uploaded' || confirmed

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

      {isUnparsed && (
        <div className="flex min-h-[40vh] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white">
          <div className="flex max-w-sm flex-col items-center text-center">
            <span className="mb-5 flex size-14 items-center justify-center rounded-2xl bg-brand-50">
              <FileSearch className="size-7 text-brand-600" aria-hidden="true" />
            </span>
            <h2 className="text-base font-semibold text-slate-900">Ready to parse</h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-500">
              We'll scan the uploaded file and detect its questions for you to review.
            </p>
            <ErrorBanner error={parseError} />
            <Button
              onClick={() => parseProject({ orgId, projectId })}
              loading={parsing || questionsLoading}
              className="mt-6"
            >
              {parsing ? 'Parsing…' : 'Parse questionnaire'}
            </Button>
          </div>
        </div>
      )}

      {isMappingReview && (
        <div>
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm text-slate-600">
              Detected <strong>{questions.length}</strong> question{questions.length === 1 ? '' : 's'}. Review and
              correct before drafting starts.
            </p>
            <Button
              onClick={async () => {
                const result = await confirmQuestions({ orgId, projectId })
                if (result.data) setConfirmed(true)
              }}
              loading={confirming}
            >
              {confirming ? 'Confirming…' : 'Confirm and continue'}
            </Button>
          </div>
          <ErrorBanner error={confirmError} />
          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-slate-200 text-xs font-medium uppercase tracking-wide text-slate-500">
                  <th className="pb-2 pr-4">Question</th>
                  <th className="w-44 pb-2">Type</th>
                  <th className="w-40 pb-2">Section</th>
                </tr>
              </thead>
              <tbody>
                {questions.map((question) => (
                  <QuestionRow key={question.id} orgId={orgId} projectId={projectId} question={question} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {isPastMapping && (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-sm text-slate-500">
          {questions.length} question{questions.length === 1 ? '' : 's'} confirmed. Drafting lands in the next
          sub-phase.
        </div>
      )}
    </div>
  )
}
