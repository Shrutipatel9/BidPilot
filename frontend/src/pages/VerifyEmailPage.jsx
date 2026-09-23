import { useEffect, useRef } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import AuthCard from '../components/form/AuthCard'
import { useVerifyEmailMutation } from '../features/auth/authApi'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const [verifyEmail, { isLoading, isSuccess, error }] = useVerifyEmailMutation()
  const attemptedRef = useRef(false)

  useEffect(() => {
    if (token && !attemptedRef.current) {
      attemptedRef.current = true
      verifyEmail({ token })
    }
  }, [token, verifyEmail])

  return (
    <AuthCard title="Verify your email">
      {!token && <p className="text-sm text-gray-600">This link is missing a verification token.</p>}
      {isLoading && <p className="text-sm text-gray-600">Verifying…</p>}
      {isSuccess && (
        <p className="text-sm text-gray-700">
          Your email is verified.{' '}
          <Link className="text-purple-600 underline" to="/login">
            Log in
          </Link>
        </p>
      )}
      {error && <p className="text-sm text-red-700">That link is invalid or expired.</p>}
    </AuthCard>
  )
}
