# Git Workflow Skill Overview

## Purpose

The Git Workflow Skill provides comprehensive expertise in version control workflows, branching strategies, and collaboration patterns. It enables teams to work efficiently with Git while maintaining code quality, traceability, and release stability.

---

## Core Competencies

### 1. Branching Strategies
- **GitFlow** — Structured branching for scheduled releases
- **Trunk-Based Development** — Continuous integration with short-lived branches
- **GitHub Flow** — Simplified workflow for continuous deployment
- **Release Branches** — Parallel maintenance of multiple versions
- **Custom Hybrid Models** — Tailored strategies for specific needs

### 2. Branch Management
- Branch naming conventions
- Branch lifecycle management
- Branch protection rules
- Merge policies and strategies
- Branch cleanup and archival

### 3. Commit Standards
- Semantic commit messages
- Conventional Commits specification
- Atomic commits
- Commit signing and verification
- Commit hooks and validation

### 4. Code Integration
- Pull request / Merge request workflows
- Code review processes
- Merge conflict resolution
- Rebase vs merge strategies
- Cherry-picking and backporting

### 5. Version Control Governance
- Repository structure and organization
- Access controls and permissions
- Audit trails and traceability
- Git hooks for enforcement
- Repository health monitoring

---

## Key Principles

### 1. Traceability
Every commit must be traceable to a requirement, task, or issue.

### 2. Atomic Changes
Commits should represent single logical changes, making rollbacks and reviews easier.

### 3. Collaboration
Workflows must support concurrent development without blocking team members.

### 4. Quality Gates
Code must pass automated checks before merging to protected branches.

### 5. Simplicity
Choose the simplest workflow that meets your team's needs.

---

## Branching Strategy Selection Guide

| Team Characteristic | Recommended Strategy |
|---------------------|---------------------|
| **Continuous deployment** | Trunk-Based Development or GitHub Flow |
| **Scheduled releases** | GitFlow or Release Branches |
| **Small team (<5)** | GitHub Flow |
| **Large team (>10)** | GitFlow or Trunk-Based |
| **Multiple prod versions** | Release Branches |
| **High deployment frequency** | Trunk-Based Development |
| **Complex release cycles** | GitFlow |

---

## Common Workflows

### Feature Development Workflow
1. Create feature branch from main/develop
2. Implement changes with atomic commits
3. Push branch and create pull request
4. Code review and automated checks
5. Merge to main/develop after approval
6. Delete feature branch

### Hotfix Workflow
1. Create hotfix branch from production tag
2. Implement minimal fix
3. Fast-track testing and review
4. Merge to production and main/develop
5. Tag new production version
6. Deploy hotfix

### Release Workflow
1. Create release branch from develop
2. Perform final testing and bug fixes
3. Update version numbers and changelog
4. Merge to main and tag release
5. Deploy to production
6. Merge back to develop

---

## Quality Standards

All Git workflows following this skill must meet:

- ✅ **Consistency:** Clear, documented branching strategy
- ✅ **Traceability:** Commits linked to tasks/issues
- ✅ **Quality:** Automated checks before merge
- ✅ **Security:** Signed commits, protected branches
- ✅ **Clarity:** Descriptive commit messages
- ✅ **Safety:** Rollback plans and tested merges
- ✅ **Compliance:** Approval workflows enforced

---

## Integration with Development Lifecycle

```
Requirement → Task → Feature Branch → Commits → PR → Review → Merge → Release → Tag
```

Each stage has clear entry/exit criteria and automated validation.

---

## Skill Structure

This skill contains:
- **workflows/** — Step-by-step procedures for Git operations
- **patterns/** — Best practices for branching, commits, and merges
- **references/** — Git commands, tools, and resources

---

Use this skill to ensure version control is **efficient, traceable, and supports team collaboration**.
