<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import Checkbox from 'primevue/checkbox'
import Button from 'primevue/button'
import Message from 'primevue/message'
import PdfUploadZone from '@/components/pdf/PdfUploadZone.vue'
import PdfViewer from '@/components/pdf/PdfViewer.vue'
import { usePdfUpload } from '@/composables/usePdfUpload'
import type { JobSettings } from '@/types'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const toast = useToast()

const { 
  pdfFile, 
  isUploading, 
  hasFile,
  updatePageCount,
  uploadFile,
  reset 
} = usePdfUpload()

// Form state
const deckName = ref('')
const maxCards = ref<number>()
const difficulty = ref<'easy' | 'medium' | 'hard'>('medium')
const includeImages = ref(true)
const selectedPages = ref<number[]>([])

// Validation
const isFormValid = computed(() => {
  return (
    hasFile.value &&
    deckName.value.trim().length > 0 &&
    selectedPages.value.length > 0 &&
    !isUploading.value
  )
})

const difficultyOptions = [
  { label: 'Easy', value: 'easy' },
  { label: 'Medium', value: 'medium' },
  { label: 'Hard', value: 'hard' }
]

/**
 * Handle file selected
 */
const handleFileSelected = (file: File) => {
  // File is already loaded in the composable
  console.log('File selected:', file.name)
}

/**
 * Handle pages selected in viewer
 */
const handlePagesSelected = (pages: number[]) => {
  selectedPages.value = pages
}

/**
 * Handle page count loaded from PDF
 */
const handlePageCountLoaded = (count: number) => {
  updatePageCount(count)
}

/**
 * Handle form submission
 */
const handleSubmit = async () => {
  if (!isFormValid.value || !pdfFile.value) {
    return
  }

  const settings: JobSettings = {
    deckName: deckName.value.trim(),
    maxCards: maxCards.value,
    difficulty: difficulty.value,
    includeImages: includeImages.value,
    pageRange: selectedPages.value
  }

  const response = await uploadFile({
    file: pdfFile.value.file,
    settings
  })

  if (response) {
    // Success - redirect to jobs page
    toast.add({
      severity: 'success',
      summary: 'Upload Successful',
      detail: 'Redirecting to jobs page...',
      life: 2000
    })

    setTimeout(() => {
      router.push({ name: 'jobs' })
    }, 2000)
  }
}

/**
 * Reset form
 */
const handleReset = () => {
  reset()
  deckName.value = ''
  maxCards.value = undefined
  difficulty.value = 'medium'
  includeImages.value = true
  selectedPages.value = []
}
</script>

<template>
  <div class="upload-page">
    <div class="page-header">
      <h1 class="page-title">Upload PDF</h1>
      <p class="page-subtitle">
        Upload your PDF document and generate Anki flashcards automatically
      </p>
    </div>

    <div class="upload-container">
      <!-- Step 1: Upload PDF -->
      <div class="upload-step">
        <h2 class="step-title">
          <span class="step-number">1</span>
          Select PDF File
        </h2>
        <PdfUploadZone @file-selected="handleFileSelected" />
      </div>

      <!-- Step 2: Preview & Select Pages (shown after file upload) -->
      <div v-if="hasFile && pdfFile" class="upload-step">
        <h2 class="step-title">
          <span class="step-number">2</span>
          Preview & Select Pages
        </h2>
        <PdfViewer
          :pdf-file="pdfFile"
          @pages-selected="handlePagesSelected"
          @page-count-loaded="handlePageCountLoaded"
        />
      </div>

      <!-- Step 3: Deck Settings (shown after file upload) -->
      <div v-if="hasFile" class="upload-step">
        <h2 class="step-title">
          <span class="step-number">3</span>
          Deck Settings
        </h2>
        
        <Card class="settings-card">
          <template #content>
            <div class="settings-form">
              <!-- Deck Name -->
              <div class="form-field">
                <label for="deck-name" class="form-label required">
                  Deck Name
                </label>
                <InputText
                  id="deck-name"
                  v-model="deckName"
                  placeholder="e.g., Biology Chapter 3"
                  :disabled="isUploading"
                  class="w-full"
                />
                <small class="form-hint">
                  Choose a descriptive name for your flashcard deck
                </small>
              </div>

              <!-- Maximum Cards -->
              <div class="form-field">
                <label for="max-cards" class="form-label">
                  Maximum Cards (Optional)
                </label>
                <InputNumber
                  id="max-cards"
                  v-model="maxCards"
                  :min="1"
                  :max="1000"
                  placeholder="Leave empty for auto"
                  :disabled="isUploading"
                  class="w-full"
                />
                <small class="form-hint">
                  Limit the number of flashcards generated
                </small>
              </div>

              <!-- Difficulty -->
              <div class="form-field">
                <label for="difficulty" class="form-label">
                  Difficulty Level
                </label>
                <Select
                  id="difficulty"
                  v-model="difficulty"
                  :options="difficultyOptions"
                  optionLabel="label"
                  optionValue="value"
                  :disabled="isUploading"
                  class="w-full"
                />
                <small class="form-hint">
                  Control the complexity of generated questions
                </small>
              </div>

              <!-- Include Images -->
              <div class="form-field">
                <div class="checkbox-wrapper">
                  <Checkbox
                    id="include-images"
                    v-model="includeImages"
                    binary
                    :disabled="isUploading"
                  />
                  <label for="include-images" class="checkbox-label">
                    Include images from PDF
                  </label>
                </div>
                <small class="form-hint">
                  Extract and embed images in flashcards when relevant
                </small>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Step 4: Submit (shown after file upload) -->
      <div v-if="hasFile" class="upload-step">
        <Card class="submit-card">
          <template #content>
            <div class="submit-section">
              <!-- Validation Message -->
              <Message
                v-if="!isFormValid && deckName.length === 0"
                severity="warn"
                :closable="false"
              >
                Please enter a deck name to continue
              </Message>

              <Message
                v-else-if="!isFormValid && selectedPages.length === 0"
                severity="warn"
                :closable="false"
              >
                Please select at least one page to generate flashcards
              </Message>

              <!-- Submit Summary -->
              <div v-else class="submit-summary">
                <h3>Ready to Generate</h3>
                <ul class="summary-list">
                  <li>
                    <i class="pi pi-file-pdf"></i>
                    <span>{{ pdfFile?.name }}</span>
                  </li>
                  <li>
                    <i class="pi pi-book"></i>
                    <span>Deck: {{ deckName }}</span>
                  </li>
                  <li>
                    <i class="pi pi-file"></i>
                    <span>{{ selectedPages.length }} pages selected</span>
                  </li>
                  <li v-if="maxCards">
                    <i class="pi pi-list"></i>
                    <span>Max {{ maxCards }} cards</span>
                  </li>
                  <li>
                    <i class="pi pi-chart-bar"></i>
                    <span>Difficulty: {{ difficulty }}</span>
                  </li>
                </ul>
              </div>

              <!-- Action Buttons -->
              <div class="submit-actions">
                <Button
                  label="Reset"
                  icon="pi pi-refresh"
                  severity="secondary"
                  outlined
                  @click="handleReset"
                  :disabled="isUploading"
                />
                <Button
                  label="Generate Flashcards"
                  icon="pi pi-send"
                  :loading="isUploading"
                  :disabled="!isFormValid"
                  @click="handleSubmit"
                />
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Instructions (shown when no file) -->
      <div v-if="!hasFile" class="instructions">
        <Card>
          <template #header>
            <div class="instructions-header">
              <i class="pi pi-info-circle"></i>
              <h3>How It Works</h3>
            </div>
          </template>
          <template #content>
            <ol class="instructions-list">
              <li>
                <strong>Upload your PDF:</strong> Drag and drop or click to select a PDF file (max 50MB)
              </li>
              <li>
                <strong>Select pages:</strong> Choose which pages you want to convert into flashcards
              </li>
              <li>
                <strong>Configure settings:</strong> Name your deck and customize generation options
              </li>
              <li>
                <strong>Generate:</strong> Our AI will extract key concepts and create flashcards
              </li>
              <li>
                <strong>Download:</strong> Get your Anki deck ready to import and start learning!
              </li>
            </ol>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.125rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.upload-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.upload-step {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.step-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 1rem;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  font-size: 1rem;
  font-weight: 700;
}

.settings-card {
  background: var(--surface-card);
}

.settings-form {
  display: grid;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 600;
  color: var(--text-color);
}

.form-label.required::after {
  content: ' *';
  color: var(--red-500);
}

.form-hint {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-label {
  cursor: pointer;
  font-weight: 500;
}

.submit-card {
  background: var(--surface-card);
}

.submit-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.submit-summary {
  padding: 1.5rem;
  background: var(--surface-50);
  border-radius: var(--border-radius);
}

.submit-summary h3 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.summary-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.summary-list li {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9375rem;
}

.summary-list i {
  color: var(--primary-color);
  font-size: 1rem;
}

.submit-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.instructions {
  margin-top: 2rem;
}

.instructions-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem 1.5rem 0;
}

.instructions-header i {
  color: var(--primary-color);
  font-size: 1.5rem;
}

.instructions-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.instructions-list {
  padding-left: 1.5rem;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.instructions-list li {
  line-height: 1.6;
}

.instructions-list strong {
  color: var(--primary-color);
  font-weight: 600;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .upload-page {
    padding: 1rem;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .page-subtitle {
    font-size: 1rem;
  }

  .step-title {
    font-size: 1.25rem;
  }

  .submit-actions {
    flex-direction: column;
  }

  .submit-actions button {
    width: 100%;
  }
}
</style>
