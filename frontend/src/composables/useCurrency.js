export const CURRENCIES = [
  { code: 'KZT', name: 'Tenge', symbol: '₸' },
  { code: 'USD', name: 'US Dollar', symbol: '$' },
  { code: 'EUR', name: 'Euro', symbol: '€' },
  { code: 'RUB', name: 'Ruble', symbol: '₽' },
  { code: 'GBP', name: 'Pound', symbol: '£' },
  { code: 'TRY', name: 'Turkish Lira', symbol: '₺' },
  { code: 'THB', name: 'Thai Baht', symbol: '฿' },
  { code: 'GEL', name: 'Georgian Lari', symbol: '₾' },
]

export function useCurrency() {
  function getSymbol(code) {
    return CURRENCIES.find((c) => c.code === code)?.symbol || code
  }
  return { CURRENCIES, getSymbol }
}
