import { defineStore } from 'pinia'

const getInitialSidebarState = () => {
  const storedValue = localStorage.getItem('sidebarCollapsed')
  return storedValue !== null ? storedValue === 'true' : true
}

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarCollapsed: getInitialSidebarState(),
    locale: localStorage.getItem('locale') || 'zh-CN'
  }),
  
  actions: {
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
      localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed.toString())
    },
    
    setSidebarCollapsed(collapsed) {
      this.sidebarCollapsed = collapsed
      localStorage.setItem('sidebarCollapsed', collapsed.toString())
    },
    
    setLocale(locale) {
      this.locale = locale
      localStorage.setItem('locale', locale)
    }
  }
})

