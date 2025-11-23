/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_MAX_FILE_SIZE: string
  readonly VITE_ALLOWED_FILE_TYPES: string
  readonly VITE_JOB_POLL_INTERVAL: string
  readonly VITE_JOB_POLL_MAX_INTERVAL: string
  readonly VITE_ENABLE_DEVTOOLS: string
  readonly VITE_KEYCLOAK_URL?: string
  readonly VITE_KEYCLOAK_REALM?: string
  readonly VITE_KEYCLOAK_CLIENT_ID?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
