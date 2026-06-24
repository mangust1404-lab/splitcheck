<template>
  <div class="min-h-screen px-4 pt-4 pb-24">
    <div v-if="cameraActive" class="fixed inset-0 z-50 bg-black flex flex-col">
      <video ref="videoEl" autoplay playsinline class="flex-1 object-cover" />
      <div class="flex justify-center gap-6 py-6 bg-black/80">
        <button @click="stopCamera" class="w-12 h-12 rounded-full bg-gray-600 text-white text-lg font-bold">✕</button>
        <button @click="capturePhoto" class="w-16 h-16 rounded-full bg-white border-4 border-gray-300"></button>
      </div>
    </div>

    <div v-if="!cameraActive" class="flex items-center gap-2 mb-4">
      <button
        @click="$router.push({ name: 'trip-detail', params: { id: groupId } })"
        class="w-9 h-9 flex-shrink-0 flex items-center justify-center rounded-full bg-gray-100 active:bg-gray-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="text-xl font-bold">{{ t('scanReceipt.title') }}</h1>
    </div>

    <div v-if="!scannedItems.length && !scanning && !cameraActive">
      <div class="flex gap-3">
        <div
          class="flex-1 border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer active:bg-gray-50"
          @click="openCamera"
        >
          <div class="text-3xl mb-1">📷</div>
          <div class="text-gray-500 text-xs">{{ t('scanReceipt.camera') }}</div>
        </div>
        <div
          class="flex-1 border-2 border-dashed border-gray-300 rounded-xl p-6 text-center cursor-pointer active:bg-gray-50"
          @click="galleryInput.click()"
        >
          <div class="text-3xl mb-1">🖼️</div>
          <div class="text-gray-500 text-xs">{{ t('scanReceipt.gallery') }}</div>
        </div>
      </div>
      <input ref="galleryInput" type="file" accept="image/*" class="hidden" @change="handleFile" />
    </div>

    <div v-if="scanning" class="text-center py-16">
      <div class="text-3xl mb-3">🔍</div>
      <div class="text-gray-500 text-sm">{{ t('scanReceipt.scanning') }}</div>
    </div>

    <div v-if="scannedItems.length && !scanning">
      <!-- Expense title and paid-by -->
      <div class="mb-3">
        <input v-model="expenseTitle" type="text" :placeholder="t('scanReceipt.expensePlaceholder')"
          class="w-full font-semibold text-base border-0 border-b border-gray-200 pb-1 outline-none" />
        <div class="flex justify-between items-center mt-1">
          <div class="text-gray-500 text-[11px]">{{ t('scanReceipt.paidBy') }}</div>
          <select v-model="paidById" class="text-xs border border-gray-300 rounded px-2 py-1 outline-none">
            <option v-for="m in members" :key="m.id" :value="m.id">{{ m.display_name }}</option>
          </select>
        </div>
      </div>

      <!-- Detected currency label -->
      <div v-if="detectedCurrency" class="mb-2">
        <span class="inline-block text-[11px] text-gray-500 bg-gray-100 rounded-full px-2.5 py-0.5">
          {{ t('scanReceipt.detectedCurrency', { currency: detectedCurrency }) }}
        </span>
      </div>

      <!-- Hint for multi-select -->
      <div v-if="selectedItems.size === 0 && !activeBrush" class="text-[11px] text-gray-400 mb-1.5">
        {{ t('scanReceipt.selectItems') }}
      </div>

      <!-- Items list -->
      <ReceiptItemRow
        v-for="(item, i) in scannedItems"
        :key="i"
        :item="{ ...item, index: i }"
        :assignees="assignments[i] || []"
        :members="members"
        :currency="displayCurrency"
        :selected="selectedItems.has(i)"
        @tap="handleItemTap(i)"
      />

      <!-- Discount line -->
      <div v-if="receiptDiscount > 0" class="flex justify-between items-center px-2 py-1.5 mt-1 bg-red-50 rounded-lg">
        <span class="text-xs text-red-600">{{ t('scanReceipt.discount') }}</span>
        <span class="text-xs font-semibold text-red-600">-{{ formatAmount(receiptDiscount, displayCurrency) }}</span>
      </div>

      <!-- Totals -->
      <div class="mt-2 space-y-1 px-1">
        <div v-if="detectedTotal > 0 && receiptDiscount > 0" class="flex justify-between text-[11px] text-gray-400">
          <span>{{ t('scanReceipt.itemsTotal') }}</span>
          <span>{{ formatAmount(itemsTotal, displayCurrency) }}</span>
        </div>
        <div v-if="detectedTotal > 0" class="flex justify-between text-xs font-semibold">
          <span>{{ t('scanReceipt.receiptTotal') }}</span>
          <span>{{ formatAmount(detectedTotal, displayCurrency) }}</span>
        </div>
      </div>

      <!-- Assignment progress bar -->
      <div class="mt-3">
        <div class="bg-gray-100 rounded-full h-1.5 overflow-hidden">
          <div class="bg-emerald-500 h-full rounded-full transition-all" :style="{ width: assignedPercent + '%' }" />
        </div>
        <div class="flex justify-between text-[11px] text-gray-500 mt-1">
          <span>{{ t('scanReceipt.assigned') }} {{ formatAmount(assignedTotal, displayCurrency) }}</span>
          <span>{{ t('scanReceipt.remaining') }} {{ formatAmount(remainingTotal, displayCurrency) }}</span>
        </div>
      </div>

      <!-- Brush mode (ParticipantBar) -->
      <div class="mt-3">
        <ParticipantBar
          :members="members"
          :active-brush="activeBrush"
          @brush-tap="handleBrushTap"
          @clear-brush="activeBrush = null"
        />
      </div>

      <!-- Save button -->
      <button
        @click="saveExpense"
        :disabled="saving"
        class="w-full mt-4 bg-primary text-white py-3 rounded-xl font-semibold text-sm disabled:opacity-50"
      >
        {{ saving ? t('scanReceipt.saving') : t('scanReceipt.save') }}
      </button>
    </div>

    <!-- Floating assignment bar when items are selected -->
    <Teleport to="body">
      <Transition name="slide-up">
        <div
          v-if="selectedItems.size > 0"
          class="fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-gray-200 shadow-lg px-4 py-3 pb-safe"
        >
          <div class="flex items-center gap-3">
            <div class="text-xs text-gray-500 flex-shrink-0">
              <span class="font-semibold text-gray-700">{{ t('scanReceipt.selectedCount', { count: selectedItems.size }) }}</span>
              <span class="ml-1">{{ t('scanReceipt.assignTo') }}</span>
            </div>
            <div class="flex gap-1.5 overflow-x-auto">
              <div
                v-for="m in members"
                :key="m.id"
                class="w-9 h-9 rounded-full text-white text-[11px] flex items-center justify-center font-semibold cursor-pointer flex-shrink-0 active:scale-95 transition-transform"
                :style="{ backgroundColor: getColor(m.id) }"
                @click="assignSelectedToMember(m.id)"
              >
                {{ getInitials(m.display_name) }}
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Per-item picker modal (still available) -->
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
import { ref, computed, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGroupsStore } from '../stores/groups'
import { scanReceipt } from '../api/receipts'
import { createExpense } from '../api/expenses'
import { formatAmount } from '../utils/format'
import { useI18n } from '../composables/useI18n'
import { useTelegram } from '../composables/useTelegram'
import ReceiptItemRow from '../components/ReceiptItemRow.vue'
import ParticipantPicker from '../components/ParticipantPicker.vue'
import ParticipantBar from '../components/ParticipantBar.vue'

const route = useRoute()
const router = useRouter()
const store = useGroupsStore()
const { t } = useI18n()
const { showAlert } = useTelegram()
const groupId = Number(route.params.id)

const members = computed(() => store.currentGroup?.members || [])
const groupCurrency = computed(() => store.currentGroup?.base_currency || 'KZT')

const galleryInput = ref(null)
const videoEl = ref(null)
const cameraActive = ref(false)
let mediaStream = null
const scanning = ref(false)
const saving = ref(false)
const scannedItems = ref([])
const assignments = reactive({})
const expenseTitle = ref('')
const paidById = ref(null)
const activeBrush = ref(null)

// Detected currency from API (fallback to group currency)
const detectedCurrency = ref(null)
const displayCurrency = computed(() => detectedCurrency.value || groupCurrency.value)

// Detected total and discount from API
const detectedTotal = ref(0)
const receiptDiscount = ref(0)

// Multi-select state
const selectedItems = ref(new Set())

const pickerVisible = ref(false)
const pickerItemIndex = ref(null)
const pickerCurrentAssignees = computed(() => assignments[pickerItemIndex.value] || [])

// Items total (sum of all item rows, before discount)
const itemsTotal = computed(() =>
  scannedItems.value.reduce((sum, item) => sum + Number(item.price) * item.quantity, 0)
)

// Use detected total if available, otherwise computed items total
const receiptTotal = computed(() => detectedTotal.value > 0 ? detectedTotal.value : itemsTotal.value)

const assignedTotal = computed(() => {
  let total = 0
  for (const [idx, memberIds] of Object.entries(assignments)) {
    if (memberIds.length > 0) {
      const item = scannedItems.value[idx]
      if (item) total += Number(item.price) * item.quantity
    }
  }
  return total
})
const remainingTotal = computed(() => receiptTotal.value - assignedTotal.value)
const assignedPercent = computed(() =>
  receiptTotal.value > 0 ? (assignedTotal.value / receiptTotal.value) * 100 : 0
)

// Color/initials helpers (shared with ParticipantBar)
const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
function getColor(id) { return colors[id % colors.length] }
function getInitials(name) { return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase() }

async function openCamera() {
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' },
      audio: false,
    })
    cameraActive.value = true
    // Wait for videoEl to mount
    await new Promise((r) => setTimeout(r, 50))
    if (videoEl.value) {
      videoEl.value.srcObject = mediaStream
    }
  } catch (e) {
    // Camera not available — fall back to file input
    galleryInput.value.click()
  }
}

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((t) => t.stop())
    mediaStream = null
  }
  cameraActive.value = false
}

async function capturePhoto() {
  if (!videoEl.value) return
  const video = videoEl.value
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext('2d').drawImage(video, 0, 0)
  stopCamera()

  const blob = await new Promise((r) => canvas.toBlob(r, 'image/jpeg', 0.85))
  const file = new File([blob], 'receipt.jpg', { type: 'image/jpeg' })
  await processFile(file)
}

async function handleFile(event) {
  const file = event.target.files[0]
  if (!file) return
  await processFile(file)
}

async function processFile(file) {
  scanning.value = true
  try {
    const result = await scanReceipt(file)

    // Store detected currency if present
    if (result.currency) {
      detectedCurrency.value = result.currency
    }

    // Store detected total and discount
    detectedTotal.value = Number(result.total) || 0
    receiptDiscount.value = Number(result.discount) || 0

    // Expand qty>1 items into individual unit rows
    const expanded = []
    result.items.forEach(item => {
      if (item.quantity > 1) {
        for (let i = 1; i <= item.quantity; i++) {
          expanded.push({ name: `${item.name} (${i})`, price: item.price, quantity: 1 })
        }
      } else {
        expanded.push(item)
      }
    })

    scannedItems.value = expanded
    expenseTitle.value = t('scanReceipt.defaultTitle')
    expanded.forEach((_, i) => { assignments[i] = [] })

    // Reset selection
    selectedItems.value = new Set()
  } catch (e) {
    const detail = e.response?.data?.detail || t('scanReceipt.scanFailed')
    showAlert(detail)
  } finally {
    scanning.value = false
  }
}

function handleItemTap(index) {
  if (activeBrush.value !== null) {
    // Brush mode: exclusive assignment — toggle this member only
    const memberId = activeBrush.value
    const current = assignments[index] || []
    if (current.includes(memberId)) {
      assignments[index] = []
    } else {
      assignments[index] = [memberId]
    }
  } else {
    // Multi-select mode: toggle item selection
    const next = new Set(selectedItems.value)
    if (next.has(index)) {
      next.delete(index)
    } else {
      next.add(index)
    }
    selectedItems.value = next
  }
}

function assignSelectedToMember(memberId) {
  // Exclusive: replace assignment with this single member
  for (const index of selectedItems.value) {
    assignments[index] = [memberId]
  }
  // Clear selection after assignment
  selectedItems.value = new Set()
}

function handlePickerAssign(memberIds) {
  // Exclusive: keep only the last selected member
  assignments[pickerItemIndex.value] = memberIds.length > 0 ? [memberIds[memberIds.length - 1]] : []
}

function handleBrushTap(memberId) {
  // Entering brush mode clears multi-select
  selectedItems.value = new Set()
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

    // Discount ratio: if receipt has discount, proportionally reduce each share
    const rawItemsSum = scannedItems.value.reduce((s, item) => s + Number(item.price) * item.quantity, 0)
    const discountRatio = rawItemsSum > 0 ? receiptTotal.value / rawItemsSum : 1

    const shares = []
    scannedItems.value.forEach((item, i) => {
      const memberIds = assignments[i] || []
      if (memberIds.length === 0) return
      const itemTotal = Number(item.price) * item.quantity * discountRatio
      const perPerson = Math.floor(itemTotal * 100 / memberIds.length) / 100
      const remainder = Math.round((itemTotal - perPerson * memberIds.length) * 100) / 100
      memberIds.forEach((memberId, j) => {
        const amt = j === 0 ? perPerson + remainder : perPerson
        shares.push({ member_id: memberId, amount: amt.toFixed(2) })
      })
    })

    await createExpense(groupId, {
      title: expenseTitle.value,
      total_amount: String(receiptTotal.value),
      currency: displayCurrency.value,
      paid_by_id: paidById.value,
      split_type: 'by_items',
      items,
      shares,
    })
    router.push({ name: 'trip-detail', params: { id: groupId } })
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  if (!store.currentGroup) await store.loadGroup(groupId)
  if (members.value.length > 0) paidById.value = members.value[0].id
})

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped>
/* Floating bar slide-up transition */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.2s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

/* Safe area padding for devices with home indicator */
.pb-safe {
  padding-bottom: max(0.75rem, env(safe-area-inset-bottom));
}
</style>
