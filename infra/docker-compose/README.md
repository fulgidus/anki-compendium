# Anki Compendium - Docker Compose Development Environment

Complete local development environment for Anki Compendium using Docker Compose.

## 🚀 Quick Start

```bash
# 1. Copy environment variables template
cp .env.example .env

# 2. (Optional) Edit .env with your preferences
nano .env

# 3. Start all services
docker-compose -f docker-compose.dev.yml up -d

# 4. Verify all services are healthy
docker-compose -f docker-compose.dev.yml ps

# 5. View logs (optional)
docker-compose -f docker-compose.dev.yml logs -f
```

**That's it!** All services are now running and accessible.

---

## 📦 Services Overview

| Service | Port(s) | UI/Console | Credentials |
|---------|---------|------------|-------------|
| **PostgreSQL 15** | 5432 | N/A | `ankiuser` / `changeme` |
| **RabbitMQ** | 5672, 15672 | http://localhost:15672 | `admin` / `changeme` |
| **MinIO** | 9000, 9001 | http://localhost:9001 | `minioadmin` / `changeme123` |
| **Keycloak** | 8080 | http://localhost:8080 | `admin` / `changeme` |

### PostgreSQL
- **Purpose**: Main database with pgvector extension for RAG embeddings
- **Database**: `anki_compendium_dev` (main), `keycloak` (auth)
- **Extensions**: pgvector, uuid-ossp, pg_trgm
- **Connection**: `postgresql://ankiuser:changeme@localhost:5432/anki_compendium_dev`

### RabbitMQ
- **Purpose**: Message broker for async task processing
- **Queues Created**:
  - `pdf.processing` - PDF upload and parsing
  - `deck.generation` - Anki deck creation
  - `embedding.generation` - Vector embeddings
  - `notifications` - User notifications
- **Management UI**: http://localhost:15672

### MinIO
- **Purpose**: S3-compatible object storage for PDFs and decks
- **Buckets Created**:
  - `pdfs` - Uploaded PDF files
  - `decks` - Generated Anki decks (.apkg files)
  - `temp` - Temporary files (auto-cleanup after 7 days)
- **Console**: http://localhost:9001
- **API**: http://localhost:9000

### Keycloak
- **Purpose**: Authentication and authorization (OAuth 2.0 / OpenID Connect)
- **Realm**: `anki-compendium`
- **Clients**:
  - `anki-compendium-web` - Frontend application
  - `anki-compendium-api` - Backend API
- **Admin Console**: http://localhost:8080
- **Test Users**:
  - Admin: `admin@example.com` / `admin123` (temporary password)
  - Demo: `demo@example.com` / `demo123`

---

## 🛠️ Management Commands

### Starting Services
```bash
# Start all services in background
docker-compose -f docker-compose.dev.yml up -d

# Start specific service
docker-compose -f docker-compose.dev.yml up -d postgres

# Start with logs visible
docker-compose -f docker-compose.dev.yml up
```

### Stopping Services
```bash
# Stop all services (preserves data)
docker-compose -f docker-compose.dev.yml down

# Stop and remove volumes (DELETE ALL DATA)
docker-compose -f docker-compose.dev.yml down -v
```

### Viewing Logs
```bash
# All services
docker-compose -f docker-compose.dev.yml logs -f

# Specific service
docker-compose -f docker-compose.dev.yml logs -f postgres

# Last 100 lines
docker-compose -f docker-compose.dev.yml logs --tail=100
```

### Health Checks
```bash
# Check service status
docker-compose -f docker-compose.dev.yml ps

# All should show (healthy) status
```

### Restarting Services
```bash
# Restart all
docker-compose -f docker-compose.dev.yml restart

# Restart specific service
docker-compose -f docker-compose.dev.yml restart postgres
```

---

## 🧪 Testing & Validation

### Smoke Test Script
Run the included smoke test to verify all services:

```bash
# Make script executable
chmod +x smoke-test.sh

# Run tests
./smoke-test.sh
```

### Manual Testing

#### PostgreSQL
```bash
# Connect via psql
psql -h localhost -U ankiuser -d anki_compendium_dev

# Test pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

# Test query
SELECT 1;
```

#### RabbitMQ
```bash
# Check management API
curl -u admin:changeme http://localhost:15672/api/overview

# List queues
curl -u admin:changeme http://localhost:15672/api/queues
```

#### MinIO
```bash
# Install MinIO client (if not installed)
brew install minio/stable/mc  # macOS
# or
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# Configure alias
mc alias set local http://localhost:9000 minioadmin changeme123

# List buckets
mc ls local

# Test upload
echo "test" > test.txt
mc cp test.txt local/temp/test.txt
mc ls local/temp
```

#### Keycloak
```bash
# Check health endpoint
curl http://localhost:8080/health

# Check realm
curl http://localhost:8080/realms/anki-compendium
```

---

## 🔧 Configuration

### Environment Variables
All configuration is in `.env` file. Key variables:

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
MINIO_ROOT_PASSWORD=changeme123

# Keycloak
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=changeme
```

**⚠️ IMPORTANT**: Change all passwords in production!

### Resource Limits
Default resource limits (can be adjusted in docker-compose.dev.yml):

| Service | CPU Limit | Memory Limit |
|---------|-----------|--------------|
| PostgreSQL | 1.0 | 512M |
| RabbitMQ | 0.5 | 512M |
| MinIO | 0.5 | 512M |
| Keycloak | 1.0 | 1024M |

**Total**: ~2GB RAM (well within Docker Desktop defaults)

---

## 📁 Data Persistence

All data is stored in named Docker volumes:

```bash
# List volumes
docker volume ls | grep anki_compendium

# Inspect volume
docker volume inspect anki_compendium_postgres_data

# Backup volume (example)
docker run --rm -v anki_compendium_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz -C /data .

# Restore volume (example)
docker run --rm -v anki_compendium_postgres_data:/data -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/postgres-backup.tar.gz"
```

### Volume Locations
- `anki_compendium_postgres_data` - PostgreSQL database
- `anki_compendium_rabbitmq_data` - RabbitMQ messages and config
- `anki_compendium_minio_data` - MinIO objects (PDFs, decks)
- `anki_compendium_keycloak_data` - Keycloak configuration

---

## 🐛 Troubleshooting

### Services Won't Start

**Port Already in Use**
```bash
# Find what's using the port
lsof -i :5432  # PostgreSQL
lsof -i :8080  # Keycloak

# Kill process or change port in .env
```

**Insufficient Resources**
```bash
# Check Docker resources
docker stats

# Increase Docker Desktop memory:
# Docker Desktop → Settings → Resources → Memory → 4GB+
```

### Service Unhealthy

**Check logs**
```bash
docker-compose -f docker-compose.dev.yml logs <service-name>
```

**PostgreSQL fails to start**
```bash
# Check permissions
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d postgres

# Check logs
docker-compose -f docker-compose.dev.yml logs postgres
```

**Keycloak database connection fails**
```bash
# Ensure PostgreSQL is fully healthy first
docker-compose -f docker-compose.dev.yml ps postgres

# Restart Keycloak
docker-compose -f docker-compose.dev.yml restart keycloak
```

### Clean Slate Reset
```bash
# CAUTION: This deletes ALL data!
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d
```

### Permission Issues (Linux)
```bash
# If you get permission errors with volumes
sudo chown -R $USER:$USER ~/.docker
```

---

## 🔐 Security Notes

### Development Only
This configuration is for **local development only**:
- ❌ Default passwords
- ❌ No SSL/TLS
- ❌ Open CORS policies
- ❌ Debug mode enabled

### Production Checklist
Before deploying to production:
- [ ] Change all default passwords
- [ ] Enable SSL/TLS for all services
- [ ] Restrict CORS origins
- [ ] Enable authentication for all UIs
- [ ] Use secrets management (Vault, AWS Secrets Manager)
- [ ] Implement network segmentation
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup strategy implemented

---

## 📚 Additional Resources

### Docker Compose
- [Official Documentation](https://docs.docker.com/compose/)
- [Compose File Reference](https://docs.docker.com/compose/compose-file/)

### Service Documentation
- [PostgreSQL + pgvector](https://github.com/pgvector/pgvector)
- [RabbitMQ](https://www.rabbitmq.com/documentation.html)
- [MinIO](https://min.io/docs/minio/linux/index.html)
- [Keycloak](https://www.keycloak.org/documentation)

### Anki Compendium
- [Main README](../../README.md)
- [Architecture Documentation](../../docs/ARCHITECTURE.md)
- [API Documentation](../../docs/API.md)

---

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose -f docker-compose.dev.yml logs -f`
2. Verify environment variables: `cat .env`
3. Check Docker resources: `docker stats`
4. Try clean restart: `docker-compose down && docker-compose up -d`
5. Open an issue on GitHub with logs and configuration

---

## ✅ Success Verification

After starting services, you should be able to:

- ✅ Connect to PostgreSQL: `psql -h localhost -U ankiuser -d anki_compendium_dev`
- ✅ Access RabbitMQ UI: http://localhost:15672
- ✅ Access MinIO Console: http://localhost:9001
- ✅ Access Keycloak Admin: http://localhost:8080
- ✅ All services show `(healthy)` in `docker-compose ps`
- ✅ Data persists after `docker-compose down` (without `-v`)

**Happy Development! 🎉**
