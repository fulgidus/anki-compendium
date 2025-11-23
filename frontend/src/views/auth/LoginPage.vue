<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as z from 'zod';
import { useToast } from 'primevue/usetoast';
import { useAuthStore } from '@/stores/auth';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Message from 'primevue/message';

const router = useRouter();
const toast = useToast();
const authStore = useAuthStore();

const loading = ref(false);
const errorMessage = ref('');

// Validation schema
const loginSchema = toTypedSchema(
  z.object({
    email: z.string().email('Invalid email address').min(1, 'Email is required'),
    password: z.string().min(1, 'Password is required'),
  })
);

const { defineField, handleSubmit, errors } = useForm({
  validationSchema: loginSchema,
});

const [email, emailAttrs] = defineField('email');
const [password, passwordAttrs] = defineField('password');

const onSubmit = handleSubmit(async (values) => {
  loading.value = true;
  errorMessage.value = '';

  try {
    await authStore.login(values.email, values.password);
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Logged in successfully',
      life: 3000,
    });
    router.push('/dashboard');
  } catch (error: any) {
    errorMessage.value =
      error.response?.data?.detail || 'Login failed. Please check your credentials.';
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage.value,
      life: 5000,
    });
  } finally {
    loading.value = false;
  }
});

const goToRegister = () => {
  router.push('/register');
};
</script>

<template>
  <div class="login-page">
    <Card class="login-card">
      <template #title>
        <div class="text-center">
          <h1 class="text-3xl font-bold mb-2">Welcome Back</h1>
          <p class="text-surface-500">Sign in to your Anki Compendium account</p>
        </div>
      </template>
      <template #content>
        <Message v-if="errorMessage" severity="error" :closable="false" class="mb-4">
          {{ errorMessage }}
        </Message>

        <form @submit="onSubmit" class="flex flex-col gap-4">
          <div class="field">
            <label for="email" class="font-semibold block mb-2">Email</label>
            <InputText
              id="email"
              v-model="email"
              v-bind="emailAttrs"
              type="email"
              placeholder="your.email@example.com"
              class="w-full"
              :class="{ 'p-invalid': errors.email }"
              autocomplete="email"
            />
            <small v-if="errors.email" class="p-error">{{ errors.email }}</small>
          </div>

          <div class="field">
            <label for="password" class="font-semibold block mb-2">Password</label>
            <Password
              id="password"
              v-model="password"
              v-bind="passwordAttrs"
              placeholder="Enter your password"
              :feedback="false"
              toggle-mask
              class="w-full"
              :class="{ 'p-invalid': errors.password }"
              :input-class="'w-full'"
              autocomplete="current-password"
            />
            <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
          </div>

          <Button
            type="submit"
            label="Sign In"
            :loading="loading"
            class="w-full"
            :disabled="loading"
          />

          <div class="text-center mt-4">
            <p class="text-surface-600">
              Don't have an account?
              <a @click.prevent="goToRegister" href="#" class="text-primary font-semibold"
                >Create one</a
              >
            </p>
          </div>
        </form>
      </template>
    </Card>
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
}

.field {
  margin-bottom: 1rem;
}

a {
  cursor: pointer;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>
