import axiosInstance from './axiosInstance'
import { logout, setCredentials } from '../features/auth/authSlice'

const rawBaseQuery = async ({ url, method = 'GET', data, params }, api) => {
  const token = api.getState().auth.accessToken
  try {
    const result = await axiosInstance({
      url,
      method,
      data,
      params,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    return { data: result.data }
  } catch (axiosError) {
    return {
      error: {
        status: axiosError.response?.status,
        data: axiosError.response?.data ?? axiosError.message,
      },
    }
  }
}

let refreshPromise = null

// RTK Query's documented re-auth pattern (https://redux-toolkit.js.org/rtk-query/usage/customizing-queries#automatic-re-authorization-by-extending-fetchbasequery),
// adapted to the axios-based rawBaseQuery above. A single in-flight refresh is shared across
// concurrent 401s so a page that fires several queries at once doesn't race multiple refreshes.
const baseQueryWithReauth = async (args, api, extraOptions) => {
  let result = await rawBaseQuery(args, api, extraOptions)

  if (result.error?.status === 401 && args.url !== '/api/auth/refresh') {
    const refreshToken = api.getState().auth.refreshToken

    if (refreshToken) {
      refreshPromise ??= rawBaseQuery(
        { url: '/api/auth/refresh', method: 'POST', data: { refresh_token: refreshToken } },
        api,
        extraOptions,
      ).finally(() => {
        refreshPromise = null
      })

      const refreshResult = await refreshPromise

      if (refreshResult.data) {
        api.dispatch(setCredentials(refreshResult.data))
        result = await rawBaseQuery(args, api, extraOptions)
      } else {
        api.dispatch(logout())
      }
    } else {
      api.dispatch(logout())
    }
  }

  return result
}

export default baseQueryWithReauth
