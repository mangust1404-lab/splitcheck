<template>
  <div class="min-h-screen pb-24">
    <div class="text-center pt-4 pb-2 px-4">
      <div class="font-bold text-lg">{{ group?.name }}</div>
      <div class="text-gray-500 text-xs">{{ group?.base_currency }}</div>
    </div>

    <div class="flex gap-1 px-4 mb-3">
      <button
        v-for="t in ['expenses', 'balances', 'settlements']"
        :key="t"
        @click="tab = t"
        class="flex-1 py-2 rounded-lg text-xs font-semibold transition-colors"
        :class="tab === t ? 'bg-primary text-white' : 'bg-gray-100 text-gray-500'"
      >
        {{ t === 'expenses' ? 'Expenses' : t === 'balances' ? 'Balances' : 'Settlements' }}
      </button>
    </div>

    <div v-if="tab === 'expenses'" class="px-4">
      <ExpenseItem v-for="expense in expenses" :key="expense.id" :expense="expense" :members="group?.members || []" />
      <div v-if="expenses.length === 0" class="text-center text-gray-400 py-12 text-sm">No expenses yet</div>
    </div>

    <div v-if="tab === 'balances'" class="px-4">
      <div class="text-center mb-4">
        <div class="text-[11px] text-gray-500 uppercase tracking-wide">Total Spending</div>
        <div class="text-2xl font-bold">{{ formatAmount(totalSpending, group?.base_currency) }}</div>
      </div>
      <BalanceBar
        v-for="(b, i) in balances"
        :key="b.member_id"
        :balance="b"
        :max-abs-balance="maxAbsBalance"
        :currency="group?.base_currency"
        :color="memberColor(b.member_id)"
      />
    </div>

    <div v-if="tab === 'settlements'" class="px-4">
      <SettlementCard v-for="s in settlements" :key="s.id" :settlement="s" @mark-paid="handleMarkPaid" @remind="handleRemind" />
      <div v-if="settlements.length === 0" class="text-center text-gray-400 py-12 text-sm">All settled!</div>
    </div>

    <div class="fixed bottom-4 left-4 right-4 flex gap-2">
      <router-link
        :to="{ name: 'scan-receipt', params: { id: groupId } }"
        class="flex-1 bg-primary text-white py-3 rounded-xl text-center text-sm font-semibold no-underline"
      >
        Scan Receipt
      </router-link>
      <router-link
        :to="{ name: 'add-expense', params: { id: groupId } }"
        class="flex-1 bg-gray-100 py-3 rounded-xl text-center text-sm font-semibold no-underline"
      >
        Manual
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useGroupsStore } from '../stores/groups'
import { fetchExpenses } from '../api/expenses'
import { fetchBalances, fetchSettlements, updateSettlement } from '../api/settlements'
import { formatAmount } from '../utils/format'
import ExpenseItem from '../components/ExpenseItem.vue'
import BalanceBar from '../components/BalanceBar.vue'
import SettlementCard from '../components/SettlementCard.vue'
import client from '../api/client'

const route = useRoute()
const store = useGroupsStore()
const groupId = Number(route.params.id)

const tab = ref('expenses')
const expenses = ref([])
const balances = ref([])
const settlements = ref([])

const group = computed(() => store.currentGroup)

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function memberColor(id) { return colors[id % colors.length] }

const totalSpending = computed(() =>
  expenses.value.reduce((sum, e) => sum + Number(e.total_amount), 0)
)

const maxAbsBalance = computed(() =>
  Math.max(...balances.value.map((b) => Math.abs(Number(b.balance))), 1)
)

async function handleMarkPaid(settlementId) {
  await updateSettlement(settlementId, { is_settled: true })
  settlements.value = await fetchSettlements(groupId)
}

async function handleRemind(settlement) {
  try {
    await client.post(`/api/settlements/${settlement.id}/remind`)
    alert('Reminder sent!')
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to send reminder')
  }
}

onMounted(async () => {
  await store.loadGroup(groupId)
  expenses.value = await fetchExpenses(groupId)
  balances.value = await fetchBalances(groupId)
  settlements.value = await fetchSettlements(groupId)
})
</script>
