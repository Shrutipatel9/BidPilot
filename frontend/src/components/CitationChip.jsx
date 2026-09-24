import { useState } from 'react'
import { FileText } from 'lucide-react'

export default function CitationChip({ citation }) {
  const [expanded, setExpanded] = useState(false)
  const location = citation.page ? `p. ${citation.page}` : citation.section

  return (
    <div>
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
      >
        <FileText className="size-3" aria-hidden="true" />
        {citation.document_title}
        {location && <span className="text-slate-400">· {location}</span>}
      </button>
      {expanded && (
        <div className="mt-1.5 max-w-sm rounded-lg border border-slate-200 bg-white p-2.5 text-xs leading-relaxed text-slate-600 shadow-sm">
          {citation.snippet}
        </div>
      )}
    </div>
  )
}
