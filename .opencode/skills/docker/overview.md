# Docker Skill Overview

## Purpose

The Docker Skill provides comprehensive expertise in containerization using Docker technology. It enables agents to create production-ready container images, manage container lifecycles, optimize builds, and implement container best practices.

---

## Core Competencies

### 1. Container Image Creation
- Writing efficient, secure, and maintainable Dockerfiles
- Multi-stage builds for optimized image sizes
- Layer caching strategies for faster builds
- Base image selection and security considerations

### 2. Container Management
- Container lifecycle operations (create, start, stop, remove)
- Resource constraints and limits (CPU, memory, I/O)
- Health checks and readiness probes
- Logging and monitoring strategies

### 3. Image Optimization
- Reducing image size through layer consolidation
- Minimizing attack surface with distroless/alpine images
- Vulnerability scanning and remediation
- Build-time vs runtime dependencies

### 4. Networking & Storage
- Container networking models (bridge, host, overlay)
- Volume management and data persistence
- Port mapping and service exposure
- Network isolation and security

### 5. Security & Best Practices
- Principle of least privilege (non-root users)
- Secret management and environment variables
- Image signing and verification
- Security scanning and compliance

---

## Key Principles

### Immutability
Containers should be immutable and disposable. Configuration and state should be externalized.

### Reproducibility
Builds must be deterministic. Same Dockerfile + dependencies = same image.

### Minimal Attack Surface
Use minimal base images, remove unnecessary packages, run as non-root.

### Observability
Containers must expose logs, metrics, and health endpoints.

### Portability
Images should run consistently across development, staging, and production environments.

---

## When to Use This Skill

Load the Docker Skill when:
- Creating or modifying Dockerfiles
- Building container images for applications
- Optimizing container builds or reducing image size
- Implementing container security best practices
- Troubleshooting container runtime issues
- Setting up local development environments with containers
- Preparing containerized applications for deployment

---

## Integration with Other Skills

The Docker Skill often works alongside:
- **Kubernetes Skill** — for orchestration and deployment
- **DevOps Skill** — for CI/CD pipeline integration
- **Security Skill** — for vulnerability scanning and hardening
- **Language Skills** (C#, Python, Node.js) — for application-specific containerization
- **Infrastructure Skill** — for registry management and cloud integration

---

## Supported Technologies

- **Docker Engine** — Core container runtime
- **Docker Compose** — Multi-container application definition
- **Docker BuildKit** — Advanced build features and caching
- **Container Registries** — Docker Hub, AWS ECR, Azure ACR, GCP GCR, Harbor
- **Base Images** — Alpine, Debian Slim, Ubuntu, Distroless, Scratch

---

## Quality Standards

All Docker implementations following this skill must meet:

- ✅ **Security**: Non-root execution, minimal packages, no secrets in layers
- ✅ **Size**: Optimized layers, multi-stage builds where applicable
- ✅ **Maintainability**: Clear layer structure, documented decisions
- ✅ **Performance**: Efficient caching, optimized layer ordering
- ✅ **Compliance**: Vulnerability scanning passed, signed images for production

---

## Skill Structure

This skill contains:
- **workflows/** — Step-by-step procedures for common Docker tasks
- **patterns/** — Reusable Dockerfile templates and architectural patterns
- **examples/** — Reference implementations for various tech stacks
- **troubleshooting/** — Common issues and resolutions
- **references/** — Official docs, best practices, security guidelines

---

Use this skill to ensure Docker containers are **production-ready, secure, and optimized**.
