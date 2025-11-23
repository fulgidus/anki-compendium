// User types
export interface User {
  id: string
  email: string
  username: string
  created_at: string
  updated_at: string
}

// Auth types
export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

// Job types
export const JobStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed'
} as const

export type JobStatusType = typeof JobStatus[keyof typeof JobStatus]

export type JobStageStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface JobStage {
  stage: number
  name: string
  status: JobStageStatus
  startTime?: string
  endTime?: string
  error?: string
}

export interface Job {
  id: string
  userId: string
  deckName: string
  fileName: string
  pageCount: number
  status: JobStatusType
  progress: number // 0-100
  currentStage: number // 1-8
  stageName: string
  stages: JobStage[]
  errorMessage?: string
  createdAt: string
  startedAt?: string
  completedAt?: string
  deckId?: string // if completed
  // Backend compatibility
  user_id?: string
  source_filename?: string
  created_at?: string
  updated_at?: string
  error_message?: string
}

export interface JobFilters {
  status?: JobStatusType
  sortBy?: 'date' | 'status' | 'name'
  sortOrder?: 'asc' | 'desc'
}

// Deck types
export interface Deck {
  id: string
  userId: string
  name: string
  cardCount: number
  tags: string[]
  fileName: string // source PDF name
  pageRange: number[]
  jobId: string
  createdAt: string
  updatedAt: string
  fileSize: number // .apkg file size in bytes
  downloadUrl: string // pre-signed URL
  // Backend compatibility
  user_id?: string
  card_count?: number
  created_at?: string
  updated_at?: string
  file_name?: string
  page_range?: number[]
  job_id?: string
  file_size?: number
  download_url?: string
}

export interface DeckFilters {
  search?: string
  sortBy?: 'date' | 'name' | 'cardCount'
  sortOrder?: 'asc' | 'desc'
  tags?: string[]
}

export interface DeckStats {
  totalDecks: number
  totalCards: number
  decksThisWeek: number
  decksThisMonth: number
  topTags: Array<{ tag: string; count: number }>
}

// Dashboard types
export interface DashboardStats {
  totalDecks: number
  totalCards: number
  activeJobs: number
  decksThisWeek: number
  decksThisMonth: number
}

export interface Activity {
  id: string
  type: 'job' | 'deck' | 'upload'
  title: string
  timestamp: string
  status?: JobStatusType
  metadata?: {
    deckId?: string
    jobId?: string
    cardCount?: number
    progress?: number
  }
}

// User profile types
export interface UserProfile {
  id: string
  email: string
  fullName: string
  createdAt: string
  lastLoginAt: string
  preferences: UserPreferences
}

export interface UserPreferences {
  defaultMaxCards: number
  defaultDifficulty: 'easy' | 'medium' | 'hard'
  includeImages: boolean
  emailOnCompletion: boolean
  emailOnFailure: boolean
}

export interface UserStats {
  totalDecks: number
  totalCards: number
  accountCreatedAt: string
  lastLoginAt: string
}

export interface PasswordChangeRequest {
  currentPassword: string
  newPassword: string
  confirmPassword: string
}

// Upload types
export interface UploadProgress {
  loaded: number
  total: number
  percent: number
}

export interface PdfFile {
  file: File
  name: string
  size: number
  pageCount: number
  url?: string
}

export interface JobSettings {
  deckName: string
  maxCards?: number
  difficulty?: 'easy' | 'medium' | 'hard'
  includeImages?: boolean
  pageRange: number[]
}

export interface UploadRequest {
  file: File
  settings: JobSettings
}

export interface UploadResponse {
  job_id: string
  message: string
}
