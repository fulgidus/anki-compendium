<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Deck } from '@/types'
import Card from 'primevue/card'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

interface Props {
  deck: Deck
  viewMode?: 'grid' | 'list'
  selected?: boolean
}

interface Emits {
  (e: 'download', deckId: string): void
  (e: 'delete', deckId: string): void
  (e: 'view-details', deckId: string): void
  (e: 'select', deckId: string): void
}

const props = withDefaults(defineProps<Props>(), {
  viewMode: 'grid',
  selected: false
})

const emit = defineEmits<Emits>()

const router = useRouter()

const relativeCreatedAt = computed(() => {
  return dayjs(props.deck.createdAt).fromNow()
})

const formattedFileSize = computed(() => {
  const bytes = props.deck.fileSize
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
})

const pageRangeText = computed(() => {
  if (!props.deck.pageRange || props.deck.pageRange.length === 0) {
    return 'All pages'
  }
  
  if (props.deck.pageRange.length === 1) {
    return `Page ${props.deck.pageRange[0]}`
  }
  
  if (props.deck.pageRange.length === 2) {
    return `Pages ${props.deck.pageRange[0]}-${props.deck.pageRange[1]}`
  }
  
  return `${props.deck.pageRange.length} pages`
})

const handleDownload = () => {
  emit('download', props.deck.id)
}

const handleDelete = () => {
  emit('delete', props.deck.id)
}

const handleViewDetails = () => {
  emit('view-details', props.deck.id)
}

const handleSelect = () => {
  emit('select', props.deck.id)
}

const goToJob = () => {
  if (props.deck.jobId) {
    router.push({ name: 'jobs', query: { id: props.deck.jobId } })
  }
}
</script>

<template>
  <Card 
    :class="[
      'deck-card',
      `deck-card--${viewMode}`,
      { 'deck-card--selected': selected }
    ]"
  >
    <template #header v-if="viewMode === 'grid'">
      <div class="deck-card-header">
        <div class="deck-icon">
          <i class="pi pi-box text-4xl"></i>
        </div>
        <div
          v-if="$slots.checkbox"
          class="select-checkbox"
          @click.stop="handleSelect"
        >
          <slot name="checkbox"></slot>
        </div>
      </div>
    </template>

    <template #title>
      <div class="flex items-center justify-between gap-2">
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <div
            v-if="viewMode === 'list' && $slots.checkbox"
            class="select-checkbox"
            @click.stop="handleSelect"
          >
            <slot name="checkbox"></slot>
          </div>
          <h3 class="deck-title" :title="deck.name">
            {{ deck.name }}
          </h3>
        </div>
        <Chip 
          :label="`${deck.cardCount} cards`"
          class="card-count-chip"
        />
      </div>
    </template>

    <template #subtitle>
      <div class="deck-subtitle">
        <div class="subtitle-item">
          <i class="pi pi-file-pdf"></i>
          <span>{{ deck.fileName }}</span>
        </div>
        <div class="subtitle-item">
          <i class="pi pi-calendar"></i>
          <span>{{ relativeCreatedAt }}</span>
        </div>
        <div class="subtitle-item">
          <i class="pi pi-file"></i>
          <span>{{ pageRangeText }}</span>
        </div>
      </div>
    </template>

    <template #content>
      <!-- Tags -->
      <div v-if="deck.tags && deck.tags.length > 0" class="deck-tags">
        <Chip
          v-for="tag in deck.tags.slice(0, 3)"
          :key="tag"
          :label="tag"
          class="tag-chip"
        />
        <span v-if="deck.tags.length > 3" class="more-tags">
          +{{ deck.tags.length - 3 }} more
        </span>
      </div>

      <!-- Metadata -->
      <div class="deck-metadata">
        <div class="metadata-item">
          <span class="metadata-label">File Size:</span>
          <span class="metadata-value">{{ formattedFileSize }}</span>
        </div>
        <div v-if="deck.jobId" class="metadata-item link" @click="goToJob">
          <span class="metadata-label">Job:</span>
          <span class="metadata-value">
            {{ deck.jobId.substring(0, 8) }}...
            <i class="pi pi-external-link ml-1"></i>
          </span>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="deck-actions">
        <Button
          label="Download"
          icon="pi pi-download"
          severity="primary"
          @click="handleDownload"
          :aria-label="`Download ${deck.name}`"
        />
        <Button
          label="Details"
          icon="pi pi-info-circle"
          severity="secondary"
          outlined
          @click="handleViewDetails"
          :aria-label="`View details of ${deck.name}`"
        />
        <Button
          icon="pi pi-trash"
          severity="danger"
          outlined
          @click="handleDelete"
          :aria-label="`Delete ${deck.name}`"
        />
      </div>
    </template>
  </Card>
</template>

<style scoped>
.deck-card {
  height: 100%;
  transition: all 0.2s;
  position: relative;
}

.deck-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.deck-card--selected {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color);
}

.deck-card--list {
  margin-bottom: 0.5rem;
}

.deck-card--list .deck-actions {
  display: flex;
  gap: 0.5rem;
}

.deck-card-header {
  position: relative;
  background: linear-gradient(135deg, var(--primary-100) 0%, var(--primary-200) 100%);
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.deck-icon {
  color: var(--primary-600);
  opacity: 0.8;
}

.select-checkbox {
  cursor: pointer;
  z-index: 10;
}

.deck-card--grid .select-checkbox {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.deck-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-count-chip {
  background: var(--green-100);
  color: var(--green-700);
  font-weight: 600;
  flex-shrink: 0;
}

.deck-subtitle {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  margin-top: 0.5rem;
}

.subtitle-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.subtitle-item i {
  font-size: 0.75rem;
  flex-shrink: 0;
}

.subtitle-item span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.deck-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
  align-items: center;
}

.tag-chip {
  background: var(--blue-100);
  color: var(--blue-700);
  font-size: 0.75rem;
}

.more-tags {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.deck-metadata {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--surface-50);
  border-radius: var(--border-radius);
}

.metadata-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.metadata-item.link {
  cursor: pointer;
  color: var(--primary-color);
}

.metadata-item.link:hover {
  text-decoration: underline;
}

.metadata-label {
  color: var(--text-color-secondary);
  font-weight: 500;
}

.metadata-value {
  color: var(--text-color);
  font-weight: 600;
}

.deck-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.deck-actions :deep(.p-button) {
  flex: 1;
  min-width: fit-content;
}

@media (max-width: 640px) {
  .deck-actions {
    flex-direction: column;
  }

  .deck-actions :deep(.p-button) {
    width: 100%;
  }
}
</style>
