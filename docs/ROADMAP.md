# Anki Compendium - Development Roadmap

## Overview

This document outlines the development phases for Anki Compendium, from MVP to future enhancements.

---

## Phase 1: Foundation & Setup ✅ (Current)

**Duration**: 1-2 weeks  
**Status**: In Progress

### Deliverables
- [x] System architecture documentation
- [x] Database schema design
- [x] RAG pipeline specification
- [x] Monorepo structure creation
- [ ] Docker Compose local environment
- [ ] Helm charts base structure
- [ ] CI/CD pipeline setup

### Success Criteria
- Complete documentation available
- Local development environment running
- CI/CD pipeline validates code on push

---

## Phase 2: Backend Core (MVP)

**Duration**: 3-4 weeks  
**Status**: Not Started

### Backend API
- [ ] FastAPI project setup
- [ ] Database models (SQLAlchemy)
- [ ] Alembic migrations
- [ ] Authentication integration (Keycloak)
- [ ] File upload endpoint (multipart/form-data)
- [ ] Job management endpoints (create, status, list)
- [ ] Deck download endpoint (pre-signed URLs)
- [ ] Admin settings API (CRUD)
- [ ] Rate limiting middleware
- [ ] Error handling and logging

### Worker & Job Queue
- [ ] Celery setup with RabbitMQ
- [ ] PDF extraction worker (PyMuPDF/pdfplumber)
- [ ] Basic RAG pipeline implementation
  - [ ] Stage 1: Extraction & Recursion
  - [ ] Stage 2: Chunking
  - [ ] Stage 3: Topic Extraction
  - [ ] Stage 4: Topic Refinement
  - [ ] Stage 5: Tag Generation
  - [ ] Stage 6: Question Generation
  - [ ] Stage 7: Question Answering
  - [ ] Stage 8: Card Generation
- [ ] Gemini API integration
- [ ] genanki integration (.apkg export)
- [ ] Job progress tracking
- [ ] Error handling and retry logic

### Storage & Infrastructure
- [ ] PostgreSQL schema implementation
- [ ] MinIO bucket setup
- [ ] RabbitMQ queue configuration
- [ ] Keycloak deployment and configuration

### Success Criteria
- User can register and authenticate
- User can upload PDF and create job
- Worker processes PDF and generates .apkg file
- User can download generated deck
- Admin can modify global settings

---

## Phase 3: Frontend (MVP)

**Duration**: 3-4 weeks  
**Status**: Not Started

### Core UI
- [ ] Vue.js 3 project setup (Vite)
- [ ] UI component library selection and setup
- [ ] Authentication pages (login, register, OAuth)
- [ ] Dashboard page (user decks, statistics)
- [ ] Profile/settings page

### PDF Upload & Preview
- [ ] PDF.js integration
- [ ] File upload component with drag-and-drop
- [ ] PDF page preview and selection UI
- [ ] Page range selector (interactive)
- [ ] Client-side PDF slicing (extract selected pages)
- [ ] Upload progress indicator

### Job Management
- [ ] Job creation flow
- [ ] Job status polling (real-time updates)
- [ ] Job history list
- [ ] Manual retry for failed jobs

### Deck Management
- [ ] Deck list view
- [ ] Deck download button
- [ ] "Open in Anki" button (AnkiConnect)
- [ ] Deck metadata display (card count, tags, date)

### PWA Features
- [ ] Service worker setup
- [ ] App manifest (Add to Home Screen)
- [ ] Web Push notification subscription
- [ ] Notification permission handling
- [ ] Offline fallback page

### Success Criteria
- User can upload PDF and select pages
- Real-time job status updates
- Download .apkg file works
- AnkiConnect integration functional
- PWA installable on mobile and desktop
- Push notifications delivered on job completion

---

## Phase 4: Deployment & Testing

**Duration**: 2 weeks  
**Status**: Not Started

### Kubernetes Deployment
- [ ] Helm chart finalization
- [ ] ConfigMaps and Secrets setup
- [ ] Ingress configuration (HTTPS)
- [ ] cert-manager setup (Let's Encrypt)
- [ ] Persistent volumes for PostgreSQL, MinIO
- [ ] Resource limits and requests tuning
- [ ] Horizontal Pod Autoscaler (HPA) configuration

### Testing & QA
- [ ] Backend unit tests (pytest)
- [ ] Frontend unit tests (Vitest)
- [ ] Integration tests (API + DB)
- [ ] End-to-end tests (Playwright)
- [ ] Smoke tests for critical paths
- [ ] Performance testing (load testing workers)
- [ ] Security audit (OWASP Top 10)

### Monitoring & Logging
- [ ] Structured logging (JSON)
- [ ] Centralized log aggregation (ready for Sentry)
- [ ] Healthcheck endpoints
- [ ] Basic metrics collection

### Success Criteria
- Application deployed to OVH Kubernetes
- HTTPS working with valid certificate
- All critical paths covered by tests
- Production logs centralized and queryable
- Performance benchmarks established

---

## Phase 5: Polish & Launch Preparation

**Duration**: 2-3 weeks  
**Status**: Not Started

### Features
- [ ] Admin backoffice UI (settings management)
- [ ] User statistics dashboard (cards generated, decks created)
- [ ] GDPR compliance features
  - [ ] Terms of service acceptance
  - [ ] Privacy policy
  - [ ] Account deletion flow
  - [ ] Data export functionality
- [ ] Email notifications (job completion, errors)
- [ ] Onboarding flow for new users
- [ ] Help/documentation pages

### Payment Integration (Premium Tier)
- [ ] Stripe integration (payment processing)
- [ ] Subscription management
- [ ] Upgrade/downgrade flow
- [ ] Invoice generation

### Ads Integration (Free Tier)
- [ ] Google AdSense integration
- [ ] Ad placement optimization
- [ ] Ad-free experience for premium users

### Beta Testing
- [ ] Recruit beta testers (university students)
- [ ] Feedback collection system
- [ ] Bug tracking and prioritization
- [ ] Iterative improvements based on feedback

### Success Criteria
- Payment flow fully functional
- Ads displayed for free tier users
- Beta testers provide positive feedback
- Major bugs identified and fixed
- Application ready for public launch

---

## Phase 6: Public Launch 🚀

**Duration**: 1 week  
**Status**: Not Started

### Launch Activities
- [ ] Domain and branding finalization
- [ ] Marketing materials (landing page, social media)
- [ ] Press kit and blog post
- [ ] Launch on Product Hunt, Hacker News
- [ ] University student communities outreach
- [ ] Analytics setup (Google Analytics, Mixpanel)

### Post-Launch Support
- [ ] Monitor error rates and performance
- [ ] Rapid bug fixes
- [ ] User support (email, Discord, etc.)
- [ ] Collect feature requests

### Success Criteria
- 100+ registered users in first week
- <1% error rate in production
- Positive user reviews and feedback
- Payment conversions (if applicable)

---

## Phase 7: Post-MVP Enhancements

**Duration**: Ongoing  
**Status**: Not Started

### Additional Document Formats
- [ ] EPUB support
- [ ] Markdown support
- [ ] DOCX support
- [ ] Web page scraping
- [ ] PPTX support
- [ ] YouTube video transcription

### Advanced Card Types
- [ ] Cloze deletion cards
- [ ] Image occlusion cards
- [ ] Reversed cards (bidirectional)

### Collaboration Features
- [ ] Shared decks marketplace
- [ ] Deck rating and reviews
- [ ] User profiles (public decks)
- [ ] Social features (follow, like, comment)

### AnkiWeb Integration
- [ ] Sync decks to AnkiWeb
- [ ] Import decks from AnkiWeb
- [ ] Two-way synchronization

### Advanced Features
- [ ] Interactive deck preview (swipe through cards)
- [ ] In-app card editor
- [ ] Advanced statistics dashboard
- [ ] Spaced repetition analytics
- [ ] Custom note types
- [ ] Batch processing (multiple PDFs)
- [ ] Scheduled deck generation (recurring jobs)

### Performance & Scale
- [ ] Redis caching layer
- [ ] CDN for static assets (CloudFlare)
- [ ] Multi-region deployment
- [ ] Distributed MinIO (multi-node)
- [ ] Database read replicas
- [ ] GraphQL API (alternative to REST)

### Monitoring & Observability
- [ ] Prometheus + Grafana
- [ ] Sentry integration (error tracking)
- [ ] Advanced alerting (PagerDuty)
- [ ] A/B testing framework
- [ ] Feature flags (LaunchDarkly)

---

## Success Metrics (KPIs)

### MVP Success
- 500+ registered users in first month
- 1000+ decks generated
- <5% error rate
- Average processing time <5 minutes per deck
- 10+ premium subscribers

### Long-Term Goals (6-12 months)
- 10,000+ active users
- 50,000+ decks generated
- 99.9% uptime
- <2 minute average processing time
- 5% conversion rate (free to premium)
- Break-even on infrastructure costs

---

## Risk Management

### Technical Risks
- **Gemini API rate limits**: Mitigate with rate limiting, caching, fallback models
- **Worker performance bottlenecks**: Scale horizontally, optimize pipeline
- **Storage costs**: Implement lifecycle policies, cleanup old data
- **GDPR compliance**: Regular audits, legal consultation

### Business Risks
- **Low user adoption**: Marketing, user research, feature pivots
- **High churn rate**: Improve onboarding, card quality, support
- **Payment fraud**: Stripe fraud detection, manual review
- **Competition**: Differentiate with quality, UX, community

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-22 | Use Python for backend (not Rust/Go) | Faster development, rich ML/AI ecosystem |
| 2025-11-22 | Self-host MinIO on K8s | Cost control, data sovereignty |
| 2025-11-22 | Use Helm charts (not Terraform) | Kubernetes-native, easier templating |
| 2025-11-22 | MVP: PDF only | Focus on core use case, faster launch |
| 2025-11-22 | Free tier: 30 cards/month | Generous enough for trial, incentivizes upgrade |

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-22  
**Maintained By**: Project Manager Agent
