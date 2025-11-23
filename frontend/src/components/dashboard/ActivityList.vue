<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import type { Activity } from '@/types'
import { JobStatusBadge } from '@/components/jobs'

dayjs.extend(relativeTime)

interface ActivityListProps {
  activities: Activity[]
  loading?: boolean
  showViewAll?: boolean
}

withDefaults(defineProps<ActivityListProps>(), {
  loading: false,
  showViewAll: true
})

const emit = defineEmits<{
  viewAll: []
}>()

const router = useRouter()

const getActivityIcon = (type: string): string => {
  const iconMap: Record<string, string> = {
    job: 'pi-briefcase',
    deck: 'pi-book',
    upload: 'pi-upload'
  }
  return iconMap[type] || 'pi-circle'
}

const getActivityColor = (type: string): string => {
  const colorMap: Record<string, string> = {
    job: 'text-blue-600 bg-blue-100',
    deck: 'text-green-600 bg-green-100',
    upload: 'text-purple-600 bg-purple-100'
  }
  return colorMap[type] || 'text-gray-600 bg-gray-100'
}

const formatTimestamp = (timestamp: string): string => {
  return dayjs(timestamp).fromNow()
}

const handleActivityClick = (activity: Activity) => {
  if (activity.type === 'job' && activity.metadata?.jobId) {
    router.push({ name: 'jobs', query: { id: activity.metadata.jobId } })
  } else if (activity.type === 'deck' && activity.metadata?.deckId) {
    router.push({ name: 'decks', query: { id: activity.metadata.deckId } })
  }
}

const handleViewAll = () => {
  emit('viewAll')
}
</script>

<template>
  <Card>
    <template #header>
      <div class="flex items-center justify-between p-4 border-b">
        <h3 class="text-lg font-semibold">Recent Activity</h3>
      </div>
    </template>

    <template #content>
      <div class="flex flex-col">
        <!-- Loading State -->
        <div v-if="loading" class="flex flex-col gap-3">
          <div v-for="i in 5" :key="i" class="flex items-center gap-3 p-3">
            <Skeleton shape="circle" size="3rem" />
            <div class="flex-1">
              <Skeleton width="60%" height="1.5rem" class="mb-2" />
              <Skeleton width="40%" height="1rem" />
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="activities.length === 0" class="flex flex-col items-center justify-center py-12 text-center">
          <i class="pi pi-inbox text-6xl text-gray-300 mb-4" />
          <h4 class="text-lg font-semibold text-gray-600 mb-2">No Activity Yet</h4>
          <p class="text-sm text-gray-500 mb-4">Start by uploading a PDF to generate your first deck</p>
          <Button
            label="Upload PDF"
            icon="pi pi-upload"
            @click="router.push({ name: 'upload' })"
          />
        </div>

        <!-- Activity List -->
        <div v-else class="flex flex-col">
          <div
            v-for="activity in activities"
            :key="activity.id"
            class="activity-item flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
            @click="handleActivityClick(activity)"
          >
            <!-- Icon -->
            <div :class="['activity-icon flex items-center justify-center w-12 h-12 rounded-full', getActivityColor(activity.type)]">
              <i :class="['text-xl', getActivityIcon(activity.type)]" />
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="font-medium text-gray-900 truncate">{{ activity.title }}</span>
                <JobStatusBadge v-if="activity.status" :status="activity.status" />
              </div>
              <div class="flex items-center gap-2 text-sm text-gray-500">
                <span>{{ formatTimestamp(activity.timestamp) }}</span>
                <span v-if="activity.metadata?.cardCount" class="flex items-center gap-1">
                  <i class="pi pi-credit-card text-xs" />
                  {{ activity.metadata.cardCount }} cards
                </span>
              </div>
            </div>

            <!-- Action Icon -->
            <i class="pi pi-chevron-right text-gray-400" />
          </div>
        </div>

        <!-- View All Link -->
        <div v-if="showViewAll && activities.length > 0" class="mt-4 pt-4 border-t text-center">
          <Button
            label="View All Activity"
            link
            icon="pi pi-arrow-right"
            icon-pos="right"
            @click="handleViewAll"
          />
        </div>
      </div>
    </template>
  </Card>
</template>

<style scoped>
.activity-item {
  transition: all 0.2s;
}

.activity-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.activity-icon {
  transition: transform 0.2s;
}

.activity-item:hover .activity-icon {
  transform: scale(1.05);
}
</style>
