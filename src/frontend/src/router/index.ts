import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'menu',
    component: () => import('@/views/MenuView.vue')
  },
  {
    path: '/item/:id',
    name: 'item-detail',
    component: () => import('@/views/ItemDetailView.vue')
  },
  {
    path: '/cart',
    name: 'cart',
    component: () => import('@/views/CartView.vue')
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: () => import('@/views/CheckoutView.vue')
  },
  {
    path: '/payment/:orderId',
    name: 'payment',
    component: () => import('@/views/PaymentView.vue')
  },
  {
    path: '/order/:orderId/confirm',
    name: 'order-confirm',
    component: () => import('@/views/OrderConfirmView.vue')
  },
  {
    path: '/order/:orderId/status',
    name: 'order-status',
    component: () => import('@/views/OrderStatusView.vue')
  },
  {
    path: '/orders/history',
    name: 'order-history',
    component: () => import('@/views/OrderHistoryView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior() {
    return { top: 0 }
  },
  routes
})

export default router
