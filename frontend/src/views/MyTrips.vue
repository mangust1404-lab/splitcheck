<template>
  <div class="min-h-screen pb-20">
    <div class="px-4 pt-4 pb-2">
      <h1 class="text-xl font-bold">{{ t('myTrips.title') }}</h1>
    </div>

    <div class="flex border-b-2 border-gray-200 px-4">
      <button
        class="flex-1 py-3 text-center font-semibold text-sm transition-colors"
        :class="tab === 'active' ? 'text-primary border-b-2 border-primary -mb-[2px]' : 'text-gray-400'"
        @click="tab = 'active'"
      >
        {{ t('myTrips.active') }}
      </button>
      <button
        class="flex-1 py-3 text-center font-semibold text-sm transition-colors"
        :class="tab === 'archived' ? 'text-primary border-b-2 border-primary -mb-[2px]' : 'text-gray-400'"
        @click="tab = 'archived'"
      >
        {{ t('myTrips.archive') }}
      </button>
    </div>

    <div v-if="!auth.isLoggedIn && !auth.loading" class="p-8 text-center text-gray-400">
      {{ t('myTrips.authFailed') }}
    </div>

    <div v-else-if="store.loading || auth.loading" class="p-8 text-center text-gray-400">{{ t('myTrips.loading') }}</div>

    <div v-else class="px-4 pt-3 space-y-2.5">
      <GroupCard v-for="group in displayedGroups" :key="group.id" :group="group" />
      <div v-if="displayedGroups.length === 0" class="text-center text-gray-400 py-12">
        {{ tab === 'active' ? t('myTrips.noActive') : t('myTrips.noArchived') }}
      </div>
    </div>

    <div class="fixed bottom-6 left-0 right-0 flex justify-center">
      <router-link
        :to="{ name: 'create-group' }"
        class="bg-primary text-white px-6 py-3 rounded-full font-semibold text-sm shadow-lg active:bg-primary-dark no-underline"
      >
        {{ t('myTrips.newTrip') }}
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGroupsStore } from '../stores/groups'
import { useAuthStore } from '../stores/auth'
import { useTelegram } from '../composables/useTelegram'
import { useI18n } from '../composables/useI18n'
import GroupCard from '../components/GroupCard.vue'

const router = useRouter()
const store = useGroupsStore()
const auth = useAuthStore()
const { ready } = useTelegram()
const { t } = useI18n()

const tab = ref('active')

const displayedGroups = computed(() =>
  tab.value === 'active' ? store.activeGroups() : store.archivedGroups()
)

onMounted(async () => {
  ready()
  await auth.init()

  // Handle deep link: redirect to join page if start_param contains invite code
  const startParam = window.Telegram?.WebApp?.initDataUnsafe?.start_param
  if (startParam && startParam.startsWith('join_')) {
    const inviteCode = startParam.slice(5) // strip "join_" prefix
    router.replace({ name: 'join-group', params: { inviteCode } })
    return
  }

  if (auth.isLoggedIn) {
    await store.loadGroups()
  }
})
</script>
