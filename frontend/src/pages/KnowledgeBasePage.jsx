import { useState } from 'react'
import { BookOpen, Plus, Trash2 } from 'lucide-react'
import { useSelector } from 'react-redux'

import DocumentStatusBadge from '../components/DocumentStatusBadge'
import Button from '../components/form/Button'
import ErrorBanner from '../components/form/ErrorBanner'
import FileInput from '../components/form/FileInput'
import TextInput from '../components/form/TextInput'
import { selectCurrentOrgId } from '../features/auth/authSlice'
import {
  useCreateKnowledgeDocumentMutation,
  useDeleteKnowledgeDocumentMutation,
  useListKnowledgeDocumentsQuery,
} from '../features/knowledge/knowledgeApi'

function UploadForm({ orgId, onDone }) {
  const [title, setTitle] = useState('')
  const [tags, setTags] = useState('')
  const [reviewDate, setReviewDate] = useState('')
  const [file, setFile] = useState(null)
  const [createDocument, { isLoading, error }] = useCreateKnowledgeDocumentMutation()

  async function handleSubmit(e) {
    e.preventDefault()
    const tagList = tags
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)
    const result = await createDocument({ orgId, file, title, tags: tagList, reviewDate })
    if (result.data) onDone()
  }

  return (
    <form
      className="mb-6 flex flex-col gap-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
      onSubmit={handleSubmit}
    >
      <TextInput label="Title" required value={title} onChange={(e) => setTitle(e.target.value)} />
      <TextInput
        label="Tags"
        hint="Comma-separated (e.g. Security, Legal)"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
      />
      <TextInput
        label="Review date"
        type="date"
        value={reviewDate}
        onChange={(e) => setReviewDate(e.target.value)}
      />
      <FileInput label="Document file" accept=".pdf,.docx,.xlsx,.txt,.md" value={file} onChange={setFile} />
      <ErrorBanner error={error} />
      <div className="flex gap-2">
        <Button type="submit" loading={isLoading} disabled={!file || !title}>
          {isLoading ? 'Uploading…' : 'Upload'}
        </Button>
        <Button type="button" variant="ghost" onClick={onDone}>
          Cancel
        </Button>
      </div>
    </form>
  )
}

export default function KnowledgeBasePage() {
  const orgId = useSelector(selectCurrentOrgId)
  // Polls while any document is still being ingested — the same "no push channel yet" gap as
  // project drafting status, so it uses the same render-time-derived-state trick (comparing
  // against the last-seen value rather than an effect, to avoid a redundant render pass).
  const [pollDocuments, setPollDocuments] = useState(false)
  const { data: documents = [], isLoading } = useListKnowledgeDocumentsQuery(orgId, {
    skip: !orgId,
    pollingInterval: pollDocuments ? 2000 : 0,
  })
  // "uploaded" is pre-ingestion (not yet picked up by a worker), "processing" is mid-ingestion
  // — both are transient. Polling only on "processing" missed fast ingestion runs entirely: the
  // worker can finish before the next poll fires if the list only starts polling once it
  // observes "processing", which a quick run may never be caught in.
  const hasPendingIngestion = documents.some((d) => d.status === 'uploaded' || d.status === 'processing')
  if (hasPendingIngestion !== pollDocuments) {
    setPollDocuments(hasPendingIngestion)
  }
  const [deleteDocument] = useDeleteKnowledgeDocumentMutation()
  const [showUpload, setShowUpload] = useState(false)

  if (!orgId) {
    return <p className="text-sm text-slate-500">Create or select an organization first.</p>
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Knowledge base</h1>
          <p className="mt-1 text-sm text-slate-500">
            Documents BidPilot grounds AI-drafted answers in, with citations back to the source.
          </p>
        </div>
        {!showUpload && (
          <Button onClick={() => setShowUpload(true)}>
            <Plus className="size-4" aria-hidden="true" />
            Upload document
          </Button>
        )}
      </div>

      {showUpload && <UploadForm orgId={orgId} onDone={() => setShowUpload(false)} />}

      {isLoading ? (
        <p className="text-sm text-slate-400">Loading…</p>
      ) : documents.length === 0 ? (
        <div className="flex min-h-[40vh] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white">
          <div className="flex max-w-sm flex-col items-center text-center">
            <span className="mb-5 flex size-14 items-center justify-center rounded-2xl bg-brand-50">
              <BookOpen className="size-7 text-brand-600" aria-hidden="true" />
            </span>
            <h2 className="text-base font-semibold text-slate-900">No documents yet</h2>
            <p className="mt-2 text-sm leading-relaxed text-slate-500">
              Upload a policy, past questionnaire, or reference doc to start grounding AI drafts in it.
            </p>
            {!showUpload && (
              <Button onClick={() => setShowUpload(true)} className="mt-6">
                Upload document
              </Button>
            )}
          </div>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <ul className="divide-y divide-slate-100">
            {documents.map((doc) => (
              <li key={doc.id} className="flex items-center justify-between gap-4 px-5 py-4">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-slate-900">{doc.title}</p>
                  <p className="truncate text-xs text-slate-500">
                    {doc.tags.length > 0 ? doc.tags.join(', ') : 'No tags'}
                    {doc.review_date && ` · Review by ${doc.review_date}`}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <DocumentStatusBadge status={doc.status} />
                  <button
                    type="button"
                    onClick={() => deleteDocument({ orgId, documentId: doc.id })}
                    className="rounded-lg p-1.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600"
                    aria-label={`Delete ${doc.title}`}
                  >
                    <Trash2 className="size-4" aria-hidden="true" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
