import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layouts/index.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/alerts',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '总览' }
      },
      {
        path: 'alerts',
        name: 'Alerts',
        component: () => import('@/views/alerts/index.vue'),
        meta: { title: '告警管理' }
      },
      {
        path: 'incidents',
        name: 'Incidents',
        component: () => import('@/views/incidents/index.vue'),
        meta: { title: '事件管理' }
      },
      {
        path: 'incidents/:id',
        name: 'IncidentDetail',
        component: () => import('@/views/incidents/detail.vue'),
        meta: { title: '事件详情' }
      },
      {
        path: 'vulnerabilities',
        name: 'Vulnerabilities',
        component: () => import('@/views/placeholder/index.vue'),
        meta: { title: '漏洞管理' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

