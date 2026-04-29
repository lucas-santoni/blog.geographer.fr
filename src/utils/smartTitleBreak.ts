const MIN_LEN = 4

export function smartTitleBreak(title: string): string {
  const parts = title.split(' ')
  if (parts.length <= MIN_LEN) return title
  const start = parts.slice(0, -2).join(' ')
  const end = parts.slice(-2).join('&nbsp;')
  return `${start} ${end}`
}
