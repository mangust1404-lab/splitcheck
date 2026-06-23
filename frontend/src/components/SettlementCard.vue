<template>
  <div
    class="border rounded-xl p-3.5 mb-2.5"
    :class="settlement.is_settled && settlement.confirmed_by_to
      ? 'bg-emerald-50 border-emerald-200'
      : 'bg-white border-gray-200'"
  >
    <div class="flex items-center justify-center gap-3 mb-2.5">
      <div class="text-center">
        <div
          class="w-10 h-10 rounded-full text-white text-xs flex items-center justify-center mx-auto font-semibold"
          :style="{ backgroundColor: fromColor }"
        >
          {{ fromInitials }}
        </div>
        <div class="text-[11px] mt-1">{{ settlement.from_member_name }}</div>
      </div>
      <div class="text-center">
        <div class="font-bold text-base">{{ formatAmount(settlement.amount, settlement.currency) }}</div>
        <div class="text-gray-400 text-lg">&rarr;</div>
      </div>
      <div class="text-center">
        <div
          class="w-10 h-10 rounded-full text-white text-xs flex items-center justify-center mx-auto font-semibold"
          :style="{ backgroundColor: toColor }"
        >
          {{ toInitials }}
        </div>
        <div class="text-[11px] mt-1">{{ settlement.to_member_name }}</div>
      </div>
    </div>

    <div v-if="settlement.is_settled && settlement.confirmed_by_to" class="text-center text-xs text-emerald-600 font-medium">
      {{ t('settlementCard.paidConfirmed') }}
    </div>
    <div v-else class="flex gap-2">
      <button
        @click="$emit('markPaid', settlement.id)"
        class="flex-1 py-2 rounded-lg text-xs font-semibold bg-emerald-500 text-white"
      >
        {{ settlement.is_settled ? t('settlementCard.paid') : t('settlementCard.markPaid') }}
      </button>
      <button
        @click="$emit('remind', settlement)"
        class="flex-1 bg-gray-100 py-2 rounded-lg text-xs text-gray-600 font-semibold"
      >
        {{ t('settlementCard.remind') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatAmount } from '../utils/format'
import { useI18n } from '../composables/useI18n'

const { t } = useI18n()

const props = defineProps({ settlement: Object })
defineEmits(['markPaid', 'remind'])

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase() }

const fromColor = computed(() => getColor(props.settlement.from_member_id))
const toColor = computed(() => getColor(props.settlement.to_member_id))
const fromInitials = computed(() => getInitials(props.settlement.from_member_name))
const toInitials = computed(() => getInitials(props.settlement.to_member_name))
</script>
