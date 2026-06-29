<template>
  <div class="min-h-screen px-4 pt-4">
    <div class="flex items-center gap-2 mb-4">
      <button
        @click="$router.push({ name: 'my-trips' })"
        class="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-full bg-gray-100 active:bg-gray-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="text-xl font-bold">{{ t('createGroup.title') }}</h1>
    </div>

    <form @submit.prevent="submit" class="space-y-5">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('createGroup.tripName') }}</label>
        <input
          v-model="name"
          type="text"
          :placeholder="t('createGroup.tripPlaceholder')"
          class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
          required
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('createGroup.baseCurrency') }}</label>
        <select
          v-model="currency"
          class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-primary outline-none"
        >
          <option v-for="c in CURRENCIES" :key="c.code" :value="c.code">
            {{ c.symbol }} {{ c.code }} — {{ c.name }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('createGroup.participants') }}</label>
        <div class="space-y-2">
          <div v-for="(member, i) in members" :key="i" class="flex items-center gap-2">
            <input
              v-model="members[i]"
              type="text"
              :placeholder="t('createGroup.participantN', { n: i + 1 })"
              class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary"
            />
            <button
              v-if="members.length > 1"
              type="button"
              @click="members.splice(i, 1)"
              class="text-red-400 text-lg px-2"
            >×</button>
          </div>
        </div>
        <button type="button" @click="members.push('')" class="mt-2 text-primary text-sm font-medium">
          {{ t('createGroup.addParticipant') }}
        </button>
      </div>

      <button
        type="submit"
        :disabled="saving"
        class="w-full bg-primary text-white py-3 rounded-xl font-semibold text-sm disabled:opacity-50"
      >
        {{ saving ? t('createGroup.creating') : t('createGroup.create') }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createGroup, addMember } from '../api/groups'
import { useAuthStore } from '../stores/auth'
import { useCurrency } from '../composables/useCurrency'
import { useI18n } from '../composables/useI18n'

const router = useRouter()
const auth = useAuthStore()
const { CURRENCIES } = useCurrency()
const { t } = useI18n()

const name = ref('')
const currency = ref('KZT')
const members = ref([''])
const saving = ref(false)

async function submit() {
  saving.value = true
  try {
    const group = await createGroup({ name: name.value, base_currency: currency.value })

    // Skip empty names; creator is already added by backend
    const validMembers = members.value.filter((m) => m.trim())
    for (const memberName of validMembers) {
      await addMember(group.id, memberName.trim())
    }

    router.push({ name: 'trip-detail', params: { id: group.id } })
  } finally {
    saving.value = false
  }
}
</script>
