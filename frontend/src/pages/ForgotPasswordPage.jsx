import { useState } from 'react'
import { Link } from 'react-router-dom'

import AuthCard from '../components/form/AuthCard'
import Button from '../components/form/Button'
import Callout from '../components/form/Callout'
import ErrorBanner from '../components/form/ErrorBanner'
import TextInput from '../components/form/TextInput'
import { useRequestPasswordResetMutation } from '../features/auth/authApi'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [requestReset, { isLoading, error, data, isSuccess }] = useRequestPasswordResetMutation()

  function handleSubmit(e) {
    e.preventDefault()
    requestReset({ email })
  }

  return (
    <AuthCard title="Reset your password" subtitle="We'll email you a link to choose a new one.">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <TextInput
          label="Email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          placeholder="jane@company.com"
        />
        <ErrorBanner error={error} />
        <Button type="submit" loading={isLoading} className="w-full">
          {isLoading ? 'Sending…' : 'Send reset link'}
        </Button>
      </form>
      {isSuccess && (
        <Callout variant="success">
          If that email exists, a reset link has been sent.
          {data?.debug_link && (
            <>
              {' '}
              Dev mode:{' '}
              <a className="font-medium underline underline-offset-2" href={data.debug_link}>
                open it
              </a>
            </>
          )}
        </Callout>
      )}
      <p className="mt-6 text-center text-sm text-slate-500">
        <Link className="font-medium text-brand-600 hover:text-brand-700" to="/login">
          Back to log in
        </Link>
      </p>
    </AuthCard>
  )
}
