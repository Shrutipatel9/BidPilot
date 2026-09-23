import { useState } from 'react'
import { Clock, Loader2, XCircle } from 'lucide-react'
import { useDispatch } from 'react-redux'
import { useNavigate, useSearchParams } from 'react-router-dom'

import RoleBadge from '../components/RoleBadge'
import AuthCard from '../components/form/AuthCard'
import Button from '../components/form/Button'
import ErrorBanner from '../components/form/ErrorBanner'
import TextInput from '../components/form/TextInput'
import { setCredentials } from '../features/auth/authSlice'
import { useAcceptInvitationMutation, usePreviewInvitationQuery } from '../features/org/orgApi'

export default function AcceptInvitationPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const { data: preview, isLoading: previewLoading, error: previewError } = usePreviewInvitationQuery(token, {
    skip: !token,
  })
  const [password, setPassword] = useState('')
  const [acceptInvitation, { isLoading: accepting, error: acceptError }] = useAcceptInvitationMutation()
  const dispatch = useDispatch()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    const result = await acceptInvitation({ token, password: preview.requires_password ? password : undefined })
    if (result.data) {
      dispatch(setCredentials(result.data))
      navigate('/')
    }
  }

  if (!token) {
    return (
      <AuthCard title="Accept invitation">
        <p className="text-sm text-slate-500">This link is missing an invitation token.</p>
      </AuthCard>
    )
  }

  if (previewLoading) {
    return (
      <AuthCard title="Accept invitation">
        <div className="flex flex-col items-center gap-3 py-4 text-center">
          <Loader2 className="size-8 animate-spin text-brand-600" aria-hidden="true" />
          <p className="text-sm text-slate-500">Loading your invitation…</p>
        </div>
      </AuthCard>
    )
  }

  if (previewError || !preview) {
    return (
      <AuthCard title="Accept invitation">
        <div className="flex flex-col items-center gap-3 py-4 text-center">
          <XCircle className="size-10 text-rose-500" aria-hidden="true" />
          <p className="text-sm text-slate-600">This invitation link is invalid or has expired.</p>
        </div>
      </AuthCard>
    )
  }

  if (preview.expired) {
    return (
      <AuthCard title="Accept invitation">
        <div className="flex flex-col items-center gap-3 py-4 text-center">
          <Clock className="size-10 text-amber-500" aria-hidden="true" />
          <p className="text-sm text-slate-600">This invitation has expired. Ask an admin to send a new one.</p>
        </div>
      </AuthCard>
    )
  }

  return (
    <AuthCard title={`Join ${preview.org_name}`}>
      <p className="text-sm leading-relaxed text-slate-500">
        You've been invited to join <span className="font-medium text-slate-900">{preview.org_name}</span> as{' '}
        <RoleBadge role={preview.role} />
      </p>
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        {preview.requires_password && (
          <TextInput
            label="Choose a password"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            placeholder="At least 8 characters"
          />
        )}
        <ErrorBanner error={acceptError} />
        <Button type="submit" loading={accepting} className="w-full">
          {accepting ? 'Joining…' : 'Accept invitation'}
        </Button>
      </form>
    </AuthCard>
  )
}
