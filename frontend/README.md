# Anki Compendium - Frontend

Vue 3 + TypeScript + Vite frontend for the Anki Compendium application.

## Tech Stack

- **Framework**: Vue 3.5+ with Composition API
- **Build Tool**: Vite 7.x
- **Language**: TypeScript (strict mode)
- **UI Library**: PrimeVue 4.4 + PrimeIcons + PrimeFlex
- **Styling**: Tailwind CSS 3.x
- **State Management**: Pinia 2.3
- **Routing**: Vue Router 4.6
- **Form Validation**: VeeValidate 4.15 + Zod 3.25
- **HTTP Client**: Axios 1.13
- **PDF Viewer**: vue-pdf-embed 2.1
- **Package Manager**: pnpm

## Prerequisites

- Node.js 18+ or 20+
- pnpm 8+
- Backend API running (default: http://localhost:8000)

## Installation

```bash
# Install dependencies
pnpm install

# Copy environment variables
cp .env.example .env

# Edit .env if backend URL differs from default
```

## Development

```bash
# Start dev server (http://localhost:5173)
pnpm dev

# Type checking
pnpm type-check

# Linting
pnpm lint

# Format code
pnpm format
```

## Build

```bash
# Production build
pnpm build

# Preview production build
pnpm preview
```

## Testing

```bash
# Run unit tests
pnpm test:unit

# Run e2e tests
pnpm test:e2e

# Run all tests
pnpm test
```

## Project Structure

```
src/
├── api/              # API client and service functions
├── assets/           # Static assets (styles, images)
├── components/       # Vue components
│   ├── auth/        # Authentication components
│   ├── common/      # Shared/reusable components
│   ├── decks/       # Deck management components
│   ├── jobs/        # Job status components
│   └── pdf/         # PDF viewer components
├── composables/      # Vue composables (reusable logic)
├── layouts/          # Layout components
├── router/           # Vue Router configuration
├── stores/           # Pinia stores
├── types/            # TypeScript type definitions
├── utils/            # Utility functions
├── views/            # Page components
└── main.ts           # Application entry point
```

## Key Features

### Authentication
- JWT-based authentication with access/refresh tokens
- Automatic token refresh on 401 errors
- Protected routes with auth guards
- Login/Register forms with validation

### PDF Upload & Processing
- Drag-and-drop PDF upload
- Multi-file support
- Upload progress tracking
- Background job processing

### Deck Management
- View all generated decks
- Download decks as .apkg files
- Deck metadata display
- Delete decks

### Job Monitoring
- Real-time job status updates
- Progress tracking
- Error handling and retry
- Job history

## Environment Variables

```bash
VITE_API_BASE_URL=http://localhost:8000  # Backend API URL
```

## Architecture

### State Management (Pinia)
- **auth.ts**: User authentication state and token management
- Modular stores for each feature domain
- Type-safe with TypeScript

### Routing
- Declarative routes with Vue Router 4
- Navigation guards for authentication
- Lazy-loaded route components

### API Client
- Axios instance with interceptors
- Automatic token attachment
- Request/response transformation
- Error handling

### Form Validation
- VeeValidate + Zod schemas
- Type-safe validation
- Accessible error messages
- Async validation support

## Code Style

- **ESLint**: Vue 3 + TypeScript rules
- **Prettier**: Opinionated formatting
- **Composition API**: `<script setup>` syntax
- **TypeScript**: Strict mode enabled

## Component Naming

- **Views/Pages**: `*Page.vue` (e.g., `LoginPage.vue`)
- **Components**: PascalCase (e.g., `PdfViewer.vue`)
- **Composables**: `use*` (e.g., `useAuth.ts`)

## API Integration

Base URL is configured in `.env` and defaults to `http://localhost:8000`.

All API requests automatically:
- Include authentication token (if logged in)
- Refresh expired tokens
- Handle common errors (401, 403, 500)

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Follow Vue 3 Composition API best practices
2. Use TypeScript strict mode
3. Run linting and formatting before commits
4. Write unit tests for business logic
5. Update documentation for new features

## License

See root project LICENSE file.

## Related Documentation

- [Backend API Documentation](../backend/README.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Project Roadmap](../docs/ROADMAP.md)
