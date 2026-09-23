import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'

import AuthCard from '../components/form/AuthCard'
import Button from '../components/form/Button'
import ErrorBanner from '../components/form/ErrorBanner'
import TextInput from '../components/form/TextInput'
import { setCurrentOrgId } from '../features/auth/authSlice'
import { useCreateOrganizationMutation } from '../features/org/orgApi'

export default function CreateOrgPage() {
  const [name, setName] = useState('')
  const [createOrganization, { isLoading, error }] = useCreateOrganizationMutation()
  const dispatch = useDispatch()
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    const result = await createOrganization({ name })
    if (result.data) {
      dispatch(setCurrentOrgId(result.data.id))
      navigate('/')
    }
  }

  return (
    <AuthCard title="Create your organization" subtitle="This is your team's shared workspace.">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <TextInput
          label="Organization name"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoFocus
          placeholder="Acme Inc"
        />
        <ErrorBanner error={error} />
        <Button type="submit" loading={isLoading} className="w-full">
          {isLoading ? 'Creating…' : 'Create organization'}
        </Button>
      </form>
    </AuthCard>
  )
}
