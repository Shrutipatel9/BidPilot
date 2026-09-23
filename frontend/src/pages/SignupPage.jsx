import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { Link, useNavigate } from 'react-router-dom'

import AuthCard from '../components/form/AuthCard'
import Button from '../components/form/Button'
import Callout from '../components/form/Callout'
import ErrorBanner from '../components/form/ErrorBanner'
import TextInput from '../components/form/TextInput'
import { setCredentials } from '../features/auth/authSlice'
import { useSignupMutation } from '../features/auth/authApi'

export default function SignupPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [signup, { isLoading, error, data }] = useSignupMutation()
  const dispatch = useDispatch()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    const result = await signup({ email, password, name: name || undefined })
    if (result.data) {
      dispatch(setCredentials(result.data))
      navigate('/create-organization')
    }
  }

  return (
    <AuthCard title="Create your account" subtitle="Start drafting answers your team can trust.">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <TextInput
          label="Full name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoComplete="name"
          placeholder="Jane Cooper"
        />
        <TextInput
          label="Work email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
          placeholder="jane@company.com"
        />
        <TextInput
          label="Password"
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
          placeholder="At least 8 characters"
        />
        <ErrorBanner error={error} />
        {data?.debug_link && (
          <Callout variant="info">
            Dev mode — verification link:{' '}
            <a className="font-medium underline underline-offset-2" href={data.debug_link}>
              open it
            </a>
          </Callout>
        )}
        <Button type="submit" loading={isLoading} className="mt-1 w-full">
          {isLoading ? 'Creating account…' : 'Create account'}
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-500">
        Already have an account?{' '}
        <Link className="font-medium text-brand-600 hover:text-brand-700" to="/login">
          Log in
        </Link>
      </p>
    </AuthCard>
  )
}
