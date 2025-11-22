# Kubernetes Skill

**Version:** 1.0.0  
**ID:** kubernetes  
**Type:** Container Orchestration & Infrastructure

---

## Metadata

- **Name:** Kubernetes Skill
- **Description:** Provides expert knowledge for deploying, managing, and orchestrating containerized applications using Kubernetes.
- **Tags:** kubernetes, k8s, orchestration, containers, cloud-native, devops
- **Applicable Roles:** system-engineer, devops-engineer, developer, security-engineer
- **Applicable Phases:** design, implementation, deployment, qa

---

## Skill Contents

This skill includes:

- [Overview](./overview.md) — Core Kubernetes concepts and architecture
- **Workflows** — Step-by-step deployment procedures
  - [Deploying an Application](./workflows/deploying-application.md)
  - [Creating Kubernetes Manifests](./workflows/creating-manifests.md)
- **Patterns** — Production-ready configurations
  - [Deployment Patterns](./patterns/deployment-patterns.md)
  - [ConfigMap and Secrets](./patterns/config-secrets.md)
  - [Resource Management](./patterns/resource-management.md)
- **Troubleshooting** — Common issues and debugging
  - [Pod Issues](./troubleshooting/pod-issues.md)

---

## Purpose

The Kubernetes Skill provides comprehensive expertise in container orchestration. It enables agents to deploy applications, manage workloads, implement scaling strategies, ensure high availability, and maintain production Kubernetes clusters.

---

## When to Load This Skill

Load the Kubernetes Skill when:
- Deploying containerized applications to Kubernetes
- Creating or modifying Kubernetes manifests (Deployments, Services, ConfigMaps, etc.)
- Implementing auto-scaling and resource management
- Setting up service discovery and load balancing
- Troubleshooting pod, node, or cluster issues
- Implementing CI/CD pipelines with Kubernetes
- Managing secrets and configuration
- Designing cloud-native application architectures

---

## Integration

This skill works alongside:
- **Docker Skill** — for container image creation
- **DevOps Skill** — for CI/CD pipeline integration with kubectl, Helm
- **Security Skill** — for RBAC, network policies, pod security
- **Cloud Skills** (AWS, Azure, GCP) — for managed Kubernetes services (EKS, AKS, GKE)
- **Infrastructure Skill** — for cluster provisioning and management

---

## Prerequisites

Agents using this skill should understand:
- Docker and container fundamentals
- YAML syntax
- Basic networking concepts
- Infrastructure-as-Code principles

---

For detailed documentation, see [overview.md](./overview.md).
