import { createApi } from '@reduxjs/toolkit/query/react'

import baseQueryWithReauth from '../../app/baseQuery'

function buildDocumentFormData({ file, title, tags, reviewDate }) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('title', title)
  formData.append('tags', JSON.stringify(tags ?? []))
  if (reviewDate) formData.append('review_date', reviewDate)
  return formData
}

export const knowledgeApi = createApi({
  reducerPath: 'knowledgeApi',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['KnowledgeDocuments'],
  endpoints: (builder) => ({
    createKnowledgeDocument: builder.mutation({
      query: ({ orgId, ...fields }) => ({
        url: `/api/orgs/${orgId}/knowledge/documents`,
        method: 'POST',
        data: buildDocumentFormData(fields),
      }),
      invalidatesTags: ['KnowledgeDocuments'],
    }),
    listKnowledgeDocuments: builder.query({
      query: (orgId) => ({ url: `/api/orgs/${orgId}/knowledge/documents`, method: 'GET' }),
      providesTags: ['KnowledgeDocuments'],
    }),
    updateKnowledgeDocument: builder.mutation({
      query: ({ orgId, documentId, ...body }) => ({
        url: `/api/orgs/${orgId}/knowledge/documents/${documentId}`,
        method: 'PATCH',
        data: body,
      }),
      invalidatesTags: ['KnowledgeDocuments'],
    }),
    replaceKnowledgeDocument: builder.mutation({
      query: ({ orgId, documentId, file }) => {
        const formData = new FormData()
        formData.append('file', file)
        return { url: `/api/orgs/${orgId}/knowledge/documents/${documentId}/replace`, method: 'POST', data: formData }
      },
      invalidatesTags: ['KnowledgeDocuments'],
    }),
    deleteKnowledgeDocument: builder.mutation({
      query: ({ orgId, documentId }) => ({
        url: `/api/orgs/${orgId}/knowledge/documents/${documentId}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['KnowledgeDocuments'],
    }),
  }),
})

export const {
  useCreateKnowledgeDocumentMutation,
  useListKnowledgeDocumentsQuery,
  useUpdateKnowledgeDocumentMutation,
  useReplaceKnowledgeDocumentMutation,
  useDeleteKnowledgeDocumentMutation,
} = knowledgeApi
