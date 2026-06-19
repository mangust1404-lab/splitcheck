<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-end justify-center bg-black/30" @click.self="$emit('close')">
    <div class="bg-white w-full max-w-md rounded-t-2xl p-4 pb-8">
      <div class="text-sm font-semibold mb-3">Who had this item?</div>
      <div class="space-y-2">
        <label v-for="m in members" :key="m.id" class="flex items-center gap-3 p-2 rounded-lg active:bg-gray-50">
          <input type="checkbox" :value="m.id" v-model="selected" class="rounded border-gray-300 text-primary focus:ring-primary w-5 h-5" />
          <div class="w-8 h-8 rounded-full text-white text-xs flex items-center justify-center font-semibold" :style="{ backgroundColor: getColor(m.id) }">
            {{ getInitials(m.display_name) }}
          </div>
          <span class="text-sm">{{ m.display_name }}</span>
        </label>
      </div>
      <button @click="$emit('assign', [...selected]); $emit('close')" class="w-full mt-4 bg-primary text-white py-3 rounded-xl font-semibold text-sm">
        Done
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: Boolean,
  members: Array,
  currentAssignees: { type: Array, default: () => [] },
})
defineEmits(['assign', 'close'])

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() }

const selected = ref([])
watch(() => props.currentAssignees, (v) => { selected.value = [...v] }, { immediate: true })
</script>
