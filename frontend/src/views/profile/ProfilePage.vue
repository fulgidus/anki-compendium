<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useUserStore } from '@/stores/user'
import { useAuthStore } from '@/stores/auth'
import { useDecksStore } from '@/stores/decks'
import PasswordChangeModal from '@/components/profile/PasswordChangeModal.vue'
import dayjs from 'dayjs'
import type { UserPreferences } from '@/types'

const router = useRouter()
const toast = useToast()
const confirm = useConfirm()
const userStore = useUserStore()
const authStore = useAuthStore()
const decksStore = useDecksStore()

const showPasswordModal = ref(false)
const editMode = ref(false)
const savingProfile = ref(false)
const savingPreferences = ref(false)

// Form data
const profileForm = ref({
  fullName: '',
  email: ''
})

const preferencesForm = ref<UserPreferences>({
  defaultMaxCards: 50,
  defaultDifficulty: 'medium',
  includeImages: true,
  emailOnCompletion: true,
  emailOnFailure: true
})

// Computed properties
const memberSince = computed(() => {
  if (!userStore.profile?.createdAt) return ''
  return dayjs(userStore.profile.createdAt).format('MMMM D, YYYY')
})

const lastLogin = computed(() => {
  if (!userStore.profile?.lastLoginAt) return ''
  return dayjs(userStore.profile.lastLoginAt).format('MMMM D, YYYY [at] h:mm A')
})

const getInitials = computed(() => {
  const name = userStore.fullName || authStore.user?.username || ''
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

// Load data on mount
onMounted(async () => {
  await Promise.all([
    userStore.fetchProfile(),
    userStore.fetchStats(),
    decksStore.fetchStats()
  ])

  // Initialize forms with data
  if (userStore.profile) {
    profileForm.value.fullName = userStore.profile.fullName
    profileForm.value.email = userStore.profile.email
    preferencesForm.value = { ...userStore.profile.preferences }
  }
})

// Handlers
const handleEditProfile = () => {
  editMode.value = true
}

const handleCancelEdit = () => {
  editMode.value = false
  // Reset form to original values
  if (userStore.profile) {
    profileForm.value.fullName = userStore.profile.fullName
    profileForm.value.email = userStore.profile.email
  }
}

const handleSaveProfile = async () => {
  savingProfile.value = true

  try {
    const success = await userStore.updateProfile({
      fullName: profileForm.value.fullName
    })

    if (success) {
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Profile updated successfully',
        life: 3000
      })
      editMode.value = false
    } else {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: userStore.error || 'Failed to update profile',
        life: 5000
      })
    }
  } finally {
    savingProfile.value = false
  }
}

const handleSavePreferences = async () => {
  savingPreferences.value = true

  try {
    const success = await userStore.updatePreferences(preferencesForm.value)

    if (success) {
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Preferences updated successfully',
        life: 3000
      })
    } else {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: userStore.error || 'Failed to update preferences',
        life: 5000
      })
    }
  } finally {
    savingPreferences.value = false
  }
}

const handleDeleteAllDecks = () => {
  confirm.require({
    message: 'Are you sure you want to delete all your decks? This action cannot be undone.',
    header: 'Delete All Decks',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: async () => {
      const deckIds = decksStore.decks.map(d => d.id)
      const success = await decksStore.deleteDecks(deckIds)
      
      if (success) {
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'All decks deleted successfully',
          life: 3000
        })
      } else {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete decks',
          life: 5000
        })
      }
    }
  })
}

const handleDeleteAccount = () => {
  confirm.require({
    message: 'Are you absolutely sure? This will permanently delete your account, all decks, and jobs. This action CANNOT be undone.',
    header: 'Delete Account - FINAL WARNING',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: () => {
      // Double confirmation
      confirm.require({
        message: 'Type "DELETE" to confirm account deletion.',
        header: 'Confirm Account Deletion',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: async () => {
          const success = await userStore.deleteAccount()
          
          if (success) {
            toast.add({
              severity: 'info',
              summary: 'Account Deleted',
              detail: 'Your account has been permanently deleted',
              life: 3000
            })
            
            // Logout and redirect
            await authStore.logout()
            router.push({ name: 'home' })
          } else {
            toast.add({
              severity: 'error',
              summary: 'Error',
              detail: userStore.error || 'Failed to delete account',
              life: 5000
            })
          }
        }
      })
    }
  })
}
</script>

<template>
  <div class="profile-page p-4 md:p-6 lg:p-8">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Profile & Settings</h1>
      <p class="text-gray-600">Manage your account information and preferences</p>
    </div>

    <!-- Profile Header Card -->
    <Card class="mb-6">
      <template #content>
        <div class="flex items-center gap-4 p-4">
          <!-- Avatar -->
          <div class="flex-shrink-0">
            <div class="w-20 h-20 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-2xl font-bold">
              {{ getInitials }}
            </div>
          </div>

          <!-- User Info -->
          <div class="flex-1 min-w-0">
            <h2 class="text-2xl font-bold text-gray-900 mb-1">{{ userStore.fullName || 'User' }}</h2>
            <p class="text-gray-600 mb-1">{{ userStore.email }}</p>
            <p class="text-sm text-gray-500">Member since {{ memberSince }}</p>
          </div>

          <!-- Edit Button -->
          <div>
            <Button
              v-if="!editMode"
              label="Edit Profile"
              icon="pi pi-pencil"
              @click="handleEditProfile"
            />
          </div>
        </div>
      </template>
    </Card>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column - Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Account Information -->
        <Card>
          <template #header>
            <div class="p-4 border-b">
              <h3 class="text-lg font-semibold">Account Information</h3>
            </div>
          </template>

          <template #content>
            <div class="space-y-4">
              <!-- Full Name -->
              <div class="flex flex-col gap-2">
                <label for="fullName" class="font-semibold">Full Name</label>
                <InputText
                  id="fullName"
                  v-model="profileForm.fullName"
                  :disabled="!editMode"
                  placeholder="Enter your full name"
                />
              </div>

              <!-- Email (Read-only) -->
              <div class="flex flex-col gap-2">
                <label for="email" class="font-semibold">Email</label>
                <InputText
                  id="email"
                  v-model="profileForm.email"
                  disabled
                  placeholder="Your email address"
                />
                <small class="text-gray-500">Email cannot be changed</small>
              </div>

              <!-- Password -->
              <div class="flex flex-col gap-2">
                <label class="font-semibold">Password</label>
                <Button
                  label="Change Password"
                  icon="pi pi-lock"
                  severity="secondary"
                  @click="showPasswordModal = true"
                />
              </div>

              <!-- Save/Cancel Buttons -->
              <div v-if="editMode" class="flex gap-2 pt-4">
                <Button
                  label="Save Changes"
                  icon="pi pi-check"
                  :loading="savingProfile"
                  @click="handleSaveProfile"
                />
                <Button
                  label="Cancel"
                  icon="pi pi-times"
                  severity="secondary"
                  @click="handleCancelEdit"
                  :disabled="savingProfile"
                />
              </div>
            </div>
          </template>
        </Card>

        <!-- Preferences -->
        <Card>
          <template #header>
            <div class="p-4 border-b">
              <h3 class="text-lg font-semibold">Preferences</h3>
            </div>
          </template>

          <template #content>
            <div class="space-y-4">
              <!-- Default Deck Settings -->
              <div class="space-y-4">
                <h4 class="font-semibold text-gray-700">Default Deck Settings</h4>
                
                <!-- Max Cards -->
                <div class="flex flex-col gap-2">
                  <label for="maxCards" class="text-sm">Max Cards per Deck</label>
                  <InputNumber
                    id="maxCards"
                    v-model="preferencesForm.defaultMaxCards"
                    :min="10"
                    :max="200"
                    show-buttons
                  />
                </div>

                <!-- Difficulty -->
                <div class="flex flex-col gap-2">
                  <label for="difficulty" class="text-sm">Default Difficulty</label>
                  <Select
                    id="difficulty"
                    v-model="preferencesForm.defaultDifficulty"
                    :options="['easy', 'medium', 'hard']"
                    placeholder="Select difficulty"
                  />
                </div>

                <!-- Include Images -->
                <div class="flex items-center gap-2">
                  <Checkbox
                    id="includeImages"
                    v-model="preferencesForm.includeImages"
                    binary
                  />
                  <label for="includeImages" class="text-sm cursor-pointer">Include images in cards</label>
                </div>
              </div>

              <Divider />

              <!-- Notification Preferences -->
              <div class="space-y-4">
                <h4 class="font-semibold text-gray-700">Email Notifications</h4>
                
                <!-- Email on Completion -->
                <div class="flex items-center gap-2">
                  <Checkbox
                    id="emailCompletion"
                    v-model="preferencesForm.emailOnCompletion"
                    binary
                  />
                  <label for="emailCompletion" class="text-sm cursor-pointer">Email me when job completes</label>
                </div>

                <!-- Email on Failure -->
                <div class="flex items-center gap-2">
                  <Checkbox
                    id="emailFailure"
                    v-model="preferencesForm.emailOnFailure"
                    binary
                  />
                  <label for="emailFailure" class="text-sm cursor-pointer">Email me when job fails</label>
                </div>
              </div>

              <!-- Save Button -->
              <div class="pt-4">
                <Button
                  label="Save Preferences"
                  icon="pi pi-check"
                  :loading="savingPreferences"
                  @click="handleSavePreferences"
                />
              </div>
            </div>
          </template>
        </Card>

        <!-- Danger Zone -->
        <Card>
          <template #header>
            <div class="p-4 border-b border-red-200 bg-red-50">
              <h3 class="text-lg font-semibold text-red-700">Danger Zone</h3>
            </div>
          </template>

          <template #content>
            <div class="space-y-4">
              <div class="flex items-center justify-between p-4 border border-red-200 rounded-lg">
                <div>
                  <h4 class="font-semibold text-gray-900">Delete All Decks</h4>
                  <p class="text-sm text-gray-600">Permanently delete all your Anki decks</p>
                </div>
                <Button
                  label="Delete All Decks"
                  icon="pi pi-trash"
                  severity="danger"
                  outlined
                  @click="handleDeleteAllDecks"
                />
              </div>

              <div class="flex items-center justify-between p-4 border border-red-300 rounded-lg bg-red-50">
                <div>
                  <h4 class="font-semibold text-red-900">Delete Account</h4>
                  <p class="text-sm text-red-700">Permanently delete your account and all data</p>
                </div>
                <Button
                  label="Delete Account"
                  icon="pi pi-exclamation-triangle"
                  severity="danger"
                  @click="handleDeleteAccount"
                />
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Right Column - Statistics -->
      <div class="space-y-6">
        <!-- Statistics -->
        <Card>
          <template #header>
            <div class="p-4 border-b">
              <h3 class="text-lg font-semibold">Statistics</h3>
            </div>
          </template>

          <template #content>
            <div class="space-y-4">
              <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span class="text-sm text-gray-600">Total Decks</span>
                <span class="text-lg font-bold text-primary-600">{{ decksStore.totalDecks }}</span>
              </div>

              <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span class="text-sm text-gray-600">Total Cards</span>
                <span class="text-lg font-bold text-green-600">{{ decksStore.totalCards }}</span>
              </div>

              <Divider />

              <div class="space-y-2 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-600">Account Created</span>
                  <span class="font-medium">{{ memberSince }}</span>
                </div>
                
                <div class="flex justify-between">
                  <span class="text-gray-600">Last Login</span>
                  <span class="font-medium">{{ lastLogin }}</span>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Password Change Modal -->
    <PasswordChangeModal
      v-model:visible="showPasswordModal"
      @success="showPasswordModal = false"
    />

    <!-- Confirmation Dialog -->
    <ConfirmDialog />

    <!-- Toast -->
    <Toast />
  </div>
</template>

<style scoped>
.profile-page {
  min-height: 100vh;
  background-color: #f9fafb;
}

@media (max-width: 768px) {
  .profile-page {
    padding: 1rem;
  }
}
</style>
