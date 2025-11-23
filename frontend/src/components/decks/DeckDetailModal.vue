<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Deck } from '@/types'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Chip from 'primevue/chip'
import dayjs from 'dayjs'

interface Props {
  deck: Deck | null
  visible: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'download', deckId: string): void
  (e: 'delete', deckId: string): void
  (e: 'regenerate', deck: Deck): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const router = useRouter()

const formattedCreatedAt = computed(() => {
  if (!props.deck) return ''
  return dayjs(props.deck.createdAt).format('MMMM D, YYYY [at] h:mm A')
})

const formattedFileSize = computed(() => {
  if (!props.deck) return ''
  
  const bytes = props.deck.fileSize
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
})

const pageRangeText = computed(() => {
  if (!props.deck || !props.deck.pageRange || props.deck.pageRange.length === 0) {
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

const handleClose = () => {
  emit('update:visible', false)
}

const handleDownload = () => {
  if (props.deck) {
    emit('download', props.deck.id)
  }
}

const handleDelete = () => {
  if (props.deck) {
    emit('delete', props.deck.id)
    handleClose()
  }
}

const handleRegenerate = () => {
  if (props.deck) {
    emit('regenerate', props.deck)
    handleClose()
  }
}

const goToJob = () => {
  if (props.deck?.jobId) {
    router.push({ name: 'jobs', query: { id: props.deck.jobId } })
    handleClose()
  }
}
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    :closable="true"
    :draggable="false"
    class="deck-detail-modal"
    :style="{ width: '90vw', maxWidth: '600px' }"
    @update:visible="handleClose"
  >
    <template #header>
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="pi pi-box mr-2"></i>
          Deck Details
        </h2>
      </div>
    </template>

    <div v-if="deck" class="modal-content">
      <!-- Deck Name -->
      <div class="detail-section">
        <h3 class="detail-section-title">{{ deck.name }}</h3>
      </div>

      <!-- Quick Stats -->
      <div class="stats-row">
        <div class="stat-badge">
          <i class="pi pi-clone"></i>
          <span>{{ deck.cardCount }} cards</span>
        </div>
        <div class="stat-badge">
          <i class="pi pi-file"></i>
          <span>{{ formattedFileSize }}</span>
        </div>
        <div class="stat-badge">
          <i class="pi pi-calendar"></i>
          <span>{{ formattedCreatedAt }}</span>
        </div>
      </div>

      <!-- Metadata -->
      <div class="detail-section">
        <h4 class="section-label">Source Information</h4>
        <div class="metadata-grid">
          <div class="metadata-row">
            <span class="metadata-key">PDF File:</span>
            <span class="metadata-value">{{ deck.fileName }}</span>
          </div>
          <div class="metadata-row">
            <span class="metadata-key">Page Range:</span>
            <span class="metadata-value">{{ pageRangeText }}</span>
          </div>
          <div v-if="deck.jobId" class="metadata-row clickable" @click="goToJob">
            <span class="metadata-key">Job ID:</span>
            <span class="metadata-value link">
              {{ deck.jobId.substring(0, 16) }}...
              <i class="pi pi-external-link ml-1"></i>
            </span>
          </div>
        </div>
      </div>

      <!-- Tags -->
      <div v-if="deck.tags && deck.tags.length > 0" class="detail-section">
        <h4 class="section-label">Tags</h4>
        <div class="tags-container">
          <Chip
            v-for="tag in deck.tags"
            :key="tag"
            :label="tag"
            class="tag-chip"
          />
        </div>
      </div>

      <!-- Download URL Info (if available) -->
      <div v-if="deck.downloadUrl" class="detail-section">
        <div class="info-box">
          <i class="pi pi-info-circle mr-2"></i>
          <span>This deck is available for download</span>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="modal-actions">
        <Button
          label="Download"
          icon="pi pi-download"
          severity="primary"
          @click="handleDownload"
        />
        <Button
          label="Regenerate"
          icon="pi pi-refresh"
          severity="secondary"
          outlined
          @click="handleRegenerate"
          :disabled="!deck"
        />
        <Button
          label="Delete"
          icon="pi pi-trash"
          severity="danger"
          outlined
          @click="handleDelete"
        />
      </div>
    </template>
  </Dialog>
</template>

<style scoped>
.deck-detail-modal :deep(.p-dialog-header) {
  padding: 1.5rem;
}

.deck-detail-modal :deep(.p-dialog-content) {
  padding: 1.5rem;
}

.deck-detail-modal :deep(.p-dialog-footer) {
  padding: 1.5rem;
  border-top: 1px solid var(--surface-border);
}

.modal-header {
  width: 100%;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  color: var(--text-color);
}

.modal-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-section-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-color);
  line-height: 1.4;
}

.section-label {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-color-secondary);
  margin: 0;
  letter-spacing: 0.05em;
}

.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--surface-100);
  border: 1px solid var(--surface-200);
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.stat-badge i {
  color: var(--primary-color);
}

.metadata-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.metadata-row {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 1rem;
  padding: 0.75rem;
  background: var(--surface-50);
  border-radius: var(--border-radius);
}

.metadata-row.clickable {
  cursor: pointer;
  transition: background 0.2s;
}

.metadata-row.clickable:hover {
  background: var(--surface-100);
}

.metadata-key {
  font-weight: 500;
  color: var(--text-color-secondary);
  flex-shrink: 0;
}

.metadata-value {
  font-weight: 600;
  color: var(--text-color);
  text-align: right;
  word-break: break-word;
}

.metadata-value.link {
  color: var(--primary-color);
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-chip {
  background: var(--blue-100);
  color: var(--blue-700);
  font-weight: 500;
}

.info-box {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: var(--blue-50);
  border: 1px solid var(--blue-200);
  border-radius: var(--border-radius);
  color: var(--blue-700);
  font-size: 0.875rem;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.modal-actions :deep(.p-button) {
  min-width: 120px;
}

@media (max-width: 640px) {
  .modal-actions {
    flex-direction: column;
  }

  .modal-actions :deep(.p-button) {
    width: 100%;
  }

  .stats-row {
    flex-direction: column;
  }

  .metadata-row {
    flex-direction: column;
    align-items: start;
  }

  .metadata-value {
    text-align: left;
  }
}
</style>
