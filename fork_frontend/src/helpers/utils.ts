export function getFormattedDate(
  daysOffset: number = 0,
  referenceDate: string | Date = new Date(),
): string {
  // Initialize the date object from the reference provided
  const date = new Date(referenceDate)

  // Apply the offset
  date.setDate(date.getDate() + daysOffset)

  const year = date.getFullYear()
  // getMonth() is zero-indexed, so we add 1
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}
