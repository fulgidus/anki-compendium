<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUIStore } from '@/stores/ui'
import { useAuthStore } from '@/stores/auth'
import Sidebar from 'primevue/sidebar'
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'

const route = useRoute()
const router = useRouter()
const uiStore = useUIStore()
const authStore = useAuthStore()

interface NavItem {
  label: string
  icon: string
  to: string
}

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    icon: 'pi pi-home',
    to: '/dashboard'
  },
  {
    label: 'Upload PDF',
    icon: 'pi pi-upload',
    to: '/upload'
  },
  {
    label: 'My Jobs',
    icon: 'pi pi-clock',
    to: '/jobs'
  },
  {
    label: 'My Decks',
    icon: 'pi pi-box',
    to: '/decks'
  },
  {
    label: 'Profile',
    icon: 'pi pi-user',
    to: '/profile'
  }
]

const isActive = (path: string) => {
  return route.path === path || route.path.startsWith(path + '/')
}

const navigateTo = (path: string) => {
  router.push(path)
  uiStore.closeMobileMenu()
}

const userInitials = computed(() => {
  if (!authStore.user) return 'U'
  const email = authStore.user.email || ''
  const username = authStore.user.username || email
  
  if (username.includes('@')) {
    return email.charAt(0).toUpperCase()
  }
  
  const parts = username.split(' ')
  if (parts.length >= 2 && parts[0] && parts[1]) {
    return (parts[0].charAt(0) + parts[1].charAt(0)).toUpperCase()
  }
  
  return username.slice(0, 2).toUpperCase()
})

const userDisplayName = computed(() => {
  if (!authStore.user) return 'User'
  return authStore.user.username || authStore.user.email || 'User'
})

const userEmail = computed(() => {
  return authStore.user?.email || ''
})
</script>

<template>
  <Sidebar
    v-model:visible="uiStore.mobileMenuOpen"
    position="left"
    class="mobile-nav lg:hidden"
    :showCloseIcon="false"
  >
    <template #header>
      <div class="flex items-center justify-between w-full">
        <h2 class="text-xl font-bold text-surface-900 dark:text-surface-0">
          Menu
        </h2>
        <Button
          icon="pi pi-times"
          text
          rounded
          @click="uiStore.closeMobileMenu"
          aria-label="Close menu"
        />
      </div>
    </template>

    <div class="flex flex-col h-full">
      <!-- User Info Section -->
      <div class="mb-6 pb-4 border-b border-surface-200 dark:border-surface-700">
        <div class="flex items-center gap-3">
          <Avatar
            :label="userInitials"
            size="large"
            shape="circle"
            class="bg-primary text-primary-contrast"
          />
          <div class="flex flex-col">
            <span class="text-base font-semibold text-surface-900 dark:text-surface-0">
              {{ userDisplayName }}
            </span>
            <span class="text-sm text-surface-600 dark:text-surface-400">
              {{ userEmail }}
            </span>
          </div>
        </div>
      </div>

      <!-- Navigation Links -->
      <nav class="flex-1" role="navigation" aria-label="Mobile navigation">
        <ul class="flex flex-col gap-1">
          <li v-for="item in navItems" :key="item.to">
            <button
              @click="navigateTo(item.to)"
              :class="[
                'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors text-left',
                isActive(item.to)
                  ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400 font-semibold'
                  : 'text-surface-700 dark:text-surface-200 hover:bg-surface-100 dark:hover:bg-surface-800'
              ]"
              :aria-current="isActive(item.to) ? 'page' : undefined"
            >
              <i :class="['text-xl', item.icon]" aria-hidden="true"></i>
              <span class="text-base">{{ item.label }}</span>
            </button>
          </li>
        </ul>
      </nav>

      <!-- Footer Info -->
      <div class="mt-auto pt-4 border-t border-surface-200 dark:border-surface-700">
        <p class="text-xs text-surface-500 dark:text-surface-400 text-center">
          Anki Compendium v1.0
        </p>
      </div>
    </div>
  </Sidebar>
</template>

<style scoped>
.bg-primary {
  background-color: var(--primary-color);
}

.text-primary-contrast {
  color: var(--primary-contrast-color);
}

:deep(.p-sidebar) {
  width: 320px;
  max-width: 85vw;
}

:deep(.p-sidebar-content) {
  padding: 1.5rem;
}
</style>
