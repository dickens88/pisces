<template>
  <aside 
    :class="[
      'flex h-screen flex-col bg-[#111822] p-4 fixed left-0 top-0 z-10 transition-all duration-300',
      appStore.sidebarCollapsed ? 'w-20' : 'w-64'
    ]"
  >
    <div class="flex flex-col gap-4">
      <!-- Logo和标题 -->
      <div class="flex items-center gap-3">
        <div 
          class="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 flex-shrink-0"
          style='background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuCOBkqQyna6RaiQ7Pi4IHAio_mVba4O6BC2LKE3ILZpZR0zG6pkRfrua86wFIE9mgetUord3xZuqe7sVkeIuGruDVMShsTZTHcECA5jY9YTjlpSEXjIhD8600R4TXJveWrJCXIPWYF5RoSQJQE5x6qTuq2nz96_hR4TysTsP6lO6havPf7ykmCiBVbgtkCj-eRwAhFfSWOedlfBq7tuOchbtp_lKARKF-NFpMkAFpg2ul34Lr0IsB2flZ9blgJJwZDtUmUGQSbrHHDr");'
        ></div>
        <div v-if="!appStore.sidebarCollapsed" class="flex flex-col">
          <h1 class="text-white text-base font-medium leading-normal">SIEM Platform</h1>
          <p class="text-gray-400 text-sm font-normal leading-normal">SOC Center</p>
        </div>
      </div>
      
      <!-- 导航菜单 -->
      <nav class="flex flex-col gap-2 mt-4">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
            isActive(item.path) 
              ? 'bg-primary text-white' 
              : 'text-gray-300 hover:bg-primary/20 hover:text-white'
          ]"
        >
          <span 
            class="material-symbols-outlined flex-shrink-0"
            :class="isActive(item.path) ? 'text-white' : 'text-gray-300'"
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
    
    <!-- 底部折叠按钮 -->
    <div class="mt-auto">
      <button 
        @click="appStore.toggleSidebar()"
        class="flex w-full items-center justify-center gap-2 p-2 rounded-lg text-gray-300 hover:bg-white/10 transition-colors"
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

const menuItems = [
  { path: '/dashboard', icon: 'dashboard', label: 'nav.dashboard' },
  { path: '/alerts', icon: 'security', label: 'nav.alerts' },
  { path: '/incidents', icon: 'list_alt', label: 'nav.incidents' },
  { path: '/vulnerabilities', icon: 'bug_report', label: 'nav.vulnerabilities' }
]

const isActive = (path) => {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

