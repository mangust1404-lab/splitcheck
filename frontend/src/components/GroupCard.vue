<template>
  <router-link
    :to="{ name: 'trip-detail', params: { id: group.id } }"
    class="block bg-gray-50 rounded-xl p-4 border-l-4 active:bg-gray-100 no-underline"
    :class="group.status === 'archived' ? 'border-gray-300 opacity-60' : 'border-primary'"
  >
    <div class="flex justify-between items-start">
      <div>
        <div class="font-semibold text-[15px]">{{ group.name }}</div>
        <div class="text-gray-500 text-xs mt-0.5">
          {{ group.members.length }} participants · {{ group.base_currency }}
        </div>
      </div>
      <div v-if="group.status === 'archived'" class="text-xs text-gray-400">
        Archived
      </div>
    </div>
    <div class="flex mt-2.5 gap-1">
      <div
        v-for="member in group.members.slice(0, 6)"
        :key="member.id"
        class="w-7 h-7 rounded-full bg-primary text-white text-[10px] flex items-center justify-center font-semibold"
        :style="{ backgroundColor: memberColor(member.id) }"
      >
        {{ initials(member.display_name) }}
      </div>
      <div
        v-if="group.members.length > 6"
        class="w-7 h-7 rounded-full bg-gray-300 text-gray-600 text-[10px] flex items-center justify-center"
      >
        +{{ group.members.length - 6 }}
      </div>
    </div>
  </router-link>
</template>

<script setup>
const props = defineProps({ group: Object })

const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']

function memberColor(id) {
  return colors[id % colors.length]
}

function initials(name) {
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}
</script>
