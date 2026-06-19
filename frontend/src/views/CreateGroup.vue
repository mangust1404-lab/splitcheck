<template>
  <div class="min-h-screen px-4 pt-4">
    <h1 class="text-xl font-bold mb-6">New Trip</h1>

    <form @submit.prevent="submit" class="space-y-5">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Trip name</label>
        <input
          v-model="name"
          type="text"
          placeholder="e.g. Bali with friends"
          class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
          required
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Base currency</label>
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
        <label class="block text-sm font-medium text-gray-700 mb-1">Participants</label>
        <div class="space-y-2">
          <div v-for="(member, i) in members" :key="i" class="flex items-center gap-2">
            <input
              v-model="members[i]"
              type="text"
              :placeholder="`Participant ${i + 1}`"
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
          + Add participant
        </button>
      </div>

      <button
        type="submit"
        :disabled="saving"
        class="w-full bg-primary text-white py-3 rounded-xl font-semibold text-sm disabled:opacity-50"
      >
        {{ saving ? 'Creating...' : 'Create Trip' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createGroup, addMember } from '../api/groups'
import { useCurrency } from '../composables/useCurrency'

const router = useRouter()
const { CURRENCIES } = useCurrency()

const name = ref('')
const currency = ref('KZT')
const members = ref([''])
const saving = ref(false)

async function submit() {
  saving.value = true
  try {
    const group = await createGroup({ name: name.value, base_currency: currency.value })

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
