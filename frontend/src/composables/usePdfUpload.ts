import { ref, computed } from 'vue'
import type { PdfFile, UploadProgress, UploadRequest, UploadResponse } from '@/types'
import { useToast } from 'primevue/usetoast'

const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB
const ALLOWED_FILE_TYPE = 'application/pdf'

export function usePdfUpload() {
  const toast = useToast()
  
  const pdfFile = ref<PdfFile | null>(null)
  const isUploading = ref(false)
  const uploadProgress = ref<UploadProgress>({
    loaded: 0,
    total: 0,
    percent: 0
  })
  const error = ref<string | null>(null)

  const hasFile = computed(() => pdfFile.value !== null)
  const canUpload = computed(() => hasFile.value && !isUploading.value)

  /**
   * Validate PDF file
   */
  const validateFile = (file: File): string | null => {
    // Check file type
    if (file.type !== ALLOWED_FILE_TYPE) {
      return 'Only PDF files are allowed'
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      const maxSizeMB = MAX_FILE_SIZE / (1024 * 1024)
      return `File size must be less than ${maxSizeMB}MB`
    }

    // Check file name
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return 'File must have .pdf extension'
    }

    return null
  }

  /**
   * Format file size to human-readable format
   */
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  /**
   * Load PDF file and extract page count
   */
  const loadPdfFile = async (file: File): Promise<PdfFile> => {
    // Create object URL for preview
    const url = URL.createObjectURL(file)

    // For now, we'll set pageCount to 0 and let PdfViewer component determine it
    // This avoids loading PDF.js twice
    return {
      file,
      name: file.name,
      size: file.size,
      pageCount: 0, // Will be updated by PdfViewer
      url
    }
  }

  /**
   * Select and validate PDF file
   */
  const selectFile = async (file: File) => {
    error.value = null

    // Validate file
    const validationError = validateFile(file)
    if (validationError) {
      error.value = validationError
      toast.add({
        severity: 'error',
        summary: 'Invalid File',
        detail: validationError,
        life: 5000
      })
      return false
    }

    try {
      // Load PDF file
      pdfFile.value = await loadPdfFile(file)
      
      toast.add({
        severity: 'success',
        summary: 'File Selected',
        detail: `${file.name} (${formatFileSize(file.size)})`,
        life: 3000
      })
      
      return true
    } catch (err) {
      error.value = 'Failed to load PDF file'
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load PDF file',
        life: 5000
      })
      return false
    }
  }

  /**
   * Update page count after PDF is loaded in viewer
   */
  const updatePageCount = (count: number) => {
    if (pdfFile.value) {
      pdfFile.value.pageCount = count
    }
  }

  /**
   * Upload PDF file with settings
   */
  const uploadFile = async (request: UploadRequest): Promise<UploadResponse | null> => {
    if (!pdfFile.value) {
      error.value = 'No file selected'
      return null
    }

    isUploading.value = true
    error.value = null
    uploadProgress.value = { loaded: 0, total: 0, percent: 0 }

    try {
      // Create FormData
      const formData = new FormData()
      formData.append('file', request.file)
      formData.append('deck_name', request.settings.deckName)
      formData.append('page_range', JSON.stringify(request.settings.pageRange))
      
      if (request.settings.maxCards) {
        formData.append('max_cards', request.settings.maxCards.toString())
      }
      if (request.settings.difficulty) {
        formData.append('difficulty', request.settings.difficulty)
      }
      if (request.settings.includeImages !== undefined) {
        formData.append('include_images', request.settings.includeImages.toString())
      }

      // Upload with progress tracking using api client
      const { api } = await import('@/api/client')
      const response = await api.uploadPdf(formData, (progress) => {
        uploadProgress.value = progress
      })

      toast.add({
        severity: 'success',
        summary: 'Upload Successful',
        detail: 'Your PDF is being processed',
        life: 3000
      })

      return response
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to upload PDF'
      error.value = errorMessage
      
      toast.add({
        severity: 'error',
        summary: 'Upload Failed',
        detail: errorMessage,
        life: 5000
      })
      
      return null
    } finally {
      isUploading.value = false
    }
  }

  /**
   * Clear selected file and reset state
   */
  const reset = () => {
    if (pdfFile.value?.url) {
      URL.revokeObjectURL(pdfFile.value.url)
    }
    pdfFile.value = null
    isUploading.value = false
    uploadProgress.value = { loaded: 0, total: 0, percent: 0 }
    error.value = null
  }

  /**
   * Remove selected file
   */
  const removeFile = () => {
    reset()
    toast.add({
      severity: 'info',
      summary: 'File Removed',
      detail: 'Selected file has been removed',
      life: 2000
    })
  }

  return {
    // State
    pdfFile,
    isUploading,
    uploadProgress,
    error,
    
    // Computed
    hasFile,
    canUpload,
    
    // Methods
    selectFile,
    updatePageCount,
    uploadFile,
    removeFile,
    reset,
    validateFile,
    formatFileSize
  }
}
