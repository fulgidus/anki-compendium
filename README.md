# Anki Compendium

AI-powered progressive web app that transforms academic documents into high-quality Anki flashcard decks. Built for university students worldwide, Anki Compendium uses advanced RAG (Retrieval-Augmented Generation) pipelines powered by Google Gemini to create expertly crafted flashcards optimized for spaced repetition learning.

---

## ✨ Features

### MVP (V1)
- 📄 **PDF Processing**: Upload PDFs and select specific page ranges for card generation
- 🔍 **Intelligent Extraction**: 8-stage RAG pipeline for high-quality card generation
- 🎯 **Customizable Output**: Configure card density, language, and generation instructions
- 📥 **Anki Integration**: Download `.apkg` files or open directly in Anki Desktop via AnkiConnect
- 🔐 **Secure Authentication**: Email/password + OAuth (Google, GitHub) via Keycloak
- 💳 **Freemium Model**: 30 cards/month free, premium tier for unlimited usage
- 📱 **Progressive Web App**: Install on any device with offline capabilities
- 🔔 **Push Notifications**: Get notified when your deck is ready

### Planned (V2+)
- 📚 Support for EPUB, Markdown, DOCX, web pages, PPTX
- 🎥 YouTube video transcription and card generation
- 🌐 AnkiWeb synchronization
- 📊 Advanced statistics dashboard
- 🎨 Interactive deck preview and card editor
- 🤝 Shared decks marketplace

---

## 🏗️ Architecture

### High-Level Overview

```
Frontend (Vue.js PWA) 
    ↓ REST API
Backend (Python/FastAPI)
    ↓
┌──────────┬──────────┬──────────┐
│PostgreSQL│ RabbitMQ │  MinIO   │
└──────────┴──────────┴──────────┘
    ↓
Worker Processes (Celery)
    ↓
RAG Pipeline → Gemini API → .apkg Export
```

### Tech Stack

**Frontend**
- Vue.js 3 + Vite
- PDF.js for client-side preview
- Pinia for state management
- PWA with service workers

**Backend**
- Python 3.11+ with FastAPI
- Celery + RabbitMQ for async processing
- SQLAlchemy + Alembic for database
- genanki for Anki deck generation
- Google Gemini API for AI processing

**Infrastructure**
- PostgreSQL 15+ (metadata & settings)
- RabbitMQ (job queue)
- MinIO (S3-compatible storage)
- Keycloak (authentication)
- Kubernetes (OVH managed)
- Helm charts for deployment

**Development**
- Monorepo structure
- Docker Compose for local dev
- GitHub Actions for CI/CD
- pytest + Vitest for testing

---

## 📖 Documentation

- [**Architecture**](./docs/ARCHITECTURE.md) - Complete system design and component breakdown
- [**Database Schema**](./docs/DATABASE_SCHEMA.md) - PostgreSQL table definitions and relationships
- [**RAG Pipeline**](./docs/RAG_PIPELINE.md) - AI-powered card generation process

---

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Kubernetes cluster (for production deployment)

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/anki-compendium.git
cd anki-compendium

# Start all services with Docker Compose
docker-compose -f infra/docker-compose/docker-compose.dev.yml up -d

# Frontend development (separate terminal)
cd frontend
npm install
npm run dev

# Backend development (separate terminal)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Configuration

Create `.env` files in both `frontend/` and `backend/` directories. See `.env.example` for required variables.

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test

# Smoke tests
pytest tests/smoke/ -v
```

---

## 🚢 Deployment

### Production Deployment (Kubernetes)

```bash
# Build and push Docker images
docker build -t anki-compendium-frontend:latest ./frontend
docker build -t anki-compendium-backend:latest ./backend
docker push <your-registry>/anki-compendium-frontend:latest
docker push <your-registry>/anki-compendium-backend:latest

# Deploy with Helm
helm upgrade --install anki-compendium ./infra/helm/anki-compendium \
  --namespace anki-compendium \
  --values ./infra/helm/anki-compendium/values/values-prod.yaml
```

---

## 🤝 Contributing

This is currently a personal hobby project. Contributions, issues, and feature requests are welcome once the MVP is complete.

---

## 📋 Project Status

🚧 **Current Phase**: MVP Development

- [x] Architecture design
- [x] Database schema definition
- [x] RAG pipeline specification
- [ ] Monorepo setup
- [ ] Docker Compose environment
- [ ] Backend API implementation
- [ ] Frontend UI development
- [ ] RAG pipeline implementation
- [ ] Kubernetes deployment

---

## 📄 License

TBD

---

## 🙏 Acknowledgments

- [Anki](https://apps.ankiweb.net/) - The spaced repetition software that inspired this project
- [Google Gemini](https://ai.google.dev/) - AI models powering the card generation
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Vue.js](https://vuejs.org/) - Progressive JavaScript framework

---

**Made with ❤️ for students everywhere**
