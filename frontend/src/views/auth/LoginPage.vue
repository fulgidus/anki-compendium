<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import { getErrorMessage } from '@/utils/errors'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const formState = ref({
  email: '',
  password: '',
})

const rules = {
  email: [
    { required: true, message: 'Please input your email!', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email!', trigger: 'blur' },
  ],
  password: [
    { required: true, message: 'Please input your password!', trigger: 'blur' },
  ],
}

const onFinish = async () => {
  loading.value = true

  try {
    await authStore.login(formState.value.email, formState.value.password)
    message.success('Logged in successfully')
    router.push('/dashboard')
  } catch (error: any) {
    const errorMsg = getErrorMessage(error, 'Login failed. Please check your credentials.')
    message.error(errorMsg)
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/auth/register')
}
</script>

<template>
  <div class="login-page">
    <a-card class="login-card" :bordered="false">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold mb-2">Welcome Back</h1>
        <p class="text-gray-500">Sign in to your Anki Compendium account</p>
      </div>

      <a-form
        :model="formState"
        :rules="rules"
        layout="vertical"
        @finish="onFinish"
      >
        <a-form-item label="Email" name="email">
          <a-input
            v-model:value="formState.email"
            type="email"
            placeholder="your.email@example.com"
            size="large"
            autocomplete="email"
          />
        </a-form-item>

        <a-form-item label="Password" name="password">
          <a-input-password
            v-model:value="formState.password"
            placeholder="Enter your password"
            size="large"
            autocomplete="current-password"
          />
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            :loading="loading"
            block
            size="large"
          >
            Sign In
          </a-button>
        </a-form-item>

        <div class="text-center">
          <span class="text-gray-600">Don't have an account? </span>
          <a @click.prevent="goToRegister" class="text-primary font-semibold cursor-pointer hover:underline">
            Create one
          </a>
        </div>
      </a-form>
    </a-card>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border-radius: 8px;
}

.text-primary {
  color: #1890ff;
}
</style>
