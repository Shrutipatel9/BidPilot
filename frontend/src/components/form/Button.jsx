export default function Button({ children, disabled, ...buttonProps }) {
  return (
    <button
      {...buttonProps}
      disabled={disabled}
      className="rounded bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {children}
    </button>
  )
}
