# Agent Phantom Recovery — Production Deployment Guide

This guide details production deployment for **Agent Phantom Recovery** using Kubernetes, Helm/kubectl, and Redis/PostgreSQL clusters.

---

## 1. Production Architecture Overview

- **API Pods**: 3+ replicas running FastAPI (`k8s/api-deployment.yaml`).
- **Worker Pods**: 3+ replicas running `python worker_entry.py` (`k8s/worker-deployment.yaml`) with `terminationGracePeriodSeconds: 60`.
- **Web Frontend**: 2+ replicas running Next.js (`k8s/web-deployment.yaml`).
- **Database**: PostgreSQL 15+ cluster with connection pooling (`pool_size=20`, `max_overflow=10`).
- **Cache/Queue**: Redis 7+ cluster using `phantom:*` key namespaces.

---

## 2. Kubernetes Deployment Steps

### 1. Create System Namespace & Secrets
```bash
kubectl create namespace phantom-system
kubectl apply -f k8s/secrets.yaml -n phantom-system
kubectl apply -f k8s/configmap.yaml -n phantom-system
```

### 2. Apply Deployments
```bash
kubectl apply -f k8s/api-deployment.yaml -n phantom-system
kubectl apply -f k8s/worker-deployment.yaml -n phantom-system
kubectl apply -f k8s/web-deployment.yaml -n phantom-system
```

### 3. Verify Health Probes
```bash
kubectl get pods -n phantom-system
kubectl logs -l app=agent-phantom-api -n phantom-system
```

- Liveness probe: `GET /livez` (port 8000)
- Readiness probe: `GET /readyz` (port 8000)
- Health probe: `GET /healthz` (port 8000)
- Metrics endpoint: `GET /metrics` (Header `X-Metrics-Token`)

---

## 3. Database Migration Execution

Run Alembic migrations before starting new API deployments:
```bash
kubectl exec -it deployment/agent-phantom-api -n phantom-system -- alembic upgrade head
```
Reversible downgrade:
```bash
kubectl exec -it deployment/agent-phantom-api -n phantom-system -- alembic downgrade -1
```
