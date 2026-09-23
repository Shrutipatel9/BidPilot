import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Navigate, Outlet } from 'react-router-dom'

import { useGetMeQuery } from '../features/auth/authApi'
import { selectIsAuthenticated, setUser } from '../features/auth/authSlice'

export default function ProtectedRoute() {
  const isAuthenticated = useSelector(selectIsAuthenticated)
  const dispatch = useDispatch()
  // Not every auth flow's response includes `user` (only signup's does) — refetching /me here
  // keeps state.auth.user in sync with whichever identity the current token actually belongs
  // to, rather than trusting a stale value left over from a previous session/tab.
  const { data: me } = useGetMeQuery(undefined, { skip: !isAuthenticated })

  useEffect(() => {
    if (me) dispatch(setUser(me))
  }, [me, dispatch])

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
