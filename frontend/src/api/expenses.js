import client from './client'

export async function fetchExpenses(groupId) {
  const { data } = await client.get(`/groups/${groupId}/expenses`)
  return data
}

export async function createExpense(groupId, payload) {
  const { data } = await client.post(`/groups/${groupId}/expenses`, payload)
  return data
}

export async function getExpense(id) {
  const { data } = await client.get(`/expenses/${id}`)
  return data
}

export async function deleteExpense(id) {
  await client.delete(`/expenses/${id}`)
}
