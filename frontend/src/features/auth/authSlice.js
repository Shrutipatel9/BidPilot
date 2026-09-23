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

export const { setCredentials, setUser, setCurrentOrgId, logout } = authSlice.actions
export default authSlice.reducer

export const selectIsAuthenticated = (state) => Boolean(state.auth.accessToken)
export const selectCurrentUser = (state) => state.auth.user
export const selectCurrentOrgId = (state) => state.auth.currentOrgId
