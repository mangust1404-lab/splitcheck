<template>
  <div class="min-h-screen px-4 pt-4">
    <div v-if="loading" class="p-8 text-center text-gray-400">{{ t('joinGroup.loading') }}</div>

    <div v-else-if="error" class="p-8 text-center">
      <div class="text-red-500 text-sm mb-4">{{ error }}</div>
      <router-link :to="{ name: 'my-trips' }" class="text-primary text-sm font-semibold no-underline">
        {{ t('joinGroup.backToTrips') }}
      </router-link>
    </div>

    <div v-else-if="group" class="space-y-5">
      <div class="text-center pt-2">
        <div class="text-xs text-gray-400 uppercase tracking-wide mb-1">{{ t('joinGroup.invitedTo') }}</div>
        <h1 class="text-xl font-bold">{{ group.name }}</h1>
        <div class="text-gray-500 text-xs mt-1">{{ group.base_currency }}</div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          {{ t('joinGroup.participants', { count: group.members.length }) }}
        </label>
        <div class="space-y-2">
          <div
            v-for="m in group.members"
            :key="m.id"
            class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg"
          >
            <div
              class="w-8 h-8 rounded-full text-white text-xs flex items-center justify-center font-semibold"
              :style="{ backgroundColor: getColor(m.id) }"
            >
              {{ getInitials(m.display_name) }}
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium">{{ m.display_name }}</div>
              <div class="text-[11px] text-gray-400">
                {{ m.user_id ? t('joinGroup.telegramLinked') : t('joinGroup.virtual') }}
              </div>
            </div>
            <button
              v-if="!m.user_id"
              @click="handleJoin(m.id)"
              :disabled="joining"
              class="bg-primary text-white px-3 py-1.5 rounded-lg text-xs font-semibold disabled:opacity-50"
            >
              {{ t('joinGroup.thisIsMe') }}
            </button>
          </div>
        </div>
      </div>

      <button
        @click="handleJoin(null)"
        :disabled="joining"
        class="w-full bg-primary text-white py-3 rounded-xl font-semibold text-sm disabled:opacity-50"
      >
        {{ joining ? t('joinGroup.joining') : t('joinGroup.joinAsNew') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchGroupByInvite, joinGroup } from '../api/groups'
import { useAuthStore } from '../stores/auth'
import { useTelegram } from '../composables/useTelegram'
import { useI18n } from '../composables/useI18n'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { ready, hapticFeedback } = useTelegram()
const { t } = useI18n()

const inviteCode = route.params.inviteCode
const group = ref(null)
const loading = ref(true)
const joining = ref(false)
const error = ref(null)

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() }

async function handleJoin(linkToMemberId) {
  joining.value = true
  try {
    await joinGroup(group.value.id, inviteCode, linkToMemberId)
    hapticFeedback('notification')
    router.push({ name: 'trip-detail', params: { id: group.value.id } })
  } catch (e) {
    const detail = e.response?.data?.detail
    if (detail === 'Already a member') {
      // Already in the group — just navigate there
      router.push({ name: 'trip-detail', params: { id: group.value.id } })
    } else {
      error.value = detail || t('joinGroup.joinFailed')
    }
  } finally {
    joining.value = false
  }
}

onMounted(async () => {
  ready()
  await auth.init()
  if (!auth.isLoggedIn) {
    error.value = t('joinGroup.authFailed')
    loading.value = false
    return
  }
  try {
    group.value = await fetchGroupByInvite(inviteCode)
  } catch (e) {
    error.value = e.response?.data?.detail || t('joinGroup.invalidInvite')
  } finally {
    loading.value = false
  }
})
</script>
