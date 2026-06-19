<template>
  <div class="flex gap-1.5 items-center p-2 bg-gray-50 rounded-xl">
    <div
      v-for="m in members"
      :key="m.id"
      class="w-9 h-9 rounded-full text-white text-[11px] flex items-center justify-center font-semibold cursor-pointer transition-all"
      :class="activeBrush === m.id ? 'ring-2 ring-offset-2 ring-primary scale-110' : ''"
      :style="{ backgroundColor: getColor(m.id) }"
      @click="$emit('brushTap', m.id)"
      @touchstart.prevent="startLongPress(m.id)"
      @touchend="cancelLongPress"
      @touchcancel="cancelLongPress"
    >
      {{ getInitials(m.display_name) }}
    </div>
    <div class="flex-1" />
    <div v-if="activeBrush" class="text-[10px] text-gray-500">
      Tap items to assign · <button @click="$emit('clearBrush')" class="text-primary font-medium">Done</button>
    </div>
    <div v-else class="text-[10px] text-gray-400">Hold = brush</div>
  </div>
</template>

<script setup>
const props = defineProps({
  members: Array,
  activeBrush: { type: Number, default: null },
})
const emit = defineEmits(['brushTap', 'clearBrush', 'activateBrush'])

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() }

let longPressTimer = null

function startLongPress(memberId) {
  longPressTimer = setTimeout(() => {
    emit('activateBrush', memberId)
  }, 500)
}

function cancelLongPress() {
  clearTimeout(longPressTimer)
}
</script>
