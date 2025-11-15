import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/alerts',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '总览' }
      },
      {
        path: 'alerts',
        name: 'Alerts',
        component: () => import('@/views/alerts/AlertsView.vue'),
        meta: { title: '告警管理' }
      },
      {
        path: 'alerts/:id',
        name: 'AlertsWithDetail',
        component: () => import('@/views/alerts/AlertsView.vue'),
        meta: { title: '告警管理' }
      },
      {
        path: 'incidents',
        name: 'Incidents',
        component: () => import('@/views/incidents/IncidentsView.vue'),
        meta: { title: '事件管理' }
      },
      {
        path: 'incidents/:id',
        name: 'IncidentDetail',
        component: () => import('@/views/incidents/IncidentsDetail.vue'),
        meta: { title: '事件详情' }
      },
      {
        path: 'vulnerabilities',
        name: 'Vulnerabilities',
        component: () => import('@/views/vulnerabilities/VulnerabilitiesView.vue'),
        meta: { title: '漏洞管理' }
      },
      {
        path: 'vulnerabilities/:id',
        name: 'VulnerabilityDetail',
        component: () => import('@/views/vulnerabilities/VulnerabilitiesDetail.vue'),
        meta: { title: '漏洞详情' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

