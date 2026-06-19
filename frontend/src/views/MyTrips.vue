<template>
  <div class="min-h-screen pb-20">
    <div class="px-4 pt-4 pb-2">
      <h1 class="text-xl font-bold">My Trips</h1>
    </div>

    <div class="flex border-b-2 border-gray-200 px-4">
      <button
        class="flex-1 py-3 text-center font-semibold text-sm transition-colors"
        :class="tab === 'active' ? 'text-primary border-b-2 border-primary -mb-[2px]' : 'text-gray-400'"
        @click="tab = 'active'"
      >
        Active
      </button>
      <button
        class="flex-1 py-3 text-center font-semibold text-sm transition-colors"
        :class="tab === 'archived' ? 'text-primary border-b-2 border-primary -mb-[2px]' : 'text-gray-400'"
        @click="tab = 'archived'"
      >
        Archive
      </button>
    </div>

    <div v-if="store.loading" class="p-8 text-center text-gray-400">Loading...</div>

    <div v-else class="px-4 pt-3 space-y-2.5">
      <GroupCard v-for="group in displayedGroups" :key="group.id" :group="group" />
      <div v-if="displayedGroups.length === 0" class="text-center text-gray-400 py-12">
        {{ tab === 'active' ? 'No active trips' : 'No archived trips' }}
      </div>
    </div>

    <div class="fixed bottom-6 left-0 right-0 flex justify-center">
      <router-link
        :to="{ name: 'create-group' }"
        class="bg-primary text-white px-6 py-3 rounded-full font-semibold text-sm shadow-lg active:bg-primary-dark no-underline"
      >
        + New Trip
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useGroupsStore } from '../stores/groups'
import { useAuthStore } from '../stores/auth'
import { useTelegram } from '../composables/useTelegram'
import GroupCard from '../components/GroupCard.vue'

const store = useGroupsStore()
const auth = useAuthStore()
const { ready } = useTelegram()

const tab = ref('active')

const displayedGroups = computed(() =>
  tab.value === 'active' ? store.activeGroups() : store.archivedGroups()
)

onMounted(async () => {
  ready()
  await auth.init()
  await store.loadGroups()
})
</script>
