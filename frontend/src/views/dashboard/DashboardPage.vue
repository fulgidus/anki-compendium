<script setup lang="ts">
import { onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import { useDecksStore } from '@/stores/decks'
import { useAuthStore } from '@/stores/auth'
import StatCard from '@/components/common/StatCard.vue'
import ActivityList from '@/components/dashboard/ActivityList.vue'
import QuickActionsPanel from '@/components/dashboard/QuickActionsPanel.vue'
import { DeckCard } from '@/components/decks'

const router = useRouter()
const dashboardStore = useDashboardStore()
const decksStore = useDecksStore()
const authStore = useAuthStore()

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
})

const userName = computed(() => {
  return authStore.user?.username || 'User'
})

onMounted(async () => {
  // Fetch dashboard data
  await dashboardStore.fetchDashboardData()
  
  // Start auto-refresh for stats
  dashboardStore.startAutoRefresh()
})

onUnmounted(() => {
  // Stop auto-refresh when leaving dashboard
  dashboardStore.stopAutoRefresh()
})

const handleViewAllJobs = () => {
  router.push({ name: 'jobs' })
}

const handleViewAllDecks = () => {
  router.push({ name: 'decks' })
}

const handleDownloadDeck = async (deckId: string, deckName: string) => {
  await decksStore.downloadDeck(deckId, deckName)
}
</script>

<template>
  <div class="dashboard-page p-4 md:p-6 lg:p-8">
    <!-- Welcome Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">
        {{ greeting }}, {{ userName }}! 👋
      </h1>
      <p class="text-gray-600">
        Here's an overview of your Anki deck generation activity
      </p>
    </div>

    <!-- Stats Cards Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-8">
      <StatCard
        icon="pi-book"
        label="Total Decks"
        :value="dashboardStore.stats.totalDecks"
        color="primary"
        :loading="dashboardStore.loading"
        subtitle="All time"
      />
      
      <StatCard
        icon="pi-credit-card"
        label="Total Cards"
        :value="dashboardStore.stats.totalCards"
        color="success"
        :loading="dashboardStore.loading"
        subtitle="Across all decks"
      />
      
      <StatCard
        icon="pi-briefcase"
        label="Active Jobs"
        :value="dashboardStore.stats.activeJobs"
        color="info"
        :loading="dashboardStore.loading"
        subtitle="Currently processing"
      />
      
      <StatCard
        icon="pi-calendar"
        label="Decks This Week"
        :value="dashboardStore.stats.decksThisWeek"
        color="warning"
        :loading="dashboardStore.loading"
        subtitle="Last 7 days"
      />
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      <!-- Recent Activity (2/3 width) -->
      <div class="lg:col-span-2">
        <ActivityList
          :activities="dashboardStore.recentActivity"
          :loading="dashboardStore.loading"
          @view-all="handleViewAllJobs"
        />
      </div>

      <!-- Quick Actions (1/3 width) -->
      <div>
        <QuickActionsPanel />
      </div>
    </div>

    <!-- Recent Decks Section -->
    <div>
      <Card>
        <template #header>
          <div class="flex items-center justify-between p-4 border-b">
            <h3 class="text-lg font-semibold">Recent Decks</h3>
            <Button
              v-if="dashboardStore.recentDecks.length > 0"
              label="View All"
              link
              icon="pi pi-arrow-right"
              icon-pos="right"
              @click="handleViewAllDecks"
            />
          </div>
        </template>

        <template #content>
          <!-- Loading State -->
          <div v-if="dashboardStore.loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="i in 3" :key="i" class="p-4 border rounded-lg">
              <Skeleton width="100%" height="8rem" class="mb-3" />
              <Skeleton width="80%" height="1.5rem" class="mb-2" />
              <Skeleton width="60%" height="1rem" />
            </div>
          </div>

          <!-- Empty State -->
          <div v-else-if="dashboardStore.recentDecks.length === 0" class="flex flex-col items-center justify-center py-12 text-center">
            <i class="pi pi-book text-6xl text-gray-300 mb-4" />
            <h4 class="text-lg font-semibold text-gray-600 mb-2">No Decks Yet</h4>
            <p class="text-sm text-gray-500 mb-4">
              Start by uploading a PDF to generate your first Anki deck
            </p>
            <Button
              label="Upload PDF"
              icon="pi pi-upload"
              @click="router.push({ name: 'upload' })"
            />
          </div>

          <!-- Decks Grid -->
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <DeckCard
              v-for="deck in dashboardStore.recentDecks"
              :key="deck.id"
              :deck="deck"
              @download="handleDownloadDeck(deck.id, deck.name)"
            />
          </div>
        </template>
      </Card>
    </div>

    <!-- Error Message -->
    <Message
      v-if="dashboardStore.error"
      severity="error"
      class="mt-4"
      @close="dashboardStore.clearError"
    >
      {{ dashboardStore.error }}
    </Message>
  </div>
</template>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background-color: #f9fafb;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .dashboard-page {
    padding: 1rem;
  }
}
</style>
