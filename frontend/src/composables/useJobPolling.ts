import { ref, onUnmounted, watch } from 'vue'
import { useJobsStore } from '@/stores/jobs'
import type { Job } from '@/types'

interface UseJobPollingOptions {
  interval?: number // Initial polling interval in ms (default: 5000)
  maxInterval?: number // Maximum polling interval in ms (default: 60000)
  exponentialBackoff?: boolean // Use exponential backoff (default: false)
  pauseOnHidden?: boolean // Pause polling when tab is hidden (default: true)
}

export function useJobPolling(
  jobId: string | (() => string),
  options: UseJobPollingOptions = {}
) {
  const jobsStore = useJobsStore()
  
  const {
    interval = 5000,
    maxInterval = 60000,
    exponentialBackoff = false,
    pauseOnHidden = true
  } = options

  const job = ref<Job | null>(null)
  const isPolling = ref(false)
  const error = ref<string | null>(null)
  const pollCount = ref(0)
  
  let timerId: ReturnType<typeof setInterval> | null = null
  let currentInterval = interval
  let visibilityHandler: (() => void) | null = null

  /**
   * Check if job needs polling (pending or processing)
   */
  function shouldPoll(jobData: Job | null): boolean {
    if (!jobData) return false
    return jobData.status === 'pending' || jobData.status === 'processing'
  }

  /**
   * Calculate next polling interval with exponential backoff
   */
  function getNextInterval(): number {
    if (!exponentialBackoff) {
      return interval
    }

    // Exponential backoff: 5s -> 10s -> 20s -> 40s -> 60s (max)
    pollCount.value++
    const nextInterval = Math.min(interval * Math.pow(2, Math.floor(pollCount.value / 10)), maxInterval)
    return nextInterval
  }

  /**
   * Fetch job status
   */
  async function fetchJobStatus(): Promise<void> {
    const id = typeof jobId === 'function' ? jobId() : jobId
    if (!id) return

    try {
      error.value = null
      const fetchedJob = await jobsStore.fetchJob(id)
      
      if (fetchedJob) {
        job.value = fetchedJob
        
        // Stop polling if job is completed or failed
        if (!shouldPoll(fetchedJob)) {
          stopPolling()
        } else if (exponentialBackoff) {
          // Update interval with backoff
          currentInterval = getNextInterval()
          if (timerId) {
            stopPolling()
            startPolling()
          }
        }
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch job status'
      console.error('Error polling job:', err)
      
      // Continue polling even on error (network issues might be temporary)
      // But use exponential backoff to reduce server load
      if (exponentialBackoff) {
        currentInterval = getNextInterval()
      }
    }
  }

  /**
   * Start polling
   */
  function startPolling(): void {
    if (isPolling.value) return

    const id = typeof jobId === 'function' ? jobId() : jobId
    if (!id) return

    isPolling.value = true
    pollCount.value = 0
    currentInterval = interval
    
    jobsStore.addActivePolling(id)
    
    // Initial fetch
    fetchJobStatus()
    
    // Start interval
    timerId = setInterval(() => {
      // Check if tab is visible
      if (pauseOnHidden && document.hidden) {
        return
      }
      
      fetchJobStatus()
    }, currentInterval)

    // Setup visibility change handler
    if (pauseOnHidden && !visibilityHandler) {
      visibilityHandler = () => {
        if (!document.hidden && isPolling.value) {
          // Resume polling when tab becomes visible
          fetchJobStatus()
        }
      }
      document.addEventListener('visibilitychange', visibilityHandler)
    }
  }

  /**
   * Stop polling
   */
  function stopPolling(): void {
    if (!isPolling.value) return

    isPolling.value = false
    
    if (timerId) {
      clearInterval(timerId)
      timerId = null
    }

    const id = typeof jobId === 'function' ? jobId() : jobId
    if (id) {
      jobsStore.removeActivePolling(id)
    }

    // Cleanup visibility handler
    if (visibilityHandler) {
      document.removeEventListener('visibilitychange', visibilityHandler)
      visibilityHandler = null
    }
  }

  /**
   * Restart polling (useful after retry)
   */
  function restartPolling(): void {
    stopPolling()
    startPolling()
  }

  /**
   * Manual refresh
   */
  async function refresh(): Promise<void> {
    await fetchJobStatus()
  }

  // Watch for job status changes
  watch(() => job.value?.status, (newStatus, oldStatus) => {
    if (oldStatus && newStatus !== oldStatus) {
      if (newStatus === 'completed' || newStatus === 'failed') {
        stopPolling()
      }
    }
  })

  // Cleanup on unmount
  onUnmounted(() => {
    stopPolling()
  })

  return {
    job,
    isPolling,
    error,
    pollCount,
    startPolling,
    stopPolling,
    restartPolling,
    refresh
  }
}
