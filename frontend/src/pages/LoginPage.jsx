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
    <AuthCard title="Log in to BidPilot">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
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
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
        />
        <ErrorBanner error={error} />
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Logging in…' : 'Log in'}
        </Button>
      </form>
      <p className="mt-4 flex justify-between text-sm text-gray-600">
        <Link className="text-purple-600 underline" to="/signup">
          Sign up
        </Link>
        <Link className="text-purple-600 underline" to="/forgot-password">
          Forgot password?
        </Link>
      </p>
    </AuthCard>
  )
}
