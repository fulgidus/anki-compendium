# Workflow: Creating a Dockerfile

## Purpose
This workflow guides you through creating a production-ready Dockerfile following best practices for security, optimization, and maintainability.

---

## Pre-Requisites
- Understanding of the application's runtime requirements
- Knowledge of base image options
- Awareness of security and size constraints
- Access to the application source code

---

## Step-by-Step Process

### 1. Select Base Image

**Choose the most appropriate base image:**

| Use Case | Recommended Base |
|----------|------------------|
| Production | `alpine`, `distroless`, `debian-slim` |
| Development | Official language images (e.g., `node:20-alpine`) |
| Legacy Apps | Ubuntu/Debian if dependencies require |

**Example:**
```dockerfile
FROM node:20-alpine AS base
```

**Security Tip:** Always specify exact versions, never use `latest`.

---

### 2. Define Build Arguments and Environment

```dockerfile
ARG NODE_ENV=production
ENV NODE_ENV=$NODE_ENV
ENV PORT=3000
```

**Best Practice:** Use `ARG` for build-time variables, `ENV` for runtime.

---

### 3. Set Working Directory

```dockerfile
WORKDIR /app
```

**Why:** Ensures consistent paths and prevents file pollution in root.

---

### 4. Copy Dependency Definitions First

```dockerfile
# Copy only dependency files for better caching
COPY package.json package-lock.json ./
```

**Layer Caching:** Dependency files change less frequently than source code.

---

### 5. Install Dependencies

```dockerfile
RUN npm ci --only=production && \
    npm cache clean --force
```

**Optimization:**
- Use `npm ci` instead of `npm install` for deterministic builds
- Clean package manager cache to reduce image size
- Chain commands with `&&` to reduce layers

---

### 6. Copy Application Source

```dockerfile
COPY . .
```

**Why Last:** Source code changes frequently; placing it after dependencies maximizes cache reuse.

---

### 7. Implement Multi-Stage Build (if applicable)

**For compiled languages or frontend builds:**

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package.json package-lock.json ./
RUN npm ci --only=production && \
    npm cache clean --force
```

**Benefit:** Final image contains only runtime artifacts, not build tools.

---

### 8. Create Non-Root User

```dockerfile
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser

USER appuser
```

**Security:** Never run containers as root in production.

---

### 9. Expose Ports

```dockerfile
EXPOSE 3000
```

**Note:** This is documentation only; actual port binding happens at runtime.

---

### 10. Define Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js || exit 1
```

**Why:** Enables orchestrators (Docker, Kubernetes) to monitor container health.

---

### 11. Set Entrypoint and Command

```dockerfile
ENTRYPOINT ["node"]
CMD ["server.js"]
```

**Best Practice:**
- Use `ENTRYPOINT` for the executable
- Use `CMD` for default arguments (can be overridden)

---

## Complete Example (Node.js Application)

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production && \
    npm cache clean --force

# Stage 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Production
FROM node:20-alpine AS production
WORKDIR /app

# Copy production dependencies
COPY --from=deps /app/node_modules ./node_modules

# Copy built application
COPY --from=builder /app/dist ./dist
COPY package.json ./

# Create non-root user
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -s /bin/sh -D appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

ENTRYPOINT ["node"]
CMD ["dist/server.js"]
```

---

## Validation Checklist

Before finalizing your Dockerfile, verify:

- ✅ Specific version tags (no `latest`)
- ✅ Multi-stage build used (if applicable)
- ✅ Non-root user configured
- ✅ Minimal base image selected
- ✅ Layer caching optimized (dependencies before source)
- ✅ No secrets or sensitive data in layers
- ✅ Health check defined
- ✅ `.dockerignore` file created
- ✅ Build tested locally: `docker build -t myapp:test .`
- ✅ Image size reviewed: `docker images myapp:test`
- ✅ Security scan passed: `docker scan myapp:test` or `trivy image myapp:test`

---

## Next Steps

After creating the Dockerfile:
1. Create a `.dockerignore` file (see `patterns/dockerignore.md`)
2. Build and test locally
3. Run security scanning
4. Integrate into CI/CD pipeline
5. Document image usage and configuration

---

**Result:** A production-ready, secure, optimized Dockerfile ready for deployment.
