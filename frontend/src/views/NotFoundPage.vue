<script setup lang="ts">
</script>

<template>
  <div class="not-found-page">
    <h1>404 - Page Not Found</h1>
    <router-link to="/">Go Home</router-link>
  </div>
</template>

<style scoped>
.not-found-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  text-align: center;
}
</style>
