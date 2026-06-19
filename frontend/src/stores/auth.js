import { defineStore } from 'pinia'
import { ref } from 'vue'
import { loginWithTelegram, getMe } from '../api/auth'
import { useTelegram } from '../composables/useTelegram'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const loading = ref(false)

  async function login() {
    loading.value = true
    try {
      const { getInitData } = useTelegram()
      const initData = getInitData()

      if (!initData) {
        console.warn('No Telegram initData — running outside Telegram')
        return false
      }

      const result = await loginWithTelegram(initData)
      localStorage.setItem('access_token', result.access_token)
      user.value = { id: result.user_id, display_name: result.display_name }
      isLoggedIn.value = true
      return true
    } catch (e) {
      console.error('Auth failed:', e)
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    try {
      user.value = await getMe()
      isLoggedIn.value = true
    } catch {
      isLoggedIn.value = false
    }
  }

  async function init() {
    const token = localStorage.getItem('access_token')
    if (token) {
      await fetchUser()
    }
    if (!isLoggedIn.value) {
      await login()
    }
  }

  return { user, isLoggedIn, loading, login, init }
})
