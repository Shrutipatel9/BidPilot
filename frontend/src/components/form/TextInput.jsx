export default function TextInput({ label, ...inputProps }) {
  return (
    <label className="flex flex-col gap-1 text-sm text-gray-700">
      {label}
      <input
        {...inputProps}
        className="rounded border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none"
      />
    </label>
  )
}
