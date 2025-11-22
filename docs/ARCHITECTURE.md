# Anki Compendium - System Architecture

## 1. Overview

Anki Compendium is a Progressive Web Application that transforms academic documents (primarily PDFs) into high-quality Anki flashcard decks using AI-powered RAG (Retrieval-Augmented Generation) pipelines.

### Target Audience
- **Primary**: University students (international)
- **Scale**: Initially small, designed to scale on-demand
- **Business Model**: Freemium with ads, paid tier for ad removal and increased limits

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Vue.js PWA)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ PDF Preview  │  │  Dashboard   │  │  Settings/Profile    │  │
│  │  (PDF.js)    │  │              │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────┬────────────────────────────────────────────────────┘
             │ HTTPS/REST API
┌────────────▼────────────────────────────────────────────────────┐
│                      API Gateway / Backend                       │
│                         (Python/FastAPI)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │     Auth     │  │  Upload API  │  │    Job Status API    │  │
│  │  (Keycloak)  │  │              │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────┬───────────────────┬─────────────────────┬──────────────┘
         │                   │                     │
         ├───────────────────┼─────────────────────┤
         ▼                   ▼                     ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   PostgreSQL    │  │    RabbitMQ      │  │   MinIO (S3)     │
│   (Metadata)    │  │  (Job Queue)     │  │  (PDF + .apkg)   │
└─────────────────┘  └────────┬─────────┘  └──────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │   Worker Processes   │
                    │    (Python/Celery)   │
                    │  ┌────────────────┐  │
                    │  │  RAG Pipeline  │  │
                    │  │  - Extraction  │  │
                    │  │  - Chunking    │  │
                    │  │  - Topic Ext.  │  │
                    │  │  - Q&A Gen.    │  │
                    │  │  - Card Gen.   │  │
                    │  └────────────────┘  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Gemini API         │
                    │   (Google AI)        │
                    └──────────────────────┘
```

### 2.2 Component Breakdown

#### Frontend (Vue.js 3 + PWA)
- **Framework**: Vue.js 3 with Composition API
- **UI Library**: TBD (Vuetify / PrimeVue / Tailwind CSS)
- **PDF Rendering**: PDF.js for client-side preview
- **State Management**: Pinia
- **PWA Features**:
  - Service Worker for offline capabilities
  - Web Push Notifications for job completion
  - Add to Home Screen manifest
  - Responsive design (mobile-first)

#### Backend API (Python + FastAPI)
- **Framework**: FastAPI (async, high-performance)
- **Authentication**: Integration with Keycloak (OAuth2/OIDC)
- **API Features**:
  - RESTful endpoints for CRUD operations
  - File upload with multipart/form-data
  - WebSocket for real-time job status (optional, V2)
  - Rate limiting middleware (30 cards/month for free tier)
  - Admin backoffice API for settings management

#### Authentication (Keycloak)
- **Deployment**: Self-hosted on K8s
- **Providers**:
  - Email/Password (native)
  - OAuth: Google, GitHub
- **Features**:
  - User registration and login
  - Token-based authentication (JWT)
  - Role-based access control (user, admin)

#### Database (PostgreSQL)
- **Schema**:
  - `users` - User accounts and profiles
  - `decks` - Generated deck metadata
  - `jobs` - PDF processing job queue status
  - `settings` - Global admin settings (chunk size, overlap, Gemini models)
  - `subscriptions` - User tier and limits tracking
  - `audit_logs` - Activity tracking for GDPR compliance

#### Message Queue (RabbitMQ)
- **Purpose**: Asynchronous job processing
- **Queues**:
  - `pdf_processing` - Main processing queue
  - `card_generation` - Card generation tasks
  - `notifications` - Push notification delivery
- **Features**:
  - Dead letter queue for failed jobs
  - Manual retry capability
  - Job priority support

#### Object Storage (MinIO)
- **Deployment**: Self-hosted on K8s
- **Buckets**:
  - `pdfs` - Original uploaded PDFs (temporary, deleted after processing)
  - `decks` - Generated .apkg files (persistent until account deletion)
- **Features**:
  - S3-compatible API
  - Pre-signed URLs for secure download
  - Lifecycle policies for auto-cleanup

#### Worker Processes (Celery)
- **Framework**: Celery with RabbitMQ backend
- **Concurrency**: Multi-process workers (configurable)
- **Tasks**:
  - PDF text extraction
  - RAG pipeline execution
  - Card generation and .apkg creation
  - Notification dispatch

#### RAG Pipeline
- **Vector Database**: pgvector (PostgreSQL extension) or ChromaDB self-hosted
- **Embeddings**: Google Gemini Embeddings API
- **Pipeline Stages**:
  1. **Extraction/Recursion**: Extract text from PDF pages
  2. **Chunking**: Split text (500 tokens, 20% overlap, configurable)
  3. **Topic Extraction**: Identify main topics and subtopics
  4. **Topic Refinement**: Improve topic hierarchy
  5. **Tag Generation**: Generate relevant tags for cards
  6. **Question Generation**: Generate Q&A pairs
  7. **Question Answering**: Validate and refine answers
  8. **Card Generation**: Create Anki Basic cards (front/back)

#### Gemini Integration
- **Models**:
  - Gemini 1.5 Flash: Chunking, topic extraction, Q&A generation
  - Gemini 1.5 Pro: Final refinement (optional, configurable)
- **Settings**: Admin-configurable model selection per pipeline stage
- **Rate Limiting**: Track API usage per user for billing

#### Anki Export
- **Format**: .apkg (Anki package format)
- **Library**: `genanki` (Python) for programmatic deck creation
- **Note Type**: Basic (Front/Back)
- **Card Quality**:
  - Answers: 2-10 sentences
  - Atomic facts (minimum information principle)
  - User-configurable density via prompt settings

---

## 3. Data Flow

### 3.1 PDF Upload & Processing Flow

```
User uploads PDF → Frontend validates size → Backend API receives file
  → Save to MinIO (pdfs bucket)
  → Create job entry in PostgreSQL
  → Enqueue job to RabbitMQ
  → Return job_id to user
  
Worker picks up job → Download PDF from MinIO
  → Extract text from selected pages
  → Execute RAG pipeline (8 stages)
  → Generate Anki cards with genanki
  → Save .apkg to MinIO (decks bucket)
  → Update job status in PostgreSQL
  → Trigger push notification
  → Delete original PDF from MinIO
```

### 3.2 Download Flow

```
User requests deck download → Backend verifies ownership
  → Generate pre-signed MinIO URL (15 min expiry)
  → Return download link to frontend
  → User downloads .apkg file
```

### 3.3 AnkiConnect Integration (V1)

```
User clicks "Open in Anki" → Frontend calls AnkiConnect API (localhost:8765)
  → Send deck data via addNote API
  → Display success/error message
```

---

## 4. Tech Stack Summary

### Frontend
- **Framework**: Vue.js 3
- **Build Tool**: Vite
- **PDF Rendering**: PDF.js
- **HTTP Client**: Axios
- **PWA**: Vite PWA Plugin
- **UI**: TBD (Vuetify/PrimeVue/Tailwind)

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Task Queue**: Celery + RabbitMQ
- **ORM**: SQLAlchemy
- **Migration**: Alembic
- **Validation**: Pydantic
- **PDF Extraction**: PyMuPDF (fitz) or pdfplumber
- **Anki Export**: genanki
- **AI**: Google Gemini API (via official SDK)

### Infrastructure
- **Container Runtime**: Docker
- **Orchestration**: Kubernetes (OVH Managed)
- **IaC**: Helm Charts
- **Database**: PostgreSQL 15+
- **Message Queue**: RabbitMQ
- **Object Storage**: MinIO (S3-compatible)
- **Authentication**: Keycloak
- **Reverse Proxy**: Nginx Ingress Controller
- **TLS**: cert-manager + Let's Encrypt

### Development
- **Local Dev**: Docker Compose
- **CI/CD**: GitHub Actions
- **Version Control**: Git + GitHub
- **Linting**: Ruff (Python), ESLint (Vue.js)
- **Testing**: pytest (backend), Vitest (frontend)

---

## 5. Deployment Architecture

### 5.1 Kubernetes Cluster Layout

```
OVH Managed Kubernetes Cluster
├── Namespace: anki-compendium-prod
│   ├── Deployment: frontend (Vue.js PWA)
│   ├── Deployment: backend-api (FastAPI)
│   ├── Deployment: worker (Celery workers)
│   ├── StatefulSet: postgresql
│   ├── StatefulSet: rabbitmq
│   ├── StatefulSet: minio
│   ├── Deployment: keycloak
│   ├── Service: frontend-svc (ClusterIP)
│   ├── Service: backend-svc (ClusterIP)
│   ├── Service: postgresql-svc (ClusterIP)
│   ├── Service: rabbitmq-svc (ClusterIP)
│   ├── Service: minio-svc (ClusterIP)
│   ├── Service: keycloak-svc (ClusterIP)
│   ├── Ingress: main-ingress (HTTPS termination)
│   └── PersistentVolumeClaim: postgres-data, minio-data, rabbitmq-data
```

### 5.2 Helm Chart Structure

```
charts/
├── anki-compendium/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── frontend-deployment.yaml
│   │   ├── backend-deployment.yaml
│   │   ├── worker-deployment.yaml
│   │   ├── postgresql-statefulset.yaml
│   │   ├── rabbitmq-statefulset.yaml
│   │   ├── minio-statefulset.yaml
│   │   ├── keycloak-deployment.yaml
│   │   ├── ingress.yaml
│   │   ├── services.yaml
│   │   ├── configmaps.yaml
│   │   ├── secrets.yaml
│   │   └── pvcs.yaml
│   └── values/
│       ├── values-dev.yaml
│       ├── values-staging.yaml
│       └── values-prod.yaml
```

---

## 6. Security & Compliance

### 6.1 Data Protection
- **GDPR Compliance**:
  - User consent checkbox for PDF uploads
  - No sensitive data in PDFs (user responsibility)
  - Right to erasure (delete account → delete all data)
  - Audit logs for data access
- **Storage**:
  - PDFs deleted after processing
  - Decks stored until account deletion
  - No long-term retention of raw PDFs

### 6.2 Authentication & Authorization
- OAuth2/OIDC via Keycloak
- JWT tokens with short expiry (15 min access, 7 day refresh)
- RBAC for admin backoffice access

### 6.3 API Security
- Rate limiting per user (IP + user_id)
- Input validation (file size, file type, page range)
- CORS policy (whitelist frontend domain)
- HTTPS only (TLS 1.2+)

### 6.4 Monitoring & Logging
- Centralized logging (ready for Sentry integration)
- Audit logs for critical operations
- No sensitive data in logs (GDPR compliance)

---

## 7. Scalability & Performance

### 7.1 Horizontal Scaling
- **Frontend**: Stateless, scale via K8s replicas
- **Backend API**: Stateless, scale via K8s replicas
- **Workers**: Scale Celery workers based on queue depth
- **Database**: PostgreSQL connection pooling (PgBouncer)
- **Storage**: MinIO distributed mode (future)

### 7.2 Performance Optimizations
- **PDF Processing**: Parallel processing with multi-threaded workers
- **Caching**: Redis for API response caching (future)
- **CDN**: CloudFlare for static assets (future)
- **Database**: Indexed queries, connection pooling

### 7.3 Resource Limits
- **PDF Upload**: 100 MB max per file
- **Processing**: Best-effort, deferred with notifications
- **Concurrency**: Configurable Celery worker count

---

## 8. Monitoring & Observability

### 8.1 Metrics (Future)
- Prometheus + Grafana for infrastructure metrics
- Custom metrics: jobs/min, success rate, avg processing time

### 8.2 Logging
- Structured JSON logging
- Centralized aggregation (ready for Sentry)
- Log retention: 30 days

### 8.3 Alerting (Future)
- High error rate
- Queue depth threshold
- Worker health checks

---

## 9. Cost Estimation

### Monthly Costs (Estimated)
- **OVH Kubernetes**: €20-30/month (small cluster)
- **Gemini API**: Variable (pay-per-use, depends on volume)
- **Domain + SSL**: €10/year (negligible monthly)
- **Sentry (if used)**: Free tier initially
- **Total**: ~€50/month budget

---

## 10. Future Enhancements (Post-MVP)

### V2 Features
- Support for EPUB, Markdown, DOCX, Web pages
- Video transcription (YouTube)
- PPTX extraction
- AnkiWeb sync integration
- Interactive deck preview
- Card editor in-app
- Shared decks marketplace
- Advanced statistics dashboard

### Technical Improvements
- WebSocket for real-time processing status
- GraphQL API (alternative to REST)
- Multi-region deployment
- CDN integration
- Advanced caching strategies
- A/B testing framework

---

## 11. Development Phases

### Phase 1: MVP (Current Focus)
- ✅ Architecture definition
- 🔄 Monorepo setup
- 🔄 Docker Compose local environment
- 🔄 Basic frontend (PDF upload + preview)
- 🔄 Backend API (upload, auth, job management)
- 🔄 RAG pipeline implementation
- 🔄 Anki export (.apkg generation)
- 🔄 Keycloak integration
- 🔄 Basic deployment to K8s

### Phase 2: Polish & Launch
- Payment integration (Stripe)
- Ads integration (Google AdSense)
- User dashboard with statistics
- Admin backoffice for settings
- Performance optimizations
- Beta testing with students

### Phase 3: Growth
- Additional document formats
- Community features (shared decks)
- Mobile app (React Native or Flutter)
- Advanced analytics
- Referral program

---

## 12. References

- [Anki Manual](https://docs.ankiweb.net/)
- [AnkiConnect API](https://foosoft.net/projects/anki-connect/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue.js Guide](https://vuejs.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Helm Documentation](https://helm.sh/docs/)
- [Google Gemini API](https://ai.google.dev/docs)

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-22  
**Author**: Project Manager Agent
