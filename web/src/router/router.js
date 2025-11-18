import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layouts/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { getAppConfig } from '@config'
const config = getAppConfig(import.meta.env, import.meta.env.PROD)

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: '登录', requiresAuth: false }
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
        meta: { title: '总览', requiresAuth: true }
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
      }
    ]
  }
]

const getRouterBase = () => {
  const raw = import.meta.env.VITE_WEB_BASE_URL
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
  // 如果禁用了认证，直接放行
  if (!config.enableAuth) {
    next()
    return
  }

  // 如果使用tianyan-web认证模式，关闭pisces的登录页面
  // 访问登录页面时重定向到tianyan-web登录页面
  if (config.authMode === 'tianyan' && to.name === 'Login') {
    const currentUrl = window.location.href
    const loginUrl = `${config.tianyanWebBaseURL}/login?redirect=${encodeURIComponent(currentUrl)}`
    window.location.href = loginUrl
    return
  }

  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.isAuthenticated) {
    // 需要认证但未登录
    if (config.authMode === 'tianyan') {
      // 使用tianyan-web认证，重定向到tianyan-web登录页面
      const currentUrl = window.location.href
      const loginUrl = `${config.tianyanWebBaseURL}/login?redirect=${encodeURIComponent(currentUrl)}`
      window.location.href = loginUrl
    } else {
      // 使用本地认证，重定向到本地登录页
      next({ name: 'Login', query: { redirect: to.fullPath } })
    }
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    // 已登录但访问登录页，重定向到首页
    next('/')
  } else {
    next()
  }
})

export default router

