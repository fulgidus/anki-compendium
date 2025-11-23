<script setup lang="ts">
import { ref, computed } from 'vue'
import Card from 'primevue/card'
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import { usePdfUpload } from '@/composables/usePdfUpload'

const emit = defineEmits<{
  fileSelected: [file: File]
}>()

const { 
  pdfFile, 
  isUploading, 
  uploadProgress, 
  hasFile, 
  selectFile, 
  removeFile,
  formatFileSize 
} = usePdfUpload()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

const progressPercent = computed(() => uploadProgress.value.percent)

/**
 * Handle file input change
 */
const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    const success = await selectFile(file)
    if (success) {
      emit('fileSelected', file)
    }
  }
}

/**
 * Handle drag over
 */
const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = true
}

/**
 * Handle drag leave
 */
const handleDragLeave = () => {
  isDragging.value = false
}

/**
 * Handle file drop
 */
const handleDrop = async (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = false

  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    const file = event.dataTransfer.files[0]
    const success = await selectFile(file)
    if (success) {
      emit('fileSelected', file)
    }
  }
}

/**
 * Open file browser
 */
const openFileBrowser = () => {
  fileInput.value?.click()
}

/**
 * Handle remove file
 */
const handleRemove = () => {
  removeFile()
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<template>
  <Card class="pdf-upload-zone">
    <!-- Upload Area (shown when no file) -->
    <template v-if="!hasFile" #content>
      <div
        class="upload-drop-zone"
        :class="{ 'is-dragging': isDragging }"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
        @click="openFileBrowser"
      >
        <i class="pi pi-cloud-upload upload-icon"></i>
        <h3 class="upload-title">Drop your PDF here</h3>
        <p class="upload-subtitle">or click to browse</p>
        <p class="upload-hint">Maximum file size: 50MB</p>

        <!-- Hidden file input -->
        <input
          ref="fileInput"
          type="file"
          accept="application/pdf,.pdf"
          style="display: none"
          @change="handleFileChange"
        />
      </div>
    </template>

    <!-- File Info (shown when file selected) -->
    <template v-else #content>
      <div class="file-info">
        <div class="file-icon-container">
          <i class="pi pi-file-pdf file-icon"></i>
        </div>
        
        <div class="file-details">
          <h3 class="file-name">{{ pdfFile?.name }}</h3>
          <p class="file-size">{{ formatFileSize(pdfFile?.size || 0) }}</p>
          <p v-if="pdfFile?.pageCount" class="file-pages">
            {{ pdfFile.pageCount }} page{{ pdfFile.pageCount !== 1 ? 's' : '' }}
          </p>
        </div>

        <div class="file-actions">
          <Button
            icon="pi pi-times"
            severity="danger"
            text
            rounded
            @click="handleRemove"
            :disabled="isUploading"
            v-tooltip.top="'Remove file'"
          />
        </div>
      </div>

      <!-- Upload Progress -->
      <div v-if="isUploading" class="upload-progress">
        <ProgressBar :value="progressPercent" />
        <p class="progress-text">Uploading... {{ progressPercent }}%</p>
      </div>
    </template>
  </Card>
</template>

<style scoped>
.pdf-upload-zone {
  margin-bottom: 1.5rem;
}

.upload-drop-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  border: 2px dashed var(--surface-border);
  border-radius: var(--border-radius);
  background: var(--surface-ground);
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 250px;
}

.upload-drop-zone:hover {
  border-color: var(--primary-color);
  background: var(--surface-hover);
}

.upload-drop-zone.is-dragging {
  border-color: var(--primary-color);
  background: var(--primary-50);
  transform: scale(1.02);
}

.upload-icon {
  font-size: 4rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.upload-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.upload-subtitle {
  font-size: 1rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.5rem;
}

.upload-hint {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  background: var(--surface-50);
  border-radius: var(--border-radius);
}

.file-icon-container {
  flex-shrink: 0;
}

.file-icon {
  font-size: 3rem;
  color: var(--red-500);
}

.file-details {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
  word-break: break-word;
}

.file-size {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.25rem;
}

.file-pages {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.file-actions {
  flex-shrink: 0;
}

.upload-progress {
  margin-top: 1rem;
}

.progress-text {
  text-align: center;
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

/* Mobile responsive */
@media (max-width: 768px) {
  .upload-drop-zone {
    padding: 2rem 1rem;
    min-height: 200px;
  }

  .upload-icon {
    font-size: 3rem;
  }

  .upload-title {
    font-size: 1.25rem;
  }

  .file-info {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }

  .file-icon {
    font-size: 2.5rem;
  }
}
</style>
