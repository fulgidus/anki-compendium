<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useJobsStore } from '@/stores/jobs'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import Skeleton from 'primevue/skeleton'
import Message from 'primevue/message'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'
import JobCard from '@/components/jobs/JobCard.vue'
import type { JobStatusType, JobFilters } from '@/types'

const router = useRouter()
const jobsStore = useJobsStore()

const statusFilter = ref<JobStatusType | 'all'>('all')
const sortBy = ref<'date' | 'status' | 'name'>('date')
const sortOrder = ref<'asc' | 'desc'>('desc')
const autoRefreshInterval = ref<ReturnType<typeof setInterval> | null>(null)

const statusOptions = [
  { label: 'All Jobs', value: 'all' },
  { label: 'Pending', value: 'pending' },
  { label: 'Processing', value: 'processing' },
  { label: 'Completed', value: 'completed' },
  { label: 'Failed', value: 'failed' }
]

const sortOptions = [
  { label: 'Date', value: 'date' },
  { label: 'Status', value: 'status' },
  { label: 'Name', value: 'name' }
]

const sortOrderOptions = [
  { label: 'Newest First', value: 'desc' },
  { label: 'Oldest First', value: 'asc' }
]

const filteredJobs = computed(() => {
  let jobs = [...jobsStore.jobs]
  
  // Apply status filter
  if (statusFilter.value !== 'all') {
    jobs = jobs.filter(job => job.status === statusFilter.value)
  }
  
  // Apply sorting
  jobs.sort((a, b) => {
    let comparison = 0
    
    switch (sortBy.value) {
      case 'date':
        comparison = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
        break
      case 'status':
        comparison = a.status.localeCompare(b.status)
        break
      case 'name':
        comparison = a.deckName.localeCompare(b.deckName)
        break
    }
    
    return sortOrder.value === 'asc' ? comparison : -comparison
  })
  
  return jobs
})

const hasActiveJobs = computed(() => {
  return jobsStore.activeJobs.length > 0
})

const isEmpty = computed(() => {
  return !jobsStore.loading && jobsStore.jobs.length === 0
})

async function fetchJobs() {
  const filters: JobFilters = {
    sortBy: sortBy.value,
    sortOrder: sortOrder.value
  }
  
  if (statusFilter.value !== 'all') {
    filters.status = statusFilter.value as JobStatusType
  }
  
  await jobsStore.fetchJobs(filters)
}

function handleRefresh() {
  fetchJobs()
}

function handleUploadNew() {
  router.push({ name: 'upload' })
}

function setupAutoRefresh() {
  // Only auto-refresh if there are active jobs
  if (hasActiveJobs.value) {
    // Refresh every 30 seconds when there are active jobs
    autoRefreshInterval.value = setInterval(() => {
      if (hasActiveJobs.value) {
        fetchJobs()
      } else {
        stopAutoRefresh()
      }
    }, 30000)
  }
}

function stopAutoRefresh() {
  if (autoRefreshInterval.value) {
    clearInterval(autoRefreshInterval.value)
    autoRefreshInterval.value = null
  }
}

onMounted(async () => {
  await fetchJobs()
  setupAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<template>
  <div class="jobs-page">
    <!-- Confirmation Dialog -->
    <ConfirmDialog />
    
    <!-- Toast for notifications -->
    <Toast />
    
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title">Jobs</h1>
          <p class="page-subtitle">Track your PDF processing jobs and download completed decks</p>
        </div>
        <div class="header-actions">
          <Button 
            label="Refresh" 
            icon="pi pi-refresh"
            text
            @click="handleRefresh"
            :loading="jobsStore.loading"
          />
          <Button 
            label="Upload New PDF" 
            icon="pi pi-plus"
            @click="handleUploadNew"
          />
        </div>
      </div>
    </div>

    <!-- Filters and Sort Controls -->
    <div class="controls-bar">
      <div class="control-group">
        <label class="control-label">Status:</label>
        <Dropdown 
          v-model="statusFilter" 
          :options="statusOptions" 
          optionLabel="label" 
          optionValue="value"
          placeholder="Filter by status"
          @change="fetchJobs"
          class="control-dropdown"
        />
      </div>

      <div class="control-group">
        <label class="control-label">Sort by:</label>
        <Dropdown 
          v-model="sortBy" 
          :options="sortOptions" 
          optionLabel="label" 
          optionValue="value"
          @change="fetchJobs"
          class="control-dropdown"
        />
      </div>

      <div class="control-group">
        <label class="control-label">Order:</label>
        <Dropdown 
          v-model="sortOrder" 
          :options="sortOrderOptions" 
          optionLabel="label" 
          optionValue="value"
          @change="fetchJobs"
          class="control-dropdown"
        />
      </div>
    </div>

    <!-- Active Jobs Notice -->
    <Message 
      v-if="hasActiveJobs" 
      severity="info" 
      :closable="false"
      class="active-jobs-message"
    >
      <div class="flex items-center gap-2">
        <i class="pi pi-spin pi-spinner"></i>
        <span>{{ jobsStore.activeJobs.length }} job(s) are currently being processed. Real-time updates are active.</span>
      </div>
    </Message>

    <!-- Error Message -->
    <Message 
      v-if="jobsStore.error" 
      severity="error" 
      @close="jobsStore.clearError()"
      class="error-message"
    >
      {{ jobsStore.error }}
    </Message>

    <!-- Loading Skeleton -->
    <div v-if="jobsStore.loading && jobsStore.jobs.length === 0" class="jobs-list">
      <div v-for="i in 3" :key="i" class="skeleton-card">
        <Skeleton height="200px" borderRadius="8px" />
      </div>
    </div>

    <!-- Jobs List -->
    <div v-else-if="filteredJobs.length > 0" class="jobs-list">
      <JobCard 
        v-for="job in filteredJobs" 
        :key="job.id" 
        :job="job"
        :autoStartPolling="job.status === 'pending' || job.status === 'processing'"
      />
    </div>

    <!-- Empty State -->
    <div v-else-if="isEmpty" class="empty-state">
      <div class="empty-state-icon">
        <i class="pi pi-inbox"></i>
      </div>
      <h3 class="empty-state-title">No jobs yet</h3>
      <p class="empty-state-text">
        Upload a PDF to get started with generating your first Anki deck
      </p>
      <Button 
        label="Upload PDF" 
        icon="pi pi-upload"
        size="large"
        @click="handleUploadNew"
        class="mt-4"
      />
    </div>

    <!-- No Results from Filter -->
    <div v-else class="empty-state">
      <div class="empty-state-icon">
        <i class="pi pi-filter-slash"></i>
      </div>
      <h3 class="empty-state-title">No jobs found</h3>
      <p class="empty-state-text">
        Try adjusting your filters to see more results
      </p>
      <Button 
        label="Clear Filters" 
        text
        @click="statusFilter = 'all'; fetchJobs()"
        class="mt-4"
      />
    </div>
  </div>
</template>

<style scoped>
.jobs-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Page Header */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: #111827;
}

.page-subtitle {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
}

/* Controls Bar */
.controls-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  padding: 1.5rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.control-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.control-dropdown {
  min-width: 180px;
}

/* Messages */
.active-jobs-message {
  margin-bottom: 1.5rem;
}

.error-message {
  margin-bottom: 1.5rem;
}

/* Jobs List */
.jobs-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Loading Skeleton */
.skeleton-card {
  margin-bottom: 1rem;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-state-icon {
  width: 5rem;
  height: 5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f3f4f6;
  border-radius: 50%;
  margin-bottom: 1.5rem;
}

.empty-state-icon i {
  font-size: 2.5rem;
  color: #9ca3af;
}

.empty-state-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.5rem 0;
}

.empty-state-text {
  font-size: 1rem;
  color: #6b7280;
  max-width: 400px;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .jobs-page {
    padding: 1.5rem;
  }
}

@media (max-width: 768px) {
  .jobs-page {
    padding: 1rem;
  }

  .header-content {
    flex-direction: column;
    gap: 1rem;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .header-actions > * {
    width: 100%;
  }

  .controls-bar {
    flex-direction: column;
    gap: 1rem;
  }

  .control-group {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .control-dropdown {
    width: 100%;
  }

  .page-title {
    font-size: 1.5rem;
  }
}

/* Dark Mode Support */
@media (prefers-color-scheme: dark) {
  .page-title {
    color: #f9fafb;
  }

  .page-subtitle {
    color: #9ca3af;
  }

  .controls-bar {
    background-color: #1f2937;
  }

  .control-label {
    color: #d1d5db;
  }

  .empty-state-icon {
    background-color: #374151;
  }

  .empty-state-title {
    color: #f9fafb;
  }

  .empty-state-text {
    color: #9ca3af;
  }
}
</style>
