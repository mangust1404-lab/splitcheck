<template>
  <div class="min-h-screen px-4 pt-4 pb-24">
    <div v-if="!scannedItems.length && !scanning">
      <h1 class="text-xl font-bold mb-4">Scan Receipt</h1>
      <div
        class="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer active:bg-gray-50"
        @click="$refs.fileInput.click()"
      >
        <div class="text-4xl mb-2">📷</div>
        <div class="text-gray-500 text-sm">Tap to take a photo or choose from gallery</div>
      </div>
      <input ref="fileInput" type="file" accept="image/*" capture="environment" class="hidden" @change="handleFile" />
    </div>

    <div v-if="scanning" class="text-center py-16">
      <div class="text-3xl mb-3">🔍</div>
      <div class="text-gray-500 text-sm">Scanning receipt...</div>
    </div>

    <div v-if="scannedItems.length && !scanning">
      <div class="mb-3">
        <input v-model="expenseTitle" type="text" placeholder="Expense title"
          class="w-full font-semibold text-base border-0 border-b border-gray-200 pb-1 outline-none" />
        <div class="flex justify-between items-center mt-1">
          <div class="text-gray-500 text-[11px]">Paid by:</div>
          <select v-model="paidById" class="text-xs border border-gray-300 rounded px-2 py-1 outline-none">
            <option v-for="m in members" :key="m.id" :value="m.id">{{ m.display_name }}</option>
          </select>
        </div>
      </div>

      <ReceiptItemRow
        v-for="(item, i) in scannedItems"
        :key="i"
        :item="{ ...item, index: i }"
        :assignees="assignments[i] || []"
        :members="members"
        :currency="currency"
        @tap="handleItemTap(i)"
      />

      <div class="mt-3">
        <div class="bg-gray-100 rounded-full h-1.5 overflow-hidden">
          <div class="bg-emerald-500 h-full rounded-full transition-all" :style="{ width: assignedPercent + '%' }" />
        </div>
        <div class="flex justify-between text-[11px] text-gray-500 mt-1">
          <span>Assigned: {{ formatAmount(assignedTotal, currency) }}</span>
          <span>Remaining: {{ formatAmount(remainingTotal, currency) }}</span>
        </div>
      </div>

      <div class="mt-3">
        <ParticipantBar
          :members="members"
          :active-brush="activeBrush"
          @brush-tap="handleBrushTap"
          @clear-brush="activeBrush = null"
        />
      </div>

      <button
        @click="saveExpense"
        :disabled="saving"
        class="w-full mt-4 bg-primary text-white py-3 rounded-xl font-semibold text-sm disabled:opacity-50"
      >
        {{ saving ? 'Saving...' : 'Save Expense' }}
      </button>
    </div>

    <ParticipantPicker
      :visible="pickerVisible"
      :members="members"
      :current-assignees="pickerCurrentAssignees"
      @assign="handlePickerAssign"
      @close="pickerVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '../stores/groups'
import { scanReceipt } from '../api/receipts'
import { createExpense } from '../api/expenses'
import { formatAmount } from '../utils/format'
import ReceiptItemRow from '../components/ReceiptItemRow.vue'
import ParticipantPicker from '../components/ParticipantPicker.vue'
import ParticipantBar from '../components/ParticipantBar.vue'

const route = useRoute()
const router = useRouter()
const store = useGroupsStore()
const groupId = Number(route.params.id)

const members = computed(() => store.currentGroup?.members || [])
const currency = computed(() => store.currentGroup?.base_currency || 'KZT')

const scanning = ref(false)
const saving = ref(false)
const scannedItems = ref([])
const assignments = reactive({})
const expenseTitle = ref('')
const paidById = ref(null)
const activeBrush = ref(null)

const pickerVisible = ref(false)
const pickerItemIndex = ref(null)
const pickerCurrentAssignees = computed(() => assignments[pickerItemIndex.value] || [])

const receiptTotal = computed(() =>
  scannedItems.value.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0)
)
const assignedTotal = computed(() => {
  let total = 0
  for (const [idx, memberIds] of Object.entries(assignments)) {
    if (memberIds.length > 0) {
      const item = scannedItems.value[idx]
      total += Number(item.price) * item.quantity
    }
  }
  return total
})
const remainingTotal = computed(() => receiptTotal.value - assignedTotal.value)
const assignedPercent = computed(() =>
  receiptTotal.value > 0 ? (assignedTotal.value / receiptTotal.value) * 100 : 0
)

async function handleFile(event) {
  const file = event.target.files[0]
  if (!file) return
  scanning.value = true
  try {
    const result = await scanReceipt(file)
    scannedItems.value = result.items
    expenseTitle.value = 'Scanned receipt'
    result.items.forEach((_, i) => { assignments[i] = [] })
  } finally {
    scanning.value = false
  }
}

function handleItemTap(index) {
  if (activeBrush.value !== null) {
    const memberId = activeBrush.value
    const current = assignments[index] || []
    if (current.includes(memberId)) {
      assignments[index] = current.filter((id) => id !== memberId)
    } else {
      assignments[index] = [...current, memberId]
    }
  } else {
    pickerItemIndex.value = index
    pickerVisible.value = true
  }
}

function handlePickerAssign(memberIds) {
  assignments[pickerItemIndex.value] = memberIds
}

function handleBrushTap(memberId) {
  activeBrush.value = activeBrush.value === memberId ? null : memberId
}

async function saveExpense() {
  saving.value = true
  try {
    const items = scannedItems.value.map((item) => ({
      name: item.name,
      price: String(item.price),
      quantity: item.quantity,
    }))

    const shares = []
    scannedItems.value.forEach((item, i) => {
      const memberIds = assignments[i] || []
      if (memberIds.length === 0) return
      const itemTotal = Number(item.price) * item.quantity
      const perPerson = (itemTotal / memberIds.length).toFixed(2)
      memberIds.forEach((memberId) => {
        shares.push({ member_id: memberId, amount: perPerson })
      })
    })

    await createExpense(groupId, {
      title: expenseTitle.value,
      total_amount: String(receiptTotal.value),
      currency: currency.value,
      paid_by_id: paidById.value,
      split_type: 'by_items',
      items,
      shares,
    })
    router.back()
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  if (!store.currentGroup) await store.loadGroup(groupId)
  if (members.value.length > 0) paidById.value = members.value[0].id
})
</script>
