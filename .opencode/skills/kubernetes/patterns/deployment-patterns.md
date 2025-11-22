# Pattern: Kubernetes Deployment Patterns

## Overview

This document describes production-ready Kubernetes deployment patterns for various application types and use cases.

---

## 1. Stateless Application Pattern

### Use Case
Web applications, APIs, microservices without persistent state

### Implementation

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: stateless-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero-downtime deployment
  selector:
    matchLabels:
      app: stateless-app
  template:
    metadata:
      labels:
        app: stateless-app
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - stateless-app
              topologyKey: kubernetes.io/hostname
      containers:
      - name: app
        image: myapp:1.0.0
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

**Key Features:**
- Multiple replicas for high availability
- Pod anti-affinity spreads pods across nodes
- Zero-downtime rolling updates
- Health checks for resilience

---

## 2. Stateful Application Pattern (Database, Cache)

### Use Case
Databases, message queues, stateful services requiring stable network identity and persistent storage

### Implementation

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mongodb
spec:
  clusterIP: None  # Headless service for stable DNS
  selector:
    app: mongodb
  ports:
  - port: 27017
    name: mongodb
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
spec:
  serviceName: mongodb
  replicas: 3
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:7.0
        ports:
        - containerPort: 27017
          name: mongodb
        volumeMounts:
        - name: data
          mountPath: /data/db
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 10Gi
```

**Key Features:**
- Stable pod identities (mongodb-0, mongodb-1, mongodb-2)
- Persistent volumes automatically provisioned per pod
- Ordered deployment and scaling
- Headless service for direct pod addressing

---

## 3. Background Job / Worker Pattern

### Use Case
Scheduled tasks, batch processing, queue workers

### Cron Job Example

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: data-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  concurrencyPolicy: Forbid  # Don't run concurrent jobs
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      backoffLimit: 3
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: backup-tool:1.0.0
            command: ["/bin/sh", "-c"]
            args:
            - |
              echo "Starting backup..."
              /app/backup.sh
              echo "Backup complete"
            env:
            - name: BACKUP_DESTINATION
              value: "s3://my-bucket/backups"
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: access-key-id
```

### One-Time Job Example

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: database-migration
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: migrate
        image: myapp:1.0.0
        command: ["npm", "run", "migrate"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
```

---

## 4. Sidecar Pattern

### Use Case
Logging, monitoring, proxies running alongside main application

### Implementation

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-sidecar
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      # Main application
      - name: app
        image: myapp:1.0.0
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: logs
          mountPath: /var/log/app
      
      # Sidecar: Log forwarder
      - name: log-forwarder
        image: fluent/fluent-bit:2.0
        volumeMounts:
        - name: logs
          mountPath: /var/log/app
          readOnly: true
        - name: fluent-config
          mountPath: /fluent-bit/etc/
      
      volumes:
      - name: logs
        emptyDir: {}
      - name: fluent-config
        configMap:
          name: fluent-bit-config
```

**Use Cases:**
- Log aggregation (Fluentd, Fluent Bit)
- Service mesh proxies (Envoy, Linkerd)
- Configuration reloaders
- Security scanners

---

## 5. Init Container Pattern

### Use Case
Pre-flight checks, database migrations, configuration setup before main app starts

### Implementation

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-with-init
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      initContainers:
      # Wait for database to be ready
      - name: wait-for-db
        image: busybox:1.36
        command: ['sh', '-c']
        args:
        - |
          until nc -z postgres-service 5432; do
            echo "Waiting for PostgreSQL..."
            sleep 2
          done
          echo "PostgreSQL is ready!"
      
      # Run database migrations
      - name: run-migrations
        image: myapp:1.0.0
        command: ["npm", "run", "migrate"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
      
      containers:
      - name: app
        image: myapp:1.0.0
        ports:
        - containerPort: 8080
```

**Execution Order:**
1. Init containers run sequentially to completion
2. Main container starts only after all init containers succeed

---

## 6. DaemonSet Pattern

### Use Case
Run a pod on every node (logging agents, monitoring, node maintenance)

### Implementation

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true
      hostPID: true
      containers:
      - name: node-exporter
        image: prom/node-exporter:v1.6.0
        ports:
        - containerPort: 9100
          name: metrics
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
      tolerations:
      - effect: NoSchedule
        operator: Exists  # Run on all nodes including control plane
```

---

## 7. Blue-Green Deployment Pattern

### Strategy
Maintain two identical production environments; switch traffic instantly

### Implementation

```yaml
# Blue deployment (current production)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-blue
  labels:
    app: myapp
    version: blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: myapp:1.0.0
---
# Green deployment (new version)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-green
  labels:
    app: myapp
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: app
        image: myapp:2.0.0
---
# Service (switch by changing selector)
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
    version: blue  # Change to "green" to switch traffic
  ports:
  - port: 80
    targetPort: 8080
```

**Process:**
1. Deploy green version alongside blue
2. Test green deployment
3. Switch service selector from `blue` to `green`
4. Monitor, rollback if needed by switching back to `blue`

---

## 8. Canary Deployment Pattern

### Strategy
Gradually shift traffic from old version to new version

### Implementation (using Ingress weights)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-canary
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "10"  # 10% traffic to canary
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-canary
            port:
              number: 80
```

**Process:**
1. Deploy canary version with minimal replicas
2. Route 10% traffic to canary
3. Monitor metrics, errors
4. Gradually increase canary weight (20%, 50%, 100%)
5. Promote canary to stable, remove old version

---

## Best Practices Summary

| Pattern | Use Case | Key Benefit |
|---------|----------|-------------|
| **Deployment** | Stateless apps | Easy scaling, zero-downtime updates |
| **StatefulSet** | Databases | Stable identity, persistent storage |
| **CronJob** | Scheduled tasks | Automated execution |
| **Sidecar** | Auxiliary services | Separation of concerns |
| **Init Container** | Setup tasks | Guaranteed execution order |
| **DaemonSet** | Node-level services | Runs on every node |
| **Blue-Green** | Instant switch | Zero-downtime, easy rollback |
| **Canary** | Gradual rollout | Risk mitigation |

---

**Choose the pattern that best matches your application's requirements and operational constraints.**
