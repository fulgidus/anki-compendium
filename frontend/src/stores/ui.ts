import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ThemeType = 'light' | 'dark'

export const useUIStore = defineStore('ui', () => {
  // State
  const sidebarOpen = ref(true)
  const sidebarCollapsed = ref(false)
  const mobileMenuOpen = ref(false)
  const theme = ref<ThemeType>('light')

  // Load theme from localStorage
  const loadTheme = () => {
    const stored = localStorage.getItem('theme') as ThemeType | null
    if (stored) {
      theme.value = stored
      applyTheme(stored)
    }
  }

  // Apply theme to document
  const applyTheme = (newTheme: ThemeType) => {
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark-mode')
    } else {
      document.documentElement.classList.remove('dark-mode')
    }
  }

  // Actions
  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
  }

  const toggleMobileMenu = () => {
    mobileMenuOpen.value = !mobileMenuOpen.value
  }

  const closeMobileMenu = () => {
    mobileMenuOpen.value = false
  }

  const collapseSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  const setTheme = (newTheme: ThemeType) => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    applyTheme(newTheme)
  }

  const openSidebar = () => {
    sidebarOpen.value = true
  }

  const closeSidebar = () => {
    sidebarOpen.value = false
  }

  return {
    sidebarOpen,
    sidebarCollapsed,
    mobileMenuOpen,
    theme,
    toggleSidebar,
    toggleMobileMenu,
    closeMobileMenu,
    collapseSidebar,
    setTheme,
    loadTheme,
    openSidebar,
    closeSidebar
  }
})
