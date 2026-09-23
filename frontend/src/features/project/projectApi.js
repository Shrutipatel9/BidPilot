import { createApi } from '@reduxjs/toolkit/query/react'

import baseQueryWithReauth from '../../app/baseQuery'

function buildProjectFormData({ file, name, buyer, dueDate, tags }) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', name)
  if (buyer) formData.append('buyer', buyer)
  if (dueDate) formData.append('due_date', dueDate)
  formData.append('tags', JSON.stringify(tags ?? []))
  return formData
}

export const projectApi = createApi({
  reducerPath: 'projectApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Projects', 'Questions', 'Answers'],
  endpoints: (builder) => ({
    createProject: builder.mutation({
      query: ({ orgId, ...fields }) => ({
        url: `/api/orgs/${orgId}/projects`,
        method: 'POST',
        data: buildProjectFormData(fields),
      }),
      invalidatesTags: ['Projects'],
    }),
    listProjects: builder.query({
      query: (orgId) => ({ url: `/api/orgs/${orgId}/projects`, method: 'GET' }),
      providesTags: ['Projects'],
    }),
    getProject: builder.query({
      query: ({ orgId, projectId }) => ({ url: `/api/orgs/${orgId}/projects/${projectId}`, method: 'GET' }),
      providesTags: ['Projects'],
    }),
    parseProject: builder.mutation({
      query: ({ orgId, projectId }) => ({
        url: `/api/orgs/${orgId}/projects/${projectId}/parse`,
        method: 'POST',
      }),
      invalidatesTags: ['Questions'],
    }),
    listQuestions: builder.query({
      query: ({ orgId, projectId }) => ({
        url: `/api/orgs/${orgId}/projects/${projectId}/questions`,
        method: 'GET',
      }),
      providesTags: ['Questions'],
    }),
    updateQuestion: builder.mutation({
      query: ({ orgId, projectId, questionId, ...body }) => ({
        url: `/api/orgs/${orgId}/projects/${projectId}/questions/${questionId}`,
        method: 'PATCH',
        data: body,
      }),
      invalidatesTags: ['Questions'],
    }),
    confirmQuestions: builder.mutation({
      query: ({ orgId, projectId }) => ({
        url: `/api/orgs/${orgId}/projects/${projectId}/questions/confirm`,
        method: 'POST',
      }),
      invalidatesTags: ['Projects', 'Questions'],
    }),
  }),
})

export const {
  useCreateProjectMutation,
  useListProjectsQuery,
  useGetProjectQuery,
  useParseProjectMutation,
  useListQuestionsQuery,
  useUpdateQuestionMutation,
  useConfirmQuestionsMutation,
} = projectApi
