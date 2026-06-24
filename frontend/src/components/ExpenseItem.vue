<template>
  <router-link
    :to="{ name: 'expense-detail', params: { id: expense.group_id, expenseId: expense.id } }"
    class="block border-b border-gray-100 py-3 no-underline active:bg-gray-50 -mx-1 px-1 rounded"
  >
    <div class="flex justify-between">
      <div>
        <div class="font-semibold text-sm text-gray-900">{{ expense.title }}</div>
        <div class="text-gray-500 text-[11px] mt-0.5">
          {{ t('expenseItem.paid', { name: paidByName, splitType: expense.split_type }) }}
        </div>
      </div>
      <div class="flex items-center gap-1.5">
        <div class="text-right">
          <div class="font-semibold text-sm text-gray-900">
            {{ formatAmount(expense.total_amount, expense.currency) }}
          </div>
          <div v-if="isConverted" class="text-[10px] text-gray-400">
            {{ formatAmount(convertedAmount, baseCurrency) }}
          </div>
        </div>
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { formatAmount } from '../utils/format'
import { useI18n } from '../composables/useI18n'

const { t } = useI18n()

const props = defineProps({
  expense: Object,
  members: { type: Array, default: () => [] },
  baseCurrency: { type: String, default: 'KZT' },
})

const paidByName = computed(() => {
  const m = props.members.find((m) => m.id === props.expense.paid_by_id)
  return m?.display_name || '?'
})

const isConverted = computed(() => {
  const rate = Number(props.expense.exchange_rate)
  return rate !== 1 && props.expense.currency !== props.baseCurrency
})

const convertedAmount = computed(() =>
  Number(props.expense.total_amount) * Number(props.expense.exchange_rate)
)
</script>
