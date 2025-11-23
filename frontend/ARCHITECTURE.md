# Frontend Architecture - Anki Compendium

**Version:** 1.0  
**Last Updated:** 2025-11-23  
**Status:** Production-Ready Blueprint  
**Target:** Rapid deployment of stable Vue.js 3 application

---

## 1. Executive Summary

This document defines the complete frontend architecture for Anki Compendium, a web application that transforms academic PDFs into Anki flashcard decks using AI. The frontend interfaces with a production-ready FastAPI backend deployed on OVH Kubernetes.

### Key Constraints
- ✅ **Backend**: 100% complete, production-ready FastAPI with Keycloak OAuth2
- ✅ **Infrastructure**: OVH Kubernetes cluster ready
- ⚠️ **Scope**: NO PWA features in Phase 1 (deferred to future phases)
- 🎯 **Priority**: Rapid deployment with stability over feature richness

### Architecture Philosophy
- **Mobile-first responsive design** (not PWA installable yet)
- **Modern, maintainable TypeScript codebase**
- **Component-driven architecture** with atomic design principles
- **Performance-optimized** build pipeline
- **Developer experience** optimized for rapid iteration

---

## 2. Technology Stack Decisions

### 2.1 Core Framework: Vue.js 3 + Vite

**Decision: Vue.js 3 with Composition API + `<script setup>`**

**Rationale:**
- Native TypeScript support with excellent inference
- Composition API provides superior code organization and reusability
- Smaller bundle size than React (23KB vs 45KB)
- Reactivity system perfect for real-time job status updates
- Excellent ecosystem maturity (Vue Router 4, Pinia)
- Vite provides instant HMR and optimized production builds
- Strong OVH Kubernetes compatibility

**Alternatives Considered:**
- ❌ React: Larger bundle, more boilerplate for TypeScript
- ❌ Angular: Overkill for this scope, steeper learning curve
- ❌ Svelte: Smaller ecosystem, less corporate backing

---

### 2.2 UI Component Library: **PrimeVue 4**

**Decision: PrimeVue 4.x (NOT Vuetify, NOT Naive UI)**

**Rationale:**
✅ **60+ production-ready components** covering all use cases  
✅ **Unstyled mode + theming system** (full design control)  
✅ **Excellent TypeScript support** with full type definitions  
✅ **Accessibility built-in** (WCAG 2.1 Level AA compliant)  
✅ **File upload component** with drag-drop and progress tracking  
✅ **Tree component** for PDF page selection UI  
✅ **Data table** for deck/job management  
✅ **Active maintenance** (weekly releases, 10+ years in production)  
✅ **Documentation quality** superior to alternatives  
✅ **No Material Design lock-in** (unlike Vuetify)

**Comparison:**

| Feature | PrimeVue | Vuetify | Naive UI | Element Plus |
|---------|----------|---------|----------|--------------|
| TypeScript | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Components | 60+ | 100+ | 80+ | 60+ |
| Bundle Size | Medium | Large | Small | Medium |
| Customization | Excellent | Limited | Good | Good |
| Accessibility | Built-in | Partial | Partial | Limited |
| Docs Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Maintenance | Active | Active | Active | Active |
| Design Lock-in | None | Material | Custom | Element |

**Installation:**
```bash
npm install primevue primeicons
npm install @primevue/themes  # For theming
```

---

### 2.3 State Management: **Pinia**

**Decision: Pinia (official Vue.js store)**

**Rationale:**
- Official Vue.js state management (replaces Vuex)
- TypeScript support out-of-the-box (no manual typing needed)
- Devtools integration for debugging
- Simple API with Composition API style
- Tree-shakable (only used stores are bundled)
- Perfect for auth state, user profile, job polling

**Store Structure:**
```typescript
stores/
├── auth.ts          // Authentication, tokens, user profile
├── decks.ts         // Deck list, download management
├── jobs.ts          // Job creation, status polling
├── upload.ts        // PDF upload state, progress tracking
└── settings.ts      // User preferences, theme
```

---

### 2.4 Routing: **Vue Router 4**

**Decision: Vue Router 4 with TypeScript route definitions**

**Features:**
- File-based route structure
- Navigation guards for authentication
- Route-level code splitting
- Typed route params
- Scroll behavior management

**Route Structure:**
```typescript
routes/
├── /                       → Landing page (public)
├── /login                  → Login page (public)
├── /register               → Registration page (public)
├── /dashboard              → User dashboard (auth required)
├── /upload                 → PDF upload flow (auth required)
├── /jobs                   → Job history (auth required)
├── /decks                  → Deck management (auth required)
├── /profile                → User profile (auth required)
├── /settings               → Settings page (auth required)
└── /404                    → Not found fallback
```

---

### 2.5 HTTP Client: **Axios**

**Decision: Axios (NOT native Fetch API)**

**Rationale:**
✅ Request/response interceptors (auth token injection)  
✅ Automatic JSON transformation  
✅ Timeout handling and retry logic  
✅ TypeScript support with typed responses  
✅ Better error handling than Fetch  
✅ Progress tracking for file uploads  
✅ Request cancellation (AbortController)  

**API Client Structure:**
```typescript
api/
├── client.ts           // Axios instance with interceptors
├── auth.api.ts         // Authentication endpoints
├── decks.api.ts        // Deck management endpoints
├── jobs.api.ts         // Job status endpoints
├── upload.api.ts       // PDF upload endpoint
└── types.ts            // API response types
```

**Alternative Rejected:**
- ❌ Fetch API: No interceptors, manual JSON handling, verbose error handling

---

### 2.6 Form Handling: **VeeValidate + Zod**

**Decision: VeeValidate 4.x + Zod schema validation**

**Rationale:**
- VeeValidate: Vue-first validation library with Composition API
- Zod: Runtime type checking + TypeScript inference
- Field-level and form-level validation
- Custom async validators (email uniqueness check)
- Integrates perfectly with PrimeVue input components

**Example Usage:**
```typescript
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'

const schema = toTypedSchema(
  z.object({
    email: z.string().email(),
    password: z.string().min(8),
  })
)

const { handleSubmit, errors } = useForm({ validationSchema: schema })
```

**Alternatives Rejected:**
- ❌ Manual validation: Error-prone, inconsistent
- ❌ Vuelidate: Less TypeScript-friendly

---

### 2.7 PDF.js Integration: **vue-pdf-embed**

**Decision: `vue-pdf-embed` wrapper for PDF.js**

**Rationale:**
- Vue 3 compatible wrapper around Mozilla's PDF.js
- Page-by-page rendering with lazy loading
- Canvas-based rendering (best quality)
- Thumbnail generation for page selection
- Text selection support (future feature)
- No external dependencies (self-hosted PDF.js worker)

**Features Needed:**
- PDF preview with page navigation
- Multi-page selection UI (checkboxes or range selector)
- Page thumbnail grid
- Zoom controls

**Installation:**
```bash
npm install vue-pdf-embed
```

---

### 2.8 Styling Approach: **PrimeVue Themes + Tailwind CSS**

**Decision: Hybrid approach - PrimeVue for components, Tailwind for utilities**

**Rationale:**
✅ PrimeVue Aura theme (modern, clean, professional)  
✅ Tailwind for spacing, layout, responsive utilities  
✅ Design tokens shared between both systems  
✅ No CSS conflicts (scoped styles in components)  

**Configuration:**
```typescript
// primevue.config.ts
import Aura from '@primevue/themes/aura'

export default {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.dark-mode',
      cssLayer: {
        name: 'primevue',
        order: 'tailwind-base, primevue, tailwind-utilities'
      }
    }
  }
}
```

**Tailwind Usage:**
- Layout: `flex`, `grid`, `container`
- Spacing: `p-4`, `m-2`, `gap-4`
- Responsive: `md:`, `lg:`, `xl:`
- Dark mode: `dark:` prefix

---

### 2.9 Job Status Polling: **Polling (NOT WebSocket)**

**Decision: HTTP polling with exponential backoff**

**Rationale:**
- Simpler to implement (no WebSocket infrastructure)
- More reliable through proxies/load balancers
- Backend already provides `/api/v1/jobs/{job_id}` endpoint
- Scales well for typical job durations (5-10 min)
- WebSocket deferred to Phase 2

**Polling Strategy:**
```typescript
// Initial: poll every 2 seconds
// After 10 polls: every 5 seconds
// After 20 polls: every 10 seconds
// Max: 60 seconds interval

const pollJob = async (jobId: string) => {
  let interval = 2000  // Start at 2s
  let pollCount = 0
  
  const timer = setInterval(async () => {
    const job = await api.getJobStatus(jobId)
    
    if (job.status === 'completed' || job.status === 'failed') {
      clearInterval(timer)
      return
    }
    
    pollCount++
    if (pollCount > 20) interval = 10000
    else if (pollCount > 10) interval = 5000
  }, interval)
}
```

---

## 3. Project Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   └── robots.txt
├── src/
│   ├── api/                    # API client layer
│   │   ├── client.ts           # Axios instance, interceptors
│   │   ├── auth.api.ts         # Auth endpoints
│   │   ├── decks.api.ts        # Deck endpoints
│   │   ├── jobs.api.ts         # Job endpoints
│   │   ├── upload.api.ts       # Upload endpoints
│   │   └── types.ts            # Shared API types
│   ├── assets/                 # Static assets
│   │   ├── images/
│   │   ├── fonts/
│   │   └── styles/
│   │       ├── main.css        # Global styles
│   │       └── tailwind.css    # Tailwind imports
│   ├── components/             # Reusable components
│   │   ├── common/             # Generic components
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppFooter.vue
│   │   │   ├── LoadingSpinner.vue
│   │   │   ├── ErrorAlert.vue
│   │   │   └── ConfirmDialog.vue
│   │   ├── auth/               # Auth-specific
│   │   │   ├── LoginForm.vue
│   │   │   ├── RegisterForm.vue
│   │   │   └── PasswordInput.vue
│   │   ├── pdf/                # PDF-related
│   │   │   ├── PdfViewer.vue
│   │   │   ├── PdfPageSelector.vue
│   │   │   ├── PdfThumbnail.vue
│   │   │   └── PdfUploadZone.vue
│   │   ├── jobs/               # Job-related
│   │   │   ├── JobStatusCard.vue
│   │   │   ├── JobList.vue
│   │   │   ├── JobProgressBar.vue
│   │   │   └── JobErrorDetails.vue
│   │   └── decks/              # Deck-related
│   │       ├── DeckCard.vue
│   │       ├── DeckList.vue
│   │       ├── DeckDownloadButton.vue
│   │       └── DeckStatistics.vue
│   ├── composables/            # Composition API utilities
│   │   ├── useAuth.ts          # Auth state & methods
│   │   ├── useJobPolling.ts    # Job status polling
│   │   ├── usePdfUpload.ts     # PDF upload logic
│   │   ├── useFileValidation.ts # File validation
│   │   ├── useNotification.ts  # Toast notifications
│   │   └── useBreakpoints.ts   # Responsive utilities
│   ├── layouts/                # Layout components
│   │   ├── DefaultLayout.vue   # Authenticated layout
│   │   ├── AuthLayout.vue      # Login/register layout
│   │   └── EmptyLayout.vue     # Minimal layout
│   ├── router/                 # Vue Router configuration
│   │   ├── index.ts            # Router instance
│   │   ├── routes.ts           # Route definitions
│   │   └── guards.ts           # Navigation guards
│   ├── stores/                 # Pinia stores
│   │   ├── auth.ts             # Authentication state
│   │   ├── decks.ts            # Deck management
│   │   ├── jobs.ts             # Job tracking
│   │   ├── upload.ts           # Upload state
│   │   └── settings.ts         # User preferences
│   ├── types/                  # TypeScript types
│   │   ├── auth.types.ts
│   │   ├── deck.types.ts
│   │   ├── job.types.ts
│   │   ├── upload.types.ts
│   │   └── api.types.ts
│   ├── utils/                  # Utility functions
│   │   ├── format.ts           # Date/size formatting
│   │   ├── validation.ts       # Custom validators
│   │   ├── errors.ts           # Error handling
│   │   └── constants.ts        # App constants
│   ├── views/                  # Page components (routed)
│   │   ├── HomePage.vue
│   │   ├── LoginPage.vue
│   │   ├── RegisterPage.vue
│   │   ├── DashboardPage.vue
│   │   ├── UploadPage.vue
│   │   ├── JobsPage.vue
│   │   ├── DecksPage.vue
│   │   ├── ProfilePage.vue
│   │   ├── SettingsPage.vue
│   │   └── NotFoundPage.vue
│   ├── App.vue                 # Root component
│   ├── main.ts                 # Application entry point
│   └── env.d.ts                # Environment types
├── .env.development            # Dev environment variables
├── .env.production             # Prod environment variables
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json               # TypeScript configuration
├── tsconfig.node.json          # Node TypeScript config
├── vite.config.ts              # Vite configuration
├── tailwind.config.js          # Tailwind configuration
└── README.md
```

---

## 4. Component Architecture

### 4.1 Component Design Principles

**Atomic Design Pattern:**
- **Atoms**: Basic UI elements (Button, Input, Badge)
- **Molecules**: Simple component groups (SearchBar, JobStatusCard)
- **Organisms**: Complex UI sections (PdfViewer, JobList)
- **Templates**: Page layouts (DefaultLayout, AuthLayout)
- **Pages**: Route-level views (DashboardPage, UploadPage)

**Component Guidelines:**
1. **Single Responsibility**: Each component has one clear purpose
2. **Prop Typing**: All props strictly typed with TypeScript
3. **Event Emission**: Use typed emits with payload interfaces
4. **Composable Logic**: Extract reusable logic into composables
5. **Slot Usage**: Flexible content injection where appropriate
6. **Accessibility**: ARIA labels, keyboard navigation, focus management

---

### 4.2 Key Component Specifications

#### **PdfViewer.vue**
```vue
<script setup lang="ts">
interface Props {
  fileUrl: string
  selectedPages: Set<number>
}

interface Emits {
  (e: 'pageSelect', page: number): void
  (e: 'pageDeselect', page: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Features:
// - Page-by-page rendering with lazy loading
// - Thumbnail grid for quick navigation
// - Zoom controls (50%, 100%, 150%, 200%)
// - Page selection checkboxes
// - Keyboard navigation (arrow keys)
</script>
```

#### **JobStatusCard.vue**
```vue
<script setup lang="ts">
import { useJobPolling } from '@/composables/useJobPolling'

interface Props {
  jobId: string
}

const props = defineProps<Props>()

const { job, isPolling, error } = useJobPolling(props.jobId)

// Features:
// - Real-time status updates via polling
// - Progress bar (0-100%)
// - Stage indicator (extraction → chunking → generation)
// - Estimated time remaining
// - Error display with retry button
// - Download button when completed
</script>
```

#### **PdfUploadZone.vue**
```vue
<script setup lang="ts">
import { usePdfUpload } from '@/composables/usePdfUpload'

const {
  file,
  uploadProgress,
  isUploading,
  error,
  selectFile,
  uploadFile,
  reset
} = usePdfUpload()

// Features:
// - Drag-and-drop zone
// - File browser fallback
// - File validation (type, size)
// - Upload progress bar
// - Error handling with retry
// - File preview before upload
</script>
```

---

## 5. State Management Strategy

### 5.1 Pinia Store Architecture

#### **Auth Store** (`stores/auth.ts`)
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth.api'
import type { User, LoginCredentials } from '@/types/auth.types'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  
  // Getters
  const isAuthenticated = computed(() => !!accessToken.value)
  const userProfile = computed(() => user.value)
  
  // Actions
  const login = async (credentials: LoginCredentials) => {
    const response = await authApi.login(credentials)
    accessToken.value = response.access_token
    refreshToken.value = response.refresh_token
    user.value = response.user
    
    // Store tokens in localStorage
    localStorage.setItem('accessToken', response.access_token)
    localStorage.setItem('refreshToken', response.refresh_token)
  }
  
  const logout = async () => {
    await authApi.logout()
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    localStorage.clear()
  }
  
  const refreshAccessToken = async () => {
    if (!refreshToken.value) throw new Error('No refresh token')
    
    const response = await authApi.refresh(refreshToken.value)
    accessToken.value = response.access_token
    localStorage.setItem('accessToken', response.access_token)
  }
  
  const loadStoredAuth = () => {
    const token = localStorage.getItem('accessToken')
    const refresh = localStorage.getItem('refreshToken')
    
    if (token && refresh) {
      accessToken.value = token
      refreshToken.value = refresh
      // Fetch user profile
      fetchUserProfile()
    }
  }
  
  const fetchUserProfile = async () => {
    user.value = await authApi.getProfile()
  }
  
  return {
    user,
    accessToken,
    isAuthenticated,
    userProfile,
    login,
    logout,
    refreshAccessToken,
    loadStoredAuth,
    fetchUserProfile
  }
})
```

#### **Jobs Store** (`stores/jobs.ts`)
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { jobsApi } from '@/api/jobs.api'
import type { Job } from '@/types/job.types'

export const useJobsStore = defineStore('jobs', () => {
  const jobs = ref<Job[]>([])
  const activePolls = ref<Set<string>>(new Set())
  
  const createJob = async (pdfUrl: string, pageRange: number[]) => {
    const job = await jobsApi.create({ pdfUrl, pageRange })
    jobs.value.unshift(job)
    return job
  }
  
  const updateJobStatus = async (jobId: string) => {
    const job = await jobsApi.getStatus(jobId)
    const index = jobs.value.findIndex(j => j.id === jobId)
    if (index !== -1) {
      jobs.value[index] = job
    }
    return job
  }
  
  const fetchAllJobs = async () => {
    jobs.value = await jobsApi.list()
  }
  
  return {
    jobs,
    activePolls,
    createJob,
    updateJobStatus,
    fetchAllJobs
  }
})
```

---

## 6. Routing Structure

### 6.1 Route Definitions

```typescript
// router/routes.ts
import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomePage.vue'),
    meta: { layout: 'empty', requiresAuth: false }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginPage.vue'),
    meta: { layout: 'auth', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterPage.vue'),
    meta: { layout: 'auth', requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardPage.vue'),
    meta: { layout: 'default', requiresAuth: true }
  },
  {
    path: '/upload',
    name: 'upload',
    component: () => import('@/views/UploadPage.vue'),
    meta: { layout: 'default', requiresAuth: true }
  },
  {
    path: '/jobs',
    name: 'jobs',
    component: () => import('@/views/JobsPage.vue'),
    meta: { layout: 'default', requiresAuth: true }
  },
  {
    path: '/decks',
    name: 'decks',
    component: () => import('@/views/DecksPage.vue'),
    meta: { layout: 'default', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/ProfilePage.vue'),
    meta: { layout: 'default', requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsPage.vue'),
    meta: { layout: 'default', requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundPage.vue'),
    meta: { layout: 'empty', requiresAuth: false }
  }
]
```

### 6.2 Navigation Guards

```typescript
// router/guards.ts
import { useAuthStore } from '@/stores/auth'
import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'

export const authGuard = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
}
```

---

## 7. API Integration Patterns

### 7.1 Axios Client Configuration

```typescript
// api/client.ts
import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useNotification } from '@/composables/useNotification'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor: inject auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    
    if (authStore.accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle errors, token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const authStore = useAuthStore()
    const notification = useNotification()
    
    // Token expired - try refresh
    if (error.response?.status === 401) {
      try {
        await authStore.refreshAccessToken()
        // Retry original request
        return apiClient(error.config!)
      } catch (refreshError) {
        // Refresh failed - logout user
        await authStore.logout()
        notification.error('Session expired. Please login again.')
        window.location.href = '/login'
      }
    }
    
    // Other errors
    if (error.response?.status === 403) {
      notification.error('You do not have permission to perform this action.')
    } else if (error.response?.status >= 500) {
      notification.error('Server error. Please try again later.')
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
```

### 7.2 API Module Pattern

```typescript
// api/upload.api.ts
import apiClient from './client'
import type { UploadResponse, UploadProgress } from './types'

export const uploadApi = {
  uploadPdf: async (
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await apiClient.post<UploadResponse>(
      '/upload',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
            onProgress({
              loaded: progressEvent.loaded,
              total: progressEvent.total,
              percent: percentCompleted
            })
          }
        }
      }
    )
    
    return response.data
  }
}
```

---

## 8. Authentication Flow

### 8.1 Login Sequence

```
User enters credentials
  ↓
LoginForm validates input (VeeValidate + Zod)
  ↓
Submit → authStore.login(credentials)
  ↓
POST /api/v1/auth/login
  ↓
Backend validates with Keycloak
  ↓
Return { access_token, refresh_token, user }
  ↓
Store tokens in localStorage + Pinia store
  ↓
Redirect to /dashboard
  ↓
Dashboard loads user data
```

### 8.2 Token Refresh Strategy

```typescript
// Automatic token refresh before expiration
// Token lifetime: 15 minutes
// Refresh trigger: 2 minutes before expiry (13 min mark)

setInterval(async () => {
  const authStore = useAuthStore()
  
  if (authStore.isAuthenticated) {
    const tokenAge = getTokenAge(authStore.accessToken)
    
    if (tokenAge > 13 * 60 * 1000) {  // 13 minutes
      try {
        await authStore.refreshAccessToken()
      } catch (error) {
        await authStore.logout()
      }
    }
  }
}, 60000)  // Check every minute
```

### 8.3 Protected Route Access

```
User navigates to /dashboard
  ↓
Router authGuard checks isAuthenticated
  ↓
If NOT authenticated → redirect to /login?redirect=/dashboard
  ↓
If authenticated → proceed to /dashboard
  ↓
Dashboard component mounted
  ↓
Check if user profile loaded
  ↓
If not → fetch from /api/v1/auth/me
  ↓
Render dashboard with user data
```

---

## 9. Build & Deployment Strategy

### 9.1 Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    target: 'esnext',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'primevue': ['primevue'],
          'pdf': ['vue-pdf-embed'],
          'utils': ['axios', 'zod']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### 9.2 Production Build Pipeline

```bash
# Build process
npm run build
  ↓
Vite bundles with tree-shaking
  ↓
Output to dist/
├── index.html
├── assets/
│   ├── index-[hash].js        # Main bundle (~150KB gzipped)
│   ├── vendor-[hash].js       # Vue, Router, Pinia (~80KB)
│   ├── primevue-[hash].js     # PrimeVue components (~120KB)
│   ├── pdf-[hash].js          # PDF.js (~200KB)
│   └── [name]-[hash].css      # Styles (~40KB)
└── favicon.ico
```

### 9.3 Docker Configuration

```dockerfile
# Dockerfile (multi-stage build)
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 9.4 Nginx Configuration

```nginx
# nginx.conf
server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;
  
  # Gzip compression
  gzip on;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
  
  # Cache static assets
  location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }
  
  # SPA fallback
  location / {
    try_files $uri $uri/ /index.html;
  }
  
  # API proxy (if backend on same domain)
  location /api/ {
    proxy_pass http://backend-svc:8000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
  
  # Security headers
  add_header X-Frame-Options "DENY";
  add_header X-Content-Type-Options "nosniff";
  add_header X-XSS-Protection "1; mode=block";
  add_header Referrer-Policy "strict-origin-when-cross-origin";
}
```

### 9.5 Kubernetes Deployment

```yaml
# k8s/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: anki-compendium-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: registry.example.com/anki-compendium-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-svc
  namespace: anki-compendium-prod
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 80
  selector:
    app: frontend
```

---

## 10. Development Guidelines

### 10.1 Code Style Standards

**TypeScript:**
- Use `interface` for object shapes, `type` for unions/intersections
- Enable `strict` mode in `tsconfig.json`
- Avoid `any` - use `unknown` or proper typing
- Use `const` assertions for immutable objects

**Vue Components:**
- Use `<script setup lang="ts">` syntax
- Props via `defineProps<Interface>()`
- Emits via `defineEmits<Interface>()`
- Composables for reusable logic
- Avoid `ref()` pollution - group related state

**Naming Conventions:**
- Components: PascalCase (`PdfViewer.vue`)
- Composables: camelCase with `use` prefix (`useAuth.ts`)
- Stores: camelCase with `Store` suffix (`authStore`)
- Constants: UPPER_SNAKE_CASE
- Variables: camelCase

### 10.2 Component Template Structure

```vue
<script setup lang="ts">
// 1. Imports
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 2. Props & Emits
interface Props {
  id: string
}

interface Emits {
  (e: 'submit', value: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 3. Composables
const router = useRouter()

// 4. Reactive State
const loading = ref(false)
const error = ref<string | null>(null)

// 5. Computed Properties
const isValid = computed(() => !error.value)

// 6. Methods
const handleSubmit = () => {
  emit('submit', props.id)
}

// 7. Lifecycle Hooks
onMounted(() => {
  // Initialize component
})
</script>

<template>
  <div class="component-name">
    <!-- Template content -->
  </div>
</template>

<style scoped>
/* Component-specific styles */
</style>
```

### 10.3 Error Handling Pattern

```typescript
// utils/errors.ts
export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public details?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export const handleApiError = (error: unknown): string => {
  if (error instanceof ApiError) {
    switch (error.statusCode) {
      case 400:
        return 'Invalid request. Please check your input.'
      case 401:
        return 'Authentication required. Please login.'
      case 403:
        return 'You do not have permission for this action.'
      case 404:
        return 'Resource not found.'
      case 429:
        return 'Too many requests. Please try again later.'
      case 500:
        return 'Server error. Please contact support.'
      default:
        return error.message || 'An unexpected error occurred.'
    }
  }
  
  if (error instanceof Error) {
    return error.message
  }
  
  return 'An unknown error occurred.'
}
```

### 10.4 Performance Best Practices

**Code Splitting:**
- Lazy load route components
- Dynamic imports for heavy libraries
- Separate PDF.js into its own chunk

**Image Optimization:**
- Use WebP with fallback
- Lazy load images below fold
- Responsive image sizes

**Bundle Size:**
- Target: Main bundle < 150KB gzipped
- Monitor with `vite-bundle-visualizer`
- Tree-shake unused PrimeVue components

**Caching Strategy:**
- Immutable assets with hash in filename
- Service Worker for offline (Phase 2)
- API response caching with stale-while-revalidate

---

## 11. Testing Strategy

### 11.1 Testing Pyramid

```
                    /\
                   /  \
                  / E2E \          Playwright (5%)
                 /------\
                /        \
               / Integr.  \        Vitest (15%)
              /------------\
             /              \
            /  Unit Tests    \     Vitest (80%)
           /------------------\
```

### 11.2 Unit Testing (Vitest)

```typescript
// components/__tests__/PdfViewer.spec.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import PdfViewer from '../PdfViewer.vue'

describe('PdfViewer', () => {
  it('renders PDF pages', async () => {
    const wrapper = mount(PdfViewer, {
      props: {
        fileUrl: '/test.pdf',
        selectedPages: new Set([1, 2])
      }
    })
    
    expect(wrapper.find('.pdf-viewer').exists()).toBe(true)
  })
  
  it('emits page selection events', async () => {
    const wrapper = mount(PdfViewer, {
      props: {
        fileUrl: '/test.pdf',
        selectedPages: new Set()
      }
    })
    
    await wrapper.find('.page-checkbox').trigger('click')
    
    expect(wrapper.emitted('pageSelect')).toBeTruthy()
    expect(wrapper.emitted('pageSelect')?.[0]).toEqual([1])
  })
})
```

### 11.3 Integration Testing

```typescript
// composables/__tests__/useJobPolling.spec.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useJobPolling } from '../useJobPolling'
import { setActivePinia, createPinia } from 'pinia'

describe('useJobPolling', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })
  
  afterEach(() => {
    vi.restoreAllMocks()
  })
  
  it('polls job status until completion', async () => {
    const { job, startPolling } = useJobPolling('job-123')
    
    startPolling()
    
    // Advance timers
    vi.advanceTimersByTime(2000)
    
    await vi.waitFor(() => {
      expect(job.value?.status).toBe('completed')
    })
  })
})
```

### 11.4 E2E Testing (Playwright)

```typescript
// e2e/upload-flow.spec.ts
import { test, expect } from '@playwright/test'

test('complete PDF upload and deck generation flow', async ({ page }) => {
  // Login
  await page.goto('/login')
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password123')
  await page.click('button[type="submit"]')
  
  // Navigate to upload
  await expect(page).toHaveURL('/dashboard')
  await page.click('a[href="/upload"]')
  
  // Upload PDF
  await page.setInputFiles('input[type="file"]', './fixtures/sample.pdf')
  await expect(page.locator('.pdf-preview')).toBeVisible()
  
  // Select pages
  await page.click('[data-testid="page-1"]')
  await page.click('[data-testid="page-2"]')
  
  // Submit
  await page.click('button:has-text("Generate Deck")')
  
  // Wait for job completion
  await expect(page.locator('.job-status')).toContainText('Completed', {
    timeout: 300000  // 5 minutes max
  })
  
  // Download deck
  const downloadPromise = page.waitForEvent('download')
  await page.click('button:has-text("Download Deck")')
  const download = await downloadPromise
  expect(download.suggestedFilename()).toMatch(/\.apkg$/)
})
```

### 11.5 Testing Coverage Goals

| Category | Target | Command |
|----------|--------|---------|
| Unit Tests | 80%+ | `npm run test:unit` |
| Integration | 60%+ | `npm run test:integration` |
| E2E | Critical paths | `npm run test:e2e` |

---

## 12. Environment Configuration

### 12.1 Environment Variables

```env
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Anki Compendium (Dev)
VITE_MAX_FILE_SIZE=104857600  # 100MB
VITE_ALLOWED_FILE_TYPES=application/pdf
VITE_JOB_POLL_INTERVAL=2000
VITE_ENABLE_DEVTOOLS=true
```

```env
# .env.production
VITE_API_BASE_URL=https://api.anki-compendium.example.com/api/v1
VITE_APP_NAME=Anki Compendium
VITE_MAX_FILE_SIZE=104857600
VITE_ALLOWED_FILE_TYPES=application/pdf
VITE_JOB_POLL_INTERVAL=5000
VITE_ENABLE_DEVTOOLS=false
```

### 12.2 TypeScript Environment Types

```typescript
// src/env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_MAX_FILE_SIZE: string
  readonly VITE_ALLOWED_FILE_TYPES: string
  readonly VITE_JOB_POLL_INTERVAL: string
  readonly VITE_ENABLE_DEVTOOLS: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

---

## 13. Accessibility Standards

### 13.1 WCAG 2.1 Level AA Compliance

**Requirements:**
- ✅ Keyboard navigation for all interactive elements
- ✅ Focus indicators visible and clear
- ✅ Color contrast ratio ≥ 4.5:1 for text
- ✅ Alt text for all images
- ✅ ARIA labels for icon-only buttons
- ✅ Semantic HTML structure
- ✅ Screen reader compatibility

**PrimeVue Accessibility:**
- Built-in ARIA attributes
- Keyboard navigation support
- Focus management
- Screen reader announcements

### 13.2 Responsive Design Breakpoints

```css
/* Tailwind breakpoints (matching PrimeVue) */
sm: 640px    /* Small devices (phones) */
md: 768px    /* Medium devices (tablets) */
lg: 1024px   /* Large devices (laptops) */
xl: 1280px   /* Extra large devices (desktops) */
2xl: 1536px  /* 2X large devices (large desktops) */
```

**Mobile-First Approach:**
- Base styles for mobile (320px+)
- Progressive enhancement for larger screens
- Touch-friendly targets (44x44px minimum)
- Swipe gestures for mobile navigation

---

## 14. Security Considerations

### 14.1 Frontend Security Checklist

- ✅ **XSS Prevention**: Vue's automatic escaping, DOMPurify for user HTML
- ✅ **CSRF Protection**: SameSite cookies for refresh tokens
- ✅ **Secure Storage**: Tokens in localStorage (short-lived), refresh in HttpOnly cookie
- ✅ **Input Validation**: Client-side validation + server-side enforcement
- ✅ **Content Security Policy**: Restrict script sources
- ✅ **Subresource Integrity**: Hash-based script verification
- ✅ **HTTPS Only**: Strict-Transport-Security header
- ✅ **Sensitive Data**: No passwords or secrets in localStorage/sessionStorage

### 14.2 Content Security Policy

```html
<!-- index.html -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline'; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data: https:; 
               font-src 'self' data:; 
               connect-src 'self' https://api.anki-compendium.example.com;">
```

---

## 15. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| First Contentful Paint | < 1.5s | Lighthouse |
| Largest Contentful Paint | < 2.5s | Lighthouse |
| Time to Interactive | < 3.5s | Lighthouse |
| Cumulative Layout Shift | < 0.1 | Lighthouse |
| Bundle Size (gzipped) | < 500KB | vite-bundle-visualizer |
| API Response (avg) | < 200ms | Browser DevTools |
| PDF Render (first page) | < 2s | Custom metrics |

---

## 16. Monitoring & Analytics

### 16.1 Error Tracking (Future: Sentry)

```typescript
// main.ts
import * as Sentry from '@sentry/vue'

if (import.meta.env.PROD) {
  Sentry.init({
    app,
    dsn: import.meta.env.VITE_SENTRY_DSN,
    integrations: [
      new Sentry.BrowserTracing({
        routingInstrumentation: Sentry.vueRouterInstrumentation(router)
      })
    ],
    tracesSampleRate: 0.2,
    environment: import.meta.env.VITE_ENVIRONMENT
  })
}
```

### 16.2 User Analytics (Future: Plausible/Matomo)

```typescript
// Lightweight, privacy-friendly analytics
// Track:
// - Page views
// - Upload success/failure rates
// - Job completion times
// - Deck download counts
```

---

## 17. Migration Path to PWA (Phase 2)

### 17.1 PWA Features (Deferred)

**Phase 2 Additions:**
- ✅ Service Worker for offline caching
- ✅ Web App Manifest for installability
- ✅ Push Notifications for job completion
- ✅ Background Sync for offline uploads
- ✅ Add to Home Screen prompt

**Implementation Plan:**
1. Install `vite-plugin-pwa`
2. Configure service worker with Workbox
3. Define caching strategies (network-first for API, cache-first for assets)
4. Implement push notification subscription flow
5. Test offline functionality

---

## 18. Development Workflow

### 18.1 Git Workflow

```
main (production)
  ↓
develop (staging)
  ↓
feature/upload-ui
feature/job-polling
feature/deck-management
```

**Branch Naming:**
- `feature/[task-name]` - New features
- `bugfix/[issue-name]` - Bug fixes
- `hotfix/[critical-issue]` - Production hotfixes

**Commit Messages:**
```
feat: add PDF page selection component
fix: resolve job polling memory leak
docs: update API integration guide
test: add unit tests for auth store
chore: upgrade PrimeVue to 4.1.0
```

### 18.2 CI/CD Pipeline

```yaml
# .github/workflows/frontend-ci.yml
name: Frontend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'frontend/**'
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: frontend
        run: npm ci
      
      - name: Lint
        run: npm run lint
      
      - name: Type check
        run: npm run type-check
      
      - name: Unit tests
        run: npm run test:unit -- --coverage
      
      - name: Build
        run: npm run build
      
      - name: E2E tests
        run: npm run test:e2e
  
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker image
        run: docker build -t anki-frontend:${{ github.sha }} .
      
      - name: Push to registry
        run: docker push anki-frontend:${{ github.sha }}
      
      - name: Deploy to Kubernetes
        run: kubectl set image deployment/frontend frontend=anki-frontend:${{ github.sha }}
```

---

## 19. Package.json Scripts

```json
{
  "name": "anki-compendium-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview",
    "test:unit": "vitest run",
    "test:unit:watch": "vitest",
    "test:e2e": "playwright test",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore",
    "type-check": "vue-tsc --noEmit -p tsconfig.app.json --composite false",
    "format": "prettier --write src/"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.0",
    "primevue": "^4.0.0",
    "primeicons": "^7.0.0",
    "@primevue/themes": "^4.0.0",
    "axios": "^1.6.0",
    "vue-pdf-embed": "^2.0.0",
    "vee-validate": "^4.12.0",
    "@vee-validate/zod": "^4.12.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "@vue/test-utils": "^2.4.0",
    "vite": "^5.2.0",
    "vitest": "^1.5.0",
    "vue-tsc": "^2.0.0",
    "typescript": "^5.4.0",
    "@playwright/test": "^1.43.0",
    "@types/node": "^20.12.0",
    "eslint": "^8.57.0",
    "eslint-plugin-vue": "^9.25.0",
    "prettier": "^3.2.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

---

## 20. Critical Success Factors

### ✅ Must-Have for MVP
1. **Authentication**: Keycloak OAuth2 login/register flow
2. **PDF Upload**: Drag-drop + file browser with validation
3. **PDF Preview**: Page-by-page viewing with PDF.js
4. **Page Selection**: Multi-select interface for page range
5. **Job Status**: Real-time polling with progress updates
6. **Deck Download**: One-click .apkg file download
7. **Responsive Design**: Mobile, tablet, desktop layouts
8. **Error Handling**: User-friendly error messages
9. **Loading States**: Spinners, skeletons, progress bars
10. **TypeScript**: Full type safety across codebase

### ⚠️ Nice-to-Have (Phase 2)
- PWA installability
- Push notifications
- Offline mode
- WebSocket real-time updates
- AnkiConnect integration
- Advanced statistics dashboard

---

## 21. Implementation Timeline

### Week 1: Foundation
- ✅ Project scaffolding (Vite + Vue 3 + TypeScript)
- ✅ Install dependencies (PrimeVue, Axios, Pinia, etc.)
- ✅ Configure Tailwind CSS + PrimeVue theming
- ✅ Setup API client with interceptors
- ✅ Authentication store + composables
- ✅ Routing with guards

### Week 2: Core Features
- ✅ Login/Register pages with VeeValidate
- ✅ Dashboard layout with navigation
- ✅ PDF upload component with drag-drop
- ✅ PDF viewer integration (vue-pdf-embed)
- ✅ Page selection UI

### Week 3: Job Management
- ✅ Job status polling composable
- ✅ Job list page with filtering
- ✅ Job detail page with progress tracking
- ✅ Deck download functionality
- ✅ Error handling and retry logic

### Week 4: Polish & Deploy
- ✅ Responsive design refinements
- ✅ Accessibility audit and fixes
- ✅ Unit + integration tests
- ✅ E2E test suite (Playwright)
- ✅ Production build optimization
- ✅ Docker containerization
- ✅ Kubernetes deployment

---

## 22. Dependencies List

### Core Dependencies
```json
{
  "vue": "^3.4.21",
  "vue-router": "^4.3.0",
  "pinia": "^2.1.7",
  "primevue": "^4.0.0",
  "primeicons": "^7.0.0",
  "@primevue/themes": "^4.0.0",
  "axios": "^1.6.8",
  "vue-pdf-embed": "^2.0.0",
  "vee-validate": "^4.12.6",
  "@vee-validate/zod": "^4.12.6",
  "zod": "^3.22.4"
}
```

### Development Dependencies
```json
{
  "@vitejs/plugin-vue": "^5.0.4",
  "@vue/test-utils": "^2.4.5",
  "vite": "^5.2.8",
  "vitest": "^1.5.0",
  "vue-tsc": "^2.0.11",
  "typescript": "^5.4.5",
  "@playwright/test": "^1.43.1",
  "@types/node": "^20.12.7",
  "eslint": "^8.57.0",
  "eslint-plugin-vue": "^9.25.0",
  "@typescript-eslint/parser": "^7.7.0",
  "@typescript-eslint/eslint-plugin": "^7.7.0",
  "prettier": "^3.2.5",
  "tailwindcss": "^3.4.3",
  "autoprefixer": "^10.4.19",
  "postcss": "^8.4.38"
}
```

---

## 23. Conclusion

This frontend architecture provides a **production-ready blueprint** for rapid deployment of the Anki Compendium Vue.js application. Key architectural decisions prioritize:

1. **Stability** over bleeding-edge features
2. **Developer experience** with TypeScript and modern tooling
3. **Maintainability** through clear structure and patterns
4. **Performance** via code splitting and optimization
5. **Scalability** with modular components and state management

### Next Steps for @developer:

1. **Initialize Project**: `npm create vite@latest frontend -- --template vue-ts`
2. **Install Dependencies**: Follow package.json above
3. **Configure Tools**: Setup Tailwind, PrimeVue, Axios, Pinia
4. **Implement Auth Flow**: Login/Register pages + guards
5. **Build Upload Feature**: PDF upload + preview + page selection
6. **Integrate Job Polling**: Status tracking + notifications
7. **Create Deck Management**: List, download, statistics
8. **Test & Deploy**: Unit tests, E2E tests, Docker build

**This architecture is ready for implementation. No additional design decisions required.**

---

**Document Status**: ✅ **APPROVED FOR IMPLEMENTATION**  
**Approved By**: Architect Agent  
**Date**: 2025-11-23  
**Version**: 1.0
