import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'

import Button from '../components/form/Button'
import ErrorBanner from '../components/form/ErrorBanner'
import FileInput from '../components/form/FileInput'
import TextInput from '../components/form/TextInput'
import { selectCurrentOrgId } from '../features/auth/authSlice'
import { useCreateProjectMutation } from '../features/project/projectApi'

export default function NewProjectPage() {
  const orgId = useSelector(selectCurrentOrgId)
  const [name, setName] = useState('')
  const [buyer, setBuyer] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [file, setFile] = useState(null)
  const [createProject, { isLoading, error }] = useCreateProjectMutation()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    const result = await createProject({ orgId, name, buyer, dueDate, file })
    if (result.data) {
      navigate(`/projects/${result.data.id}`)
    }
  }

  return (
    <div className="max-w-xl">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">New project</h1>
        <p className="mt-1 text-sm text-slate-500">Upload a questionnaire to start drafting answers.</p>
      </div>

      <form
        className="flex flex-col gap-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
        onSubmit={handleSubmit}
      >
        <TextInput label="Project name" required value={name} onChange={(e) => setName(e.target.value)} />
        <TextInput label="Buyer" value={buyer} onChange={(e) => setBuyer(e.target.value)} />
        <TextInput
          label="Due date"
          type="date"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
        />
        <FileInput
          label="Questionnaire file"
          accept=".xlsx,.docx,.pdf"
          value={file}
          onChange={setFile}
        />
        <ErrorBanner error={error} />
        <Button type="submit" loading={isLoading} disabled={!file} className="self-start">
          {isLoading ? 'Uploading…' : 'Create project'}
        </Button>
      </form>
    </div>
  )
}
