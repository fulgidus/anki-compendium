# Pattern: Branch Naming Conventions

## Purpose

Consistent branch naming improves collaboration, automation, and repository organization. This pattern defines standard naming conventions for all branch types.

---

## General Rules

### 1. Format Structure
```
<type>/<identifier>-<short-description>
```

**Examples:**
- `feature/AUTH-123-user-login`
- `bugfix/PROD-456-memory-leak`
- `hotfix/CRIT-789-security-patch`

### 2. Naming Requirements
- **Lowercase only** — `feature/user-auth`, not `Feature/User-Auth`
- **Hyphens for spaces** — `feature/add-login`, not `feature/add_login` or `feature/addLogin`
- **No special characters** — Only alphanumeric, hyphens, and slashes
- **Descriptive** — Clear purpose from name alone
- **Short but meaningful** — 2-5 words in description

---

## Branch Types

### Protected Branches

#### `main` (or `master`)
- **Purpose:** Production-ready code
- **Protected:** Yes
- **Merges from:** release/*, hotfix/*
- **Direct commits:** Never

#### `develop`
- **Purpose:** Integration branch for next release
- **Protected:** Yes
- **Merges from:** feature/*, bugfix/*
- **Direct commits:** Never (except small fixes)

---

### Temporary Branches

#### Feature Branches
**Pattern:** `feature/<ticket-id>-<description>`

**Examples:**
```
feature/AUTH-123-oauth-integration
feature/USER-456-profile-page
feature/API-789-graphql-endpoint
```

**Rules:**
- Created from: `develop`
- Merged to: `develop`
- Lifetime: Until feature complete
- Naming: Include ticket/issue ID when available

---

#### Bugfix Branches
**Pattern:** `bugfix/<ticket-id>-<description>`

**Examples:**
```
bugfix/BUG-123-null-pointer
bugfix/UI-456-button-alignment
bugfix/DATA-789-query-timeout
```

**Rules:**
- Created from: `develop`
- Merged to: `develop`
- Lifetime: Until bug fixed
- Naming: Include severity if critical

---

#### Hotfix Branches
**Pattern:** `hotfix/<version>-<description>`

**Examples:**
```
hotfix/1.2.1-security-patch
hotfix/2.0.1-memory-leak
hotfix/3.5.2-critical-api-fix
```

**Rules:**
- Created from: `main` (production)
- Merged to: `main` AND `develop`
- Lifetime: Short (emergency fixes only)
- Naming: Include target version number

---

#### Release Branches
**Pattern:** `release/<version>`

**Examples:**
```
release/1.0.0
release/2.1.0
release/3.0.0-beta
```

**Rules:**
- Created from: `develop`
- Merged to: `main` AND `develop`
- Lifetime: Until release deployed
- Naming: Semantic version number

---

### Special Purpose Branches

#### Experimental Branches
**Pattern:** `experiment/<description>`

**Examples:**
```
experiment/new-architecture
experiment/performance-optimization
experiment/ml-integration
```

**Rules:**
- Created from: Any branch
- Merged to: Maybe (after validation)
- Lifetime: Variable
- Naming: Clearly marked as experimental

---

#### Documentation Branches
**Pattern:** `docs/<description>`

**Examples:**
```
docs/api-reference
docs/setup-guide
docs/architecture-diagrams
```

**Rules:**
- Created from: `develop`
- Merged to: `develop` or `main`
- Lifetime: Until docs complete

---

#### Refactor Branches
**Pattern:** `refactor/<component>-<description>`

**Examples:**
```
refactor/auth-service-cleanup
refactor/database-schema
refactor/frontend-components
```

**Rules:**
- Created from: `develop`
- Merged to: `develop`
- Lifetime: Until refactor complete

---

## Automation-Friendly Patterns

### CI/CD Integration
Branch names trigger specific pipelines:

```yaml
# GitHub Actions example
on:
  push:
    branches:
      - 'feature/**'
      - 'bugfix/**'
      - 'hotfix/**'
      - 'release/**'
```

### Automated Branch Policies
```yaml
# Example policy configuration
branches:
  feature/*:
    require_pr: true
    require_reviews: 2
    run_tests: true
  
  hotfix/*:
    require_pr: true
    require_reviews: 1
    fast_track: true
  
  main:
    protected: true
    require_signed_commits: true
```

---

## Team-Specific Prefixes

### Personal Development Branches
**Pattern:** `<username>/<description>`

**Examples:**
```
john/spike-graphql
sarah/poc-websockets
mike/test-new-library
```

**Rules:**
- For personal experiments
- Not merged to main branches
- Cleaned up regularly

---

### Team-Based Branches
**Pattern:** `<team>/<description>`

**Examples:**
```
frontend/redesign-dashboard
backend/api-v2
devops/ci-migration
```

**Rules:**
- Long-lived collaboration branches
- Eventual merge to develop
- Team ownership

---

## Validation and Enforcement

### Git Hooks
Create a pre-push hook to validate branch names:

```bash
#!/bin/bash
# .git/hooks/pre-push

branch=$(git rev-parse --abbrev-ref HEAD)

valid_pattern="^(feature|bugfix|hotfix|release|docs|refactor|experiment)/[a-z0-9-]+$"

if ! [[ $branch =~ $valid_pattern ]] && [[ $branch != "main" ]] && [[ $branch != "develop" ]]; then
  echo "❌ Invalid branch name: $branch"
  echo "Branch names must match: <type>/<description>"
  echo "Types: feature, bugfix, hotfix, release, docs, refactor, experiment"
  exit 1
fi
```

### Server-Side Validation
Configure Git server to reject invalid branch names:

```bash
# GitLab example - push rules
# Settings → Repository → Push Rules
# Branch name regex: ^(feature|bugfix|hotfix|release)/[a-z0-9-]+$
```

---

## Migration Strategy

### Renaming Existing Branches

```bash
# Rename local branch
git branch -m old-name new-name

# Delete old remote branch
git push origin --delete old-name

# Push new branch
git push origin -u new-name
```

### Communicating Changes
1. Document new naming convention
2. Provide examples and templates
3. Give transition period
4. Enforce with automation after deadline

---

## Benefits Summary

✅ **Clarity** — Branch purpose obvious from name  
✅ **Organization** — Easy to filter and search  
✅ **Automation** — Triggers CI/CD pipelines correctly  
✅ **Traceability** — Links to tickets/issues  
✅ **Cleanup** — Easy to identify stale branches  
✅ **Collaboration** — Team understands ownership  

---

## Quick Reference

| Branch Type | Pattern | Example |
|-------------|---------|---------|
| **Feature** | `feature/<id>-<desc>` | `feature/AUTH-123-login` |
| **Bugfix** | `bugfix/<id>-<desc>` | `bugfix/BUG-456-crash` |
| **Hotfix** | `hotfix/<version>-<desc>` | `hotfix/1.2.1-patch` |
| **Release** | `release/<version>` | `release/2.0.0` |
| **Docs** | `docs/<desc>` | `docs/api-guide` |
| **Refactor** | `refactor/<desc>` | `refactor/auth-cleanup` |

---

**Adopt these conventions to maintain a clean, organized, and automation-friendly repository.**
