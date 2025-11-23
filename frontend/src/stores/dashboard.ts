import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/client'
import type { DashboardStats, Activity, Deck } from '@/types'

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const stats = ref<DashboardStats>({
    totalDecks: 0,
    totalCards: 0,
    activeJobs: 0,
    decksThisWeek: 0,
    decksThisMonth: 0
  })
  
  const recentActivity = ref<Activity[]>([])
  const recentDecks = ref<Deck[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const autoRefreshInterval = ref<number | null>(null)

  // Actions
  const fetchDashboardData = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      // Fetch dashboard stats, recent activity, and recent decks in parallel
      const [statsData, activityData, decksData] = await Promise.all([
        api.getDashboardStats(),
        api.getRecentActivity(5),
        api.getDecks({ sortBy: 'date', sortOrder: 'desc' })
      ])

      stats.value = statsData
      recentActivity.value = activityData
      recentDecks.value = decksData.slice(0, 5)
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to load dashboard data'
      console.error('Error fetching dashboard data:', err)
    } finally {
      loading.value = false
    }
  }

  const refreshStats = async (): Promise<void> => {
    try {
      const statsData = await api.getDashboardStats()
      stats.value = statsData
    } catch (err: any) {
      console.error('Error refreshing stats:', err)
      // Don't update error state for background refresh
    }
  }

  const startAutoRefresh = (): void => {
    // Auto-refresh stats every 60 seconds
    if (autoRefreshInterval.value) {
      clearInterval(autoRefreshInterval.value)
    }

    autoRefreshInterval.value = window.setInterval(() => {
      refreshStats()
    }, 60000) // 60 seconds
  }

  const stopAutoRefresh = (): void => {
    if (autoRefreshInterval.value) {
      clearInterval(autoRefreshInterval.value)
      autoRefreshInterval.value = null
    }
  }

  const clearError = (): void => {
    error.value = null
  }

  const reset = (): void => {
    stats.value = {
      totalDecks: 0,
      totalCards: 0,
      activeJobs: 0,
      decksThisWeek: 0,
      decksThisMonth: 0
    }
    recentActivity.value = []
    recentDecks.value = []
    loading.value = false
    error.value = null
    stopAutoRefresh()
  }

  return {
    // State
    stats,
    recentActivity,
    recentDecks,
    loading,
    error,

    // Actions
    fetchDashboardData,
    refreshStats,
    startAutoRefresh,
    stopAutoRefresh,
    clearError,
    reset
  }
})
