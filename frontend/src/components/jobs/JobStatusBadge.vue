<script setup lang="ts">
import { computed } from 'vue'
import type { JobStatusType } from '@/types'

interface Props {
  status: JobStatusType
  showIcon?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showIcon: true
})

const badgeConfig = computed(() => {
  switch (props.status) {
    case 'pending':
      return {
        severity: 'secondary',
        label: 'Pending',
        icon: 'pi pi-clock',
        tooltip: 'Job is queued and waiting to start'
      }
    case 'processing':
      return {
        severity: 'info',
        label: 'Processing',
        icon: 'pi pi-spin pi-spinner',
        tooltip: 'Job is currently being processed'
      }
    case 'completed':
      return {
        severity: 'success',
        label: 'Completed',
        icon: 'pi pi-check-circle',
        tooltip: 'Job completed successfully'
      }
    case 'failed':
      return {
        severity: 'danger',
        label: 'Failed',
        icon: 'pi pi-times-circle',
        tooltip: 'Job failed with errors'
      }
    default:
      return {
        severity: 'secondary',
        label: 'Unknown',
        icon: 'pi pi-question-circle',
        tooltip: 'Unknown status'
      }
  }
})
</script>

<template>
  <div 
    v-tooltip.top="badgeConfig.tooltip"
    :class="[
      'job-status-badge inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-semibold',
      `badge-${badgeConfig.severity}`
    ]"
  >
    <i v-if="showIcon" :class="badgeConfig.icon"></i>
    <span>{{ badgeConfig.label }}</span>
  </div>
</template>

<style scoped>
.job-status-badge {
  white-space: nowrap;
}

.badge-secondary {
  background-color: var(--surface-200);
  color: var(--surface-700);
}

.badge-info {
  background-color: var(--blue-100);
  color: var(--blue-700);
}

.badge-success {
  background-color: var(--green-100);
  color: var(--green-700);
}

.badge-danger {
  background-color: var(--red-100);
  color: var(--red-700);
}

.dark .badge-secondary {
  background-color: var(--surface-700);
  color: var(--surface-200);
}

.dark .badge-info {
  background-color: var(--blue-900);
  color: var(--blue-300);
}

.dark .badge-success {
  background-color: var(--green-900);
  color: var(--green-300);
}

.dark .badge-danger {
  background-color: var(--red-900);
  color: var(--red-300);
}
</style>
