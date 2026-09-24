import { useMemo, useState } from 'react'
import { Check, Download, FileSearch, Loader2, Sparkles, X } from 'lucide-react'
import { useSelector } from 'react-redux'
import { useParams } from 'react-router-dom'

import CitationChip from '../components/CitationChip'
import ConfidenceBadge from '../components/ConfidenceBadge'
import ProjectStatusBadge from '../components/ProjectStatusBadge'
import StatusBadge from '../components/StatusBadge'
import Button from '../components/form/Button'
import Callout from '../components/form/Callout'
import ErrorBanner from '../components/form/ErrorBanner'
import { selectCurrentOrgId, selectCurrentUser } from '../features/auth/authSlice'
import { downloadProjectExport } from '../features/project/exportDownload'
import { useListMembersQuery } from '../features/org/orgApi'
import {
  useApproveAnswerMutation,
  useConfirmQuestionsMutation,
  useGetProjectQuery,
  useListAnswersQuery,
  useListQuestionsQuery,
  useParseProjectMutation,
  useRejectAnswerMutation,
  useStartDraftingMutation,
  useUpdateAnswerMutation,
  useUpdateQuestionMutation,
} from '../features/project/projectApi'
import { QUESTION_TYPE_LABELS } from '../lib/questionTypes'

const _EDITOR_ROLES = new Set(['owner', 'admin', 'responder'])
const _REVIEW_ROLES = new Set(['owner', 'admin', 'responder', 'reviewer'])

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

function ReviewDetailPane({ orgId, projectId, question, answer, myRole }) {
  const [text, setText] = useState(answer.text)
  const [showRejectForm, setShowRejectForm] = useState(false)
  const [reason, setReason] = useState('')

  const [updateAnswer, { isLoading: saving, error: saveError }] = useUpdateAnswerMutation()
  const [approveAnswer, { isLoading: approving, error: approveError }] = useApproveAnswerMutation()
  const [rejectAnswer, { isLoading: rejecting, error: rejectError }] = useRejectAnswerMutation()

  // Reset local edit state when the selected question changes (not on every re-render).
  const [lastAnswerId, setLastAnswerId] = useState(answer.id)
  if (answer.id !== lastAnswerId) {
    setLastAnswerId(answer.id)
    setText(answer.text)
    setShowRejectForm(false)
    setReason('')
  }

  const canEdit = _EDITOR_ROLES.has(myRole)
  const canReview = _REVIEW_ROLES.has(myRole)
  const dirty = text !== answer.text
  const isInsufficient = answer.text === 'Insufficient information'

  return (
    <div className="flex h-full flex-col">
      <div className="mb-4 flex items-start justify-between gap-4">
        <h3 className="text-sm font-medium leading-relaxed text-slate-900">{question.text}</h3>
        <StatusBadge status={answer.status} />
      </div>
      <div className="mb-3">
        <ConfidenceBadge confidence={answer.confidence} />
        {answer.choice && (
          <span className="ml-2 text-xs font-medium text-slate-500">Selected: {answer.choice}</span>
        )}
      </div>

      {isInsufficient && (
        <div className="mb-3">
          <Callout variant="warning">
            The AI found no evidence in the knowledge base to answer this question. Write the answer manually
            or upload a relevant document and re-draft.
          </Callout>
        </div>
      )}

      {answer.citations.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {answer.citations.map((citation) => (
            <CitationChip key={citation.chunk_id} citation={citation} />
          ))}
        </div>
      )}

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        readOnly={!canEdit}
        rows={8}
        className="w-full flex-1 resize-none rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15 disabled:bg-slate-50"
      />

      <ErrorBanner error={saveError || approveError || rejectError} />

      {showRejectForm ? (
        <div className="mt-3 flex flex-col gap-2">
          <input
            autoFocus
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Why is this answer being rejected?"
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15"
          />
          <div className="flex gap-2">
            <Button
              variant="secondary"
              onClick={() =>
                rejectAnswer({ orgId, projectId, answerId: answer.id, reason }).then((r) => {
                  if (r.data) setShowRejectForm(false)
                })
              }
              loading={rejecting}
              disabled={!reason.trim()}
            >
              Confirm reject
            </Button>
            <Button variant="ghost" onClick={() => setShowRejectForm(false)}>
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        <div className="mt-3 flex gap-2">
          {canEdit && (
            <Button
              variant="secondary"
              onClick={() => updateAnswer({ orgId, projectId, answerId: answer.id, text })}
              loading={saving}
              disabled={!dirty}
            >
              Save
            </Button>
          )}
          {canReview && (
            <>
              <Button
                onClick={() => approveAnswer({ orgId, projectId, answerId: answer.id })}
                loading={approving}
              >
                <Check className="size-4" aria-hidden="true" />
                Approve
              </Button>
              <Button variant="ghost" onClick={() => setShowRejectForm(true)}>
                <X className="size-4" aria-hidden="true" />
                Reject
              </Button>
            </>
          )}
        </div>
      )}
    </div>
  )
}

function ExportSection({ orgId, projectId, project, answers }) {
  const accessToken = useSelector((state) => state.auth.accessToken)
  const [format, setFormat] = useState(project.source_file_ext === 'pdf' ? 'csv' : project.source_file_ext)
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState(null)

  const unapprovedCount = answers.filter((a) => a.status !== 'approved').length
  const formatOptions = project.source_file_ext === 'pdf' ? ['csv'] : [project.source_file_ext, 'csv']

  const handleExport = async () => {
    setDownloading(true)
    setError(null)
    try {
      await downloadProjectExport({ orgId, projectId, format, accessToken })
    } catch {
      setError('Export failed. Please try again.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="mt-6 rounded-xl border border-slate-200 bg-white p-5">
      <h3 className="text-sm font-semibold text-slate-900">Export</h3>
      {unapprovedCount > 0 && (
        <div className="mt-3">
          <Callout variant="warning">
            {unapprovedCount} answer{unapprovedCount === 1 ? ' is' : 's are'} not yet approved. They'll still be
            included using their current draft text.
          </Callout>
        </div>
      )}
      {error && <p className="mt-3 text-sm text-rose-600">{error}</p>}
      <div className="mt-4 flex items-center gap-3">
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15"
        >
          {formatOptions.map((opt) => (
            <option key={opt} value={opt}>
              {opt.toUpperCase()}
            </option>
          ))}
        </select>
        <Button onClick={handleExport} loading={downloading}>
          <Download className="size-4" aria-hidden="true" />
          {downloading ? 'Exporting…' : 'Export'}
        </Button>
      </div>
    </div>
  )
}

function DraftingSection({ orgId, projectId, project, questions, myRole }) {
  const questionCount = questions.length
  const [startDrafting, { isLoading: starting, error: startError }] = useStartDraftingMutation()
  const isDrafting = project.status === 'drafting'
  const { data: answers = [] } = useListAnswersQuery(
    { orgId, projectId },
    { pollingInterval: isDrafting ? 2000 : 0 },
  )
  const [selectedQuestionId, setSelectedQuestionId] = useState(null)

  const answersByQuestionId = useMemo(() => {
    const map = new Map()
    for (const answer of answers) map.set(answer.question_id, answer)
    return map
  }, [answers])

  if (project.status === 'questions_confirmed') {
    return (
      <div className="flex min-h-[40vh] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white">
        <div className="flex max-w-sm flex-col items-center text-center">
          <span className="mb-5 flex size-14 items-center justify-center rounded-2xl bg-brand-50">
            <Sparkles className="size-7 text-brand-600" aria-hidden="true" />
          </span>
          <h2 className="text-base font-semibold text-slate-900">Ready to draft</h2>
          <p className="mt-2 text-sm leading-relaxed text-slate-500">
            {questionCount} question{questionCount === 1 ? '' : 's'} confirmed. BidPilot will draft an answer for
            each one.
          </p>
          <ErrorBanner error={startError} />
          <Button onClick={() => startDrafting({ orgId, projectId })} loading={starting} className="mt-6">
            {starting ? 'Starting…' : 'Start drafting'}
          </Button>
        </div>
      </div>
    )
  }

  const draftedCount = answers.filter((a) => a.status !== 'not_started').length

  if (isDrafting) {
    return (
      <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-300 bg-white">
        <Loader2 className="size-8 animate-spin text-brand-600" aria-hidden="true" />
        <p className="text-sm text-slate-600">
          Drafting answers… {draftedCount} / {questionCount}
        </p>
      </div>
    )
  }

  const selectedQuestion =
    questions.find((q) => q.id === selectedQuestionId) ?? questions[0] ?? null
  const selectedAnswer = selectedQuestion ? answersByQuestionId.get(selectedQuestion.id) : null

  return (
    <div>
      <div className="grid grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)] gap-4">
        <div className="max-h-[70vh] overflow-y-auto rounded-xl border border-slate-200 bg-white">
          {questions.map((question) => {
            const answer = answersByQuestionId.get(question.id)
            const isSelected = selectedQuestion?.id === question.id
            return (
              <button
                key={question.id}
                onClick={() => setSelectedQuestionId(question.id)}
                className={`flex w-full flex-col gap-1.5 border-b border-slate-100 px-4 py-3 text-left last:border-0 hover:bg-slate-50 ${isSelected ? 'bg-brand-50/60' : ''}`}
              >
                <p className="line-clamp-2 text-sm text-slate-800">{question.text}</p>
                {answer && <StatusBadge status={answer.status} />}
              </button>
            )
          })}
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          {selectedQuestion && selectedAnswer ? (
            <ReviewDetailPane
              key={selectedAnswer.id}
              orgId={orgId}
              projectId={projectId}
              question={selectedQuestion}
              answer={selectedAnswer}
              myRole={myRole}
            />
          ) : (
            <p className="text-sm text-slate-400">Select a question to review its answer.</p>
          )}
        </div>
      </div>
      <ExportSection orgId={orgId} projectId={projectId} project={project} answers={answers} />
    </div>
  )
}

export default function ProjectDetailPage() {
  const { projectId } = useParams()
  const orgId = useSelector(selectCurrentOrgId)
  // Polls while a background drafting run may be in progress, since RTK Query has no way to
  // push us an update when the BackgroundTasks job on the server flips the project's status.
  const [pollProjectStatus, setPollProjectStatus] = useState(false)
  const { data: project, isLoading: projectLoading } = useGetProjectQuery(
    { orgId, projectId },
    { skip: !orgId, pollingInterval: pollProjectStatus ? 2000 : 0 },
  )
  const [lastSeenStatus, setLastSeenStatus] = useState()
  if (project?.status !== lastSeenStatus) {
    setLastSeenStatus(project?.status)
    setPollProjectStatus(project?.status === 'drafting')
  }
  const { data: questions = [], isLoading: questionsLoading } = useListQuestionsQuery(
    { orgId, projectId },
    { skip: !orgId },
  )
  const [parseProject, { isLoading: parsing, error: parseError }] = useParseProjectMutation()
  const [confirmQuestions, { isLoading: confirming, error: confirmError }] = useConfirmQuestionsMutation()
  const [confirmed, setConfirmed] = useState(false)

  const currentUser = useSelector(selectCurrentUser)
  const { data: members = [] } = useListMembersQuery(orgId, { skip: !orgId })
  const myRole = members.find((m) => m.email === currentUser?.email)?.role

  if (projectLoading || !project) {
    return <p className="text-sm text-slate-400">Loading…</p>
  }

  const isUnparsed = project.status === 'uploaded' && questions.length === 0
  const isMappingReview = project.status === 'uploaded' && questions.length > 0
  const isPastMapping = project.status !== 'uploaded' || confirmed

  return (
    <div className={isPastMapping && project.status !== 'questions_confirmed' ? 'max-w-6xl' : 'max-w-4xl'}>
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
        <DraftingSection orgId={orgId} projectId={projectId} project={project} questions={questions} myRole={myRole} />
      )}
    </div>
  )
}
