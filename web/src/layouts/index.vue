<template>
  <div class="relative flex min-h-screen w-full bg-background-light dark:bg-background-dark">
    <!-- 左侧导航栏 -->
    <Sidebar />
    
    <!-- 主内容区 -->
    <div 
      :class="[
        'flex-1 flex flex-col overflow-hidden transition-all duration-300',
        appStore.sidebarCollapsed ? 'ml-20' : 'ml-64'
      ]"
    >
      <!-- 页眉 -->
      <Header :title="currentRouteTitle" />
      
      <!-- 内容区 -->
      <main class="flex-1 p-4 lg:p-6 overflow-auto">
        <div class="w-full">
          <router-view />
        </div>
      </main>
      
      <!-- 页脚 -->
      <footer class="px-6 py-4 border-t border-[#324867] bg-[#111822]">
        <div class="text-center text-gray-400 text-sm">
          © 2024 SIEM Platform. All rights reserved.
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '@/stores/app'
import Sidebar from '@/components/layout/Sidebar.vue'
import Header from '@/components/layout/Header.vue'

const route = useRoute()
const { t } = useI18n()
const appStore = useAppStore()

const currentRouteTitle = computed(() => {
  return route.meta?.title || t('nav.dashboard')
})
</script>

