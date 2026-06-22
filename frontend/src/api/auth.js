import client from './client'

export async function loginWithTelegram(initData) {
  const { data } = await client.post('/auth/telegram', { init_data: initData })
  return data
}

export async function loginDev() {
  const { data } = await client.post('/auth/dev')
  return data
}

export async function getMe() {
  const { data } = await client.get('/auth/me')
  return data
}
