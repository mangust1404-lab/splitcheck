<template>
  <div
    class="rounded-lg p-2.5 mb-1.5 cursor-pointer active:opacity-80 transition-colors"
    :class="rowClass"
    @click="$emit('tap', item.index)"
  >
    <div class="flex items-center gap-2">
      <!-- Checkbox for multi-select -->
      <div
        class="w-5 h-5 rounded border-2 flex-shrink-0 flex items-center justify-center transition-colors"
        :class="selected
          ? 'bg-primary border-primary text-white'
          : 'border-gray-300 bg-white'"
      >
        <svg v-if="selected" class="w-3 h-3" viewBox="0 0 12 12" fill="none">
          <path d="M2 6l3 3 5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- Item name -->
      <div class="flex-1 min-w-0">
        <div class="font-medium text-sm truncate">{{ item.name }}</div>
      </div>

      <!-- Assigned member avatars -->
      <div class="flex items-center gap-1.5 flex-shrink-0">
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
  selected: { type: Boolean, default: false },
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

const rowClass = computed(() => {
  if (props.selected) return 'bg-primary/10 border border-primary/40'
  if (props.assignees.length > 0) return 'bg-emerald-50 border border-emerald-200'
  return 'bg-amber-50 border border-amber-200'
})
</script>
