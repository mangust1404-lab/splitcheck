import client from './client'

export async function fetchGroups() {
  const { data } = await client.get('/groups')
  return data
}

export async function createGroup(payload) {
  const { data } = await client.post('/groups', payload)
  return data
}

export async function getGroup(id) {
  const { data } = await client.get(`/groups/${id}`)
  return data
}

export async function updateGroup(id, payload) {
  const { data } = await client.patch(`/groups/${id}`, payload)
  return data
}

export async function fetchGroupByInvite(inviteCode) {
  const { data } = await client.get(`/groups/invite/${inviteCode}`)
  return data
}

export async function joinGroup(id, inviteCode, linkToMemberId = null) {
  const { data } = await client.post(`/groups/${id}/join`, {
    invite_code: inviteCode,
    link_to_member_id: linkToMemberId,
  })
  return data
}

export async function deleteGroup(id) {
  await client.delete(`/groups/${id}`)
}

export async function addMember(groupId, displayName) {
  const { data } = await client.post(`/groups/${groupId}/members`, {
    display_name: displayName,
  })
  return data
}
