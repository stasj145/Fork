import { createRouter, createWebHistory } from 'vue-router'
import LogView from '../views/LogView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/today',
      name: 'today',
      component: () => import('../views/TodayView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/log',
      name: 'log',
      component: LogView,
      meta: { requiresAuth: true },
    },
    {
      path: '/food',
      name: 'food',
      component: () => import('../views/FoodView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/activity',
      name: 'activity',
      component: () => import('../views/ActivityView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

// Add navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.path === '/' && authStore.user) {
    return next('/today') // Redirect to dashboard instead of showing login
  }

  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!authStore.user) {
      // NOTE: Because we only check if a user store exists in the localStorage it is in theory
      // possible to add a fake "user" entry to localStorage and be able to pass this check, going
      //  past the login page without actually logging in. HOWEVER i dont really care to fix this
      // right now, as this does not allow any access to the data because JWT token authentication
      // fails. So really all it does is allow to see (some) of the ui.
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
