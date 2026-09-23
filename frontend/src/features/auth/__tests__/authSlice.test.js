import { describe, expect, it } from 'vitest'

import reducer, {
  logout,
  selectCurrentOrgId,
  selectCurrentUser,
  selectIsAuthenticated,
  setCredentials,
  setCurrentOrgId,
} from '../authSlice'

describe('authSlice', () => {
  it('starts unauthenticated', () => {
    const state = reducer(undefined, { type: '@@INIT' })
    expect(selectIsAuthenticated({ auth: state })).toBe(false)
  })

  it('setCredentials stores tokens and user, and marks the user authenticated', () => {
    const state = reducer(
      undefined,
      setCredentials({ access_token: 'a', refresh_token: 'r', user: { id: '1', email: 'x@example.com' } }),
    )
    expect(selectIsAuthenticated({ auth: state })).toBe(true)
    expect(selectCurrentUser({ auth: state })).toEqual({ id: '1', email: 'x@example.com' })
  })

  it('setCredentials without a user field leaves the existing user untouched (refresh case)', () => {
    let state = reducer(undefined, setCredentials({ access_token: 'a', refresh_token: 'r', user: { id: '1' } }))
    state = reducer(state, setCredentials({ access_token: 'a2', refresh_token: 'r2' }))
    expect(state.accessToken).toBe('a2')
    expect(state.user).toEqual({ id: '1' })
  })

  it('setCurrentOrgId updates the selected org', () => {
    const state = reducer(undefined, setCurrentOrgId('org-1'))
    expect(selectCurrentOrgId({ auth: state })).toBe('org-1')
  })

  it('logout clears tokens, user, and current org', () => {
    let state = reducer(undefined, setCredentials({ access_token: 'a', refresh_token: 'r', user: { id: '1' } }))
    state = reducer(state, setCurrentOrgId('org-1'))
    state = reducer(state, logout())
    expect(selectIsAuthenticated({ auth: state })).toBe(false)
    expect(selectCurrentUser({ auth: state })).toBeNull()
    expect(selectCurrentOrgId({ auth: state })).toBeNull()
  })
})
