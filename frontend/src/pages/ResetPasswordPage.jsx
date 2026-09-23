import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'

import AuthCard from '../components/form/AuthCard'
import Button from '../components/form/Button'
import ErrorBanner from '../components/form/ErrorBanner'
import TextInput from '../components/form/TextInput'
import { useResetPasswordMutation } from '../features/auth/authApi'

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [newPassword, setNewPassword] = useState('')
  const [resetPassword, { isLoading, error, isSuccess }] = useResetPasswordMutation()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    const result = await resetPassword({ token, new_password: newPassword })
    if (result.data) {
      setTimeout(() => navigate('/login'), 1500)
    }
  }

  if (!token) {
    return (
      <AuthCard title="Reset your password">
        <p className="text-sm text-gray-600">This link is missing a reset token.</p>
      </AuthCard>
    )
  }

  return (
    <AuthCard title="Choose a new password">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <TextInput
          label="New password"
          type="password"
          required
          minLength={8}
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          autoComplete="new-password"
        />
        <ErrorBanner error={error} />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Saving…' : 'Reset password'}
        </Button>
      </form>
      {isSuccess && (
        <p className="text-sm text-gray-700">
          Password reset.{' '}
          <Link className="text-purple-600 underline" to="/login">
            Log in
          </Link>
        </p>
      )}
    </AuthCard>
  )
}
