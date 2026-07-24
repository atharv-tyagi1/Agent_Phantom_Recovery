# Agent Phantom Recovery — Developer Onboarding Guide

Welcome to the development guide for **Agent Phantom Recovery**. This guide explains how to set up your local development environment, run services, execute test suites, and deploy to Kubernetes.

---

## 1. Architecture Quick Reference

- **Identity Layer (GitHub OAuth)**: User authentication, sign-in, profile, and organization access.
- **Automation Layer (GitHub App)**: Installation access tokens (`installation_access_token`), webhooks, checks, automated PR creation.
- **API Gateway**: FastAPI running on port 8000.
- **Frontend App**: Next.js 16 (Turbopack) with Nonce CSP Edge Middleware running on port 3000.
- **Background Queue Broker**: Redis-backed queue system with isolated namespaces (`phantom:*`).
- **Standalone Worker**: Async queue consumer running `python worker_entry.py`.

---

## 2. Local Environment Setup

### Prerequisites
- Python 3.11+
- Node.js 20+ & npm / pnpm
- Docker & Docker Compose
- PostgreSQL 15+ & Redis 7+

### Backend Setup
```bash
cd services/api
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd apps/web
npm install
```

---

## 3. Running Local Services

### Start Infrastructure Dependencies
```bash
docker-compose up -d db redis
```

### Run FastAPI Server
```bash
cd services/api
python -m uvicorn main:app --reload --port 8000
```

### Run Standalone Background Worker
```bash
cd services/api
python worker_entry.py
```

### Run Next.js Frontend
```bash
cd apps/web
npm run dev
```

---

## 4. Running Test Suites & Release Gate

### Run Pytest Suite
```bash
set PYTHONPATH=services/api
python -m pytest services/api/tests/
```

### Run TypeScript Compiler Check
```bash
cd apps/web
npx tsc --noEmit
```

### Run Production Readiness Gate
```bash
python services/api/scripts/production_readiness_gate.py
```
