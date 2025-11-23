import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'
import type { UserProfile, UserPreferences, UserStats, PasswordChangeRequest } from '@/types'

export const useUserStore = defineStore('user', () => {
  // State
  const profile = ref<UserProfile | null>(null)
  const stats = ref<UserStats | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const fullName = computed(() => profile.value?.fullName || '')
  const email = computed(() => profile.value?.email || '')
  const preferences = computed(() => profile.value?.preferences)
  const memberSince = computed(() => profile.value?.createdAt || '')

  // Actions
  const fetchProfile = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      profile.value = await api.getUserProfile()
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch profile'
      console.error('Error fetching profile:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchStats = async (): Promise<void> => {
    try {
      stats.value = await api.getUserStats()
    } catch (err: any) {
      console.error('Error fetching user stats:', err)
      // Don't set error for stats - it's not critical
    }
  }

  const updateProfile = async (updates: Partial<UserProfile>): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const updatedProfile = await api.updateUserProfile(updates)
      profile.value = updatedProfile
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update profile'
      console.error('Error updating profile:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const updatePreferences = async (prefs: Partial<UserPreferences>): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const updatedPrefs = await api.updateUserPreferences(prefs)
      
      // Update profile with new preferences
      if (profile.value) {
        profile.value.preferences = updatedPrefs
      }
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to update preferences'
      console.error('Error updating preferences:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const changePassword = async (request: PasswordChangeRequest): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      await api.changePassword(request.currentPassword, request.newPassword)
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to change password'
      console.error('Error changing password:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const deleteAccount = async (): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      await api.deleteUserAccount()
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete account'
      console.error('Error deleting account:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  const clearError = (): void => {
    error.value = null
  }

  const reset = (): void => {
    profile.value = null
    stats.value = null
    loading.value = false
    error.value = null
  }

  return {
    // State
    profile,
    stats,
    loading,
    error,

    // Getters
    fullName,
    email,
    preferences,
    memberSince,

    // Actions
    fetchProfile,
    fetchStats,
    updateProfile,
    updatePreferences,
    changePassword,
    deleteAccount,
    clearError,
    reset
  }
})
