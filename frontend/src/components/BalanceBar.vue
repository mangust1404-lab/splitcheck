<template>
  <div class="mb-3">
    <div class="flex justify-between items-center mb-1">
      <div class="flex items-center gap-2">
        <div
          class="w-7 h-7 rounded-full text-white text-[10px] flex items-center justify-center font-semibold"
          :style="{ backgroundColor: color }"
        >
          {{ initials }}
        </div>
        <span class="font-medium text-sm">{{ balance.display_name }}</span>
      </div>
      <span
        class="font-semibold text-sm"
        :class="Number(balance.balance) >= 0 ? 'text-emerald-500' : 'text-red-500'"
      >
        {{ Number(balance.balance) >= 0 ? '+' : '' }}{{ formatAmount(balance.balance, currency) }}
      </span>
    </div>
    <div class="bg-gray-100 rounded-full h-2 overflow-hidden">
      <div
        class="h-full rounded-full"
        :class="Number(balance.balance) >= 0 ? 'bg-emerald-500' : 'bg-red-500'"
        :style="{ width: barWidth + '%', float: Number(balance.balance) < 0 ? 'right' : 'left' }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatAmount } from '../utils/format'

const props = defineProps({
  balance: Object,
  maxAbsBalance: Number,
  currency: String,
  color: String,
})

const initials = computed(() =>
  props.balance.display_name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase()
)

const barWidth = computed(() => {
  if (props.maxAbsBalance === 0) return 0
  return (Math.abs(Number(props.balance.balance)) / props.maxAbsBalance) * 100
})
</script>
