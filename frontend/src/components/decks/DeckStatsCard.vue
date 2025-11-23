<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useDecksStore } from '@/stores/decks'
import Card from 'primevue/card'
import Skeleton from 'primevue/skeleton'

const decksStore = useDecksStore()

const formattedStats = computed(() => {
  if (!decksStore.stats) return null

  return {
    totalDecks: decksStore.stats.totalDecks.toLocaleString(),
    totalCards: decksStore.stats.totalCards.toLocaleString(),
    decksThisWeek: decksStore.stats.decksThisWeek.toLocaleString(),
    decksThisMonth: decksStore.stats.decksThisMonth.toLocaleString(),
    topTags: decksStore.stats.topTags.slice(0, 5) // Show top 5 tags
  }
})

onMounted(() => {
  if (!decksStore.stats) {
    decksStore.fetchStats()
  }
})
</script>

<template>
  <Card class="deck-stats-card">
    <template #title>
      <div class="flex items-center gap-2">
        <i class="pi pi-chart-bar text-primary"></i>
        <span>Statistics</span>
      </div>
    </template>

    <template #content>
      <div v-if="decksStore.statsLoading" class="space-y-4">
        <Skeleton height="3rem" />
        <Skeleton height="3rem" />
        <Skeleton height="3rem" />
        <Skeleton height="3rem" />
      </div>

      <div v-else-if="formattedStats" class="stats-grid">
        <!-- Total Decks -->
        <div class="stat-item">
          <div class="stat-icon" style="background: var(--primary-100); color: var(--primary-600)">
            <i class="pi pi-box text-2xl"></i>
          </div>
          <div class="stat-content">
            <div class="stat-label">Total Decks</div>
            <div class="stat-value">{{ formattedStats.totalDecks }}</div>
          </div>
        </div>

        <!-- Total Cards -->
        <div class="stat-item">
          <div class="stat-icon" style="background: var(--green-100); color: var(--green-600)">
            <i class="pi pi-clone text-2xl"></i>
          </div>
          <div class="stat-content">
            <div class="stat-label">Total Cards</div>
            <div class="stat-value">{{ formattedStats.totalCards }}</div>
          </div>
        </div>

        <!-- This Week -->
        <div class="stat-item">
          <div class="stat-icon" style="background: var(--blue-100); color: var(--blue-600)">
            <i class="pi pi-calendar text-2xl"></i>
          </div>
          <div class="stat-content">
            <div class="stat-label">This Week</div>
            <div class="stat-value">{{ formattedStats.decksThisWeek }}</div>
          </div>
        </div>

        <!-- This Month -->
        <div class="stat-item">
          <div class="stat-icon" style="background: var(--purple-100); color: var(--purple-600)">
            <i class="pi pi-calendar-plus text-2xl"></i>
          </div>
          <div class="stat-content">
            <div class="stat-label">This Month</div>
            <div class="stat-value">{{ formattedStats.decksThisMonth }}</div>
          </div>
        </div>

        <!-- Top Tags -->
        <div v-if="formattedStats.topTags.length > 0" class="stat-item col-span-full">
          <div class="stat-content">
            <div class="stat-label mb-2">Top Tags</div>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tagItem in formattedStats.topTags"
                :key="tagItem.tag"
                class="tag-chip"
              >
                {{ tagItem.tag }} ({{ tagItem.count }})
              </span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center text-muted-color py-4">
        <i class="pi pi-chart-bar text-4xl mb-2"></i>
        <p>No statistics available</p>
      </div>
    </template>
  </Card>
</template>

<style scoped>
.deck-stats-card {
  height: 100%;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: var(--border-radius);
  background: var(--surface-50);
  border: 1px solid var(--surface-200);
  transition: all 0.2s;
}

.stat-item:hover {
  background: var(--surface-100);
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
  line-height: 1;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  background: var(--primary-100);
  color: var(--primary-700);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  font-weight: 500;
}

.col-span-full {
  grid-column: 1 / -1;
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-value {
    font-size: 1.25rem;
  }
}
</style>
