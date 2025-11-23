<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'
import Avatar from 'primevue/avatar'
import Menu from 'primevue/menu'
import type { MenuItem } from 'primevue/menuitem'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const menu = ref()

// Get user initials for avatar
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

// Menu items
const menuItems = computed<MenuItem[]>(() => [
  {
    label: 'Profile',
    icon: 'pi pi-user',
    command: () => {
      router.push('/profile')
    }
  },
  {
    separator: true
  },
  {
    label: 'Logout',
    icon: 'pi pi-sign-out',
    command: () => {
      handleLogout()
    }
  }
])

const toggleMenu = (event: Event) => {
  menu.value.toggle(event)
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    toast.add({
      severity: 'success',
      summary: 'Logged out',
      detail: 'See you next time!',
      life: 3000
    })
    router.push('/login')
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Logout failed',
      detail: 'An error occurred while logging out',
      life: 3000
    })
  }
}
</script>

<template>
  <div class="user-menu">
    <div
      class="flex items-center gap-3 cursor-pointer hover:bg-surface-100 dark:hover:bg-surface-700 rounded-lg p-2 transition-colors"
      @click="toggleMenu"
      role="button"
      aria-label="User menu"
      tabindex="0"
      @keydown.enter="toggleMenu"
      @keydown.space.prevent="toggleMenu"
    >
      <Avatar
        :label="userInitials"
        size="normal"
        shape="circle"
        class="bg-primary text-primary-contrast"
        aria-hidden="true"
      />
      <div class="hidden md:flex flex-col items-start">
        <span class="text-sm font-semibold text-surface-900 dark:text-surface-0">
          {{ userDisplayName }}
        </span>
        <span class="text-xs text-surface-600 dark:text-surface-400">
          {{ userEmail }}
        </span>
      </div>
      <i class="pi pi-chevron-down text-sm text-surface-600 dark:text-surface-400 hidden md:block" aria-hidden="true"></i>
    </div>

    <Menu ref="menu" :model="menuItems" :popup="true" />
  </div>
</template>

<style scoped>
.bg-primary {
  background-color: var(--primary-color);
}

.text-primary-contrast {
  color: var(--primary-contrast-color);
}
</style>
