<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import ConfirmDialog from 'primevue/confirmdialog'
import { useAuthStore } from '@/stores/auth'
import { useUIStore } from '@/stores/ui'

const authStore = useAuthStore()
const uiStore = useUIStore()

// Initialize app on mount
onMounted(() => {
  // Load stored authentication
  authStore.loadStoredAuth()
  
  // Load theme preference
  uiStore.loadTheme()
})
</script>

<template>
  <div id="app">
    <!-- Global Confirmation Dialog -->
    <ConfirmDialog />
    
    <!-- Main router view (layouts will handle Toast) -->
    <RouterView />
  </div>
</template>

<style>
/* Global styles */
#app {
  min-height: 100vh;
  width: 100%;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family);
  background-color: var(--surface-ground);
  color: var(--text-color);
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--surface-100);
}

::-webkit-scrollbar-thumb {
  background: var(--surface-400);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--surface-500);
}

/* Focus visible for accessibility */
*:focus-visible {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
}
</style>
