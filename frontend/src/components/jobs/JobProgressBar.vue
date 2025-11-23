<script setup lang="ts">
import { computed } from 'vue'
import ProgressBar from 'primevue/progressbar'
import type { Job } from '@/types'

interface Props {
  job: Job
  showStages?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showStages: false
})

const progressPercent = computed(() => {
  return Math.min(Math.max(props.job.progress, 0), 100)
})

const progressColor = computed(() => {
  if (props.job.status === 'failed') return 'danger'
  if (props.job.status === 'completed') return 'success'
  return 'info'
})

const stageProgress = computed(() => {
  const total = 8
  const current = props.job.currentStage
  return {
    current,
    total,
    percent: Math.round((current / total) * 100)
  }
})
</script>

<template>
  <div class="job-progress">
    <!-- Main Progress Bar -->
    <div class="progress-header mb-2">
      <span class="text-sm font-semibold">{{ job.stageName }}</span>
      <span class="text-sm font-semibold">{{ progressPercent }}%</span>
    </div>
    
    <ProgressBar 
      :value="progressPercent" 
      :showValue="false"
      :color="progressColor"
      class="mb-3"
    />

    <!-- Stage Indicator -->
    <div v-if="showStages" class="stage-indicator">
      <div class="text-xs text-gray-600 dark:text-gray-400 mb-2">
        Stage {{ stageProgress.current }} of {{ stageProgress.total }}
      </div>
      
      <div class="stages-grid">
        <div 
          v-for="stage in job.stages" 
          :key="stage.stage"
          class="stage-item"
          :class="{
            'stage-pending': stage.status === 'pending',
            'stage-processing': stage.status === 'processing',
            'stage-completed': stage.status === 'completed',
            'stage-failed': stage.status === 'failed'
          }"
          v-tooltip.top="stage.name"
        >
          <div class="stage-number">{{ stage.stage }}</div>
          <div class="stage-bar"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.job-progress {
  width: 100%;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Stage Indicator Styles */
.stages-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 0.5rem;
}

.stage-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stage-number {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.stage-bar {
  width: 100%;
  height: 0.25rem;
  border-radius: 0.125rem;
  transition: all 0.3s ease;
}

/* Stage States */
.stage-pending .stage-number {
  background-color: #e5e7eb;
  color: #9ca3af;
}

.stage-pending .stage-bar {
  background-color: #e5e7eb;
}

.stage-processing .stage-number {
  background-color: #3b82f6;
  color: white;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.stage-processing .stage-bar {
  background-color: #3b82f6;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.stage-completed .stage-number {
  background-color: #10b981;
  color: white;
}

.stage-completed .stage-bar {
  background-color: #10b981;
}

.stage-failed .stage-number {
  background-color: #ef4444;
  color: white;
}

.stage-failed .stage-bar {
  background-color: #ef4444;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .stages-grid {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .stage-number {
    width: 1.5rem;
    height: 1.5rem;
    font-size: 0.625rem;
  }
}
</style>
