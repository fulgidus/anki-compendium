<script setup lang="ts">
import { onMounted } from 'vue'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import BrandLogo from '@/components/common/BrandLogo.vue'
import DesktopNav from '@/components/common/DesktopNav.vue'
import MobileNav from '@/components/common/MobileNav.vue'
import UserMenu from '@/components/common/UserMenu.vue'
import Button from 'primevue/button'
import Toast from 'primevue/toast'

const uiStore = useUIStore()
const authStore = useAuthStore()

onMounted(() => {
  // Load theme preference
  uiStore.loadTheme()
  
  // Load stored authentication if available
  if (!authStore.isAuthenticated) {
    authStore.loadStoredAuth()
  }
})
</script>

<template>
  <div class="main-layout min-h-screen bg-surface-50 dark:bg-surface-900">
    <Toast />
    
    <!-- Mobile Navigation Sidebar -->
    <MobileNav />

    <!-- Header -->
    <header class="fixed top-0 left-0 right-0 z-40 bg-white dark:bg-surface-800 border-b border-surface-200 dark:border-surface-700 shadow-sm">
      <div class="flex items-center justify-between px-4 md:px-6 h-16">
        <!-- Left: Logo + Mobile Menu Button -->
        <div class="flex items-center gap-4">
          <!-- Mobile Menu Button -->
          <Button
            icon="pi pi-bars"
            text
            rounded
            class="lg:hidden"
            @click="uiStore.toggleMobileMenu"
            aria-label="Open menu"
          />
          
          <!-- Brand Logo -->
          <BrandLogo size="medium" />
        </div>

        <!-- Center: Desktop Navigation -->
        <DesktopNav />

        <!-- Right: User Menu -->
        <div class="flex items-center gap-2">
          <UserMenu />
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="pt-16 min-h-screen">
      <div class="container mx-auto px-4 py-6 md:px-6 md:py-8">
        <!-- Router View with Suspense for loading states -->
        <Suspense>
          <template #default>
            <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </template>
          <template #fallback>
            <div class="flex items-center justify-center min-h-[400px]">
              <i class="pi pi-spin pi-spinner text-4xl text-primary"></i>
            </div>
          </template>
        </Suspense>
      </div>
    </main>

    <!-- Footer (optional) -->
    <footer class="bg-white dark:bg-surface-800 border-t border-surface-200 dark:border-surface-700 mt-auto">
      <div class="container mx-auto px-4 py-6 md:px-6">
        <div class="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-surface-600 dark:text-surface-400">
          <p>&copy; 2025 Anki Compendium. All rights reserved.</p>
          <div class="flex gap-4">
            <a href="#" class="hover:text-primary transition-colors">Privacy</a>
            <a href="#" class="hover:text-primary transition-colors">Terms</a>
            <a href="#" class="hover:text-primary transition-colors">Help</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.container {
  max-width: 1280px;
}
</style>
