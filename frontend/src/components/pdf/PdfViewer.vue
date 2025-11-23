<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import VuePdfEmbed from 'vue-pdf-embed'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputNumber from 'primevue/inputnumber'
import Checkbox from 'primevue/checkbox'
import Skeleton from 'primevue/skeleton'
import Message from 'primevue/message'
import type { PdfFile } from '@/types'

interface Props {
  pdfFile: PdfFile
}

interface Emits {
  pagesSelected: [pages: number[]]
  pageCountLoaded: [count: number]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const pdfRef = ref<InstanceType<typeof VuePdfEmbed> | null>(null)
const pageCount = ref(0)
const currentPage = ref(1)
const scale = ref(1.0)
const isLoading = ref(true)
const loadError = ref<string | null>(null)
const selectedPages = ref<Set<number>>(new Set())
const selectAll = ref(false)

const canGoPrevious = computed(() => currentPage.value > 1)
const canGoNext = computed(() => currentPage.value < pageCount.value)
const selectedPagesList = computed(() => Array.from(selectedPages.value).sort((a, b) => a - b))

/**
 * Handle PDF document load
 */
const handleDocumentLoad = ({ numPages }: { numPages: number }) => {
  pageCount.value = numPages
  isLoading.value = false
  loadError.value = null
  
  // Select all pages by default
  selectAllPages()
  
  // Emit page count to parent
  emit('pageCountLoaded', numPages)
}

/**
 * Handle PDF load error
 */
const handleLoadError = (error: any) => {
  isLoading.value = false
  loadError.value = 'Failed to load PDF. The file may be corrupted.'
  console.error('PDF load error:', error)
}

/**
 * Navigate to previous page
 */
const previousPage = () => {
  if (canGoPrevious.value) {
    currentPage.value--
  }
}

/**
 * Navigate to next page
 */
const nextPage = () => {
  if (canGoNext.value) {
    currentPage.value++
  }
}

/**
 * Zoom in
 */
const zoomIn = () => {
  if (scale.value < 2.0) {
    scale.value += 0.25
  }
}

/**
 * Zoom out
 */
const zoomOut = () => {
  if (scale.value > 0.5) {
    scale.value -= 0.25
  }
}

/**
 * Reset zoom
 */
const zoomReset = () => {
  scale.value = 1.0
}

/**
 * Toggle page selection
 */
const togglePage = (page: number) => {
  if (selectedPages.value.has(page)) {
    selectedPages.value.delete(page)
  } else {
    selectedPages.value.add(page)
  }
  
  // Update select all checkbox state
  selectAll.value = selectedPages.value.size === pageCount.value
  
  // Emit selected pages
  emit('pagesSelected', selectedPagesList.value)
}

/**
 * Toggle select all pages
 */
const toggleSelectAll = () => {
  if (selectAll.value) {
    selectAllPages()
  } else {
    deselectAllPages()
  }
}

/**
 * Select all pages
 */
const selectAllPages = () => {
  selectedPages.value.clear()
  for (let i = 1; i <= pageCount.value; i++) {
    selectedPages.value.add(i)
  }
  selectAll.value = true
  emit('pagesSelected', selectedPagesList.value)
}

/**
 * Deselect all pages
 */
const deselectAllPages = () => {
  selectedPages.value.clear()
  selectAll.value = false
  emit('pagesSelected', selectedPagesList.value)
}

/**
 * Handle keyboard navigation
 */
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'ArrowLeft') {
    previousPage()
  } else if (event.key === 'ArrowRight') {
    nextPage()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<template>
  <Card class="pdf-viewer">
    <template #header>
      <div class="pdf-header">
        <h3 class="pdf-title">PDF Preview</h3>
        <div class="pdf-controls">
          <!-- Zoom Controls -->
          <div class="zoom-controls">
            <Button
              icon="pi pi-minus"
              text
              rounded
              @click="zoomOut"
              :disabled="scale <= 0.5"
              v-tooltip.top="'Zoom out'"
            />
            <span class="zoom-level">{{ Math.round(scale * 100) }}%</span>
            <Button
              icon="pi pi-plus"
              text
              rounded
              @click="zoomIn"
              :disabled="scale >= 2.0"
              v-tooltip.top="'Zoom in'"
            />
            <Button
              icon="pi pi-refresh"
              text
              rounded
              @click="zoomReset"
              v-tooltip.top="'Reset zoom'"
            />
          </div>

          <!-- Page Navigation -->
          <div class="page-navigation">
            <Button
              icon="pi pi-chevron-left"
              text
              rounded
              @click="previousPage"
              :disabled="!canGoPrevious"
              v-tooltip.top="'Previous page'"
            />
            <div class="page-info">
              <InputNumber
                v-model="currentPage"
                :min="1"
                :max="pageCount"
                :disabled="isLoading"
                showButtons
                buttonLayout="horizontal"
                class="page-input"
              />
              <span class="page-total">of {{ pageCount }}</span>
            </div>
            <Button
              icon="pi pi-chevron-right"
              text
              rounded
              @click="nextPage"
              :disabled="!canGoNext"
              v-tooltip.top="'Next page'"
            />
          </div>
        </div>
      </div>
    </template>

    <template #content>
      <!-- Loading State -->
      <div v-if="isLoading" class="pdf-loading">
        <Skeleton height="600px" />
        <p class="loading-text">Loading PDF...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="loadError" class="pdf-error">
        <Message severity="error" :closable="false">
          {{ loadError }}
        </Message>
      </div>

      <!-- PDF Viewer -->
      <div v-else class="pdf-container">
        <VuePdfEmbed
          ref="pdfRef"
          :source="props.pdfFile.url"
          :page="currentPage"
          :scale="scale"
          @loaded="handleDocumentLoad"
          @loading-failed="handleLoadError"
          class="pdf-canvas"
        />
      </div>

      <!-- Page Selection -->
      <div v-if="!isLoading && !loadError" class="page-selection">
        <div class="selection-header">
          <h4>Select Pages for Flashcard Generation</h4>
          <div class="selection-actions">
            <Checkbox
              v-model="selectAll"
              binary
              @change="toggleSelectAll"
              inputId="select-all"
            />
            <label for="select-all" class="select-all-label">
              Select All ({{ selectedPages.size }} / {{ pageCount }})
            </label>
          </div>
        </div>

        <!-- Page Grid -->
        <div class="page-grid">
          <div
            v-for="page in pageCount"
            :key="page"
            class="page-item"
            :class="{ 'is-selected': selectedPages.has(page), 'is-current': currentPage === page }"
            @click="togglePage(page)"
          >
            <Checkbox
              :modelValue="selectedPages.has(page)"
              binary
              @click.stop="togglePage(page)"
              :inputId="`page-${page}`"
            />
            <label :for="`page-${page}`" class="page-label">
              Page {{ page }}
            </label>
          </div>
        </div>

        <!-- Selection Summary -->
        <div v-if="selectedPages.size > 0" class="selection-summary">
          <i class="pi pi-info-circle"></i>
          <span>
            {{ selectedPages.size }} page{{ selectedPages.size !== 1 ? 's' : '' }} selected
            <template v-if="selectedPagesList.length <= 10">
              ({{ selectedPagesList.join(', ') }})
            </template>
          </span>
        </div>
      </div>
    </template>
  </Card>
</template>

<style scoped>
.pdf-viewer {
  margin-bottom: 1.5rem;
}

.pdf-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--surface-border);
}

.pdf-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
}

.pdf-controls {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.zoom-level {
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 50px;
  text-align: center;
}

.page-navigation {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-input {
  width: 80px;
}

.page-total {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.pdf-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}

.loading-text {
  color: var(--text-color-secondary);
}

.pdf-error {
  padding: 2rem;
}

.pdf-container {
  display: flex;
  justify-content: center;
  padding: 2rem;
  background: var(--surface-ground);
  overflow: auto;
  max-height: 600px;
}

.pdf-canvas {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-selection {
  padding: 1.5rem;
  border-top: 1px solid var(--surface-border);
  background: var(--surface-50);
}

.selection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.selection-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.selection-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.select-all-label {
  cursor: pointer;
  font-weight: 500;
}

.page-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.page-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border: 2px solid var(--surface-border);
  border-radius: var(--border-radius);
  background: var(--surface-card);
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-item:hover {
  border-color: var(--primary-color);
  background: var(--surface-hover);
}

.page-item.is-selected {
  border-color: var(--primary-color);
  background: var(--primary-50);
}

.page-item.is-current {
  box-shadow: 0 0 0 2px var(--primary-color);
}

.page-label {
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
}

.selection-summary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--primary-50);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  color: var(--primary-700);
}

.selection-summary i {
  color: var(--primary-600);
}

/* Mobile responsive */
@media (max-width: 768px) {
  .pdf-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .pdf-controls {
    flex-direction: column;
    gap: 1rem;
  }

  .page-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }

  .selection-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}
</style>
