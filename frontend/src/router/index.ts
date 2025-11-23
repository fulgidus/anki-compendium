import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { requiresAuth: false },
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import('@/views/auth/LoginPage.vue'),
        meta: { requiresAuth: false }
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('@/views/auth/RegisterPage.vue'),
        meta: { requiresAuth: false }
      }
    ]
  },
  {
    path: '/',
    component: () => import('@/components/common/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/dashboard/DashboardPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'upload',
        name: 'upload',
        component: () => import('@/views/upload/UploadPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'jobs',
        name: 'jobs',
        component: () => import('@/views/jobs/JobsPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'decks',
        name: 'decks',
        component: () => import('@/views/decks/DecksPage.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('@/views/profile/ProfilePage.vue'),
        meta: { requiresAuth: true }
      }
    ]
  },
  {
    path: '/home',
    name: 'home',
    component: () => import('@/views/HomePage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundPage.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guard for authentication
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // Redirect to login if route requires auth and user is not authenticated
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if ((to.name === 'login' || to.path === '/auth/login') && authStore.isAuthenticated) {
    // Redirect to dashboard if already logged in
    next({ name: 'dashboard' })
  } else if (to.path === '/' && !authStore.isAuthenticated) {
    // Redirect unauthenticated users from root to login
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
