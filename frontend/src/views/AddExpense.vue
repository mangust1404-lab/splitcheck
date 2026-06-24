<template>
  <div class="min-h-screen px-4 pt-4">
    <div class="flex items-center gap-2 mb-4">
      <button
        @click="goBack"
        class="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-full bg-gray-100 active:bg-gray-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="text-xl font-bold">{{ isEdit ? t('addExpense.editTitle') : t('addExpense.title') }}</h1>
    </div>

    <div v-if="loadingExpense" class="text-center text-gray-400 py-16 text-sm">{{ t('expenseDetail.loading') }}</div>

    <form v-else @submit.prevent="submit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('addExpense.expenseTitle') }}</label>
        <input v-model="title" type="text" :placeholder="t('addExpense.titlePlaceholder')" required
          class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary" />
      </div>

      <div class="flex gap-3">
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('addExpense.amount') }}</label>
          <input v-model="amount" type="number" step="0.01" min="0" required
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-primary" />
        </div>
        <div class="w-24">
          <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('addExpense.currency') }}</label>
          <select v-model="currency"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none">
            <option v-for="c in CURRENCIES" :key="c.code" :value="c.code">{{ c.code }}</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('addExpense.paidBy') }}</label>
        <select v-model="paidById" required
          class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm outline-none">
          <option v-for="m in members" :key="m.id" :value="m.id">{{ m.display_name }}</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('addExpense.splitMode') }}</label>
        <div class="flex gap-2">
          <button type="button" v-for="mode in ['equal', 'custom']" :key="mode"
            @click="splitType = mode"
            class="flex-1 py-2 rounded-lg text-xs font-semibold border"
            :class="splitType === mode ? 'bg-primary text-white border-primary' : 'bg-white text-gray-600 border-gray-300'">
            {{ mode === 'equal' ? t('addExpense.equal') : t('addExpense.custom') }}
          </button>
        </div>
      </div>

      <div v-if="splitType === 'equal'">
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('addExpense.splitAmong') }}</label>
        <div class="space-y-2">
          <label v-for="m in members" :key="m.id" class="flex items-center gap-2 text-sm">
            <input type="checkbox" :value="m.id" v-model="splitAmong"
              class="rounded border-gray-300 text-primary focus:ring-primary" />
            {{ m.display_name }}
          </label>
        </div>
      </div>

      <div v-if="splitType === 'custom'">
        <label class="block text-sm font-medium text-gray-700 mb-1">{{ t('addExpense.amounts') }}</label>
        <div class="space-y-2">
          <div v-for="m in members" :key="m.id" class="flex items-center gap-2">
            <span class="text-sm w-24 truncate">{{ m.display_name }}</span>
            <input v-model="customAmounts[m.id]" type="number" step="0.01" min="0" placeholder="0"
              class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none" />
          </div>
        </div>
        <div class="mt-2 text-xs" :class="remainderColor">
          {{ t('addExpense.assigned', { assigned: assignedTotal, total: amount || 0, remaining: remainder }) }}
        </div>
        <button v-if="Number(remainder) > 0" type="button" @click="splitRemainder"
          class="mt-1 text-primary text-xs font-medium">
          {{ t('addExpense.splitRemainder') }}
        </button>
      </div>

      <button type="submit" :disabled="saving"
        class="w-full bg-primary text-white py-3 rounded-xl font-semibold text-sm disabled:opacity-50">
        {{ saving ? t('addExpense.saving') : (isEdit ? t('addExpense.update') : t('addExpense.save')) }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '../stores/groups'
import { createExpense, getExpense } from '../api/expenses'
import { useCurrency } from '../composables/useCurrency'
import { useI18n } from '../composables/useI18n'
import client from '../api/client'

const route = useRoute()
const router = useRouter()
const store = useGroupsStore()
const { CURRENCIES } = useCurrency()
const { t } = useI18n()

const groupId = Number(route.params.id)
const editId = route.query.edit ? Number(route.query.edit) : null
const isEdit = !!editId

const members = computed(() => store.currentGroup?.members || [])

const title = ref('')
const amount = ref('')
const currency = ref('')
const paidById = ref(null)
const splitType = ref('equal')
const splitAmong = ref([])
const customAmounts = reactive({})
const saving = ref(false)
const loadingExpense = ref(false)

const assignedTotal = computed(() =>
  Object.values(customAmounts).reduce((sum, v) => sum + (Number(v) || 0), 0).toFixed(2)
)
const remainder = computed(() => ((Number(amount.value) || 0) - Number(assignedTotal.value)).toFixed(2))
const remainderColor = computed(() =>
  Number(remainder.value) === 0 ? 'text-emerald-600' : Number(remainder.value) > 0 ? 'text-amber-600' : 'text-red-500'
)

function goBack() {
  if (isEdit) {
    router.push({ name: 'expense-detail', params: { id: groupId, expenseId: editId } })
  } else {
    router.push({ name: 'trip-detail', params: { id: groupId } })
  }
}

function splitRemainder() {
  const remaining = Number(remainder.value)
  const unassigned = members.value.filter((m) => !customAmounts[m.id] || Number(customAmounts[m.id]) === 0)
  if (unassigned.length === 0) return
  const each = (remaining / unassigned.length).toFixed(2)
  unassigned.forEach((m) => { customAmounts[m.id] = each })
}

async function submit() {
  saving.value = true
  try {
    const payload = {
      title: title.value,
      total_amount: amount.value,
      currency: currency.value,
      paid_by_id: paidById.value,
      split_type: splitType.value,
    }
    if (splitType.value === 'equal') {
      payload.split_among = splitAmong.value
    } else if (splitType.value === 'custom') {
      payload.shares = Object.entries(customAmounts)
        .filter(([, v]) => Number(v) > 0)
        .map(([memberId, amt]) => ({ member_id: Number(memberId), amount: amt }))
    }

    if (isEdit) {
      await client.patch(`/api/expenses/${editId}`, payload)
      router.push({ name: 'expense-detail', params: { id: groupId, expenseId: editId } })
    } else {
      await createExpense(groupId, payload)
      router.push({ name: 'trip-detail', params: { id: groupId } })
    }
  } finally {
    saving.value = false
  }
}

async function loadExpenseForEdit() {
  loadingExpense.value = true
  try {
    const exp = await getExpense(editId)
    title.value = exp.title
    amount.value = String(exp.total_amount)
    currency.value = exp.currency
    paidById.value = exp.paid_by_id

    // Determine split type for edit: by_items and custom both show as "custom"
    if (exp.split_type === 'equal') {
      splitType.value = 'equal'
      // Reconstruct splitAmong from shares
      splitAmong.value = [...new Set(exp.shares.map(s => s.member_id))]
    } else {
      splitType.value = 'custom'
      // Merge shares by member_id into customAmounts
      const merged = {}
      for (const share of exp.shares) {
        merged[share.member_id] = (merged[share.member_id] || 0) + Number(share.amount)
      }
      for (const [memberId, amt] of Object.entries(merged)) {
        customAmounts[memberId] = amt.toFixed(2)
      }
    }
  } finally {
    loadingExpense.value = false
  }
}

onMounted(async () => {
  if (!store.currentGroup) await store.loadGroup(groupId)
  currency.value = store.currentGroup?.base_currency || 'KZT'

  if (isEdit) {
    await loadExpenseForEdit()
  } else {
    members.value.forEach((m) => splitAmong.value.push(m.id))
    if (members.value.length > 0) paidById.value = members.value[0].id
  }
})
</script>
