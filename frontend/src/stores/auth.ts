import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, AuthResponse } from '@/types'
import apiClient from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  
  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const userProfile = computed(() => user.value)
  
  // Actions
  const login = async (email: string, password: string): Promise<void> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', { email, password })
    accessToken.value = response.data.access_token
    refreshToken.value = response.data.refresh_token
    user.value = response.data.user
    
    // Store tokens in localStorage
    localStorage.setItem('accessToken', response.data.access_token)
    localStorage.setItem('refreshToken', response.data.refresh_token)
  }
  
  const register = async (email: string, password: string, fullName: string): Promise<void> => {
    const response = await apiClient.post<AuthResponse>('/auth/register', { 
      email, 
      password, 
      full_name: fullName 
    })
    accessToken.value = response.data.access_token
    refreshToken.value = response.data.refresh_token
    user.value = response.data.user
    
    // Store tokens in localStorage
    localStorage.setItem('accessToken', response.data.access_token)
    localStorage.setItem('refreshToken', response.data.refresh_token)
  }
  
  const logout = async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      accessToken.value = null
      refreshToken.value = null
      user.value = null
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
    }
  }
  
  const refreshAccessToken = async (): Promise<void> => {
    if (!refreshToken.value) throw new Error('No refresh token')
    
    const response = await apiClient.post<{ access_token: string }>('/auth/refresh', {
      refresh_token: refreshToken.value
    })
    accessToken.value = response.data.access_token
    localStorage.setItem('accessToken', response.data.access_token)
  }
  
  const loadStoredAuth = async (): Promise<void> => {
    const token = localStorage.getItem('accessToken')
    const refresh = localStorage.getItem('refreshToken')
    
    if (token && refresh) {
      accessToken.value = token
      refreshToken.value = refresh
      // Fetch user profile
      try {
        await fetchUserProfile()
      } catch (error) {
        // If profile fetch fails, clear auth
        await logout()
      }
    }
  }
  
  const fetchUserProfile = async (): Promise<void> => {
    const response = await apiClient.get<User>('/auth/me')
    user.value = response.data
  }
  
  return {
    user,
    accessToken,
    isAuthenticated,
    userProfile,
    login,
    register,
    logout,
    refreshAccessToken,
    loadStoredAuth,
    fetchUserProfile
  }
})
