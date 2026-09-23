export default function AuthCard({ title, children }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-sm rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h1 className="mb-4 text-lg font-semibold text-gray-900">{title}</h1>
        <div className="flex flex-col gap-4">{children}</div>
      </div>
    </div>
  )
}
