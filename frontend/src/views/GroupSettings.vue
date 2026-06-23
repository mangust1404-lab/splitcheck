<template>
  <div class="min-h-screen px-4 pt-4">
    <div class="flex items-center gap-2 mb-4">
      <button
        @click="$router.push({ name: 'trip-detail', params: { id: groupId } })"
        class="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-full bg-gray-100 active:bg-gray-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="text-xl font-bold">{{ t('groupSettings.title') }}</h1>
    </div>

    <div v-if="group" class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('groupSettings.tripName') }}</label>
        <input v-model="groupName" type="text"
          class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary"
          @blur="updateName" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('groupSettings.inviteLink') }}</label>
        <div class="flex items-center gap-2">
          <input :value="inviteUrl" readonly
            class="flex-1 border border-gray-300 rounded-lg px-3 py-2.5 text-sm bg-gray-50 outline-none" />
          <button @click="copyInvite" class="bg-primary text-white px-4 py-2.5 rounded-lg text-sm font-semibold">
            {{ t('groupSettings.copy') }}
          </button>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          {{ t('groupSettings.participants', { count: group.members.length }) }}
        </label>
        <div class="space-y-2">
          <div v-for="m in group.members" :key="m.id"
            class="flex items-center gap-3 p-2 bg-gray-50 rounded-lg">
            <div class="w-8 h-8 rounded-full text-white text-xs flex items-center justify-center font-semibold"
              :style="{ backgroundColor: getColor(m.id) }">
              {{ getInitials(m.display_name) }}
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium">{{ m.display_name }}</div>
              <div class="text-[11px] text-gray-400">
                {{ m.user_id ? t('groupSettings.telegramLinked') : t('groupSettings.virtual') }}
                {{ m.role === 'admin' ? ' · ' + t('groupSettings.admin') : '' }}
              </div>
            </div>
          </div>
        </div>

        <div class="flex gap-2 mt-2">
          <input v-model="newMemberName" type="text" :placeholder="t('groupSettings.addPlaceholder')"
            class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none" />
          <button @click="handleAddMember" :disabled="!newMemberName.trim()"
            class="bg-primary text-white px-4 py-2 rounded-lg text-sm font-semibold disabled:opacity-50">
            {{ t('groupSettings.add') }}
          </button>
        </div>
      </div>

      <div class="pt-4 border-t border-gray-200 space-y-3">
        <button
          v-if="group.status === 'active'"
          @click="handleArchive"
          class="w-full py-3 border border-gray-300 rounded-xl text-sm font-semibold text-gray-600"
        >
          {{ t('groupSettings.archive') }}
        </button>
        <button
          v-else
          @click="handleUnarchive"
          class="w-full py-3 border border-primary rounded-xl text-sm font-semibold text-primary"
        >
          {{ t('groupSettings.reactivate') }}
        </button>
        <button
          @click="handleDelete"
          class="w-full py-3 border border-red-300 rounded-xl text-sm font-semibold text-red-500"
        >
          {{ t('groupSettings.delete') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '../stores/groups'
import { updateGroup, addMember, deleteGroup } from '../api/groups'
import { useTelegram } from '../composables/useTelegram'
import { useI18n } from '../composables/useI18n'

const route = useRoute()
const router = useRouter()
const store = useGroupsStore()
const { showAlert } = useTelegram()
const { t } = useI18n()
const groupId = Number(route.params.id)

const group = computed(() => store.currentGroup)
const groupName = ref('')
const newMemberName = ref('')

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() }

const inviteUrl = computed(() => {
  if (!group.value) return ''
  return `https://t.me/SplitCheckanalog_bot/app?startapp=join_${group.value.invite_code}`
})

function copyInvite() {
  navigator.clipboard.writeText(inviteUrl.value)
  showAlert(t('groupSettings.inviteCopied'))
}

async function updateName() {
  if (groupName.value !== group.value.name) {
    await updateGroup(groupId, { name: groupName.value })
    await store.loadGroup(groupId)
  }
}

async function handleAddMember() {
  await addMember(groupId, newMemberName.value.trim())
  newMemberName.value = ''
  await store.loadGroup(groupId)
}

async function handleDelete() {
  if (!confirm(t('groupSettings.deleteConfirm'))) return
  try {
    await deleteGroup(groupId)
    router.push({ name: 'my-trips' })
  } catch (e) {
    showAlert(e.response?.data?.detail || t('groupSettings.deleteFailed'))
  }
}

async function handleArchive() {
  await updateGroup(groupId, { status: 'archived' })
  router.push({ name: 'my-trips' })
}

async function handleUnarchive() {
  await updateGroup(groupId, { status: 'active' })
  await store.loadGroup(groupId)
}

onMounted(async () => {
  if (!store.currentGroup) await store.loadGroup(groupId)
  groupName.value = group.value?.name || ''
})
</script>
