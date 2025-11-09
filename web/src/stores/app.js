import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarCollapsed: false,
    locale: localStorage.getItem('locale') || 'zh-CN'
  }),
  
  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    
    setSidebarCollapsed(collapsed) {
      this.sidebarCollapsed = collapsed
    },
    
    setLocale(locale) {
      this.locale = locale
      localStorage.setItem('locale', locale)
    }
  }
})

