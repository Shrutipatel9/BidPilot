import { describe, expect, it } from 'vitest'

import reducer, {
  logout,
  selectCurrentOrgId,
  selectCurrentUser,
  selectIsAuthenticated,
  setCredentials,
  setCurrentOrgId,
  tokensRefreshed,
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

  it('setCredentials without a user field leaves the existing user untouched', () => {
    let state = reducer(undefined, setCredentials({ access_token: 'a', refresh_token: 'r', user: { id: '1' } }))
    state = reducer(state, setCredentials({ access_token: 'a2', refresh_token: 'r2' }))
    expect(state.accessToken).toBe('a2')
    expect(state.user).toEqual({ id: '1' })
  })

  it('setCredentials resets currentOrgId — a new login must not inherit a previous session\'s org', () => {
    let state = reducer(undefined, setCredentials({ access_token: 'a', refresh_token: 'r', user: { id: '1' } }))
    state = reducer(state, setCurrentOrgId('org-from-user-a'))
    state = reducer(state, setCredentials({ access_token: 'b', refresh_token: 'r2', user: { id: '2' } }))
    expect(selectCurrentOrgId({ auth: state })).toBeNull()
  })

  it('tokensRefreshed updates tokens but leaves user and currentOrgId untouched (same session)', () => {
    let state = reducer(undefined, setCredentials({ access_token: 'a', refresh_token: 'r', user: { id: '1' } }))
    state = reducer(state, setCurrentOrgId('org-1'))
    state = reducer(state, tokensRefreshed({ access_token: 'a2', refresh_token: 'r2' }))
    expect(state.accessToken).toBe('a2')
    expect(state.refreshToken).toBe('r2')
    expect(selectCurrentUser({ auth: state })).toEqual({ id: '1' })
    expect(selectCurrentOrgId({ auth: state })).toBe('org-1')
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
