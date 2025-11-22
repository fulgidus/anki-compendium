# Pattern: .dockerignore File

## Purpose

The `.dockerignore` file prevents unnecessary files from being included in the Docker build context, improving build performance and reducing image size.

**Key Benefits:**
- Faster builds (smaller context to transfer)
- Smaller images (excludes unnecessary files)
- Better security (prevents accidental inclusion of secrets)
- Cleaner layer caching

---

## How It Works

When you run `docker build`, Docker sends the entire build context to the Docker daemon. The `.dockerignore` file tells Docker which files and directories to exclude from this context.

**Syntax:** Similar to `.gitignore`

---

## Standard .dockerignore Template

```dockerignore
# Version control
.git
.gitignore
.gitattributes

# CI/CD
.github
.gitlab-ci.yml
.travis.yml
Jenkinsfile

# Documentation
README.md
CHANGELOG.md
LICENSE
*.md
docs/

# Development files
.vscode
.idea
.editorconfig
.env
.env.*
!.env.example

# Dependencies (will be installed in container)
node_modules/
vendor/
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# Build outputs (will be generated in container)
dist/
build/
target/
bin/
obj/
out/

# Test files (unless needed)
tests/
test/
*.test.js
*.spec.js
coverage/

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# OS files
.DS_Store
Thumbs.db
desktop.ini

# Temporary files
tmp/
temp/
*.tmp
*.swp
*.swo
*~

# IDE and editor files
*.sublime-*
.vimrc
.nvimrc

# Docker files (avoid recursive copying)
Dockerfile
docker-compose*.yml
.dockerignore
```

---

## Language-Specific Additions

### Node.js / JavaScript

```dockerignore
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.eslintcache
.parcel-cache
.cache
coverage/
```

### Python

```dockerignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.pytest_cache/
.mypy_cache/
.tox/
*.egg-info/
dist/
build/
```

### .NET / C#

```dockerignore
bin/
obj/
*.user
*.suo
*.cache
.vs/
packages/
TestResults/
*.log
```

### Go

```dockerignore
vendor/
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
```

### Java / Maven

```dockerignore
target/
*.class
*.jar
*.war
.mvn/
.gradle/
build/
```

---

## Security-Focused .dockerignore

**Critical files to always exclude:**

```dockerignore
# Secrets and credentials
*.key
*.pem
*.p12
*.pfx
.env
.env.local
.env.*.local
secrets/
*.secret
credentials.json
*.crt

# SSH keys
.ssh/
id_rsa
id_rsa.pub
known_hosts

# Cloud provider credentials
.aws/
.azure/
.gcloud/

# Database dumps
*.sql
*.dump
*.db

# Configuration with secrets
config/local.yml
config/production.yml
```

---

## Pattern: Minimal Context (Best Performance)

For maximum build performance, explicitly include only what's needed:

```dockerignore
# Exclude everything by default
*

# Then explicitly include required files
!package.json
!package-lock.json
!tsconfig.json
!src/**
```

---

## Pattern: Development vs Production

### .dockerignore (production)
```dockerignore
tests/
*.test.js
coverage/
docs/
.env.development
```

### .dockerignore.dev (development)
```dockerignore
.git
node_modules/
dist/
```

**Usage:**
```bash
# Production build
docker build -t myapp:prod .

# Development build
docker build -f Dockerfile.dev --ignore-file=.dockerignore.dev -t myapp:dev .
```

---

## Validation

### Check what's in your build context:

```bash
# See all files sent to Docker daemon
docker build --no-cache --progress=plain . 2>&1 | grep "Sending build context"

# Manually inspect context
tar -czh . | tar -tz | grep -v '.git'
```

### Verify exclusions work:

```bash
# Build and check layer contents
docker build -t test-ignore .
docker run --rm test-ignore ls -la
```

---

## Common Mistakes

### ❌ Mistake: Ignoring required source files
```dockerignore
src/  # DON'T ignore your source code!
```

### ❌ Mistake: Not ignoring node_modules
```dockerignore
# Missing node_modules/ leads to huge context and slow builds
```

### ❌ Mistake: Ignoring .dockerignore itself
```dockerignore
.dockerignore  # ✅ Safe to ignore (already processed)
```

### ❌ Mistake: Using absolute paths
```dockerignore
/home/user/project/node_modules/  # ❌ Won't work
node_modules/                      # ✅ Correct
```

---

## Debugging .dockerignore

### List what's being ignored:

```bash
# Create a test build to see context
docker build --no-cache -f- . <<EOF
FROM alpine
COPY . /context
RUN find /context -type f | sort
EOF
```

### Verify specific file is ignored:

```bash
# This should fail if .dockerignore works
docker build -f- . <<EOF
FROM alpine
COPY .git /test
EOF
```

---

## Best Practices Summary

1. ✅ **Always** create `.dockerignore` for every Dockerfile
2. ✅ **Exclude** version control (`.git/`)
3. ✅ **Exclude** dependencies that will be installed (`node_modules/`, `vendor/`)
4. ✅ **Exclude** build outputs (`dist/`, `build/`, `target/`)
5. ✅ **Exclude** secrets and credentials
6. ✅ **Exclude** documentation and test files (for production)
7. ✅ **Include** only source files and configuration needed for build
8. ✅ **Test** your ignore rules before deploying

---

## Integration with CI/CD

**.dockerignore in CI pipelines:**

```yaml
# GitHub Actions example
- name: Build Docker image
  run: |
    # Ensure .dockerignore exists
    if [ ! -f .dockerignore ]; then
      echo "❌ .dockerignore is missing!"
      exit 1
    fi
    docker build -t myapp:${{ github.sha }} .
```

---

**Result:** Faster builds, smaller images, better security through proper build context management.
