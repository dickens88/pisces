import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layouts/MainLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { config } from '@/config'

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

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 如果禁用了认证，直接放行
  if (!config.enableAuth) {
    next()
    return
  }

  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

  if (requiresAuth && !authStore.isAuthenticated) {
    // 需要认证但未登录，重定向到登录页
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    // 已登录但访问登录页，重定向到首页
    next('/')
  } else {
    next()
  }
})

export default router

