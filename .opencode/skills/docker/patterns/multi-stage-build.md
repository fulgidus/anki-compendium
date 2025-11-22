# Pattern: Multi-Stage Docker Builds

## Overview

Multi-stage builds allow you to use multiple `FROM` statements in a single Dockerfile. Each stage can copy artifacts from previous stages, enabling separation of build-time dependencies from runtime dependencies.

**Key Benefit:** Dramatically reduces final image size and attack surface.

---

## When to Use

✅ **Use multi-stage builds when:**
- Application requires compilation (Go, Java, C#, TypeScript, Rust)
- Build tools and dependencies are large
- Production image should exclude dev/build dependencies
- Security requires minimal runtime image

❌ **Skip multi-stage builds when:**
- Interpreted language with no build step (e.g., simple Python script)
- Build and runtime dependencies are identical
- Image size is not a concern (internal tooling only)

---

## Basic Pattern

```dockerfile
# Stage 1: Build Environment
FROM <build-image> AS builder
WORKDIR /build
COPY . .
RUN <build-commands>

# Stage 2: Runtime Environment
FROM <runtime-image> AS production
WORKDIR /app
COPY --from=builder /build/output ./
CMD ["./app"]
```

---

## Pattern Examples by Language

### Go Application

```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

# Runtime stage
FROM alpine:3.19
RUN apk --no-cache add ca-certificates
WORKDIR /app
COPY --from=builder /build/app ./
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser && \
    chown -R appuser:appgroup /app
USER appuser
ENTRYPOINT ["./app"]
```

**Size Reduction:** ~800MB → ~15MB

---

### .NET Application

```dockerfile
# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS builder
WORKDIR /src
COPY ["MyApp.csproj", "./"]
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine
WORKDIR /app
COPY --from=builder /app/publish ./
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser && \
    chown -R appuser:appgroup /app
USER appuser
EXPOSE 8080
ENTRYPOINT ["dotnet", "MyApp.dll"]
```

**Size Reduction:** ~1.5GB → ~200MB

---

### Node.js with TypeScript

```dockerfile
# Dependencies stage
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production && npm cache clean --force

# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package.json ./
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser && \
    chown -R appuser:appgroup /app
USER appuser
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Size Reduction:** ~1.2GB → ~150MB

---

### Python Application

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
RUN useradd -m -u 1001 appuser && \
    chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["python", "app.py"]
```

---

### Static Frontend (React/Vue)

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
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

**Size Reduction:** ~1.2GB → ~25MB

---

## Advanced Multi-Stage Patterns

### Parallel Build Stages

```dockerfile
# Base dependencies
FROM node:20-alpine AS base
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Backend build
FROM base AS backend-builder
COPY backend/ ./backend/
RUN npm run build:backend

# Frontend build
FROM base AS frontend-builder
COPY frontend/ ./frontend/
RUN npm run build:frontend

# Production
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=backend-builder /app/backend/dist ./backend/
COPY --from=frontend-builder /app/frontend/dist ./frontend/
CMD ["node", "backend/server.js"]
```

---

### Testing in Build Pipeline

```dockerfile
FROM golang:1.21-alpine AS base
WORKDIR /build
COPY . .

# Test stage
FROM base AS test
RUN go test ./... -v

# Build stage (depends on test)
FROM base AS builder
RUN go build -o app .

# Production
FROM alpine:3.19
COPY --from=builder /build/app ./
CMD ["./app"]
```

**Build with:** `docker build --target test .` to run tests only

---

## Best Practices

### 1. Name Your Stages
```dockerfile
FROM node:20-alpine AS deps
FROM node:20-alpine AS builder
FROM node:20-alpine AS production
```

### 2. Order Stages by Dependency
Place shared stages first, specialized stages last.

### 3. Use Specific Base Images per Stage
```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS builder  # Full JDK
FROM eclipse-temurin:21-jre-alpine AS runtime  # Runtime only
```

### 4. Copy Only Required Artifacts
```dockerfile
COPY --from=builder /build/target/app.jar ./app.jar
# Not: COPY --from=builder /build ./
```

### 5. Leverage Build Cache
```dockerfile
# Dependencies first (changes infrequently)
COPY package.json package-lock.json ./
RUN npm ci

# Source code last (changes frequently)
COPY . .
RUN npm run build
```

---

## Troubleshooting

### Issue: "COPY --from=builder" fails
**Cause:** Path doesn't exist in builder stage  
**Solution:** Verify output path in build stage, use `RUN ls -la` to debug

### Issue: Final image still large
**Cause:** Copying unnecessary files  
**Solution:** Be explicit about what to copy; use `.dockerignore`

### Issue: Build cache not working
**Cause:** Order of operations changed  
**Solution:** Place frequently-changing operations last

---

## Validation

After implementing multi-stage build:

```bash
# Build and check size
docker build -t myapp:multi-stage .
docker images myapp:multi-stage

# Inspect layers
docker history myapp:multi-stage

# Verify only runtime files present
docker run --rm myapp:multi-stage ls -la
```

---

**Result:** Optimized, secure production images with minimal size and attack surface.
