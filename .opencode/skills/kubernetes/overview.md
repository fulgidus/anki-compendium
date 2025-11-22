# Kubernetes Skill Overview

## Purpose

The Kubernetes Skill provides comprehensive expertise in deploying, managing, and orchestrating containerized applications using Kubernetes. It enables agents to implement production-grade container orchestration, auto-scaling, service discovery, and resilient cloud-native architectures.

---

## Core Competencies

### 1. Kubernetes Architecture & Concepts
- Understanding cluster components (control plane, nodes, kubelet, kube-proxy)
- Pod lifecycle and scheduling
- Controllers (Deployments, StatefulSets, DaemonSets, Jobs)
- Services and networking (ClusterIP, NodePort, LoadBalancer, Ingress)
- Storage (Volumes, PersistentVolumes, PersistentVolumeClaims, StorageClasses)

### 2. Application Deployment
- Writing Kubernetes manifests (YAML)
- Deploying stateless and stateful applications
- Managing application configuration with ConfigMaps
- Securing sensitive data with Secrets
- Implementing health checks (liveness, readiness, startup probes)

### 3. Scaling & Resource Management
- Horizontal Pod Autoscaling (HPA)
- Vertical Pod Autoscaling (VPA)
- Cluster autoscaling
- Resource requests and limits (CPU, memory)
- Quality of Service (QoS) classes

### 4. Networking & Service Discovery
- ClusterIP, NodePort, LoadBalancer services
- Ingress controllers and routing
- Network policies for isolation
- DNS and service discovery
- Service mesh integration (Istio, Linkerd)

### 5. Security & Access Control
- Role-Based Access Control (RBAC)
- ServiceAccounts and permissions
- Pod Security Standards (PSS) and Pod Security Policies
- Network segmentation
- Secret management and encryption at rest

### 6. Observability & Monitoring
- Logging strategies (stdout/stderr, sidecar logging)
- Metrics collection (Prometheus, metrics-server)
- Distributed tracing
- Health monitoring and alerting

### 7. High Availability & Resilience
- Multi-replica deployments
- Pod disruption budgets
- Anti-affinity and topology spread
- Graceful shutdown and termination
- Backup and disaster recovery

---

## Key Principles

### Declarative Configuration
Kubernetes follows a declarative model: you define the desired state, and Kubernetes ensures the actual state matches it.

### Immutable Infrastructure
Pods are ephemeral and disposable. State should be externalized to persistent volumes or external systems.

### Self-Healing
Kubernetes automatically restarts failed containers, reschedules pods, and replaces unhealthy instances.

### Scalability
Kubernetes enables horizontal scaling of applications and infrastructure to handle varying load.

### Cloud-Native Design
Applications should be designed as loosely-coupled microservices with well-defined APIs.

---

## When to Use This Skill

Load the Kubernetes Skill when:
- Deploying Docker containers to Kubernetes clusters
- Creating Kubernetes manifests (Deployment, Service, Ingress, ConfigMap, Secret)
- Implementing auto-scaling or resource optimization
- Troubleshooting pod failures, networking issues, or performance problems
- Setting up CI/CD pipelines that deploy to Kubernetes
- Implementing security policies and RBAC
- Designing multi-tier applications for cloud deployment

---

## Integration with Other Skills

The Kubernetes Skill often works alongside:
- **Docker Skill** — for building container images before deployment
- **DevOps Skill** — for CI/CD integration with kubectl, Helm, ArgoCD
- **Security Skill** — for RBAC, network policies, vulnerability scanning
- **Cloud Platform Skills** (AWS, Azure, GCP) — for managed Kubernetes (EKS, AKS, GKE)
- **Monitoring Skill** — for Prometheus, Grafana, and observability stacks
- **Infrastructure Skill** — for cluster provisioning via Terraform, Pulumi

---

## Supported Kubernetes Distributions

- **Managed Kubernetes:**
  - Amazon EKS (Elastic Kubernetes Service)
  - Azure AKS (Azure Kubernetes Service)
  - Google GKE (Google Kubernetes Engine)
  - DigitalOcean Kubernetes
  
- **Self-Managed:**
  - Kubeadm
  - K3s (lightweight Kubernetes)
  - Kind (Kubernetes in Docker for local development)
  - Minikube (local testing)

- **Enterprise Distributions:**
  - Red Hat OpenShift
  - Rancher
  - VMware Tanzu

---

## Quality Standards

All Kubernetes deployments following this skill must meet:

- ✅ **High Availability:** Multi-replica deployments with anti-affinity
- ✅ **Security:** RBAC configured, least privilege, secrets encrypted
- ✅ **Resource Optimization:** Requests and limits defined for all containers
- ✅ **Observability:** Logging, metrics, and health checks implemented
- ✅ **Resilience:** Liveness and readiness probes configured
- ✅ **Maintainability:** Clear naming conventions, labels, and annotations
- ✅ **Scalability:** HPA configured where appropriate
- ✅ **Documentation:** Manifests documented with comments and README

---

## Skill Structure

This skill contains:
- **workflows/** — Step-by-step procedures for deploying and managing applications
- **patterns/** — Reusable manifest templates and architectural patterns
- **examples/** — Reference implementations for common use cases
- **troubleshooting/** — Common issues, debugging techniques, and resolutions
- **references/** — Official Kubernetes docs, best practices, security guidelines

---

Use this skill to ensure Kubernetes deployments are **production-ready, scalable, secure, and resilient**.
