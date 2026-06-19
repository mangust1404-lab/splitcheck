<template>
  <div
    class="rounded-lg p-2.5 mb-1.5 cursor-pointer active:opacity-80 transition-colors"
    :class="assignees.length > 0 ? 'bg-emerald-50 border border-emerald-200' : 'bg-amber-50 border border-amber-200'"
    @click="$emit('tap', item.index)"
  >
    <div class="flex justify-between items-center">
      <div>
        <div class="font-medium text-sm">{{ item.name }}</div>
        <div v-if="item.quantity > 1" class="text-gray-500 text-[11px]">x {{ item.quantity }}</div>
      </div>
      <div class="flex items-center gap-1.5">
        <div class="flex -space-x-1">
          <div
            v-for="memberId in assignees"
            :key="memberId"
            class="w-[22px] h-[22px] rounded-full border-2 border-white text-white text-[9px] flex items-center justify-center"
            :style="{ backgroundColor: getColor(memberId) }"
          >
            {{ getMemberInitials(memberId) }}
          </div>
          <div
            v-if="assignees.length === 0"
            class="w-[22px] h-[22px] rounded-full bg-gray-200 text-gray-400 text-sm flex items-center justify-center"
          >?</div>
        </div>
        <div class="font-semibold text-xs">{{ formatAmount(itemTotal, currency) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatAmount } from '../utils/format'

const props = defineProps({
  item: Object,
  assignees: { type: Array, default: () => [] },
  members: Array,
  currency: String,
})
defineEmits(['tap'])

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function getColor(id) { return colors[id % colors.length] }

function getMemberInitials(id) {
  const m = props.members.find(m => m.id === id)
  if (!m) return '?'
  return m.display_name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

const itemTotal = computed(() => Number(props.item.price) * props.item.quantity)
</script>
