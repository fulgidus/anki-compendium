<script setup lang="ts">
import { ref, computed } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import Card from 'primevue/card'
import Button from 'primevue/button'
import { api } from '@/api/client'
import { useJobsStore } from '@/stores/jobs'
import { useJobPolling } from '@/composables/useJobPolling'
import JobStatusBadge from './JobStatusBadge.vue'
import JobProgressBar from './JobProgressBar.vue'
import type { Job } from '@/types'

interface Props {
  job: Job
  autoStartPolling?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  autoStartPolling: true
})
const confirm = useConfirm()
const toast = useToast()
const jobsStore = useJobsStore()

const expanded = ref(false)
const downloading = ref(false)
const deleting = ref(false)
const retrying = ref(false)

// Setup polling
const { job: liveJob, isPolling, startPolling, stopPolling } = useJobPolling(() => props.job.id)

// Start polling if job is active and autoStart is true
if (props.autoStartPolling && (props.job.status === 'pending' || props.job.status === 'processing')) {
  startPolling()
}

// Use live job data if available, otherwise use prop
const currentJob = computed(() => liveJob.value || props.job)

const createdDate = computed(() => {
  return new Date(currentJob.value.createdAt).toLocaleString()
})

const completedDate = computed(() => {
  if (!currentJob.value.completedAt) return null
  return new Date(currentJob.value.completedAt).toLocaleString()
})

const processingTime = computed(() => {
  if (!currentJob.value.startedAt) return null
  
  const start = new Date(currentJob.value.startedAt).getTime()
  const end = currentJob.value.completedAt 
    ? new Date(currentJob.value.completedAt).getTime()
    : Date.now()
  
  const seconds = Math.floor((end - start) / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  if (minutes > 0) {
    return `${minutes}m ${remainingSeconds}s`
  }
  return `${seconds}s`
})

const canDownload = computed(() => {
  return currentJob.value.status === 'completed' && currentJob.value.deckId
})

const canRetry = computed(() => {
  return currentJob.value.status === 'failed'
})

async function handleDownload() {
  if (!currentJob.value.deckId) return
  
  downloading.value = true
  try {
    const blob = await api.downloadDeck(currentJob.value.deckId)
    
    // Create download link
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${currentJob.value.deckName}.apkg`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    toast.add({
      severity: 'success',
      summary: 'Download Started',
      detail: `Downloading ${currentJob.value.deckName}.apkg`,
      life: 3000
    })
  } catch (error: any) {
    console.error('Download error:', error)
    toast.add({
      severity: 'error',
      summary: 'Download Failed',
      detail: error.response?.data?.message || 'Failed to download deck',
      life: 5000
    })
  } finally {
    downloading.value = false
  }
}

function handleDelete() {
  confirm.require({
    message: `Are you sure you want to delete this job? This action cannot be undone.`,
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      deleting.value = true
      try {
        const success = await jobsStore.deleteJob(currentJob.value.id)
        
        if (success) {
          toast.add({
            severity: 'success',
            summary: 'Job Deleted',
            detail: 'Job has been deleted successfully',
            life: 3000
          })
          stopPolling()
        }
      } catch (error: any) {
        console.error('Delete error:', error)
        toast.add({
          severity: 'error',
          summary: 'Delete Failed',
          detail: 'Failed to delete job',
          life: 5000
        })
      } finally {
        deleting.value = false
      }
    }
  })
}

async function handleRetry() {
  retrying.value = true
  try {
    const retriedJob = await jobsStore.retryJob(currentJob.value.id)
    
    if (retriedJob) {
      toast.add({
        severity: 'success',
        summary: 'Job Restarted',
        detail: 'Job has been queued for retry',
        life: 3000
      })
      startPolling()
    }
  } catch (error: any) {
    console.error('Retry error:', error)
    toast.add({
      severity: 'error',
      summary: 'Retry Failed',
      detail: error.response?.data?.message || 'Failed to retry job',
      life: 5000
    })
  } finally {
    retrying.value = false
  }
}

function toggleExpanded() {
  expanded.value = !expanded.value
}
</script>

<template>
  <Card class="job-card">
    <template #header>
      <div class="job-card-header">
        <div class="job-info">
          <h3 class="job-name">{{ currentJob.deckName }}</h3>
          <p class="job-filename text-sm text-gray-600 dark:text-gray-400">
            {{ currentJob.fileName }} • {{ currentJob.pageCount }} pages
          </p>
        </div>
        <JobStatusBadge :status="currentJob.status" />
      </div>
    </template>

    <template #content>
      <!-- Progress Section -->
      <div v-if="currentJob.status === 'pending' || currentJob.status === 'processing'" class="mb-4">
        <JobProgressBar :job="currentJob" :showStages="expanded" />
      </div>

      <!-- Error Message -->
      <div v-if="currentJob.status === 'failed' && currentJob.errorMessage" class="error-message mb-4">
        <i class="pi pi-exclamation-circle"></i>
        <span>{{ currentJob.errorMessage }}</span>
      </div>

      <!-- Metadata -->
      <div class="job-metadata">
        <div class="metadata-item">
          <i class="pi pi-calendar"></i>
          <span class="text-sm">Created: {{ createdDate }}</span>
        </div>
        
        <div v-if="completedDate" class="metadata-item">
          <i class="pi pi-check-circle"></i>
          <span class="text-sm">Completed: {{ completedDate }}</span>
        </div>
        
        <div v-if="processingTime" class="metadata-item">
          <i class="pi pi-clock"></i>
          <span class="text-sm">Processing time: {{ processingTime }}</span>
        </div>

        <div v-if="isPolling" class="metadata-item">
          <i class="pi pi-spin pi-spinner text-blue-500"></i>
          <span class="text-sm text-blue-500">Live updates active</span>
        </div>
      </div>

      <!-- Expandable Details -->
      <div v-if="expanded" class="expanded-details mt-4">
        <h4 class="text-sm font-semibold mb-2">Pipeline Stages:</h4>
        <div class="stages-list">
          <div 
            v-for="stage in currentJob.stages" 
            :key="stage.stage"
            class="stage-detail"
            :class="{
              'stage-detail-pending': stage.status === 'pending',
              'stage-detail-processing': stage.status === 'processing',
              'stage-detail-completed': stage.status === 'completed',
              'stage-detail-failed': stage.status === 'failed'
            }"
          >
            <div class="stage-detail-icon">
              <i v-if="stage.status === 'pending'" class="pi pi-circle"></i>
              <i v-else-if="stage.status === 'processing'" class="pi pi-spin pi-spinner"></i>
              <i v-else-if="stage.status === 'completed'" class="pi pi-check-circle"></i>
              <i v-else-if="stage.status === 'failed'" class="pi pi-times-circle"></i>
            </div>
            <div class="stage-detail-content">
              <span class="stage-detail-name">{{ stage.stage }}. {{ stage.name }}</span>
              <span v-if="stage.error" class="stage-detail-error text-xs">{{ stage.error }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="job-card-footer">
        <div class="footer-left">
          <Button 
            label="Details" 
            :icon="expanded ? 'pi pi-chevron-up' : 'pi pi-chevron-down'"
            text 
            size="small"
            @click="toggleExpanded"
          />
        </div>
        
        <div class="footer-right">
          <Button
            v-if="canDownload"
            label="Download"
            icon="pi pi-download"
            size="small"
            :loading="downloading"
            @click="handleDownload"
          />
          
          <Button
            v-if="canRetry"
            label="Retry"
            icon="pi pi-refresh"
            size="small"
            severity="warning"
            :loading="retrying"
            @click="handleRetry"
          />
          
          <Button
            label="Delete"
            icon="pi pi-trash"
            text
            size="small"
            severity="danger"
            :loading="deleting"
            @click="handleDelete"
          />
        </div>
      </div>
    </template>
  </Card>
</template>

<style scoped>
.job-card {
  margin-bottom: 1rem;
}

.job-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1.5rem 1.5rem 1rem;
  gap: 1rem;
}

.job-info {
  flex: 1;
  min-width: 0;
}

.job-name {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.job-filename {
  margin: 0;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
  color: #991b1b;
  font-size: 0.875rem;
}

.job-metadata {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 1rem;
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
}

.metadata-item i {
  font-size: 0.875rem;
}

/* Expanded Details */
.expanded-details {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.stages-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stage-detail {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s;
}

.stage-detail:hover {
  background-color: #f9fafb;
}

.stage-detail-icon {
  flex-shrink: 0;
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stage-detail-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stage-detail-name {
  font-size: 0.875rem;
  font-weight: 500;
}

.stage-detail-error {
  color: #dc2626;
}

/* Stage Status Colors */
.stage-detail-pending .stage-detail-icon {
  color: #9ca3af;
}

.stage-detail-processing .stage-detail-icon {
  color: #3b82f6;
}

.stage-detail-completed .stage-detail-icon {
  color: #10b981;
}

.stage-detail-failed .stage-detail-icon {
  color: #ef4444;
}

.stage-detail-failed .stage-detail-name {
  color: #dc2626;
}

/* Footer */
.job-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.footer-left,
.footer-right {
  display: flex;
  gap: 0.5rem;
}

/* Responsive */
@media (max-width: 768px) {
  .job-card-header {
    flex-direction: column;
  }
  
  .job-metadata {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .job-card-footer {
    flex-direction: column;
    align-items: stretch;
  }
  
  .footer-left,
  .footer-right {
    justify-content: center;
  }
}
</style>
