<script setup lang="ts">
import { ref, computed } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'
import { useToast } from 'primevue/usetoast'
import { useUserStore } from '@/stores/user'
import type { PasswordChangeRequest } from '@/types'

interface PasswordChangeModalProps {
  visible: boolean
}

const props = defineProps<PasswordChangeModalProps>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

const toast = useToast()
const userStore = useUserStore()

const loading = ref(false)

// Validation schema
const passwordSchema = toTypedSchema(
  z.object({
    currentPassword: z.string().min(1, 'Current password is required'),
    newPassword: z.string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number'),
    confirmPassword: z.string().min(1, 'Please confirm your password')
  }).refine((data) => data.newPassword === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword']
  })
)

const { errors, defineField, handleSubmit, resetForm } = useForm({
  validationSchema: passwordSchema
})

const [currentPassword] = defineField('currentPassword')
const [newPassword] = defineField('newPassword')
const [confirmPassword] = defineField('confirmPassword')

const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const onSubmit = handleSubmit(async (values) => {
  loading.value = true

  try {
    const request: PasswordChangeRequest = {
      currentPassword: values.currentPassword,
      newPassword: values.newPassword,
      confirmPassword: values.confirmPassword
    }

    const success = await userStore.changePassword(request)

    if (success) {
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Password changed successfully',
        life: 3000
      })
      
      dialogVisible.value = false
      resetForm()
      emit('success')
    } else {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: userStore.error || 'Failed to change password',
        life: 5000
      })
    }
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.message || 'An unexpected error occurred',
      life: 5000
    })
  } finally {
    loading.value = false
  }
})

const handleCancel = () => {
  dialogVisible.value = false
  resetForm()
}
</script>

<template>
  <Dialog
    v-model:visible="dialogVisible"
    modal
    header="Change Password"
    :style="{ width: '32rem' }"
    :closable="!loading"
    :dismissable-mask="!loading"
  >
    <form @submit="onSubmit" class="flex flex-col gap-4 py-4">
      <!-- Current Password -->
      <div class="flex flex-col gap-2">
        <label for="currentPassword" class="font-semibold">Current Password</label>
        <Password
          id="currentPassword"
          v-model="currentPassword"
          :feedback="false"
          toggle-mask
          :class="{ 'p-invalid': errors.currentPassword }"
          :disabled="loading"
          placeholder="Enter current password"
          autocomplete="current-password"
        />
        <small v-if="errors.currentPassword" class="text-red-600">{{ errors.currentPassword }}</small>
      </div>

      <!-- New Password -->
      <div class="flex flex-col gap-2">
        <label for="newPassword" class="font-semibold">New Password</label>
        <Password
          id="newPassword"
          v-model="newPassword"
          toggle-mask
          :class="{ 'p-invalid': errors.newPassword }"
          :disabled="loading"
          placeholder="Enter new password"
          autocomplete="new-password"
        >
          <template #footer>
            <div class="text-sm text-gray-600 mt-2">
              <p class="font-semibold mb-1">Password requirements:</p>
              <ul class="list-disc list-inside space-y-1">
                <li>At least 8 characters</li>
                <li>One uppercase letter</li>
                <li>One lowercase letter</li>
                <li>One number</li>
              </ul>
            </div>
          </template>
        </Password>
        <small v-if="errors.newPassword" class="text-red-600">{{ errors.newPassword }}</small>
      </div>

      <!-- Confirm Password -->
      <div class="flex flex-col gap-2">
        <label for="confirmPassword" class="font-semibold">Confirm New Password</label>
        <Password
          id="confirmPassword"
          v-model="confirmPassword"
          :feedback="false"
          toggle-mask
          :class="{ 'p-invalid': errors.confirmPassword }"
          :disabled="loading"
          placeholder="Re-enter new password"
          autocomplete="new-password"
        />
        <small v-if="errors.confirmPassword" class="text-red-600">{{ errors.confirmPassword }}</small>
      </div>
    </form>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          label="Cancel"
          severity="secondary"
          @click="handleCancel"
          :disabled="loading"
        />
        <Button
          label="Change Password"
          type="submit"
          :loading="loading"
          @click="onSubmit"
        />
      </div>
    </template>
  </Dialog>
</template>

<style scoped>
:deep(.p-password) {
  width: 100%;
}

:deep(.p-password input) {
  width: 100%;
}
</style>
