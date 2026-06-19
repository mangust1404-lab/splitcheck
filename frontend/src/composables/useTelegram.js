export function useTelegram() {
  const tg = window.Telegram?.WebApp

  function ready() {
    tg?.ready()
    tg?.expand()
  }

  function getInitData() {
    return tg?.initData || ''
  }

  function getUserName() {
    const user = tg?.initDataUnsafe?.user
    if (!user) return 'Guest'
    return [user.first_name, user.last_name].filter(Boolean).join(' ')
  }

  function showAlert(message) {
    if (tg?.showAlert) {
      tg.showAlert(message)
    } else {
      alert(message)
    }
  }

  function hapticFeedback(type = 'impact') {
    tg?.HapticFeedback?.[type === 'impact' ? 'impactOccurred' : 'notificationOccurred']?.(
      type === 'impact' ? 'medium' : 'success'
    )
  }

  return { tg, ready, getInitData, getUserName, showAlert, hapticFeedback }
}
