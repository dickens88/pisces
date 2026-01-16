import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layouts/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { getAppConfig } from '@config'
import { redirectToTianyanLogin } from '@/utils/auth'
const config = getAppConfig(import.meta.env, import.meta.env.PROD)

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/errors/ForbiddenView.vue'),
    meta: { title: '访问被拒绝', requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/alerts',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '态势感知', requiresAuth: true }
      },
      {
        path: 'alerts',
        name: 'Alerts',
        component: () => import('@/views/alerts/AlertsView.vue'),
        meta: { title: '告警管理', requiresAuth: true }
      },
      {
        path: 'alerts/:id',
        name: 'AlertsWithDetail',
        component: () => import('@/views/alerts/AlertsView.vue'),
        meta: { title: '告警管理', requiresAuth: true }
      },
      {
        path: 'incidents',
        name: 'Incidents',
        component: () => import('@/views/incidents/IncidentsView.vue'),
        meta: { title: '事件管理', requiresAuth: true }
      },
      {
        path: 'incidents/:id',
        name: 'IncidentDetail',
        component: () => import('@/views/incidents/IncidentsDetail.vue'),
        meta: { title: '事件详情', requiresAuth: true }
      },
      {
        path: 'asm',
        name: 'ASM',
        component: () => import('@/views/asm/ASMView.vue'),
        meta: { title: '攻击面管理', requiresAuth: true }
      },
      {
        path: 'asm/:id',
        name: 'ASMWithDetail',
        component: () => import('@/views/asm/ASMView.vue'),
        meta: { title: '攻击面管理', requiresAuth: true }
      },
      {
        path: 'vulnerabilities',
        name: 'Vulnerabilities',
        component: () => import('@/views/vulnerabilities/VulnerabilitiesView.vue'),
        meta: { title: '漏洞管理', requiresAuth: true }
      },
      {
        path: 'vulnerabilities/:id',
        name: 'VulnerabilityDetail',
        component: () => import('@/views/vulnerabilities/VulnerabilitiesDetail.vue'),
        meta: { title: '漏洞详情', requiresAuth: true }
      },
      {
        path: 'ai-playground/:id',
        name: 'AiPlaygroundWithDetail',
        component: () => import('@/views/ai/AiPlaygroundView.vue'),
        meta: { title: 'AI Playground', requiresAuth: true }
      },
      {
        path: 'ai-playground',
        name: 'AiPlayground',
        component: () => import('@/views/ai/AiPlaygroundView.vue'),
        meta: { title: 'AI Playground', requiresAuth: true }
      },
    ]
  }
]

const getRouterBase = () => {
  const raw = import.meta.env.VITE_WEB_BASE_PATH
  if (!raw || raw === '/') return '/'
  return raw.startsWith('/') ? raw : `/${raw}`
}

const base = getRouterBase()

const router = createRouter({
  history: createWebHistory(base),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 未开启认证的场景，直接放行
  if (!config.enableAuth) {
    next()
    return
  }

  // Tianyan 模式由后端判定登录态，只有在显式访问登录页时才重定向到外部 SSO
  if (config.authMode === 'tianyan') {
    if (to.name === 'Login') {
      redirectToTianyanLogin()
      return
    }
    next()
    return
  }

  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router

