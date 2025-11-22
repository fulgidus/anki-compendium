---
task_id: "TASK-003-CICD"
title: "Setup GitHub Actions CI/CD Pipeline"
phase: "Phase 1: Foundation"
complexity: "small"
estimated_duration: "2-3 hours"
assigned_to: "devops-engineer"
dependencies: ["TASK-001-DOCKERCOMPOSE"]
status: "pending"
priority: "medium"
created_at: "2025-11-22"
---

# Task: Setup GitHub Actions CI/CD Pipeline

## Objective
Create GitHub Actions workflows for continuous integration (linting, testing) and continuous deployment (build, push Docker images, deploy to K8s).

## Context
Automated CI/CD ensures code quality and streamlines deployment. For MVP, focus on essential checks (linting, smoke tests) and basic deployment automation.

## Requirements

### Functional Requirements
1. **CI Workflow**: Runs on every push and pull request
   - Lint backend (Ruff) and frontend (ESLint)
   - Run unit tests (pytest, Vitest)
   - Build Docker images (validate Dockerfile)
   - Report status to PR

2. **CD Workflow**: Runs on push to `main` branch
   - Build and tag Docker images
   - Push images to container registry
   - Deploy to Kubernetes (optional for MVP, manual for now)

### Non-Functional Requirements
- Fast feedback (<5 minutes for CI)
- Secure secrets management (GitHub Secrets)
- Clear failure messages
- Support for manual triggers (workflow_dispatch)

## File Structure

```
.github/
└── workflows/
    ├── ci.yml              # Continuous Integration
    ├── cd.yml              # Continuous Deployment (future)
    └── lint.yml            # Standalone linting (optional)
```

## Acceptance Criteria

### Must Have
- [ ] CI workflow runs on every push and PR
- [ ] Backend linting (Ruff) passes or fails appropriately
- [ ] Frontend linting (ESLint) passes or fails appropriately
- [ ] Backend tests (pytest) execute
- [ ] Frontend tests (Vitest) execute
- [ ] Docker images build successfully
- [ ] Workflow status visible in GitHub PR checks

### Nice to Have
- [ ] Test coverage reporting
- [ ] Deployment workflow (push to registry)
- [ ] Slack/Discord notifications on failure
- [ ] Caching for dependencies (faster builds)

## Technical Specifications

### CI Workflow (ci.yml)

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install ruff
      
      - name: Run Ruff
        working-directory: ./backend
        run: ruff check .

  lint-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Run ESLint
        working-directory: ./frontend
        run: npm run lint

  test-backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        working-directory: ./backend
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
        run: pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          flags: backend

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Run tests
        working-directory: ./frontend
        run: npm run test:ci

  build-docker:
    runs-on: ubuntu-latest
    needs: [lint-backend, lint-frontend, test-backend, test-frontend]
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: false
          tags: anki-compendium-backend:test
      
      - name: Build frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: false
          tags: anki-compendium-frontend:test
```

### CD Workflow (cd.yml) - Future

```yaml
name: CD

on:
  push:
    branches: [main]
  workflow_dispatch:  # Manual trigger

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ secrets.REGISTRY_URL }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: |
            ${{ secrets.REGISTRY_URL }}/anki-compendium-backend:latest
            ${{ secrets.REGISTRY_URL }}/anki-compendium-backend:${{ github.sha }}
      
      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: |
            ${{ secrets.REGISTRY_URL }}/anki-compendium-frontend:latest
            ${{ secrets.REGISTRY_URL }}/anki-compendium-frontend:${{ github.sha }}

  # deploy:
  #   runs-on: ubuntu-latest
  #   needs: build-and-push
  #   steps:
  #     - name: Deploy to Kubernetes
  #       uses: azure/k8s-deploy@v4
  #       with:
  #         manifests: |
  #           infra/helm/anki-compendium/
  #         images: |
  #           ${{ secrets.REGISTRY_URL }}/anki-compendium-backend:${{ github.sha }}
  #           ${{ secrets.REGISTRY_URL }}/anki-compendium-frontend:${{ github.sha }}
```

## Testing Requirements

### Local Workflow Testing
```bash
# Install act (https://github.com/nektos/act)
brew install act  # macOS
# or apt install act  # Linux

# Run CI workflow locally
act -j lint-backend
act -j test-backend
```

### GitHub Actions Test
```bash
# Push to a test branch and verify workflow runs
git checkout -b test/ci-pipeline
git add .github/workflows/ci.yml
git commit -m "test: Add CI workflow"
git push origin test/ci-pipeline

# Create PR and verify checks run
```

## Success Criteria
- CI workflow runs successfully on every push/PR
- Linting failures block PR merge
- Test failures block PR merge
- Docker builds succeed
- Clear failure messages in GitHub UI

## Deliverables
1. `.github/workflows/ci.yml` - Continuous Integration workflow
2. `.github/workflows/cd.yml` - Continuous Deployment workflow (basic structure)
3. Documentation in README.md about CI/CD setup

## Notes
- Use GitHub Secrets for sensitive values (API keys, registry credentials)
- Consider using workflow caching for faster builds
- Future: Add security scanning (Snyk, Trivy)
- Future: Add deployment to staging environment on PR merge

## References
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Codecov Action](https://github.com/codecov/codecov-action)
