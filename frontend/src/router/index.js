import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'my-trips', component: () => import('../views/MyTrips.vue') },
  { path: '/create', name: 'create-group', component: () => import('../views/CreateGroup.vue') },
  { path: '/trip/:id', name: 'trip-detail', component: () => import('../views/TripDetail.vue') },
  { path: '/trip/:id/expense', name: 'add-expense', component: () => import('../views/AddExpense.vue') },
  { path: '/trip/:id/scan', name: 'scan-receipt', component: () => import('../views/ScanReceipt.vue') },
  { path: '/trip/:id/settings', name: 'group-settings', component: () => import('../views/GroupSettings.vue') },
  { path: '/join/:inviteCode', name: 'join-group', component: () => import('../views/JoinGroup.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
