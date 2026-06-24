<template>
  <div class="min-h-screen px-4 pt-4 pb-8">
    <div class="flex items-center gap-2 mb-4">
      <button
        @click="$router.push({ name: 'trip-detail', params: { id: groupId } })"
        class="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-full bg-gray-100 active:bg-gray-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="text-xl font-bold truncate">{{ expense?.title }}</h1>
    </div>

    <div v-if="loading" class="text-center text-gray-400 py-16 text-sm">{{ t('expenseDetail.loading') }}</div>

    <div v-else-if="expense">
      <!-- Summary card -->
      <div class="bg-gray-50 rounded-xl p-4 mb-4">
        <div class="flex justify-between items-start">
          <div>
            <div class="text-2xl font-bold">{{ formatAmount(expense.total_amount, expense.currency) }}</div>
            <div v-if="expense.currency !== groupCurrency && Number(expense.exchange_rate) !== 1" class="text-xs text-gray-400 mt-0.5">
              {{ t('expenseDetail.rate') }}: 1 {{ expense.currency }} = {{ Number(expense.exchange_rate).toFixed(4) }} {{ groupCurrency }}
            </div>
          </div>
          <div class="text-right">
            <div class="text-xs text-gray-500">{{ formatDate(expense.created_at) }}</div>
            <div class="text-xs text-gray-400 mt-0.5">{{ expense.split_type }}</div>
          </div>
        </div>
        <div class="mt-3 flex items-center gap-2">
          <div
            class="w-7 h-7 rounded-full text-white text-[10px] flex items-center justify-center font-semibold"
            :style="{ backgroundColor: getColor(expense.paid_by_id) }"
          >
            {{ getInitials(paidByName) }}
          </div>
          <div class="text-sm text-gray-600">{{ t('expenseDetail.paidBy', { name: paidByName }) }}</div>
        </div>
      </div>

      <!-- Items section -->
      <div v-if="expense.items && expense.items.length > 0" class="mb-4">
        <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">{{ t('expenseDetail.items') }}</div>
        <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
          <div
            v-for="item in expense.items"
            :key="item.id"
            class="flex justify-between items-center px-3 py-2.5 border-b border-gray-50 last:border-b-0"
          >
            <div class="flex-1 min-w-0">
              <div class="text-sm truncate">{{ item.name }}</div>
              <div v-if="item.quantity > 1" class="text-[11px] text-gray-400">x{{ item.quantity }}</div>
            </div>
            <div class="text-sm font-medium ml-3">{{ formatAmount(Number(item.price) * item.quantity, expense.currency) }}</div>
          </div>
        </div>
      </div>

      <!-- Distribution section -->
      <div v-if="expense.shares && expense.shares.length > 0">
        <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">{{ t('expenseDetail.distribution') }}</div>
        <div class="bg-white border border-gray-100 rounded-xl overflow-hidden">
          <div
            v-for="share in mergedShares"
            :key="share.member_id"
            class="flex items-center gap-3 px-3 py-2.5 border-b border-gray-50 last:border-b-0"
          >
            <div
              class="w-8 h-8 rounded-full text-white text-[11px] flex items-center justify-center font-semibold flex-shrink-0"
              :style="{ backgroundColor: getColor(share.member_id) }"
            >
              {{ getInitials(memberName(share.member_id)) }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium truncate">{{ memberName(share.member_id) }}</div>
            </div>
            <div class="text-sm font-semibold">{{ formatAmount(share.amount, expense.currency) }}</div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="mt-6 space-y-2">
        <router-link
          :to="{ name: 'add-expense', params: { id: groupId }, query: { edit: expenseId } }"
          class="block w-full text-center bg-primary text-white py-2.5 rounded-xl text-sm font-semibold no-underline"
        >
          {{ t('expenseDetail.edit') }}
        </router-link>
        <button
          @click="handleDelete"
          :disabled="deleting"
          class="w-full border border-red-300 text-red-500 py-2.5 rounded-xl text-sm font-semibold disabled:opacity-50"
        >
          {{ deleting ? t('expenseDetail.deleting') : t('expenseDetail.delete') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '../stores/groups'
import { getExpense, deleteExpense } from '../api/expenses'
import { formatAmount, formatDate } from '../utils/format'
import { useI18n } from '../composables/useI18n'

const route = useRoute()
const router = useRouter()
const store = useGroupsStore()
const { t } = useI18n()

const groupId = Number(route.params.id)
const expenseId = Number(route.params.expenseId)

const expense = ref(null)
const loading = ref(true)
const deleting = ref(false)

const members = computed(() => store.currentGroup?.members || [])
const groupCurrency = computed(() => store.currentGroup?.base_currency || 'KZT')

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name ? name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() : '?' }

const paidByName = computed(() => {
  const m = members.value.find(m => m.id === expense.value?.paid_by_id)
  return m?.display_name || '?'
})

function memberName(memberId) {
  const m = members.value.find(m => m.id === memberId)
  return m?.display_name || `#${memberId}`
}

// Merge shares by member_id (sum amounts for same member)
const mergedShares = computed(() => {
  if (!expense.value?.shares) return []
  const map = {}
  for (const share of expense.value.shares) {
    if (map[share.member_id]) {
      map[share.member_id].amount = Number(map[share.member_id].amount) + Number(share.amount)
    } else {
      map[share.member_id] = { member_id: share.member_id, amount: Number(share.amount) }
    }
  }
  return Object.values(map).sort((a, b) => b.amount - a.amount)
})

async function handleDelete() {
  if (!confirm(t('expenseDetail.deleteConfirm'))) return
  deleting.value = true
  try {
    await deleteExpense(expenseId)
    router.push({ name: 'trip-detail', params: { id: groupId } })
  } catch (e) {
    deleting.value = false
  }
}

onMounted(async () => {
  if (!store.currentGroup) await store.loadGroup(groupId)
  try {
    expense.value = await getExpense(expenseId)
  } catch (e) {
    // fallback — stay on empty page
  } finally {
    loading.value = false
  }
})
</script>
