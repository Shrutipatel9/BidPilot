import { createApi } from '@reduxjs/toolkit/query/react'

import baseQueryWithReauth from '../../app/baseQuery'

export const authApi = createApi({
  reducerPath: 'authApi',
  baseQuery: baseQueryWithReauth,
  endpoints: (builder) => ({
    signup: builder.mutation({
      query: (body) => ({ url: '/api/auth/signup', method: 'POST', data: body }),
    }),
    login: builder.mutation({
      query: (body) => ({ url: '/api/auth/login', method: 'POST', data: body }),
    }),
    verifyEmail: builder.mutation({
      query: (body) => ({ url: '/api/auth/verify-email', method: 'POST', data: body }),
    }),
    requestPasswordReset: builder.mutation({
      query: (body) => ({ url: '/api/auth/request-password-reset', method: 'POST', data: body }),
    }),
    resetPassword: builder.mutation({
      query: (body) => ({ url: '/api/auth/reset-password', method: 'POST', data: body }),
    }),
    getMe: builder.query({
      query: () => ({ url: '/api/auth/me', method: 'GET' }),
    }),
  }),
})

export const {
  useSignupMutation,
  useLoginMutation,
  useVerifyEmailMutation,
  useRequestPasswordResetMutation,
  useResetPasswordMutation,
  useGetMeQuery,
} = authApi
