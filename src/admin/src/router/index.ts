// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      component: () => import('@/views/AdminLayout.vue'),
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue')
        },
        {
          path: 'menu',
          name: 'MenuManager',
          component: () => import('@/views/MenuManagerView.vue')
        },
        {
          path: 'seats',
          name: 'SeatManager',
          component: () => import('@/views/SeatManagerView.vue')
        }
      ]
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
