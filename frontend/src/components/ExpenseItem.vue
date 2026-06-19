<template>
  <div class="border-b border-gray-100 py-3">
    <div class="flex justify-between">
      <div>
        <div class="font-semibold text-sm">{{ expense.title }}</div>
        <div class="text-gray-500 text-[11px] mt-0.5">
          {{ paidByName }} paid · {{ expense.split_type }}
        </div>
      </div>
      <div class="font-semibold text-sm">
        {{ formatAmount(expense.total_amount, expense.currency) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatAmount } from '../utils/format'

const props = defineProps({
  expense: Object,
  members: { type: Array, default: () => [] },
})

const paidByName = computed(() => {
  const m = props.members.find((m) => m.id === props.expense.paid_by_id)
  return m?.display_name || '?'
})
</script>
