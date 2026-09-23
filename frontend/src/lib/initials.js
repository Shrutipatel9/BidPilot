export function initialsFor(nameOrUser) {
  const source = (typeof nameOrUser === 'string' ? nameOrUser : nameOrUser?.name || nameOrUser?.email) || '?'
  return source
    .split(/[\s@.]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}
