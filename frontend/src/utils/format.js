export function formatAmount(amount, currency = 'KZT') {
  const num = Number(amount)
  const symbols = { KZT: '₸', USD: '$', EUR: '€', RUB: '₽', GBP: '£' }
  const symbol = symbols[currency] || currency
  return `${num.toLocaleString('ru-RU', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}${symbol}`
}

export function formatDate(dateStr) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}
