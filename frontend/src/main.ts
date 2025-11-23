import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import Tooltip from 'primevue/tooltip'

import App from './App.vue'
import router from './router'

// Import PrimeVue styles
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'

// Import custom styles
import './assets/styles/main.css'

const app = createApp(App)

// Pinia state management
const pinia = createPinia()
app.use(pinia)

// Vue Router
app.use(router)

// PrimeVue with Aura theme
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.dark-mode',
      cssLayer: {
        name: 'primevue',
        order: 'primevue'
      }
    }
  }
})

// PrimeVue services
app.use(ToastService)
app.use(ConfirmationService)

// PrimeVue directives
app.directive('tooltip', Tooltip)

// Mount the app
app.mount('#app')
