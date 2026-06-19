import client from './client'

export async function fetchBalances(groupId) {
  const { data } = await client.get(`/groups/${groupId}/balances`)
  return data
}

export async function fetchSettlements(groupId) {
  const { data } = await client.get(`/groups/${groupId}/settlements`)
  return data
}

export async function updateSettlement(id, payload) {
  const { data } = await client.patch(`/settlements/${id}`, payload)
  return data
}
