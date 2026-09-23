import { createSlice } from '@reduxjs/toolkit'

const initialState = {
  accessToken: null,
  refreshToken: null,
  user: null,
  currentOrgId: null,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials(state, action) {
      const { access_token, refresh_token, user } = action.payload
      if (access_token) state.accessToken = access_token
      if (refresh_token) state.refreshToken = refresh_token
      if (user) state.user = user
      // A user-initiated auth event (login/signup/accept-invitation) is a new session — a
      // currentOrgId left over from a previous one (e.g. logging in as a different user
      // without an explicit logout in between) must not carry over. AppShell repopulates it
      // from that user's real org list once /api/orgs loads. Silent token refresh uses
      // tokensRefreshed below instead, which deliberately does NOT do this.
      state.currentOrgId = null
    },
    tokensRefreshed(state, action) {
      const { access_token, refresh_token } = action.payload
      if (access_token) state.accessToken = access_token
      if (refresh_token) state.refreshToken = refresh_token
    },
    setUser(state, action) {
      state.user = action.payload
    },
    setCurrentOrgId(state, action) {
      state.currentOrgId = action.payload
    },
    logout(state) {
      state.accessToken = null
      state.refreshToken = null
      state.user = null
      state.currentOrgId = null
    },
  },
})

export const { setCredentials, tokensRefreshed, setUser, setCurrentOrgId, logout } = authSlice.actions
export default authSlice.reducer

export const selectIsAuthenticated = (state) => Boolean(state.auth.accessToken)
export const selectCurrentUser = (state) => state.auth.user
export const selectCurrentOrgId = (state) => state.auth.currentOrgId
