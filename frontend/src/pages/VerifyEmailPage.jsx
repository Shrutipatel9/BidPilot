import { useEffect, useRef } from 'react'
import { CheckCircle2, Loader2, XCircle } from 'lucide-react'
import { Link, useSearchParams } from 'react-router-dom'

import AuthCard from '../components/form/AuthCard'
import Button from '../components/form/Button'
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
      <div className="flex flex-col items-center gap-4 py-4 text-center">
        {!token && <p className="text-sm text-slate-500">This link is missing a verification token.</p>}

        {isLoading && (
          <>
            <Loader2 className="size-8 animate-spin text-brand-600" aria-hidden="true" />
            <p className="text-sm text-slate-500">Verifying your email…</p>
          </>
        )}

        {isSuccess && (
          <>
            <CheckCircle2 className="size-10 text-emerald-500" aria-hidden="true" />
            <p className="text-sm text-slate-600">Your email is verified.</p>
            <Button as={Link} to="/login" className="w-full">
              Continue to log in
            </Button>
          </>
        )}

        {error && (
          <>
            <XCircle className="size-10 text-rose-500" aria-hidden="true" />
            <p className="text-sm text-slate-600">That link is invalid or has expired.</p>
          </>
        )}
      </div>
    </AuthCard>
  )
}
