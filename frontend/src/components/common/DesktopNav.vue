<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Menubar from 'primevue/menubar'
import type { MenuItem } from 'primevue/menuitem'

const route = useRoute()
const router = useRouter()

interface NavItem {
  label: string
  icon: string
  to: string
  exact?: boolean
}

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    icon: 'pi pi-home',
    to: '/dashboard',
    exact: true
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
  }
]

// Convert nav items to PrimeVue menu items with active state
const menuItems = computed<MenuItem[]>(() => {
  return navItems.map(item => {
    const isActive = item.exact 
      ? route.path === item.to 
      : route.path.startsWith(item.to)
    
    return {
      label: item.label,
      icon: item.icon,
      command: () => router.push(item.to),
      class: isActive ? 'active-menu-item' : '',
      badge: isActive ? 'active' : undefined
    }
  })
})
</script>

<template>
  <nav class="desktop-nav hidden lg:block" role="navigation" aria-label="Main navigation">
    <Menubar :model="menuItems" class="border-none bg-transparent p-0">
      <template #item="{ item, props }">
        <a
          v-ripple
          class="flex items-center gap-2 px-4 py-2 rounded-md cursor-pointer transition-colors"
          :class="[
            item.class,
            item.badge === 'active'
              ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400 font-semibold'
              : 'text-surface-700 dark:text-surface-200 hover:bg-surface-100 dark:hover:bg-surface-800'
          ]"
          v-bind="props.action"
        >
          <i :class="item.icon" aria-hidden="true"></i>
          <span>{{ item.label }}</span>
        </a>
      </template>
    </Menubar>
  </nav>
</template>

<style scoped>
:deep(.p-menubar) {
  border: none !important;
  background: transparent !important;
}

:deep(.p-menubar-root-list) {
  display: flex;
  gap: 0.25rem;
}

:deep(.p-menubar-item) {
  border-radius: 0.375rem;
}

:deep(.p-focus) {
  box-shadow: 0 0 0 0.2rem var(--primary-color) !important;
}

.active-menu-item {
  position: relative;
}

.active-menu-item::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--primary-color);
  border-radius: 2px 2px 0 0;
}
</style>
