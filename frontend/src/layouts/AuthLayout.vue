<script setup lang="ts">
import { onMounted } from 'vue'
import { useUIStore } from '@/stores/ui'
import BrandLogo from '@/components/common/BrandLogo.vue'
import Toast from 'primevue/toast'

const uiStore = useUIStore()

onMounted(() => {
  // Load theme preference
  uiStore.loadTheme()
})
</script>

<template>
  <div class="auth-layout min-h-screen bg-gradient-to-br from-primary-50 via-surface-50 to-primary-100 dark:from-surface-900 dark:via-surface-800 dark:to-surface-900">
    <Toast />
    
    <div class="flex flex-col min-h-screen">
      <!-- Header with Logo -->
      <header class="p-6">
        <div class="container mx-auto">
          <BrandLogo size="large" :clickable="false" />
        </div>
      </header>

      <!-- Main Content - Centered Card -->
      <main class="flex-1 flex items-center justify-center px-4 py-8">
        <div class="w-full max-w-md">
          <!-- Card Container -->
          <div class="bg-white dark:bg-surface-800 rounded-2xl shadow-2xl p-8">
            <!-- Router View for Auth Pages -->
            <Suspense>
              <template #default>
                <router-view v-slot="{ Component }">
                  <transition name="slide-fade" mode="out-in">
                    <component :is="Component" />
                  </transition>
                </router-view>
              </template>
              <template #fallback>
                <div class="flex items-center justify-center min-h-[300px]">
                  <i class="pi pi-spin pi-spinner text-4xl text-primary"></i>
                </div>
              </template>
            </Suspense>
          </div>

          <!-- Footer Info -->
          <div class="text-center mt-6">
            <p class="text-sm text-surface-600 dark:text-surface-400">
              &copy; 2025 Anki Compendium. All rights reserved.
            </p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  transform: translateX(-20px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}

.container {
  max-width: 1280px;
}

/* Gradient background animation */
.auth-layout {
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
}

@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}
</style>
