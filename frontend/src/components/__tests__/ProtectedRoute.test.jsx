import { configureStore } from '@reduxjs/toolkit'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import { authApi } from '../../features/auth/authApi'
import ProtectedRoute from '../ProtectedRoute'

function renderWithAuth(accessToken) {
  // Includes authApi's reducer/middleware since ProtectedRoute calls useGetMeQuery — it'll
  // fail to actually reach a server in this test environment, which is fine, we're only
  // asserting on the redirect/render behavior, not on the fetched user data.
  const store = configureStore({
    reducer: {
      auth: () => ({ accessToken, refreshToken: null, user: null, currentOrgId: null }),
      [authApi.reducerPath]: authApi.reducer,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(authApi.middleware),
  })

  return render(
    <Provider store={store}>
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<div>Login page</div>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/protected" element={<div>Secret content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </Provider>,
  )
}

describe('ProtectedRoute', () => {
  it('redirects to /login when not authenticated', () => {
    renderWithAuth(null)
    expect(screen.getByText('Login page')).toBeInTheDocument()
  })

  it('renders the nested route when authenticated', () => {
    renderWithAuth('a-token')
    expect(screen.getByText('Secret content')).toBeInTheDocument()
  })
})
