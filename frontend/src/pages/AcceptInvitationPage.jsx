import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { useNavigate, useSearchParams } from 'react-router-dom'

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
        <p className="text-sm text-gray-600">This link is missing an invitation token.</p>
      </AuthCard>
    )
  }

  if (previewLoading) {
    return (
      <AuthCard title="Accept invitation">
        <p className="text-sm text-gray-600">Loading invitation…</p>
      </AuthCard>
    )
  }

  if (previewError || !preview) {
    return (
      <AuthCard title="Accept invitation">
        <p className="text-sm text-red-700">This invitation link is invalid or has expired.</p>
      </AuthCard>
    )
  }

  if (preview.expired) {
    return (
      <AuthCard title="Accept invitation">
        <p className="text-sm text-red-700">This invitation has expired. Ask an admin to send a new one.</p>
      </AuthCard>
    )
  }

  return (
    <AuthCard title={`Join ${preview.org_name}`}>
      <p className="text-sm text-gray-600">
        You've been invited to join <strong>{preview.org_name}</strong> as <strong>{preview.role}</strong>.
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
          />
        )}
        <ErrorBanner error={acceptError} />
        <Button type="submit" disabled={accepting}>
          {accepting ? 'Joining…' : 'Accept invitation'}
        </Button>
      </form>
    </AuthCard>
  )
}
