# Docker Troubleshooting: Common Issues and Resolutions

## 1. Build Issues

### Issue: "COPY failed: no source files were specified"

**Cause:** Files excluded by `.dockerignore` or don't exist in build context

**Solution:**
```bash
# Check what's in build context
docker build --no-cache -f- . <<EOF
FROM alpine
COPY . /tmp
RUN ls -la /tmp
EOF

# Review .dockerignore
cat .dockerignore
```

---

### Issue: Build cache not working as expected

**Cause:** Layer invalidation due to instruction order

**Solution:** Reorder Dockerfile to place frequently-changing operations last

```dockerfile
# ❌ Bad - source changes invalidate dependency cache
COPY . .
RUN npm install

# ✅ Good - dependencies cached separately
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

---

### Issue: "manifest unknown" when pulling base image

**Cause:** Image tag doesn't exist or registry authentication failed

**Solution:**
```bash
# Verify image exists
docker pull node:20-alpine

# Check authentication
docker login <registry>

# Use fully qualified image name
FROM docker.io/library/node:20-alpine
```

---

### Issue: Build extremely slow

**Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Large build context | Add `.dockerignore` file |
| No layer caching | Reorder instructions (deps before source) |
| Slow network | Use local registry or mirror |
| Many layers | Combine RUN commands with `&&` |

```dockerfile
# ❌ Multiple layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get clean

# ✅ Single layer
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

---

## 2. Runtime Issues

### Issue: Container exits immediately

**Debugging:**
```bash
# Check logs
docker logs <container-id>

# Run with interactive shell
docker run -it <image> /bin/sh

# Check process status
docker ps -a
docker inspect <container-id>
```

**Common Causes:**
- Application crashes on startup
- Missing environment variables
- Incorrect CMD/ENTRYPOINT
- Permission issues

---

### Issue: "Permission denied" errors

**Cause:** Container running as non-root but files owned by root

**Solution:**
```dockerfile
# Set ownership after copying files
COPY --chown=appuser:appgroup . /app

# Or change ownership explicitly
COPY . /app
RUN chown -R appuser:appgroup /app
USER appuser
```

---

### Issue: Cannot connect to container port

**Debugging:**
```bash
# Verify port is exposed
docker inspect <container> | grep -A 10 ExposedPorts

# Check port mapping
docker port <container>

# Verify application is listening
docker exec <container> netstat -tuln
```

**Solution:**
```bash
# Ensure port is published
docker run -p 8080:3000 myapp

# Bind to 0.0.0.0 inside container, not 127.0.0.1
# app.listen(3000, '0.0.0.0')
```

---

### Issue: "exec user process caused: no such file or directory"

**Cause:** Binary not found or incorrect architecture

**Solutions:**
```bash
# Verify binary exists
docker run --rm <image> ls -la /app

# Check architecture matches
docker run --rm <image> uname -m

# Ensure executable permissions
docker run --rm <image> ls -l /app/binary
```

```dockerfile
# Fix permissions
RUN chmod +x /app/binary

# For Go, ensure static binary
RUN CGO_ENABLED=0 GOOS=linux go build -o app
```

---

## 3. Storage Issues

### Issue: Container loses data on restart

**Cause:** Data stored in container filesystem (ephemeral)

**Solution:** Use volumes or bind mounts
```bash
# Named volume
docker run -v mydata:/app/data myapp

# Bind mount
docker run -v $(pwd)/data:/app/data myapp
```

---

### Issue: "no space left on device"

**Debugging:**
```bash
# Check Docker disk usage
docker system df

# Check detailed usage
docker system df -v
```

**Solutions:**
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a --volumes
```

---

## 4. Networking Issues

### Issue: Containers cannot communicate

**Solution:** Ensure containers on same network
```bash
# Create custom network
docker network create myapp-network

# Run containers on same network
docker run --network myapp-network --name frontend frontend-image
docker run --network myapp-network --name backend backend-image

# Containers can now reach each other by name
# http://backend:3000
```

---

### Issue: DNS resolution not working

**Debugging:**
```bash
# Test DNS from container
docker exec <container> nslookup google.com
docker exec <container> cat /etc/resolv.conf
```

**Solution:**
```bash
# Specify DNS servers
docker run --dns 8.8.8.8 --dns 8.8.4.4 myapp
```

---

## 5. Security Issues

### Issue: Security scan shows vulnerabilities

**Steps:**
```bash
# Scan image
docker scan myapp:latest
# or
trivy image myapp:latest

# Update base image
# Change FROM node:16-alpine
# To     FROM node:20-alpine

# Rebuild
docker build --no-cache -t myapp:latest .
```

---

### Issue: Secrets exposed in image layers

**Debugging:**
```bash
# Check image history
docker history --no-trunc myapp:latest | grep -i password

# Inspect layers
docker save myapp:latest -o myapp.tar
tar -xf myapp.tar
find . -name "*.tar" -exec tar -tf {} \;
```

**Solution:**
```dockerfile
# ❌ Never do this
ENV DATABASE_PASSWORD=secret123
COPY .env /app/.env

# ✅ Use build secrets (BuildKit)
RUN --mount=type=secret,id=mysecret \
    SECRET=$(cat /run/secrets/mysecret) && \
    command-using-secret

# ✅ Or pass at runtime
docker run -e DATABASE_PASSWORD=$DB_PASS myapp
```

---

## 6. Performance Issues

### Issue: High memory usage

**Debugging:**
```bash
# Monitor resource usage
docker stats

# Check container limits
docker inspect <container> | grep -A 5 Memory
```

**Solution:**
```bash
# Set memory limits
docker run -m 512m --memory-reservation 256m myapp

# In docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

---

### Issue: High CPU usage

**Solution:**
```bash
# Limit CPU
docker run --cpus="1.5" myapp

# Set CPU shares (relative weight)
docker run --cpu-shares=512 myapp
```

---

## 7. Image Size Issues

### Issue: Image too large

**Debugging:**
```bash
# Check layer sizes
docker history myapp:latest

# Find large files
docker run --rm myapp:latest du -sh /* | sort -h
```

**Solutions:**

1. **Use smaller base image**
```dockerfile
FROM node:20-alpine  # Not node:20 (Debian-based)
```

2. **Multi-stage builds**
```dockerfile
FROM node:20 AS builder
# ... build steps ...

FROM node:20-alpine
COPY --from=builder /app/dist /app
```

3. **Clean up in same layer**
```dockerfile
RUN apt-get update && \
    apt-get install -y package && \
    # ... use package ... && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

4. **Remove cache files**
```dockerfile
RUN npm ci --only=production && \
    npm cache clean --force
```

---

## Quick Diagnostic Commands

```bash
# Container not starting
docker logs <container>
docker inspect <container>
docker events

# Build debugging
docker build --progress=plain --no-cache .

# Network debugging
docker network inspect bridge
docker exec <container> ping <other-container>

# Resource debugging
docker stats
docker system df
docker top <container>

# Security debugging
docker scan <image>
docker history --no-trunc <image>
```

---

## Prevention Checklist

✅ Use `.dockerignore` to reduce build context  
✅ Order Dockerfile instructions for optimal caching  
✅ Use specific base image tags (not `latest`)  
✅ Implement health checks  
✅ Run as non-root user  
✅ Set resource limits  
✅ Use multi-stage builds  
✅ Scan images for vulnerabilities  
✅ Clean up package manager caches  
✅ Test builds in CI before deployment  

---

**When in doubt:** Check logs first, then inspect configuration, then verify network/storage.
