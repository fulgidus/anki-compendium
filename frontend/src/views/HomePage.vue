<script setup lang="ts">
</script>

<template>
  <div class="home-page">
    <h1>Welcome to Anki Compendium</h1>
    <p>Transform your PDF documents into Anki flashcards using AI.</p>
    <router-link to="/login">Get Started</router-link>
  </div>
</template>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
  text-align: center;
}
</style>
