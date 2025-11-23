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
const registerSchema = toTypedSchema(
  z
    .object({
      email: z.string().email('Invalid email address').min(1, 'Email is required'),
      password: z
        .string()
        .min(8, 'Password must be at least 8 characters')
        .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
        .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
        .regex(/[0-9]/, 'Password must contain at least one number'),
      confirmPassword: z.string().min(1, 'Please confirm your password'),
      fullName: z.string().min(2, 'Full name must be at least 2 characters'),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: "Passwords don't match",
      path: ['confirmPassword'],
    })
);

const { defineField, handleSubmit, errors } = useForm({
  validationSchema: registerSchema,
});

const [email, emailAttrs] = defineField('email');
const [password, passwordAttrs] = defineField('password');
const [confirmPassword, confirmPasswordAttrs] = defineField('confirmPassword');
const [fullName, fullNameAttrs] = defineField('fullName');

const onSubmit = handleSubmit(async (values) => {
  loading.value = true;
  errorMessage.value = '';

  try {
    await authStore.register(values.email, values.password, values.fullName);
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Account created successfully! Please log in.',
      life: 3000,
    });
    router.push('/login');
  } catch (error: any) {
    errorMessage.value =
      error.response?.data?.detail || 'Registration failed. Please try again.';
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

const goToLogin = () => {
  router.push('/login');
};
</script>

<template>
  <div class="register-page">
    <Card class="register-card">
      <template #title>
        <div class="text-center">
          <h1 class="text-3xl font-bold mb-2">Create Account</h1>
          <p class="text-surface-500">Join Anki Compendium today</p>
        </div>
      </template>
      <template #content>
        <Message v-if="errorMessage" severity="error" :closable="false" class="mb-4">
          {{ errorMessage }}
        </Message>

        <form @submit="onSubmit" class="flex flex-col gap-4">
          <div class="field">
            <label for="fullName" class="font-semibold block mb-2">Full Name</label>
            <InputText
              id="fullName"
              v-model="fullName"
              v-bind="fullNameAttrs"
              placeholder="John Doe"
              class="w-full"
              :class="{ 'p-invalid': errors.fullName }"
              autocomplete="name"
            />
            <small v-if="errors.fullName" class="p-error">{{ errors.fullName }}</small>
          </div>

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
              placeholder="Create a strong password"
              toggle-mask
              class="w-full"
              :class="{ 'p-invalid': errors.password }"
              :input-class="'w-full'"
              autocomplete="new-password"
            >
              <template #footer>
                <div class="text-sm text-surface-600 mt-2">
                  <p>Password must contain:</p>
                  <ul class="list-disc ml-5">
                    <li>At least 8 characters</li>
                    <li>One uppercase letter</li>
                    <li>One lowercase letter</li>
                    <li>One number</li>
                  </ul>
                </div>
              </template>
            </Password>
            <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
          </div>

          <div class="field">
            <label for="confirmPassword" class="font-semibold block mb-2"
              >Confirm Password</label
            >
            <Password
              id="confirmPassword"
              v-model="confirmPassword"
              v-bind="confirmPasswordAttrs"
              placeholder="Re-enter your password"
              :feedback="false"
              toggle-mask
              class="w-full"
              :class="{ 'p-invalid': errors.confirmPassword }"
              :input-class="'w-full'"
              autocomplete="new-password"
            />
            <small v-if="errors.confirmPassword" class="p-error">{{
              errors.confirmPassword
            }}</small>
          </div>

          <Button
            type="submit"
            label="Create Account"
            :loading="loading"
            class="w-full"
            :disabled="loading"
          />

          <div class="text-center mt-4">
            <p class="text-surface-600">
              Already have an account?
              <a @click.prevent="goToLogin" href="#" class="text-primary font-semibold"
                >Sign in</a
              >
            </p>
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.register-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card {
  width: 100%;
  max-width: 500px;
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
