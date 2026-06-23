<template>
  <div class="min-h-screen pb-24">
    <div class="flex items-center pt-4 pb-2 px-4 gap-2">
      <button
        @click="$router.push({ name: 'my-trips' })"
        class="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-full bg-gray-100 active:bg-gray-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <div class="text-center flex-1 min-w-0">
        <div class="font-bold text-lg truncate">{{ group?.name }}</div>
        <div class="text-gray-500 text-xs">{{ group?.base_currency }}</div>
      </div>
      <button
        @click="shareInvite"
        class="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-full bg-gray-100 active:bg-gray-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4.5 h-4.5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8M16 6l-4-4-4 4M12 2v13" />
        </svg>
      </button>
      <router-link
        :to="{ name: 'group-settings', params: { id: groupId } }"
        class="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-full bg-gray-100 active:bg-gray-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </router-link>
    </div>

    <div class="flex gap-1 px-4 mb-3">
      <button
        v-for="tabKey in ['expenses', 'balances', 'settlements']"
        :key="tabKey"
        @click="tab = tabKey"
        class="flex-1 py-2 rounded-lg text-xs font-semibold transition-colors"
        :class="tab === tabKey ? 'bg-primary text-white' : 'bg-gray-100 text-gray-500'"
      >
        {{ t('tripDetail.' + tabKey) }}
      </button>
    </div>

    <div v-if="tab === 'expenses'" class="px-4">
      <ExpenseItem v-for="expense in expenses" :key="expense.id" :expense="expense" :members="group?.members || []" />
      <div v-if="expenses.length === 0" class="text-center text-gray-400 py-12 text-sm">{{ t('tripDetail.noExpenses') }}</div>
    </div>

    <div v-if="tab === 'balances'" class="px-4">
      <div class="text-center mb-4">
        <div class="text-[11px] text-gray-500 uppercase tracking-wide">{{ t('tripDetail.totalSpending') }}</div>
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
      <div v-if="settlements.length === 0" class="text-center text-gray-400 py-12 text-sm">{{ t('tripDetail.allSettled') }}</div>
    </div>

    <div class="fixed bottom-4 left-4 right-4 flex gap-2">
      <router-link
        :to="{ name: 'scan-receipt', params: { id: groupId } }"
        class="flex-1 bg-primary text-white py-3 rounded-xl text-center text-sm font-semibold no-underline"
      >
        {{ t('tripDetail.scanReceipt') }}
      </router-link>
      <router-link
        :to="{ name: 'add-expense', params: { id: groupId } }"
        class="flex-1 bg-gray-100 py-3 rounded-xl text-center text-sm font-semibold no-underline"
      >
        {{ t('tripDetail.manual') }}
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
import { useTelegram } from '../composables/useTelegram'
import { useI18n } from '../composables/useI18n'

const route = useRoute()
const { tg, showAlert, hapticFeedback } = useTelegram()
const { t } = useI18n()
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
    alert(t('tripDetail.reminderSent'))
  } catch (e) {
    alert(e.response?.data?.detail || t('tripDetail.reminderFailed'))
  }
}

function shareInvite() {
  if (!group.value) return
  const inviteUrl = `https://t.me/SplitCheckanalog_bot/app?startapp=join_${group.value.invite_code}`
  hapticFeedback('impact')

  // Copy invite link to clipboard (Telegram Mini Apps lack a native share API)
  navigator.clipboard.writeText(inviteUrl).then(() => {
    showAlert(t('tripDetail.inviteCopied'))
  }).catch(() => {
    showAlert(inviteUrl)
  })
}

onMounted(async () => {
  await store.loadGroup(groupId)
  expenses.value = await fetchExpenses(groupId)
  balances.value = await fetchBalances(groupId)
  settlements.value = await fetchSettlements(groupId)
})
</script>
