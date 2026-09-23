import { useState } from 'react'
import { useSelector } from 'react-redux'

import Button from '../components/form/Button'
import ErrorBanner from '../components/form/ErrorBanner'
import TextInput from '../components/form/TextInput'
import { selectCurrentOrgId, selectCurrentUser } from '../features/auth/authSlice'
import { useChangeRoleMutation, useInviteMemberMutation, useListMembersQuery } from '../features/org/orgApi'

const ROLES = ['owner', 'admin', 'knowledge_manager', 'responder', 'reviewer', 'viewer']

export default function SettingsMembersPage() {
  const orgId = useSelector(selectCurrentOrgId)
  const currentUser = useSelector(selectCurrentUser)
  const { data: members = [], isLoading } = useListMembersQuery(orgId, { skip: !orgId })
  const [changeRole] = useChangeRoleMutation()

  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('reviewer')
  const [inviteMember, { isLoading: inviting, error: inviteError, data: inviteData }] = useInviteMemberMutation()

  if (!orgId) {
    return <p className="text-sm text-gray-600">Create or select an organization first.</p>
  }

  const myMembership = members.find((m) => m.email === currentUser?.email)
  const canManage = myMembership?.role === 'owner' || myMembership?.role === 'admin'

  async function handleInvite(e) {
    e.preventDefault()
    const result = await inviteMember({ orgId, email: inviteEmail, role: inviteRole })
    if (result.data) {
      setInviteEmail('')
    }
  }

  return (
    <div className="max-w-2xl">
      <h1 className="mb-4 text-xl font-semibold">Members</h1>

      {isLoading ? (
        <p className="text-sm text-gray-600">Loading…</p>
      ) : (
        <table className="mb-6 w-full text-left text-sm">
          <thead>
            <tr className="border-b border-gray-200 text-gray-500">
              <th className="py-2">Email</th>
              <th className="py-2">Role</th>
            </tr>
          </thead>
          <tbody>
            {members.map((member) => (
              <tr key={member.user_id} className="border-b border-gray-100">
                <td className="py-2">{member.email}</td>
                <td className="py-2">
                  {canManage ? (
                    <select
                      className="rounded border border-gray-300 px-2 py-1 text-sm"
                      value={member.role}
                      onChange={(e) => changeRole({ orgId, userId: member.user_id, role: e.target.value })}
                    >
                      {ROLES.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                  ) : (
                    member.role
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {canManage && (
        <>
          <h2 className="mb-2 text-sm font-semibold text-gray-900">Invite a teammate</h2>
          <form className="flex items-end gap-2" onSubmit={handleInvite}>
            <TextInput
              label="Email"
              type="email"
              required
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
            />
            <label className="flex flex-col gap-1 text-sm text-gray-700">
              Role
              <select
                className="rounded border border-gray-300 px-2 py-2 text-sm"
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value)}
              >
                {ROLES.map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </select>
            </label>
            <Button type="submit" disabled={inviting}>
              {inviting ? 'Sending…' : 'Invite'}
            </Button>
          </form>
          <ErrorBanner error={inviteError} />
          {inviteData?.debug_link && (
            <p className="mt-2 text-xs text-gray-500">
              Dev mode — invite link:{' '}
              <a className="text-purple-600 underline" href={inviteData.debug_link}>
                {inviteData.debug_link}
              </a>
            </p>
          )}
        </>
      )}
    </div>
  )
}
