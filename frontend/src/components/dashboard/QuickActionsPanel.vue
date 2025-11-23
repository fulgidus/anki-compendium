<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const quickActions = [
  {
    label: 'Upload PDF',
    icon: 'pi-upload',
    color: 'primary',
    route: 'upload',
    description: 'Generate a new Anki deck'
  },
  {
    label: 'View Jobs',
    icon: 'pi-briefcase',
    color: 'info',
    route: 'jobs',
    description: 'Check processing status'
  },
  {
    label: 'Browse Decks',
    icon: 'pi-book',
    color: 'success',
    route: 'decks',
    description: 'Manage your decks'
  },
  {
    label: 'Settings',
    icon: 'pi-cog',
    color: 'secondary',
    route: 'profile',
    description: 'Update your preferences'
  }
]



const navigateTo = (route: string) => {
  router.push({ name: route })
}
</script>

<template>
  <Card>
    <template #header>
      <div class="p-4 border-b">
        <h3 class="text-lg font-semibold">Quick Actions</h3>
      </div>
    </template>

    <template #content>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div
          v-for="action in quickActions"
          :key="action.label"
          class="quick-action-item p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md"
          :class="`action-${action.color}`"
          @click="navigateTo(action.route)"
        >
          <div class="flex items-start gap-3">
            <div :class="['action-icon p-3 rounded-lg', `bg-${action.color}-100`]">
              <i :class="['text-2xl', action.icon, `text-${action.color}-600`]" />
            </div>
            <div class="flex-1 min-w-0">
              <h4 class="font-semibold text-gray-900 mb-1">{{ action.label }}</h4>
              <p class="text-sm text-gray-600">{{ action.description }}</p>
            </div>
            <i class="pi pi-arrow-right text-gray-400 mt-1" />
          </div>
        </div>
      </div>
    </template>
  </Card>
</template>

<style scoped>
.quick-action-item {
  transition: all 0.2s ease;
  border-color: #e5e7eb;
}

.quick-action-item:hover {
  transform: translateY(-2px);
  border-color: var(--primary-color);
}

.action-icon {
  transition: transform 0.2s;
}

.quick-action-item:hover .action-icon {
  transform: scale(1.1);
}

/* Color-specific hover effects */
.action-primary:hover {
  border-color: var(--primary-500);
  background-color: rgba(var(--primary-500-rgb), 0.02);
}

.action-info:hover {
  border-color: var(--blue-500);
  background-color: rgba(var(--blue-500-rgb), 0.02);
}

.action-success:hover {
  border-color: var(--green-500);
  background-color: rgba(var(--green-500-rgb), 0.02);
}

.action-secondary:hover {
  border-color: var(--surface-500);
  background-color: rgba(var(--surface-500-rgb), 0.02);
}

/* Primary */
.bg-primary-100 {
  background-color: var(--primary-50);
}

.text-primary-600 {
  color: var(--primary-600);
}

/* Info/Blue */
.bg-info-100 {
  background-color: var(--blue-50);
}

.text-info-600 {
  color: var(--blue-600);
}

/* Success/Green */
.bg-success-100 {
  background-color: var(--green-50);
}

.text-success-600 {
  color: var(--green-600);
}

/* Secondary */
.bg-secondary-100 {
  background-color: var(--surface-100);
}

.text-secondary-600 {
  color: var(--surface-600);
}
</style>
