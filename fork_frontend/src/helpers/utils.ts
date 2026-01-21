export function getFormattedDate(
  daysOffset: number = 0,
  referenceDate: string | Date | null = null,
): string {
  const storageDate = localStorage.getItem('dateToLoad')
  localStorage.setItem('lastActivityTimestamp', Date.now().toString())

  let date = new Date()

  if (referenceDate) {
    date = new Date(referenceDate)
  } else if (storageDate && storageDate != '') {
    date = new Date(storageDate)
  }

  date.setDate(date.getDate() + daysOffset)

  const year = date.getFullYear()
  // getMonth() is zero-indexed, so we add 1
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  const dateString: string = `${year}-${month}-${day}`

  return dateString
}

export function getFormattedDateToday(): string {
  const date = new Date()

  const year = date.getFullYear()
  // getMonth() is zero-indexed, so we add 1
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  const dateString: string = `${year}-${month}-${day}`

  return dateString
}
