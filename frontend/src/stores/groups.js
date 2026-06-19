import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchGroups, getGroup } from '../api/groups'

export const useGroupsStore = defineStore('groups', () => {
  const groups = ref([])
  const currentGroup = ref(null)
  const loading = ref(false)

  const activeGroups = () => groups.value.filter((g) => g.status === 'active')
  const archivedGroups = () => groups.value.filter((g) => g.status === 'archived')

  async function loadGroups() {
    loading.value = true
    try {
      groups.value = await fetchGroups()
    } finally {
      loading.value = false
    }
  }

  async function loadGroup(id) {
    loading.value = true
    try {
      currentGroup.value = await getGroup(id)
    } finally {
      loading.value = false
    }
  }

  return { groups, currentGroup, loading, activeGroups, archivedGroups, loadGroups, loadGroup }
})
