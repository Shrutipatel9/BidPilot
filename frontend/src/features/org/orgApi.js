import { createApi } from '@reduxjs/toolkit/query/react'

import baseQueryWithReauth from '../../app/baseQuery'

export const orgApi = createApi({
  reducerPath: 'orgApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Organizations', 'Members', 'AuditLog'],
  endpoints: (builder) => ({
    createOrganization: builder.mutation({
      query: (body) => ({ url: '/api/orgs', method: 'POST', data: body }),
      invalidatesTags: ['Organizations'],
    }),
    listMyOrganizations: builder.query({
      query: () => ({ url: '/api/orgs', method: 'GET' }),
      providesTags: ['Organizations'],
    }),
    listMembers: builder.query({
      query: (orgId) => ({ url: `/api/orgs/${orgId}/members`, method: 'GET' }),
      providesTags: ['Members'],
    }),
    changeRole: builder.mutation({
      query: ({ orgId, userId, role }) => ({
        url: `/api/orgs/${orgId}/members/${userId}`,
        method: 'PATCH',
        data: { role },
      }),
      invalidatesTags: ['Members'],
    }),
    getAuditLog: builder.query({
      query: (orgId) => ({ url: `/api/orgs/${orgId}/audit-log`, method: 'GET' }),
      providesTags: ['AuditLog'],
    }),
    inviteMember: builder.mutation({
      query: ({ orgId, email, role }) => ({
        url: `/api/orgs/${orgId}/invitations`,
        method: 'POST',
        data: { email, role },
      }),
    }),
    previewInvitation: builder.query({
      query: (token) => ({ url: `/api/invitations/${token}`, method: 'GET' }),
    }),
    acceptInvitation: builder.mutation({
      query: ({ token, ...body }) => ({
        url: `/api/invitations/${token}/accept`,
        method: 'POST',
        data: body,
      }),
    }),
  }),
})

export const {
  useCreateOrganizationMutation,
  useListMyOrganizationsQuery,
  useListMembersQuery,
  useChangeRoleMutation,
  useGetAuditLogQuery,
  useInviteMemberMutation,
  usePreviewInvitationQuery,
  useAcceptInvitationMutation,
} = orgApi
