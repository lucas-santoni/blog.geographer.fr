const FORMATTER = new Intl.DateTimeFormat('en-US', {
  year: 'numeric',
  month: 'long',
  day: '2-digit',
});

export function formatDate(date: Date): string {
  return FORMATTER.format(date);
}
