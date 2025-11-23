<script setup lang="ts">
import { useRouter } from 'vue-router'

interface Props {
  size?: 'small' | 'medium' | 'large'
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
  clickable: true
})

const router = useRouter()

const handleClick = () => {
  if (props.clickable) {
    router.push('/dashboard')
  }
}

const sizeClasses = {
  small: 'text-lg gap-2',
  medium: 'text-xl gap-2.5',
  large: 'text-2xl gap-3'
}

const iconSizeClasses = {
  small: 'text-2xl',
  medium: 'text-3xl',
  large: 'text-4xl'
}
</script>

<template>
  <div
    :class="[
      'flex items-center font-semibold text-primary',
      sizeClasses[size],
      clickable ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''
    ]"
    @click="handleClick"
    :role="clickable ? 'button' : undefined"
    :tabindex="clickable ? 0 : undefined"
    :aria-label="clickable ? 'Navigate to dashboard' : 'Anki Compendium'"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <i :class="['pi pi-box', iconSizeClasses[size]]" aria-hidden="true"></i>
    <span class="font-bold">Anki Compendium</span>
  </div>
</template>

<style scoped>
.text-primary {
  color: var(--primary-color);
}
</style>
