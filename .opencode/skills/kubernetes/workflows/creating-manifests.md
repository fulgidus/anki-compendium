# Workflow: Creating Kubernetes Manifests

## Purpose
This workflow guides you through creating production-ready Kubernetes manifest files following best practices for security, reliability, and maintainability.

---

## Pre-Requisites
- Docker image available in a container registry
- Understanding of application requirements (ports, environment variables, storage)
- kubectl CLI configured and connected to your cluster

---

## Step-by-Step Process

### 1. Create a Namespace (Optional but Recommended)

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
  labels:
    app: myapp
    environment: production
```

**Why:** Namespaces provide logical isolation and resource quota management.

---

### 2. Create a Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: myapp
  labels:
    app: myapp
    version: v1.0.0
spec:
  replicas: 3  # High availability
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
        version: v1.0.0
    spec:
      # Security: Run as non-root user
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      
      containers:
      - name: myapp
        image: myregistry.io/myapp:1.0.0  # Always use specific tags
        imagePullPolicy: IfNotPresent
        
        # Resource management
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        
        # Ports
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        
        # Health checks
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Environment variables from ConfigMap
        envFrom:
        - configMapRef:
            name: myapp-config
        
        # Secrets
        env:
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: myapp-secrets
              key: db-password
      
      # Image pull secrets (if private registry)
      imagePullSecrets:
      - name: registry-credentials
```

**Key Elements:**
- `replicas: 3` → High availability
- `runAsNonRoot` → Security
- `resources` → Resource management
- `livenessProbe` & `readinessProbe` → Health monitoring

---

### 3. Create a Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
  namespace: myapp
  labels:
    app: myapp
spec:
  type: ClusterIP  # Internal service
  selector:
    app: myapp
  ports:
  - name: http
    port: 80
    targetPort: http
    protocol: TCP
  sessionAffinity: None
```

**Service Types:**
- `ClusterIP` → Internal only (default)
- `NodePort` → Exposes on each node's IP
- `LoadBalancer` → Cloud provider load balancer
- `ExternalName` → DNS CNAME record

---

### 4. Create an Ingress (for external access)

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  namespace: myapp
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp
            port:
              name: http
```

**Why:** Ingress provides HTTP/HTTPS routing and TLS termination.

---

### 5. Create a ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
  namespace: myapp
data:
  LOG_LEVEL: "info"
  API_ENDPOINT: "https://api.example.com"
  FEATURE_FLAG_X: "enabled"
```

**Best Practice:** Store non-sensitive configuration separately from code.

---

### 6. Create a Secret

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
  namespace: myapp
type: Opaque
stringData:  # Auto-encodes to base64
  db-password: "super-secret-password"
  api-key: "abc123xyz"
```

**Security:**
- Never commit secrets to git
- Use external secret management (Vault, External Secrets Operator) in production
- Enable encryption at rest in etcd

---

### 7. Create a HorizontalPodAutoscaler

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp
  namespace: myapp
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Why:** Automatically scales pods based on metrics.

---

## Complete Manifest Organization

### Option 1: Separate Files
```
k8s/
├── namespace.yaml
├── configmap.yaml
├── secret.yaml
├── deployment.yaml
├── service.yaml
├── ingress.yaml
└── hpa.yaml
```

### Option 2: Single File with Separators
```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
  namespace: myapp
data:
  LOG_LEVEL: "info"
---
# ... more resources
```

---

## Deployment Commands

```bash
# Apply all manifests in directory
kubectl apply -f k8s/

# Apply specific file
kubectl apply -f k8s/deployment.yaml

# View created resources
kubectl get all -n myapp

# Check pod status
kubectl get pods -n myapp -w

# View logs
kubectl logs -n myapp deployment/myapp -f

# Describe resource for debugging
kubectl describe deployment myapp -n myapp
```

---

## Validation Checklist

Before deploying to production, verify:

- ✅ Namespace created (if using)
- ✅ Specific image tags (not `latest`)
- ✅ Resource requests and limits defined
- ✅ Liveness and readiness probes configured
- ✅ Security context set (runAsNonRoot, non-privileged)
- ✅ ConfigMaps and Secrets created
- ✅ Service correctly selects pods (labels match)
- ✅ Ingress configured with TLS
- ✅ HPA configured for scalability
- ✅ No hardcoded secrets in manifests
- ✅ Labels and annotations follow naming conventions
- ✅ YAML syntax validated: `kubectl apply --dry-run=client -f k8s/`

---

## Best Practices

### Labeling Strategy
```yaml
metadata:
  labels:
    app: myapp
    component: backend
    environment: production
    version: v1.0.0
    managed-by: kubectl
```

### Annotations
```yaml
metadata:
  annotations:
    description: "Main application backend"
    documentation: "https://docs.example.com/myapp"
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

### Resource Naming
- Lowercase alphanumeric + hyphens only
- Descriptive names: `myapp-backend`, `myapp-database`
- Consistent across resources

---

## Next Steps

After creating manifests:
1. Validate YAML syntax
2. Test in development/staging environment
3. Set up CI/CD pipeline for automated deployments
4. Implement monitoring and alerting
5. Document deployment procedure

---

**Result:** Production-ready Kubernetes manifests following security and reliability best practices.
