<script setup lang="ts">
import { computed } from 'vue'

export interface StatCardProps {
  icon: string
  label: string
  value: number | string
  subtitle?: string
  trend?: {
    direction: 'up' | 'down'
    value: number
  }
  color?: 'primary' | 'success' | 'info' | 'warning' | 'danger'
  loading?: boolean
}

const props = withDefaults(defineProps<StatCardProps>(), {
  color: 'primary',
  loading: false
})

const colorClass = computed(() => {
  const colorMap = {
    primary: 'text-primary-500 bg-primary-50',
    success: 'text-green-500 bg-green-50',
    info: 'text-blue-500 bg-blue-50',
    warning: 'text-orange-500 bg-orange-50',
    danger: 'text-red-500 bg-red-50'
  }
  return colorMap[props.color] || colorMap.primary
})

const trendClass = computed(() => {
  if (!props.trend) return ''
  return props.trend.direction === 'up' 
    ? 'text-green-600' 
    : 'text-red-600'
})

const trendIcon = computed(() => {
  if (!props.trend) return ''
  return props.trend.direction === 'up' 
    ? 'pi-arrow-up' 
    : 'pi-arrow-down'
})
</script>

<template>
  <Card class="stat-card">
    <template #content>
      <div class="flex flex-col gap-4">
        <!-- Icon and Label -->
        <div class="flex items-center justify-between">
          <div :class="['stat-icon p-3 rounded-lg', colorClass]">
            <i v-if="!loading" :class="['text-2xl', icon]" />
            <Skeleton v-else width="2rem" height="2rem" />
          </div>
        </div>

        <!-- Value -->
        <div class="flex flex-col gap-1">
          <div class="flex items-baseline gap-2">
            <span v-if="!loading" class="text-3xl font-bold">{{ value }}</span>
            <Skeleton v-else width="6rem" height="2.5rem" />
            
            <!-- Trend Indicator -->
            <div v-if="trend && !loading" :class="['flex items-center gap-1 text-sm', trendClass]">
              <i :class="['text-xs', trendIcon]" />
              <span>{{ trend.value }}%</span>
            </div>
          </div>
          
          <span v-if="!loading" class="text-sm text-gray-600">{{ label }}</span>
          <Skeleton v-else width="8rem" height="1rem" />
        </div>

        <!-- Subtitle -->
        <div v-if="subtitle && !loading" class="text-xs text-gray-500">
          {{ subtitle }}
        </div>
        <Skeleton v-else-if="subtitle && loading" width="100%" height="0.75rem" />
      </div>
    </template>
  </Card>
</template>

<style scoped>
.stat-card {
  height: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  transition: all 0.3s;
}

.stat-card:hover .stat-icon {
  transform: scale(1.05);
}
</style>
