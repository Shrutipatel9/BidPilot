import { useState } from 'react'

import AuthCard from '../components/form/AuthCard'
import Button from '../components/form/Button'
import ErrorBanner from '../components/form/ErrorBanner'
import TextInput from '../components/form/TextInput'
import { useRequestPasswordResetMutation } from '../features/auth/authApi'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [requestReset, { isLoading, error, data, isSuccess }] = useRequestPasswordResetMutation()

  async function handleSubmit(e) {
    e.preventDefault()
    requestReset({ email })
  }

  return (
    <AuthCard title="Reset your password">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <TextInput
          label="Email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
        />
        <ErrorBanner error={error} />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Sending…' : 'Send reset link'}
        </Button>
      </form>
      {isSuccess && (
        <p className="text-sm text-gray-600">
          If that email exists, a reset link has been sent.
          {data?.debug_link && (
            <>
              {' '}
              Dev mode:{' '}
              <a className="text-purple-600 underline" href={data.debug_link}>
                {data.debug_link}
              </a>
            </>
          )}
        </p>
      )}
    </AuthCard>
  )
}
