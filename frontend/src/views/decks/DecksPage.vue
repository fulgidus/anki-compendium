<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDecksStore } from '@/stores/decks'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import type { Deck } from '@/types'

// PrimeVue Components
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Checkbox from 'primevue/checkbox'
import Skeleton from 'primevue/skeleton'
import Message from 'primevue/message'
import ConfirmDialog from 'primevue/confirmdialog'
import Toast from 'primevue/toast'

// Custom Components
import { DeckCard, DeckDetailModal, DeckStatsCard } from '@/components/decks'

const router = useRouter()
const decksStore = useDecksStore()
const toast = useToast()
const confirm = useConfirm()

// State
const searchQuery = ref('')
const searchDebounceTimer = ref<number | null>(null)
const viewMode = ref<'grid' | 'list'>('grid')
const sortBy = ref<'date' | 'name' | 'cardCount'>('date')
const sortOrder = ref<'asc' | 'desc'>('desc')
const selectedDeckIds = ref<Set<string>>(new Set())
const detailModalVisible = ref(false)
const selectedDeck = ref<Deck | null>(null)
const isSelectMode = ref(false)

// Computed
const hasDecks = computed(() => decksStore.decks.length > 0)
const hasSelection = computed(() => selectedDeckIds.value.size > 0)
const isAllSelected = computed(() => 
  hasDecks.value && 
  selectedDeckIds.value.size === decksStore.filteredDecks.length
)

const sortOptions = [
  { label: 'Date Created', value: 'date' },
  { label: 'Name', value: 'name' },
  { label: 'Card Count', value: 'cardCount' }
]

// Methods
const fetchDecks = async () => {
  try {
    await decksStore.fetchDecks()
  } catch (err) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load decks',
      life: 5000
    })
  }
}

const handleSearch = (event: Event) => {
  const value = (event.target as HTMLInputElement).value
  
  // Debounce search
  if (searchDebounceTimer.value) {
    clearTimeout(searchDebounceTimer.value)
  }
  
  searchDebounceTimer.value = window.setTimeout(() => {
    searchQuery.value = value
    decksStore.searchDecks(value)
  }, 300)
}

const handleSortChange = () => {
  decksStore.setFilters({
    sortBy: sortBy.value,
    sortOrder: sortOrder.value
  })
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  handleSortChange()
}

const handleDownload = async (deckId: string) => {
  const deck = decksStore.getDeckById(deckId)
  if (!deck) return

  toast.add({
    severity: 'info',
    summary: 'Downloading',
    detail: `Downloading ${deck.name}...`,
    life: 3000
  })

  const success = await decksStore.downloadDeck(deckId, deck.name)
  
  if (success) {
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `${deck.name} downloaded successfully`,
      life: 3000
    })
  } else {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: decksStore.error || 'Failed to download deck',
      life: 5000
    })
    decksStore.clearError()
  }
}

const handleDelete = (deckId: string) => {
  const deck = decksStore.getDeckById(deckId)
  if (!deck) return

  confirm.require({
    message: `Are you sure you want to delete "${deck.name}"? This action cannot be undone.`,
    header: 'Confirm Deletion',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      const success = await decksStore.deleteDeck(deckId)
      
      if (success) {
        toast.add({
          severity: 'success',
          summary: 'Deleted',
          detail: `${deck.name} was deleted`,
          life: 3000
        })
        
        // Remove from selection if it was selected
        selectedDeckIds.value.delete(deckId)
      } else {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: decksStore.error || 'Failed to delete deck',
          life: 5000
        })
        decksStore.clearError()
      }
    }
  })
}

const handleBulkDelete = () => {
  const count = selectedDeckIds.value.size
  
  confirm.require({
    message: `Are you sure you want to delete ${count} deck${count > 1 ? 's' : ''}? This action cannot be undone.`,
    header: 'Confirm Bulk Deletion',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      const ids = Array.from(selectedDeckIds.value)
      const success = await decksStore.deleteDecks(ids)
      
      if (success) {
        toast.add({
          severity: 'success',
          summary: 'Deleted',
          detail: `${count} deck${count > 1 ? 's' : ''} deleted`,
          life: 3000
        })
        selectedDeckIds.value.clear()
        isSelectMode.value = false
      } else {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: decksStore.error || 'Failed to delete decks',
          life: 5000
        })
        decksStore.clearError()
      }
    }
  })
}

const handleViewDetails = (deckId: string) => {
  const deck = decksStore.getDeckById(deckId)
  if (deck) {
    selectedDeck.value = deck
    detailModalVisible.value = true
  }
}

const handleRegenerate = (deck: Deck) => {
  // Navigate to upload page with pre-filled settings
  router.push({
    name: 'upload',
    query: {
      regenerate: deck.jobId,
      fileName: deck.fileName
    }
  })
  
  toast.add({
    severity: 'info',
    summary: 'Regenerate Deck',
    detail: 'Redirecting to upload page...',
    life: 2000
  })
}

const toggleSelectMode = () => {
  isSelectMode.value = !isSelectMode.value
  if (!isSelectMode.value) {
    selectedDeckIds.value.clear()
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedDeckIds.value.clear()
  } else {
    decksStore.filteredDecks.forEach(deck => {
      selectedDeckIds.value.add(deck.id)
    })
  }
}

const toggleSelectDeck = (deckId: string) => {
  if (selectedDeckIds.value.has(deckId)) {
    selectedDeckIds.value.delete(deckId)
  } else {
    selectedDeckIds.value.add(deckId)
  }
}

const goToUpload = () => {
  router.push({ name: 'upload' })
}

// Lifecycle
onMounted(async () => {
  await fetchDecks()
  decksStore.fetchStats()
})

onUnmounted(() => {
  if (searchDebounceTimer.value) {
    clearTimeout(searchDebounceTimer.value)
  }
})

// Watch for sort changes
watch([sortBy, sortOrder], () => {
  handleSortChange()
})
</script>

<template>
  <div class="decks-page">
    <Toast />
    <ConfirmDialog />

    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-title">
          <h1>
            <i class="pi pi-box mr-2"></i>
            My Decks
          </h1>
          <p class="subtitle">Manage and download your Anki flashcard decks</p>
        </div>
        <div class="header-actions">
          <Button
            label="Create New Deck"
            icon="pi pi-plus"
            severity="primary"
            @click="goToUpload"
          />
        </div>
      </div>
    </div>

    <!-- Statistics Card -->
    <div class="stats-section">
      <DeckStatsCard />
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <!-- Search -->
        <span class="p-input-icon-left search-input">
          <i class="pi pi-search" />
          <InputText
            placeholder="Search decks by name or tags..."
            @input="handleSearch"
            :disabled="decksStore.loading"
          />
        </span>

        <!-- Select Mode Toggle -->
        <Button
          v-if="hasDecks"
          :label="isSelectMode ? 'Cancel' : 'Select'"
          :icon="isSelectMode ? 'pi pi-times' : 'pi pi-check-square'"
          severity="secondary"
          outlined
          @click="toggleSelectMode"
        />

        <!-- Bulk Actions -->
        <div v-if="isSelectMode && hasSelection" class="bulk-actions">
          <span class="selection-count">
            {{ selectedDeckIds.size }} selected
          </span>
          <Button
            label="Delete Selected"
            icon="pi pi-trash"
            severity="danger"
            @click="handleBulkDelete"
          />
        </div>
      </div>

      <div class="toolbar-right">
        <!-- Sort -->
        <Select
          v-model="sortBy"
          :options="sortOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Sort by"
          class="sort-select"
        />

        <!-- Sort Order Toggle -->
        <Button
          :icon="sortOrder === 'asc' ? 'pi pi-sort-amount-up' : 'pi pi-sort-amount-down'"
          severity="secondary"
          outlined
          @click="toggleSortOrder"
          :aria-label="`Sort ${sortOrder === 'asc' ? 'ascending' : 'descending'}`"
        />

        <!-- View Mode Toggle -->
        <Button
          :icon="viewMode === 'grid' ? 'pi pi-list' : 'pi pi-th-large'"
          severity="secondary"
          outlined
          @click="viewMode = viewMode === 'grid' ? 'list' : 'grid'"
          :aria-label="`Switch to ${viewMode === 'grid' ? 'list' : 'grid'} view`"
        />
      </div>
    </div>

    <!-- Select All (when in select mode) -->
    <div v-if="isSelectMode && hasDecks" class="select-all-bar">
      <Checkbox
        v-model="isAllSelected"
        :binary="true"
        inputId="select-all"
        @change="toggleSelectAll"
      />
      <label for="select-all" class="cursor-pointer">
        Select All ({{ decksStore.filteredDecks.length }} decks)
      </label>
    </div>

    <!-- Decks Grid/List -->
    <div class="decks-content">
      <!-- Loading State -->
      <div v-if="decksStore.loading" :class="['decks-grid', `decks-grid--${viewMode}`]">
        <div v-for="i in 6" :key="i" class="skeleton-card">
          <Skeleton height="200px" class="mb-2" />
          <Skeleton height="20px" class="mb-2" />
          <Skeleton height="20px" width="60%" />
        </div>
      </div>

      <!-- Error State -->
      <Message v-else-if="decksStore.error" severity="error" class="w-full">
        <div class="flex items-center justify-between">
          <span>{{ decksStore.error }}</span>
          <Button
            label="Retry"
            icon="pi pi-refresh"
            text
            @click="fetchDecks"
          />
        </div>
      </Message>

      <!-- Empty State -->
      <div v-else-if="!hasDecks" class="empty-state">
        <div class="empty-state-content">
          <i class="pi pi-box empty-icon"></i>
          <h3>No decks yet</h3>
          <p>Create your first deck by uploading a PDF document</p>
          <Button
            label="Upload PDF"
            icon="pi pi-upload"
            severity="primary"
            size="large"
            @click="goToUpload"
          />
        </div>
      </div>

      <!-- Decks Display -->
      <div v-else :class="['decks-grid', `decks-grid--${viewMode}`]">
        <DeckCard
          v-for="deck in decksStore.filteredDecks"
          :key="deck.id"
          :deck="deck"
          :view-mode="viewMode"
          :selected="selectedDeckIds.has(deck.id)"
          @download="handleDownload"
          @delete="handleDelete"
          @view-details="handleViewDetails"
          @select="toggleSelectDeck"
        >
          <template v-if="isSelectMode" #checkbox>
            <Checkbox
              :model-value="selectedDeckIds.has(deck.id)"
              :binary="true"
              @click.stop="toggleSelectDeck(deck.id)"
            />
          </template>
        </DeckCard>
      </div>
    </div>

    <!-- Detail Modal -->
    <DeckDetailModal
      :deck="selectedDeck"
      :visible="detailModalVisible"
      @update:visible="detailModalVisible = $event"
      @download="handleDownload"
      @delete="handleDelete"
      @regenerate="handleRegenerate"
    />
  </div>
</template>

<style scoped>
.decks-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

.header-title h1 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  color: var(--text-color);
}

.subtitle {
  font-size: 1rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.stats-section {
  margin-bottom: 2rem;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.search-input {
  width: 300px;
}

.search-input :deep(.p-inputtext) {
  width: 100%;
}

.bulk-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  background: var(--blue-50);
  border: 1px solid var(--blue-200);
  border-radius: var(--border-radius);
}

.selection-count {
  font-weight: 600;
  color: var(--blue-700);
}

.sort-select {
  min-width: 150px;
}

.select-all-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: var(--surface-50);
  border: 1px solid var(--surface-200);
  border-radius: var(--border-radius);
  margin-bottom: 1.5rem;
}

.select-all-bar label {
  font-weight: 500;
}

.decks-content {
  min-height: 400px;
}

.decks-grid {
  display: grid;
  gap: 1.5rem;
}

.decks-grid--grid {
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}

.decks-grid--list {
  grid-template-columns: 1fr;
}

.skeleton-card {
  padding: 1rem;
  background: var(--surface-card);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 3rem;
}

.empty-state-content {
  text-align: center;
  max-width: 400px;
}

.empty-icon {
  font-size: 5rem;
  color: var(--text-color-secondary);
  opacity: 0.5;
  margin-bottom: 1.5rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.empty-state p {
  font-size: 1rem;
  color: var(--text-color-secondary);
  margin: 0 0 2rem 0;
}

@media (max-width: 768px) {
  .decks-page {
    padding: 1rem;
  }

  .header-content {
    flex-direction: column;
    align-items: stretch;
  }

  .header-title h1 {
    font-size: 1.5rem;
  }

  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left,
  .toolbar-right {
    width: 100%;
    justify-content: space-between;
  }

  .search-input {
    width: 100%;
  }

  .decks-grid--grid {
    grid-template-columns: 1fr;
  }

  .sort-select {
    flex: 1;
  }
}
</style>
