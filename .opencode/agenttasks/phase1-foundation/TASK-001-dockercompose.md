---
task_id: "TASK-001-DOCKERCOMPOSE"
title: "Setup Docker Compose Development Environment"
phase: "Phase 1: Foundation"
complexity: "medium"
estimated_duration: "4-6 hours"
assigned_to: "devops-engineer"
dependencies: []
status: "pending"
priority: "high"
created_at: "2025-11-22"
---

# Task: Setup Docker Compose Development Environment

## Objective
Create a complete Docker Compose configuration for local development that includes all required services (PostgreSQL, RabbitMQ, MinIO, Keycloak) and allows developers to work on frontend and backend independently.

## Context
This is the foundation for local development. Developers need a one-command setup to start all infrastructure services without complex manual configuration.

## Requirements

### Functional Requirements
1. Single `docker-compose up` command starts all services
2. Services accessible on predictable ports (localhost)
3. Data persistence across container restarts
4. Environment variables externalized via `.env` files
5. Health checks for all services
6. Service dependencies properly configured (wait-for-it pattern)

### Technical Requirements
1. **PostgreSQL 15+**
   - Port: 5432
   - Database: `anki_compendium_dev`
   - User/password configurable via .env
   - Volume for data persistence
   - pgvector extension enabled (for RAG)

2. **RabbitMQ 3.12+**
   - Port: 5672 (AMQP), 15672 (Management UI)
   - Default queues created on startup
   - Volume for data persistence
   - Management plugin enabled

3. **MinIO (Latest)**
   - Port: 9000 (API), 9001 (Console)
   - Default buckets: `pdfs`, `decks`
   - Access key/secret configurable via .env
   - Volume for data persistence

4. **Keycloak 23+**
   - Port: 8080
   - Realm: `anki-compendium`
   - Admin user configurable via .env
   - PostgreSQL backend (shared with main DB or separate)
   - OAuth providers: Google, GitHub (config via env)

5. **Network Configuration**
   - All services on same Docker network
   - Service discovery via container names
   - Expose necessary ports to host

### Non-Functional Requirements
- Fast startup time (<60 seconds for all services)
- Clear logging output
- Graceful shutdown
- Resource limits defined (prevent localhost freeze)

## File Structure

```
infra/docker-compose/
├── docker-compose.dev.yml          # Main compose file
├── docker-compose.override.yml.example  # Optional overrides template
├── .env.example                    # Environment variables template
├── init-scripts/
│   ├── postgres/
│   │   └── 01-init-db.sql         # Initial DB setup, extensions
│   ├── rabbitmq/
│   │   └── init-queues.sh         # Create default queues
│   ├── minio/
│   │   └── init-buckets.sh        # Create default buckets
│   └── keycloak/
│       └── realm-export.json       # Realm configuration
└── README.md                       # Setup instructions
```

## Acceptance Criteria

### Must Have
- [ ] All services start with `docker-compose up -d`
- [ ] PostgreSQL accessible at `localhost:5432`
- [ ] RabbitMQ Management UI accessible at `http://localhost:15672`
- [ ] MinIO Console accessible at `http://localhost:9001`
- [ ] Keycloak admin console accessible at `http://localhost:8080`
- [ ] All services have health checks that report status
- [ ] Data persists across `docker-compose down` (without `-v` flag)
- [ ] `.env.example` file documents all required variables
- [ ] README.md explains setup process clearly

### Nice to Have
- [ ] Docker Compose profiles for partial service startup (e.g., only DB + queue)
- [ ] Automatic database migrations on startup (Alembic)
- [ ] Pre-configured OAuth apps in Keycloak for Google/GitHub
- [ ] Sample data seeding script (test users, settings)

## Technical Specifications

### Docker Compose Example Structure

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts/postgres:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ... other services

volumes:
  postgres_data:
  rabbitmq_data:
  minio_data:
  keycloak_data:

networks:
  anki_network:
    driver: bridge
```

### Environment Variables (.env.example)

```bash
# PostgreSQL
POSTGRES_DB=anki_compendium_dev
POSTGRES_USER=ankiuser
POSTGRES_PASSWORD=changeme

# RabbitMQ
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=changeme

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=changeme

# Keycloak
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=changeme
KEYCLOAK_DATABASE_URL=jdbc:postgresql://postgres:5432/keycloak
KEYCLOAK_DATABASE_USER=ankiuser
KEYCLOAK_DATABASE_PASSWORD=changeme

# OAuth (optional, for Keycloak providers)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

## Testing Requirements

### Smoke Tests
1. **Service Availability**
   ```bash
   # Test PostgreSQL
   psql -h localhost -U ankiuser -d anki_compendium_dev -c "SELECT 1;"
   
   # Test RabbitMQ
   curl -u admin:changeme http://localhost:15672/api/overview
   
   # Test MinIO
   mc alias set local http://localhost:9000 minioadmin changeme
   mc ls local
   
   # Test Keycloak
   curl http://localhost:8080/health
   ```

2. **Data Persistence**
   ```bash
   # Create test data, restart services, verify data still exists
   docker-compose down
   docker-compose up -d
   # Re-run queries to verify data
   ```

3. **Health Checks**
   ```bash
   docker-compose ps  # All services should show (healthy)
   ```

## Success Criteria
- All acceptance criteria met
- Documentation clear enough for new developer onboarding
- Services start reliably on Linux, macOS, Windows (Docker Desktop)
- Resource usage acceptable (<2GB RAM total)

## Deliverables
1. `docker-compose.dev.yml` file
2. `.env.example` file
3. Init scripts for all services
4. README.md with setup instructions
5. Smoke test script (bash/python)

## Notes
- Use official Docker images where possible (security, maintenance)
- Pin specific image versions (avoid `latest` tag in production-like configs)
- Consider using Docker healthcheck for service orchestration
- Document common troubleshooting scenarios in README

## References
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [pgvector Docker Image](https://hub.docker.com/r/pgvector/pgvector)
- [RabbitMQ Docker Guide](https://hub.docker.com/_/rabbitmq)
- [MinIO Docker Quickstart](https://min.io/docs/minio/container/index.html)
- [Keycloak Docker Guide](https://www.keycloak.org/server/containers)
