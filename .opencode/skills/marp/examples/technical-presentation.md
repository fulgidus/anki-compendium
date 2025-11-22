# Technical Presentation Example

This example demonstrates a technical presentation for developers or engineering teams using Marp.

---

## Complete Technical Presentation

```markdown
---
marp: true
theme: default
paginate: true
backgroundColor: #1a1a1a
color: #f0f0f0
style: |
  section {
    font-family: 'Fira Code', 'Courier New', monospace;
  }
  h1 {
    color: #4da6ff;
    font-size: 3rem;
  }
  h2 {
    color: #4da6ff;
    font-size: 2rem;
  }
  code {
    background-color: #2d2d2d;
    color: #66d9ef;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
  }
  pre {
    background-color: #2d2d2d;
    padding: 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
  }
---

<!-- _class: lead -->

# Microservices Architecture

## Building Scalable Distributed Systems

**Senior Engineer: Alex Chen**  
*Tech Talk | March 2024*

<!--
INTRO (1 minute):
"Today we'll dive into our microservices architecture evolution.
I'll cover why we made the switch, our architecture decisions,
implementation challenges, and lessons learned."

AUDIENCE: Mix of senior and junior engineers
-->

---

## Agenda

1. **Why Microservices?** — The monolith problem
2. **Architecture Overview** — System design
3. **Technology Stack** — Tools and frameworks
4. **Service Communication** — Sync vs async
5. **Data Management** — Databases and consistency
6. **Deployment** — CI/CD and orchestration
7. **Monitoring** — Observability and debugging
8. **Lessons Learned** — What worked, what didn't

<!--
TIMING: 45 minutes total
- 5 min intro
- 30 min content (slides + demos)
- 10 min Q&A
-->

---

## The Monolith Problem

### Before: Challenges

❌ **Deployment Risk** — One bug breaks everything  
❌ **Scaling Limits** — Can't scale components independently  
❌ **Tech Lock-in** — Stuck with single language/framework  
❌ **Team Bottlenecks** — All teams share one codebase  
❌ **Long Build Times** — 30+ minutes per deployment

### Impact

- Deploys: Once per week (high risk)
- Downtime: 2-3 hours per month
- Developer velocity: Slowing

<!--
CONTEXT:
Our monolith was 500K lines of C#.
6 teams, 40 engineers all working in same repo.
Merge conflicts daily.

PAIN POINT:
"Remember the Black Friday incident when a small change crashed checkout?"
-->

---

## Why Microservices?

### Goals

✅ **Independent Deployability** — Deploy services separately  
✅ **Team Autonomy** — Teams own their services  
✅ **Technology Freedom** — Choose best tool per service  
✅ **Fault Isolation** — Failures contained  
✅ **Scalability** — Scale hot paths independently

### Trade-offs

- **Complexity**: More moving parts
- **Operations**: Requires strong DevOps
- **Data Consistency**: Eventual consistency challenges

<!--
HONEST ASSESSMENT:
Microservices aren't free. They add complexity.
Only worth it if you have:
- Multiple teams
- Need for independent scaling
- Mature DevOps practices

"If you can't build a monolith well, microservices won't save you."
-->

---

## Architecture Overview

![bg right:50%](architecture-diagram.png)

### Core Services

- **API Gateway** (Kong)
- **User Service** (Node.js)
- **Product Service** (Python)
- **Order Service** (Go)
- **Payment Service** (Java)
- **Notification Service** (Node.js)

### Infrastructure

- **Kubernetes** for orchestration
- **PostgreSQL** for data
- **Redis** for caching
- **Kafka** for events

<!--
ARCHITECTURE DECISIONS:
- API Gateway: Single entry point, auth, rate limiting
- Polyglot: Use right tool per service
- Event-driven: Async communication via Kafka

DEMO:
Show live architecture dashboard (Grafana or similar)
-->

---

## Technology Stack

| Layer | Technology | Why |
|-------|------------|-----|
| **API Gateway** | Kong | High performance, plugin ecosystem |
| **Services** | Node.js, Python, Go, Java | Polyglot per service needs |
| **Orchestration** | Kubernetes | Industry standard, auto-scaling |
| **Databases** | PostgreSQL, MongoDB | SQL for transactions, NoSQL for flexibility |
| **Message Queue** | Apache Kafka | High throughput, event streaming |
| **Caching** | Redis | Fast, distributed caching |
| **Monitoring** | Prometheus + Grafana | Metrics, visualization |
| **Logging** | ELK Stack | Centralized logging |

<!--
TECH CHOICES:
- Kong over AWS API Gateway: Cost and flexibility
- Kubernetes over ECS: Portability
- Kafka over RabbitMQ: Event sourcing and replay
-->

---

## Service Communication

### Synchronous (REST/gRPC)

```javascript
// REST Example
app.get('/api/orders/:id', async (req, res) => {
  const order = await orderService.getOrder(req.params.id);
  const user = await userService.getUser(order.userId);
  const product = await productService.getProduct(order.productId);
  
  res.json({ order, user, product });
});
```

**Use Case:** Read operations, low latency needs

<!--
SYNC COMMUNICATION:
Pros: Simple, immediate response
Cons: Coupling, cascading failures, latency

ANTI-PATTERN:
Avoid deep call chains (service A → B → C → D)
-->

---

## Service Communication

### Asynchronous (Events)

```javascript
// Kafka Producer (Order Service)
await producer.send({
  topic: 'order.created',
  messages: [
    { value: JSON.stringify({ orderId, userId, total }) }
  ]
});

// Kafka Consumer (Notification Service)
consumer.on('message', async (message) => {
  const { orderId, userId } = JSON.parse(message.value);
  await sendOrderConfirmationEmail(userId, orderId);
});
```

**Use Case:** Notifications, background processing

<!--
ASYNC BENEFITS:
- Decoupling: Services don't need to know about each other
- Resilience: Failures don't cascade
- Scalability: Can process at own pace

CHALLENGE:
Eventual consistency, debugging harder
-->

---

## Data Management

### Database per Service

![width:900px](database-per-service.png)

### Challenges

1. **No Joins** — Can't join across databases
2. **Transactions** — Distributed transactions are hard
3. **Data Duplication** — Some data replicated

<!--
DATA STRATEGY:
Each service owns its data.
No shared databases.

SOLUTION TO JOINS:
- API composition (aggregate in API layer)
- CQRS (Command Query Responsibility Segregation)
- Event-driven data replication
-->

---

## Handling Distributed Transactions

### Saga Pattern

```
Order Service:    Create Order → [Rollback Order]
  ↓                                     ↑
Payment Service:  Charge Card → [Refund Card]
  ↓                                     ↑
Inventory Service: Reserve Stock → [Release Stock]
```

**Choreography:** Each service listens for events and reacts

**Orchestration:** Central coordinator manages flow

<!--
SAGA EXAMPLE:
If payment fails, order is cancelled and inventory released.

IMPLEMENTATION:
We use event-driven saga (choreography).
Each service publishes success/failure events.

TRADE-OFF:
Complexity vs. consistency
-->

---

## API Gateway Pattern

```
Client → [API Gateway] → Service Discovery
              ↓
        ┌─────┴─────┬─────────┬─────────┐
        ↓           ↓         ↓         ↓
    User Svc    Order Svc  Product  Payment
```

### Gateway Responsibilities

- **Authentication** — JWT validation
- **Rate Limiting** — Per-client throttling
- **Load Balancing** — Distribute traffic
- **Caching** — Reduce backend load
- **Request Routing** — Path-based routing

<!--
GATEWAY BENEFITS:
Single entry point simplifies client logic.
Centralized cross-cutting concerns.

RISKS:
Single point of failure (mitigate with HA)
-->

---

## CI/CD Pipeline

```
Code Push → GitHub
    ↓
  CI Build (GitHub Actions)
    ↓
  Run Tests (Unit, Integration)
    ↓
  Build Docker Image
    ↓
  Push to Registry (ECR)
    ↓
  Deploy to K8s (ArgoCD)
    ↓
  Health Check
    ↓
  Production
```

### Deployment Strategy

- **Blue-Green:** Zero downtime
- **Canary:** Gradual rollout (10% → 50% → 100%)
- **Rollback:** Automated on failure

<!--
CI/CD BENEFITS:
- Deploy 10x per day vs. once per week
- Automated testing catches regressions
- Rollback in seconds

DEMO:
Show GitHub Actions workflow and ArgoCD dashboard
-->

---

## Monitoring & Observability

### The Three Pillars

1. **Metrics** (Prometheus + Grafana)
2. **Logs** (ELK Stack)
3. **Traces** (Jaeger)

### Key Metrics

- **Latency:** p50, p95, p99 response times
- **Traffic:** Requests per second
- **Errors:** Error rate and types
- **Saturation:** CPU, memory, disk usage

<!--
OBSERVABILITY:
Essential for distributed systems.
Without it, debugging is impossible.

ALERTING:
PagerDuty integration for critical issues.
On-call rotation.
-->

---

## Distributed Tracing

```
[API Gateway] ────────────────────────────────────┐
    │                                              │
    ├─ [User Service]                             │
    │      │                                       │
    │      └─ [Database Query] 45ms               │
    │                                              │
    ├─ [Order Service]                            │ Total: 320ms
    │      ├─ [Database Query] 60ms               │
    │      └─ [Payment Service]                   │
    │             ├─ [Stripe API] 180ms           │
    │             └─ [Database Update] 20ms       │
    │                                              │
    └─ [Product Service] ──────────────────────────┘
           └─ [Cache Hit] 5ms
```

**Tool:** Jaeger for end-to-end request tracing

<!--
TRACING EXAMPLE:
This shows where time is spent in a request.
We can identify bottlenecks (Stripe API = 180ms).

ACTION:
Cache payment provider responses when possible.
-->

---

## Lessons Learned

### ✅ What Worked

- **Event-Driven Architecture** — Reduced coupling
- **Kubernetes** — Auto-scaling, self-healing
- **Polyglot** — Right tool for each job
- **Observability** — Fast debugging

### ❌ What Didn't

- **Too Many Services Initially** — Over-fragmentation
- **Shared Libraries** — Created coupling
- **Synchronous Calls** — Cascading failures
- **Under-investing in DevOps** — Operational pain

<!--
BIGGEST LESSON:
Start with fewer, larger services.
Split only when needed (team size, scaling).

ANTI-PATTERN:
Don't create one service per database table.
-->

---

## Best Practices

1. **Design for Failure** — Assume services will fail
2. **Circuit Breakers** — Prevent cascading failures
3. **Idempotency** — Retry-safe operations
4. **API Versioning** — Backward compatibility
5. **Health Checks** — Liveness and readiness probes
6. **Centralized Logging** — Correlation IDs
7. **Documentation** — OpenAPI specs for all APIs
8. **Testing** — Contract tests between services

<!--
CIRCUIT BREAKER EXAMPLE:
If payment service is down, fail fast instead of waiting.
Return cached response or degraded experience.
-->

---

## Code Example: Circuit Breaker

```javascript
const CircuitBreaker = require('opossum');

const options = {
  timeout: 3000, // 3 seconds
  errorThresholdPercentage: 50,
  resetTimeout: 30000 // 30 seconds
};

const breaker = new CircuitBreaker(callExternalService, options);

breaker.fallback(() => {
  return { status: 'degraded', message: 'Using cached data' };
});

app.get('/api/data', async (req, res) => {
  const result = await breaker.fire(req.params);
  res.json(result);
});
```

<!--
CIRCUIT BREAKER:
Protects against slow/failing dependencies.
Falls back to cached data or error gracefully.

LIBRARY: opossum (Node.js), Hystrix (Java), Polly (.NET)
-->

---

## Performance Results

### Before vs. After Microservices

| Metric | Monolith | Microservices | Improvement |
|--------|----------|---------------|-------------|
| Deployment Frequency | 1x/week | 10x/day | **10x** |
| Lead Time | 5 days | 4 hours | **30x** |
| MTTR | 2 hours | 15 minutes | **8x** |
| Availability | 99.5% | 99.95% | **+0.45%** |
| p95 Latency | 800ms | 200ms | **4x faster** |

<!--
RESULTS:
Clear improvement in velocity and reliability.

COST:
Infrastructure costs increased 2x.
But revenue increased 5x due to faster iteration.

ROI: Positive
-->

---

## Q&A

<!-- _class: lead -->

# Questions?

**Contact:**  
alex.chen@company.com  
GitHub: @alexchen

**Resources:**  
- Architecture Diagrams: [Link]
- Code Examples: [GitHub Repo]
- Microservices Guide: [Confluence]

---
```

---

## Tips for Technical Presentations

### Structure

1. **Context** — Why are we here?
2. **Problem** — What are we solving?
3. **Solution** — How did we solve it?
4. **Implementation** — Technical details
5. **Results** — Did it work?
6. **Lessons** — What did we learn?

### Code Examples

- Use syntax highlighting
- Keep code snippets short (< 20 lines)
- Focus on concepts, not implementation details
- Provide GitHub links for full code

### Visuals

- Architecture diagrams essential
- Use flowcharts for processes
- Show metrics and graphs (before/after)
- Include screenshots of tools/dashboards

### Delivery

- Know your audience (senior vs. junior)
- Live demos when possible (with backups)
- Encourage questions throughout
- Share resources and follow-up materials

---

Use this template for technical deep-dives, architecture reviews, or tech talks! 💻
