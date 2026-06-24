<template>
  <div
    class="border rounded-xl p-3.5 mb-2.5"
    :class="cardClass"
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
        <div class="font-bold text-base" :class="settlement.is_settled ? 'line-through text-gray-400' : ''">{{ formatAmount(settlement.amount, settlement.currency) }}</div>
        <div class="text-lg" :class="settlement.is_settled ? 'text-emerald-500' : 'text-gray-400'">&rarr;</div>
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

    <!-- State: Fully confirmed -->
    <div v-if="settlement.is_settled && settlement.confirmed_by_to" class="text-center text-xs text-emerald-600 font-medium py-1">
      &#10003; {{ t('settlementCard.paidConfirmed') }}
    </div>

    <!-- State: Paid, awaiting confirmation -->
    <div v-else-if="settlement.is_settled" class="space-y-2">
      <div class="text-center text-xs text-emerald-600 font-medium">&#10003; {{ t('settlementCard.paid') }}</div>
      <button
        @click="$emit('markPaid', settlement.id)"
        class="w-full py-2 rounded-lg text-xs font-semibold bg-gray-100 text-gray-500"
      >
        {{ t('settlementCard.undo') }}
      </button>
    </div>

    <!-- State: Not paid -->
    <div v-else class="flex gap-2">
      <button
        @click="$emit('markPaid', settlement.id)"
        class="flex-1 py-2 rounded-lg text-xs font-semibold bg-emerald-500 text-white"
      >
        {{ t('settlementCard.markPaid') }}
      </button>
      <button
        @click="handleRemind"
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
const emit = defineEmits(['markPaid', 'remind'])

function handleRemind() {
  if (!props.settlement.from_has_telegram) {
    alert(t('settlementCard.noTelegram', { name: props.settlement.from_member_name }))
    return
  }
  emit('remind', props.settlement)
}

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase() }

const fromColor = computed(() => getColor(props.settlement.from_member_id))
const toColor = computed(() => getColor(props.settlement.to_member_id))
const fromInitials = computed(() => getInitials(props.settlement.from_member_name))
const toInitials = computed(() => getInitials(props.settlement.to_member_name))

const cardClass = computed(() => {
  if (props.settlement.is_settled && props.settlement.confirmed_by_to) return 'bg-emerald-50 border-emerald-200'
  if (props.settlement.is_settled) return 'bg-emerald-50/50 border-emerald-200'
  return 'bg-white border-gray-200'
})
</script>
