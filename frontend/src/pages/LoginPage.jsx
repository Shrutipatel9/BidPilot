import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { Link, useNavigate } from 'react-router-dom'

import AuthCard from '../components/form/AuthCard'
import Button from '../components/form/Button'
import ErrorBanner from '../components/form/ErrorBanner'
import TextInput from '../components/form/TextInput'
import { setCredentials } from '../features/auth/authSlice'
import { useLoginMutation } from '../features/auth/authApi'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [login, { isLoading, error }] = useLoginMutation()
  const dispatch = useDispatch()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    const result = await login({ email, password })
    if (result.data) {
      dispatch(setCredentials(result.data))
      navigate('/')
    }
  }

  return (
    <AuthCard title="Welcome back" subtitle="Log in to continue where you left off.">
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
        <TextInput
          label="Password"
          labelExtra={
            <Link className="text-sm font-medium text-brand-600 hover:text-brand-700" to="/forgot-password">
              Forgot password?
            </Link>
          }
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
        />
        <ErrorBanner error={error} />
        <Button type="submit" loading={isLoading} className="mt-1 w-full">
          {isLoading ? 'Logging in…' : 'Log in'}
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-500">
        Don't have an account?{' '}
        <Link className="font-medium text-brand-600 hover:text-brand-700" to="/signup">
          Sign up
        </Link>
      </p>
    </AuthCard>
  )
}
