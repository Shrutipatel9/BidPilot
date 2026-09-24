import axiosInstance from '../../app/axiosInstance'

const FILENAME_PATTERN = /filename="(.+)"/

// Export is a binary file download (xlsx/docx/csv), which doesn't fit RTK Query's JSON-shaped
// baseQuery — a direct axios call with responseType: 'blob' instead, then a synthetic <a> click
// to trigger the browser's native save behavior.
export async function downloadProjectExport({ orgId, projectId, format, accessToken }) {
  const response = await axiosInstance.get(`/api/orgs/${orgId}/projects/${projectId}/export`, {
    params: { format },
    headers: { Authorization: `Bearer ${accessToken}` },
    responseType: 'blob',
  })

  const disposition = response.headers['content-disposition'] || ''
  const filename = FILENAME_PATTERN.exec(disposition)?.[1] || `export.${format}`

  const url = URL.createObjectURL(response.data)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
