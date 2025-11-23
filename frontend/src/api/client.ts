import axios, { type AxiosError, type InternalAxiosRequestConfig, type AxiosProgressEvent } from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'
import type { UploadProgress, UploadResponse, Job, JobFilters, JobStage, JobStageStatus, Deck, DeckFilters, DeckStats } from '@/types'

// Create axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor: inject auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    
    if (authStore.accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle errors, token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const authStore = useAuthStore()
    
    // Token expired - try refresh
    if (error.response?.status === 401) {
      try {
        await authStore.refreshAccessToken()
        // Retry original request
        if (error.config) {
          return apiClient(error.config)
        }
      } catch (refreshError) {
        // Refresh failed - logout user
        await authStore.logout()
        router.push({ name: 'login' })
      }
    }
    
    return Promise.reject(error)
  }
)

// API methods
export const api = {
  /**
   * Upload PDF file with settings
   */
  uploadPdf: async (
    formData: FormData,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResponse> => {
    const response = await apiClient.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 300000, // 5 minutes for large files
      onUploadProgress: (progressEvent: AxiosProgressEvent) => {
        if (onProgress && progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percent
          })
        }
      }
    })
    return response.data
  },

  /**
   * Get job status
   */
  getJob: async (jobId: string): Promise<Job> => {
    const response = await apiClient.get<Job>(`/jobs/${jobId}`)
    return response.data
  },

  /**
   * Get all user jobs with optional filters
   */
  getJobs: async (filters?: JobFilters): Promise<Job[]> => {
    const params = new URLSearchParams()
    
    if (filters?.status) {
      params.append('status', filters.status)
    }
    if (filters?.sortBy) {
      params.append('sort_by', filters.sortBy)
    }
    if (filters?.sortOrder) {
      params.append('sort_order', filters.sortOrder)
    }
    
    const response = await apiClient.get<Job[]>('/jobs', { params })
    return response.data.map(normalizeJob)
  },

  /**
   * Delete a job
   */
  deleteJob: async (jobId: string): Promise<void> => {
    await apiClient.delete(`/jobs/${jobId}`)
  },

  /**
   * Retry a failed job
   */
  retryJob: async (jobId: string): Promise<Job> => {
    const response = await apiClient.post<Job>(`/jobs/${jobId}/retry`)
    return normalizeJob(response.data)
  },

  /**
   * Get all user decks with optional filters
   */
  getDecks: async (filters?: DeckFilters): Promise<Deck[]> => {
    const params = new URLSearchParams()
    
    if (filters?.search) {
      params.append('search', filters.search)
    }
    if (filters?.sortBy) {
      params.append('sort_by', filters.sortBy)
    }
    if (filters?.sortOrder) {
      params.append('sort_order', filters.sortOrder)
    }
    if (filters?.tags && filters.tags.length > 0) {
      params.append('tags', filters.tags.join(','))
    }
    
    const response = await apiClient.get<Deck[]>('/decks', { params })
    return response.data.map(normalizeDeck)
  },

  /**
   * Get single deck details
   */
  getDeck: async (deckId: string): Promise<Deck> => {
    const response = await apiClient.get<Deck>(`/decks/${deckId}`)
    return normalizeDeck(response.data)
  },

  /**
   * Delete deck
   */
  deleteDeck: async (deckId: string): Promise<void> => {
    await apiClient.delete(`/decks/${deckId}`)
  },

  /**
   * Delete multiple decks
   */
  deleteDecks: async (deckIds: string[]): Promise<void> => {
    await apiClient.post('/decks/bulk-delete', { deck_ids: deckIds })
  },

  /**
   * Download deck .apkg file
   */
  downloadDeck: async (deckId: string): Promise<Blob> => {
    const response = await apiClient.get(`/decks/${deckId}/download`, {
      responseType: 'blob'
    })
    return response.data
  },

  /**
   * Get deck statistics
   */
  getDeckStats: async (): Promise<DeckStats> => {
    const response = await apiClient.get<DeckStats>('/decks/stats')
    return response.data
  },

  /**
   * Get dashboard statistics
   */
  getDashboardStats: async (): Promise<import('@/types').DashboardStats> => {
    const response = await apiClient.get('/dashboard/stats')
    return response.data
  },

  /**
   * Get recent activity
   */
  getRecentActivity: async (limit: number = 5): Promise<import('@/types').Activity[]> => {
    const response = await apiClient.get('/dashboard/activity', {
      params: { limit }
    })
    return response.data
  },

  /**
   * Get user profile
   */
  getUserProfile: async (): Promise<import('@/types').UserProfile> => {
    const response = await apiClient.get('/user/profile')
    return response.data
  },

  /**
   * Get user statistics
   */
  getUserStats: async (): Promise<import('@/types').UserStats> => {
    const response = await apiClient.get('/user/stats')
    return response.data
  },

  /**
   * Update user profile
   */
  updateUserProfile: async (profile: Partial<import('@/types').UserProfile>): Promise<import('@/types').UserProfile> => {
    const response = await apiClient.put('/user/profile', profile)
    return response.data
  },

  /**
   * Update user preferences
   */
  updateUserPreferences: async (prefs: Partial<import('@/types').UserPreferences>): Promise<import('@/types').UserPreferences> => {
    const response = await apiClient.put('/user/preferences', prefs)
    return response.data
  },

  /**
   * Change password
   */
  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await apiClient.post('/user/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
  },

  /**
   * Delete user account
   */
  deleteUserAccount: async (): Promise<void> => {
    await apiClient.delete('/user/account')
  }
}

/**
 * Normalize job data from backend to frontend format
 */
function normalizeJob(job: any): Job {
  return {
    id: job.id,
    userId: job.user_id || job.userId,
    deckName: job.deck_name || job.deckName || job.source_filename || 'Untitled Deck',
    fileName: job.source_filename || job.fileName || 'Unknown',
    pageCount: job.page_count || job.pageCount || 0,
    status: job.status,
    progress: job.progress || 0,
    currentStage: job.current_stage || job.currentStage || 1,
    stageName: job.stage_name || job.stageName || getStageName(job.current_stage || job.currentStage || 1),
    stages: job.stages || generateDefaultStages(),
    errorMessage: job.error_message || job.errorMessage,
    createdAt: job.created_at || job.createdAt,
    startedAt: job.started_at || job.startedAt,
    completedAt: job.completed_at || job.completedAt,
    deckId: job.deck_id || job.deckId,
    // Keep backend format for compatibility
    user_id: job.user_id,
    source_filename: job.source_filename,
    created_at: job.created_at,
    updated_at: job.updated_at,
    error_message: job.error_message
  }
}

/**
 * Get stage name by number
 */
function getStageName(stage: number): string {
  const stageNames = [
    'Extracting text from PDF',
    'Chunking content',
    'Identifying topics',
    'Refining topics',
    'Generating tags',
    'Creating questions',
    'Generating answers',
    'Building Anki deck'
  ]
  return stageNames[stage - 1] || 'Processing'
}

/**
 * Generate default stages for a new job
 */
function generateDefaultStages(): JobStage[] {
  const stageNames = [
    'Extracting text from PDF',
    'Chunking content',
    'Identifying topics',
    'Refining topics',
    'Generating tags',
    'Creating questions',
    'Generating answers',
    'Building Anki deck'
  ]
  
  return stageNames.map((name, index) => ({
    stage: index + 1,
    name,
    status: 'pending' as JobStageStatus
  }))
}

/**
 * Normalize deck data from backend to frontend format
 */
function normalizeDeck(deck: any): Deck {
  return {
    id: deck.id,
    userId: deck.user_id || deck.userId,
    name: deck.name || deck.deck_name || 'Untitled Deck',
    cardCount: deck.card_count || deck.cardCount || 0,
    tags: deck.tags || [],
    fileName: deck.file_name || deck.fileName || deck.source_filename || 'Unknown',
    pageRange: deck.page_range || deck.pageRange || [],
    jobId: deck.job_id || deck.jobId || '',
    createdAt: deck.created_at || deck.createdAt,
    updatedAt: deck.updated_at || deck.updatedAt,
    fileSize: deck.file_size || deck.fileSize || 0,
    downloadUrl: deck.download_url || deck.downloadUrl || '',
    // Keep backend format for compatibility
    user_id: deck.user_id,
    card_count: deck.card_count,
    created_at: deck.created_at,
    updated_at: deck.updated_at,
    file_name: deck.file_name,
    page_range: deck.page_range,
    job_id: deck.job_id,
    file_size: deck.file_size,
    download_url: deck.download_url
  }
}

// Export helper functions for use in composables
export { normalizeJob, getStageName, generateDefaultStages, normalizeDeck }

export default apiClient
