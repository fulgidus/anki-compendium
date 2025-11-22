---
task_id: "TASK-002-HELM"
title: "Create Helm Charts Base Structure for Kubernetes Deployment"
phase: "Phase 1: Foundation"
complexity: "medium"
estimated_duration: "4-6 hours"
assigned_to: "devops-engineer"
dependencies: []
status: "pending"
priority: "medium"
created_at: "2025-11-22"
---

# Task: Create Helm Charts Base Structure

## Objective
Create a complete Helm chart structure for deploying Anki Compendium to Kubernetes (OVH Managed K8s) with support for multiple environments (dev, staging, prod).

## Context
This chart will be used for production deployment on OVH Kubernetes. It must be flexible enough to support different configurations per environment while maintaining consistency.

## Requirements

### Functional Requirements
1. Single Helm chart that can deploy all application components
2. Support for multiple environments via values files
3. Secrets management (externalized, not committed)
4. Ingress configuration with TLS (cert-manager)
5. Resource limits and requests defined
6. Horizontal Pod Autoscaler (HPA) configuration
7. PersistentVolumeClaims for stateful services

### Chart Components

#### Deployments
1. **Frontend** (Vue.js PWA)
   - Nginx-based static file serving
   - Configurable replicas
   - Liveness/readiness probes
   - Resource limits

2. **Backend API** (FastAPI)
   - Configurable replicas
   - Health check endpoints
   - Environment variables via ConfigMap/Secret
   - Resource limits

3. **Worker** (Celery)
   - Configurable replicas
   - Auto-scaling based on queue depth
   - Resource limits (CPU-intensive)

4. **Keycloak** (Authentication)
   - StatefulSet or Deployment
   - PostgreSQL backend
   - Persistent storage for themes/plugins

#### StatefulSets
1. **PostgreSQL**
   - Single replica (for now)
   - PersistentVolumeClaim for data
   - Init container for pgvector extension
   - Resource limits

2. **RabbitMQ**
   - Single replica (for now)
   - PersistentVolumeClaim for data
   - Management UI exposed via Ingress

3. **MinIO**
   - Single replica (for now)
   - PersistentVolumeClaim for data
   - S3 API and Console exposed

#### Services
- ClusterIP services for internal communication
- LoadBalancer service for Ingress Controller (optional)

#### Ingress
- Single Ingress resource with multiple paths
- TLS termination (cert-manager integration)
- Redirect HTTP → HTTPS
- Annotations for rate limiting, CORS

#### ConfigMaps & Secrets
- Application configuration (non-sensitive)
- Database connection strings
- API keys (Gemini, Stripe, etc.)
- OAuth client credentials

### Non-Functional Requirements
- Helm chart passes `helm lint`
- Chart version follows SemVer
- Clear documentation in Chart.yaml and README
- Values schema validation (values.schema.json)

## File Structure

```
infra/helm/
└── anki-compendium/
    ├── Chart.yaml                  # Chart metadata
    ├── values.yaml                 # Default values (dev)
    ├── values.schema.json          # JSON schema for validation
    ├── README.md                   # Chart documentation
    ├── templates/
    │   ├── _helpers.tpl           # Template helpers
    │   ├── configmap.yaml          # Application config
    │   ├── secret.yaml             # Secrets (use external secrets operator in prod)
    │   ├── frontend-deployment.yaml
    │   ├── frontend-service.yaml
    │   ├── backend-deployment.yaml
    │   ├── backend-service.yaml
    │   ├── worker-deployment.yaml
    │   ├── postgresql-statefulset.yaml
    │   ├── postgresql-service.yaml
    │   ├── postgresql-pvc.yaml
    │   ├── rabbitmq-statefulset.yaml
    │   ├── rabbitmq-service.yaml
    │   ├── rabbitmq-pvc.yaml
    │   ├── minio-statefulset.yaml
    │   ├── minio-service.yaml
    │   ├── minio-pvc.yaml
    │   ├── keycloak-deployment.yaml
    │   ├── keycloak-service.yaml
    │   ├── ingress.yaml
    │   ├── hpa-backend.yaml        # Horizontal Pod Autoscaler for backend
    │   ├── hpa-worker.yaml         # HPA for workers
    │   └── NOTES.txt               # Post-install notes
    ├── values/
    │   ├── values-dev.yaml         # Development overrides
    │   ├── values-staging.yaml     # Staging overrides
    │   └── values-prod.yaml        # Production overrides
    └── .helmignore
```

## Acceptance Criteria

### Must Have
- [ ] Chart installs successfully: `helm install anki-compendium ./infra/helm/anki-compendium`
- [ ] All pods reach `Running` state within 5 minutes
- [ ] Ingress routes traffic correctly to frontend and backend
- [ ] TLS certificate issued automatically (cert-manager annotation)
- [ ] Environment-specific values work (e.g., `-f values/values-prod.yaml`)
- [ ] `helm lint` passes with no errors
- [ ] Chart follows Helm best practices (labels, annotations, naming)

### Nice to Have
- [ ] Helm chart published to a registry (ChartMuseum, Harbor)
- [ ] Automated chart versioning in CI/CD
- [ ] Support for external secrets (External Secrets Operator, Sealed Secrets)
- [ ] NetworkPolicy resources for security

## Technical Specifications

### Chart.yaml Example

```yaml
apiVersion: v2
name: anki-compendium
description: AI-powered Anki flashcard generator
version: 0.1.0  # Chart version
appVersion: "1.0.0"  # Application version
type: application
keywords:
  - anki
  - education
  - ai
  - rag
maintainers:
  - name: Anki Compendium Team
    email: team@example.com
sources:
  - https://github.com/yourusername/anki-compendium
```

### values.yaml Example (Partial)

```yaml
# Global settings
global:
  environment: dev
  domain: anki-compendium.local

# Frontend
frontend:
  replicaCount: 2
  image:
    repository: anki-compendium-frontend
    tag: latest
    pullPolicy: IfNotPresent
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi
  service:
    type: ClusterIP
    port: 80

# Backend
backend:
  replicaCount: 2
  image:
    repository: anki-compendium-backend
    tag: latest
    pullPolicy: IfNotPresent
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

# Worker
worker:
  replicaCount: 2
  image:
    repository: anki-compendium-backend  # Same image as backend
    tag: latest
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 4Gi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 20
    targetCPUUtilizationPercentage: 80

# PostgreSQL
postgresql:
  enabled: true
  image:
    repository: pgvector/pgvector
    tag: pg15
  persistence:
    enabled: true
    size: 10Gi
    storageClass: ""  # Use default
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 2Gi

# RabbitMQ
rabbitmq:
  enabled: true
  persistence:
    enabled: true
    size: 5Gi
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 1Gi

# MinIO
minio:
  enabled: true
  persistence:
    enabled: true
    size: 50Gi
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 1Gi

# Keycloak
keycloak:
  enabled: true
  replicaCount: 1
  resources:
    requests:
      cpu: 200m
      memory: 512Mi
    limits:
      cpu: 1000m
      memory: 2Gi

# Ingress
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: anki-compendium.example.com
      paths:
        - path: /
          pathType: Prefix
          backend: frontend
        - path: /api
          pathType: Prefix
          backend: backend
        - path: /auth
          pathType: Prefix
          backend: keycloak
  tls:
    - secretName: anki-compendium-tls
      hosts:
        - anki-compendium.example.com
```

### Deployment Template Example (backend-deployment.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "anki-compendium.fullname" . }}-backend
  labels:
    {{- include "anki-compendium.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      {{- include "anki-compendium.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: backend
  template:
    metadata:
      labels:
        {{- include "anki-compendium.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: backend
    spec:
      containers:
      - name: backend
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
        imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {{ include "anki-compendium.fullname" . }}-secret
              key: database-url
        - name: RABBITMQ_URL
          valueFrom:
            secretKeyRef:
              name: {{ include "anki-compendium.fullname" . }}-secret
              key: rabbitmq-url
        resources:
          {{- toYaml .Values.backend.resources | nindent 10 }}
```

## Testing Requirements

### Installation Test
```bash
# Install chart in test namespace
helm install anki-compendium-test ./infra/helm/anki-compendium \
  --namespace anki-test \
  --create-namespace \
  --values values/values-dev.yaml

# Verify all pods running
kubectl get pods -n anki-test

# Test Ingress
curl -k https://anki-compendium.local/api/health

# Cleanup
helm uninstall anki-compendium-test -n anki-test
```

### Upgrade Test
```bash
# Make a change to values or templates
# Upgrade existing release
helm upgrade anki-compendium ./infra/helm/anki-compendium -n anki-test

# Verify no downtime (readiness probes)
```

### Lint Test
```bash
helm lint ./infra/helm/anki-compendium
helm template ./infra/helm/anki-compendium | kubectl apply --dry-run=client -f -
```

## Success Criteria
- Helm chart installs all components successfully
- Application accessible via Ingress
- Resource limits prevent cluster overload
- Chart is reusable across environments (dev, prod)
- Documentation is clear for deployment

## Deliverables
1. Complete Helm chart in `infra/helm/anki-compendium/`
2. Environment-specific values files
3. README.md with installation instructions
4. NOTES.txt with post-install instructions

## Notes
- Use Helm hooks for database migrations (pre-upgrade hook)
- Consider using `helm-secrets` plugin for managing sensitive values
- Document OVH-specific considerations (StorageClass, LoadBalancer)
- Plan for Helm chart versioning strategy

## References
- [Helm Documentation](https://helm.sh/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [cert-manager Documentation](https://cert-manager.io/docs/)
- [Kubernetes Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
