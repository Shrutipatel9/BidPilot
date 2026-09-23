import { useState } from 'react'
import { Mail, UserPlus, Users } from 'lucide-react'
import { useSelector } from 'react-redux'

import RoleBadge from '../components/RoleBadge'
import Button from '../components/form/Button'
import ErrorBanner from '../components/form/ErrorBanner'
import Callout from '../components/form/Callout'
import TextInput from '../components/form/TextInput'
import { selectCurrentOrgId, selectCurrentUser } from '../features/auth/authSlice'
import { useChangeRoleMutation, useInviteMemberMutation, useListMembersQuery } from '../features/org/orgApi'
import { initialsFor } from '../lib/initials'
import { ROLE_LABELS } from '../lib/roles'

const ROLES = Object.keys(ROLE_LABELS)

export default function SettingsMembersPage() {
  const orgId = useSelector(selectCurrentOrgId)
  const currentUser = useSelector(selectCurrentUser)
  const { data: members = [], isLoading } = useListMembersQuery(orgId, { skip: !orgId })
  const [changeRole] = useChangeRoleMutation()

  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('reviewer')
  const [lastInvitedEmail, setLastInvitedEmail] = useState(null)
  const [inviteMember, { isLoading: inviting, error: inviteError, data: inviteData }] = useInviteMemberMutation()

  if (!orgId) {
    return <p className="text-sm text-slate-500">Create or select an organization first.</p>
  }

  const myMembership = members.find((m) => m.email === currentUser?.email)
  const canManage = myMembership?.role === 'owner' || myMembership?.role === 'admin'

  async function handleInvite(e) {
    e.preventDefault()
    const result = await inviteMember({ orgId, email: inviteEmail, role: inviteRole })
    if (result.data) {
      setLastInvitedEmail(inviteEmail)
      setInviteEmail('')
    }
  }

  return (
    <div className="max-w-3xl">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Members</h1>
        <p className="mt-1 text-sm text-slate-500">Manage who has access to this organization.</p>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center gap-2 border-b border-slate-100 px-5 py-3.5">
          <Users className="size-4 text-slate-400" aria-hidden="true" />
          <h2 className="text-sm font-semibold text-slate-700">
            {members.length} {members.length === 1 ? 'member' : 'members'}
          </h2>
        </div>

        {isLoading ? (
          <div className="p-5 text-sm text-slate-400">Loading…</div>
        ) : (
          <ul className="divide-y divide-slate-100">
            {members.map((member) => (
              <li key={member.user_id} className="flex items-center gap-3 px-5 py-3.5">
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-600">
                  {initialsFor(member)}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-slate-900">
                    {member.name || member.email}
                    {member.email === currentUser?.email && (
                      <span className="ml-2 text-xs font-normal text-slate-400">(you)</span>
                    )}
                  </p>
                  {member.name && <p className="truncate text-xs text-slate-500">{member.email}</p>}
                </div>
                {canManage ? (
                  <select
                    className="rounded-lg border border-slate-200 bg-slate-50 py-1.5 pl-3 pr-8 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 focus:border-brand-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-brand-500/15"
                    value={member.role}
                    onChange={(e) => changeRole({ orgId, userId: member.user_id, role: e.target.value })}
                  >
                    {ROLES.map((role) => (
                      <option key={role} value={role}>
                        {ROLE_LABELS[role]}
                      </option>
                    ))}
                  </select>
                ) : (
                  <RoleBadge role={member.role} />
                )}
              </li>
            ))}
          </ul>
        )}
      </div>

      {canManage && (
        <div className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center gap-2 border-b border-slate-100 px-5 py-3.5">
            <UserPlus className="size-4 text-slate-400" aria-hidden="true" />
            <h2 className="text-sm font-semibold text-slate-700">Invite a teammate</h2>
          </div>
          <form className="flex flex-col gap-4 p-5 sm:flex-row sm:items-end" onSubmit={handleInvite}>
            <div className="flex-1">
              <TextInput
                label="Email"
                type="email"
                required
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="teammate@company.com"
              />
            </div>
            <label className="flex flex-col gap-1.5 sm:w-48">
              <span className="text-sm font-medium text-slate-700">Role</span>
              <select
                className="rounded-lg border border-slate-300 bg-white px-3.5 py-2.5 text-sm font-medium text-slate-700 transition-shadow focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/15"
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value)}
              >
                {ROLES.map((role) => (
                  <option key={role} value={role}>
                    {ROLE_LABELS[role]}
                  </option>
                ))}
              </select>
            </label>
            <Button type="submit" loading={inviting}>
              <Mail className="size-4" aria-hidden="true" />
              {inviting ? 'Sending…' : 'Send invite'}
            </Button>
          </form>
          {(inviteError || inviteData) && (
            <div className="px-5 pb-5">
              <ErrorBanner error={inviteError} />
              {inviteData && !inviteData.debug_link && (
                <Callout variant="success">Invitation sent to {lastInvitedEmail}.</Callout>
              )}
              {inviteData?.debug_link && (
                <Callout variant="info">
                  Dev mode — invite link for {lastInvitedEmail}:{' '}
                  <a className="font-medium underline underline-offset-2" href={inviteData.debug_link}>
                    open it
                  </a>
                </Callout>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
