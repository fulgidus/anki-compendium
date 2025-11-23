import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'
import type { Job, JobFilters } from '@/types'

export const useJobsStore = defineStore('jobs', () => {
  // State
  const jobs = ref<Job[]>([])
  const currentJob = ref<Job | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const activePolls = ref<Set<string>>(new Set())

  // Getters
  const activeJobs = computed(() => 
    jobs.value.filter(job => 
      job.status === 'pending' || job.status === 'processing'
    )
  )

  const completedJobs = computed(() => 
    jobs.value.filter(job => job.status === 'completed')
  )

  const failedJobs = computed(() => 
    jobs.value.filter(job => job.status === 'failed')
  )

  const getJobById = computed(() => (id: string) => 
    jobs.value.find(job => job.id === id)
  )

  // Actions
  const fetchJobs = async (filters?: JobFilters): Promise<void> => {
    loading.value = true
    error.value = null
    
    try {
      const fetchedJobs = await api.getJobs(filters)
      jobs.value = fetchedJobs
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch jobs'
      console.error('Error fetching jobs:', err)
    } finally {
      loading.value = false
    }
  }

  const fetchJob = async (id: string): Promise<Job | null> => {
    try {
      const job = await api.getJob(id)
      
      // Update in the list if it exists
      const index = jobs.value.findIndex(j => j.id === id)
      if (index !== -1) {
        jobs.value[index] = job
      } else {
        jobs.value.unshift(job)
      }
      
      currentJob.value = job
      return job
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch job'
      console.error('Error fetching job:', err)
      return null
    }
  }

  const updateJobInList = (updatedJob: Job): void => {
    const index = jobs.value.findIndex(j => j.id === updatedJob.id)
    if (index !== -1) {
      jobs.value[index] = updatedJob
    }
    
    if (currentJob.value?.id === updatedJob.id) {
      currentJob.value = updatedJob
    }
  }

  const deleteJob = async (id: string): Promise<boolean> => {
    try {
      await api.deleteJob(id)
      
      // Remove from list
      jobs.value = jobs.value.filter(j => j.id !== id)
      
      if (currentJob.value?.id === id) {
        currentJob.value = null
      }
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to delete job'
      console.error('Error deleting job:', err)
      return false
    }
  }

  const retryJob = async (id: string): Promise<Job | null> => {
    try {
      const job = await api.retryJob(id)
      updateJobInList(job)
      return job
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to retry job'
      console.error('Error retrying job:', err)
      return null
    }
  }

  const addActivePolling = (jobId: string): void => {
    activePolls.value.add(jobId)
  }

  const removeActivePolling = (jobId: string): void => {
    activePolls.value.delete(jobId)
  }

  const isPolling = (jobId: string): boolean => {
    return activePolls.value.has(jobId)
  }

  const clearError = (): void => {
    error.value = null
  }

  const reset = (): void => {
    jobs.value = []
    currentJob.value = null
    loading.value = false
    error.value = null
    activePolls.value.clear()
  }

  return {
    // State
    jobs,
    currentJob,
    loading,
    error,
    activePolls,
    
    // Getters
    activeJobs,
    completedJobs,
    failedJobs,
    getJobById,
    
    // Actions
    fetchJobs,
    fetchJob,
    updateJobInList,
    deleteJob,
    retryJob,
    addActivePolling,
    removeActivePolling,
    isPolling,
    clearError,
    reset
  }
})
