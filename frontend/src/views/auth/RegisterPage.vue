<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'

const router = useRouter()
const formState = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  username: [{ required: true, message: 'Username is required' }],
  email: [
    { required: true, message: 'Email is required' },
    { type: 'email', message: 'Invalid email' }
  ],
  password: [{ required: true, message: 'Password is required' }],
  confirmPassword: [{ required: true, message: 'Please confirm password' }]
}

const onFinish = async () => {
  message.success('Registration successful!')
  router.push('/auth/login')
}
</script>

<template>
  <div class="register-page">
    <a-card class="register-card" :bordered="false">
      <h1 class="text-center text-3xl font-bold mb-2">Create Account</h1>
      <p class="text-center text-gray-500 mb-8">Join Anki Compendium</p>

      <a-form :model="formState" :rules="rules" layout="vertical" @finish="onFinish">
        <a-form-item label="Username" name="username">
          <a-input v-model:value="formState.username" size="large" />
        </a-form-item>
        <a-form-item label="Email" name="email">
          <a-input v-model:value="formState.email" type="email" size="large" />
        </a-form-item>
        <a-form-item label="Password" name="password">
          <a-input-password v-model:value="formState.password" size="large" />
        </a-form-item>
        <a-form-item label="Confirm Password" name="confirmPassword">
          <a-input-password v-model:value="formState.confirmPassword" size="large" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" html-type="submit" block size="large">
            Sign Up
          </a-button>
        </a-form-item>
      </a-form>

      <div class="text-center">
        <span>Already have an account? </span>
        <a @click="router.push('/auth/login')" class="text-primary cursor-pointer">Sign In</a>
      </div>
    </a-card>
  </div>
</template>

<style scoped>
.register-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1rem;
}

.register-card {
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.text-primary {
  color: #1890ff;
}
</style>
