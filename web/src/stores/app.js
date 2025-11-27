import { defineStore } from 'pinia'

const getInitialSidebarState = () => {
  const storedValue = localStorage.getItem('sidebarCollapsed')
  return storedValue !== null ? storedValue === 'true' : true
}

const getInitialTheme = () => {
  const storedTheme = localStorage.getItem('theme')
  if (storedTheme) {
    return storedTheme
  }
  // Default to dark mode if no preference is stored
  return 'dark'
}

export const useAppStore = defineStore('app', {
  state: () => ({
    sidebarCollapsed: getInitialSidebarState(),
    locale: localStorage.getItem('locale') || 'zh-CN',
    theme: getInitialTheme()
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
    },
    
    setTheme(theme) {
      this.theme = theme
      localStorage.setItem('theme', theme)
      // Apply theme to document
      if (theme === 'dark') {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    },
    
    toggleTheme() {
      const newTheme = this.theme === 'dark' ? 'light' : 'dark'
      this.setTheme(newTheme)
    }
  }
})

