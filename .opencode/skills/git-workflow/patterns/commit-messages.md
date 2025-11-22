# Pattern: Commit Message Standards

## Purpose

Well-structured commit messages improve code archaeology, automate changelog generation, and facilitate code reviews. This pattern defines a standard format based on Conventional Commits.

---

## Commit Message Format

### Structure
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Example
```
feat(auth): add OAuth2 authentication

Implement OAuth2 authentication flow with Google and GitHub providers.
Includes token refresh logic and session management.

Closes #123
BREAKING CHANGE: API authentication now requires OAuth2 tokens
```

---

## Components

### 1. Type (Required)

The type describes the category of change:

| Type | Description | Changelog Section |
|------|-------------|-------------------|
| `feat` | New feature | Features |
| `fix` | Bug fix | Bug Fixes |
| `docs` | Documentation changes | Documentation |
| `style` | Code style (formatting, semicolons) | - |
| `refactor` | Code refactoring (no behavior change) | - |
| `perf` | Performance improvements | Performance |
| `test` | Add or update tests | - |
| `build` | Build system or dependencies | Build |
| `ci` | CI/CD configuration | CI/CD |
| `chore` | Maintenance tasks | - |
| `revert` | Revert previous commit | - |

---

### 2. Scope (Optional)

The scope describes the area of code affected:

**Examples:**
- `feat(api): add user endpoint`
- `fix(ui): correct button alignment`
- `docs(readme): update installation steps`
- `refactor(database): optimize query performance`

**Common Scopes:**
- Component names: `auth`, `ui`, `api`, `database`
- Module names: `user-service`, `payment-gateway`
- Technology: `docker`, `kubernetes`, `terraform`

**Rules:**
- Use lowercase
- Use hyphens for multi-word scopes
- Keep consistent across project

---

### 3. Subject (Required)

The subject is a short description of the change:

**Rules:**
- **Imperative mood** — "add feature" not "added feature"
- **No period** at the end
- **Lowercase** first letter
- **Max 50 characters**
- **Clear and concise**

**Good Examples:**
```
add user authentication
fix memory leak in cache
update API documentation
remove deprecated endpoints
```

**Bad Examples:**
```
Added user authentication.  ❌ (past tense, period)
Fix  ❌ (too vague)
Updated the API documentation for v2  ❌ (too long)
feature: New Feature  ❌ (capitalized, redundant)
```

---

### 4. Body (Optional but Recommended)

The body provides detailed context:

**When to Include:**
- Complex changes requiring explanation
- Non-obvious decisions
- Context for reviewers
- Breaking changes

**Format:**
- Wrap at **72 characters**
- Blank line after subject
- Explain **what** and **why**, not **how**
- Multiple paragraphs allowed

**Example:**
```
refactor(auth): migrate to JWT tokens

Previous session-based auth didn't scale well with multiple servers.
JWT tokens enable stateless authentication across distributed systems.

This change requires updating client-side token handling and
implementing token refresh logic.
```

---

### 5. Footer (Optional)

The footer contains metadata:

**Breaking Changes:**
```
BREAKING CHANGE: API authentication now requires OAuth2 tokens
```

**Issue References:**
```
Closes #123
Fixes #456, #789
Resolves #101
```

**Co-Authors:**
```
Co-authored-by: Jane Doe <jane@example.com>
Co-authored-by: John Smith <john@example.com>
```

**Signed-off:**
```
Signed-off-by: Developer Name <dev@example.com>
```

---

## Complete Examples

### Feature Addition
```
feat(payment): add Stripe payment integration

Integrate Stripe API for credit card processing.
Supports one-time payments and subscription billing.

Includes webhook handling for payment status updates
and automatic invoice generation.

Closes #234
```

### Bug Fix
```
fix(api): prevent null pointer exception in user lookup

Added null check before accessing user properties.
This fixes crashes when querying non-existent users.

Fixes #456
```

### Breaking Change
```
feat(api): migrate to v2 REST API

Complete redesign of API endpoints following RESTful principles.
New versioned endpoints with improved response formats.

BREAKING CHANGE: All API endpoints now require /v2/ prefix.
Old /v1/ endpoints will be deprecated in 6 months.

Closes #789
```

### Documentation Update
```
docs(readme): add Docker deployment instructions

Added step-by-step guide for deploying with Docker Compose.
Includes environment variable configuration and volume setup.
```

### Refactoring
```
refactor(database): optimize user query performance

Replaced N+1 queries with single JOIN query.
Added database indexes on frequently queried columns.

Performance improvement: 500ms → 50ms average query time.
```

---

## Conventional Commits Benefits

### 1. Automated Changelog Generation
```bash
# Generate changelog from commits
npx standard-version

# Output:
# ## [1.2.0] - 2025-01-15
# ### Features
# - add OAuth2 authentication
# - implement user dashboard
# 
# ### Bug Fixes
# - fix memory leak in cache
```

### 2. Semantic Versioning
```
feat: → Minor version bump (1.0.0 → 1.1.0)
fix: → Patch version bump (1.0.0 → 1.0.1)
BREAKING CHANGE: → Major version bump (1.0.0 → 2.0.0)
```

### 3. CI/CD Integration
```yaml
# GitHub Actions example
- name: Check commit message
  run: |
    npx commitlint --from HEAD~1 --to HEAD
```

---

## Enforcement

### Git Hooks with Commitlint

**Install:**
```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional
npx husky install
npx husky add .husky/commit-msg 'npx commitlint --edit $1'
```

**Configuration (commitlint.config.js):**
```javascript
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore', 'revert']
    ],
    'subject-case': [2, 'always', 'lower-case'],
    'subject-max-length': [2, 'always', 50],
    'body-max-line-length': [2, 'always', 72]
  }
};
```

---

## Tools

### Commit Message Helpers

**Commitizen** — Interactive commit helper
```bash
npm install -g commitizen
git cz  # Instead of git commit
```

**VSCode Extension** — Conventional Commits
```
Name: Conventional Commits
ID: vivaxy.vscode-conventional-commits
```

---

## Team Guidelines

### Commit Frequency
- **Commit often** — Small, atomic changes
- **Before breaks** — End of day, before meetings
- **After tests pass** — Ensure working state

### What NOT to Commit
```
fix: fix bug  ❌ Too vague
feat: add stuff  ❌ Unclear
update  ❌ No type or scope
WIP  ❌ Work-in-progress commits (squash before merge)
```

### Rewriting History
**Before pushing:**
```bash
# Amend last commit message
git commit --amend

# Interactive rebase to fix multiple commits
git rebase -i HEAD~3
```

**After pushing to feature branch (not main/develop):**
```bash
# Force push with care
git push --force-with-lease
```

---

## Quick Reference

**Format:**
```
<type>(<scope>): <subject>
```

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation
- `refactor` — Code restructuring
- `test` — Add tests
- `chore` — Maintenance

**Rules:**
- Imperative mood: "add" not "added"
- Lowercase subject
- No period at end
- Max 50 characters
- Reference issues in footer

---

**Adopt these standards to maintain clear, searchable, and automation-friendly commit history.**
