import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { Link, useNavigate } from 'react-router-dom'

import AuthCard from '../components/form/AuthCard'
import Button from '../components/form/Button'
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
    <AuthCard title="Create your BidPilot account">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <TextInput label="Name" value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" />
        <TextInput
          label="Email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="email"
        />
        <TextInput
          label="Password"
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="new-password"
        />
        <ErrorBanner error={error} />
        {data?.debug_link && (
          <p className="text-xs text-gray-500">
            Dev mode — verification link:{' '}
            <a className="text-purple-600 underline" href={data.debug_link}>
              {data.debug_link}
            </a>
          </p>
        )}
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating account…' : 'Sign up'}
        </Button>
      </form>
      <p className="mt-4 text-sm text-gray-600">
        Already have an account?{' '}
        <Link className="text-purple-600 underline" to="/login">
          Log in
        </Link>
      </p>
    </AuthCard>
  )
}
