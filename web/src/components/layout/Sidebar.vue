<template>
  <aside 
    :class="[
      'flex h-screen flex-col bg-white dark:bg-[#111822] p-4 fixed left-0 top-0 z-10 transition-all duration-300 border-r border-gray-200 dark:border-gray-800',
      appStore.sidebarCollapsed ? 'w-20' : 'w-64'
    ]"
  >
    <div class="flex flex-col gap-4">
      <div class="flex items-center gap-3">
        <img 
          src="/pisces_logo.png"
          alt="Logo"
          class="size-10 rounded-full object-contain flex-shrink-0 border border-gray-300 dark:border-gray-500/30"
        />
        <div v-if="!appStore.sidebarCollapsed" class="flex flex-col">
          <h1 class="text-gray-900 dark:text-white text-base font-medium leading-normal">Pisces Security</h1>
          <p class="text-gray-500 dark:text-gray-400 text-sm font-normal leading-normal">SOC Center</p>
        </div>
      </div>
      
      <nav class="flex flex-col gap-2 mt-4">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
            isActive(item.path) 
              ? 'bg-primary text-white' 
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-primary/20 hover:text-gray-900 dark:hover:text-white'
          ]"
          :title="appStore.sidebarCollapsed ? $t(item.label) : null"
        >
          <span 
            class="material-symbols-outlined flex-shrink-0"
            :class="isActive(item.path) ? 'text-white' : 'text-gray-600 dark:text-gray-300'"
            :style="{ fontVariationSettings: isActive(item.path) ? '\'FILL\' 1' : '\'FILL\' 0' }"
          >
            {{ item.icon }}
          </span>
          <p v-if="!appStore.sidebarCollapsed" class="text-sm font-medium leading-normal">
            {{ $t(item.label) }}
          </p>
        </router-link>
      </nav>
    </div>
    
    <div class="mt-auto">
      <button 
        @click="appStore.toggleSidebar()"
        class="flex w-full items-center justify-center gap-2 p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/10 transition-colors"
      >
        <span class="material-symbols-outlined">
          {{ appStore.sidebarCollapsed ? 'menu' : 'menu_open' }}
        </span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const appStore = useAppStore()
const { t } = useI18n()

const allMenuItems = [
  { path: '/dashboard', icon: 'dashboard', label: 'nav.dashboard' },
  { path: '/alerts', icon: 'security', label: 'nav.alerts' },
  { path: '/incidents', icon: 'list_alt', label: 'nav.incidents' },
  { path: '/asm', icon: 'radar', label: 'nav.asm' },
  { path: '/vulnerabilities', icon: 'bug_report', label: 'nav.vulnerabilities' }
]

const enabledRoutes = computed(() => {
  const envRoutes = import.meta.env.VITE_ENABLED_MENU_ROUTES
  if (!envRoutes || envRoutes.trim() === '') {
    return allMenuItems.map(item => item.path)
  }
  return envRoutes.split(',').map(route => route.trim()).filter(route => route)
})

const menuItems = computed(() => {
  return allMenuItems.filter(item => enabledRoutes.value.includes(item.path))
})

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

