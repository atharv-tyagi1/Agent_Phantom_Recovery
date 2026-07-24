# Agent Phantom Recovery 🚀
*The Long-Horizon Autonomous AI Engineering System That Thinks, Acts & Audits Itself.*

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/atharv-tyagi1/Agent_Phantom_Recovery)
[![Next.js 16](https://img.shields.io/badge/Next.js-16.2-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Production Gate Score](https://img.shields.io/badge/Release_Gate-100%25_Pass-emerald)](docs/production_readiness_report.md)

---

## ⚡ What is Agent Phantom Recovery?

**Agent Phantom Recovery** is an enterprise-grade autonomous engineering workforce built to solve complex software engineering problems, debug multi-service codebases, fix vulnerabilities, and execute full codebase recoveries.

Unlike conversational AI coding assistants that function as simple chatbots, Agent Phantom operates as a **closed-loop, goal-driven agentic system**:
1. **Plans & Investigates**: Uses Tree-Sitter AST call-graphs and RAG to locate exact code paths.
2. **Executes & Edits**: Modifies code in isolated workspace sandboxes with automatic Git checkpoints.
3. **Verifies & Audits**: Runs test suites and subjects every patch to an independent **Adversarial GLM 5.2 Quality Audit** before committing changes or opening a GitHub Pull Request.

---

## 🏛 Architecture Diagram

```
                                  ┌────────────────────────────────────────────────────────┐
                                  │            Enterprise Next.js 16 Edge                  │
                                  │     (Nonce-based CSP, OAuth PKCE, Antigravity IDE)     │
                                  └───────────────┬────────────────────────┬───────────────┘
                                                  │ HTTP REST              │ WebSockets
                                                  ▼                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                             FastAPI Security Gateway (Port 8000)                                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                                            │
│  ┌──────────────────────────────┐    ┌──────────────────────────────┐    ┌──────────────────────────────────────────────┐  │
│  │   Security & CSP Middleware  │    │  OAuth PKCE / State Manager  │    │  OpenTelemetry & Health Engine               │  │
│  │   (CSP, HSTS, Secret Redactor)│    │  (Replay & CSRF Protection)  │    │  (/livez, /readyz, /healthz, /metrics)       │  │
│  └──────────────┬───────────────┘    └──────────────┬───────────────┘    └──────────────────────┬───────────────────────┘  │
│                 │                                   │                                           │                          │
│                 ▼                                   ▼                                           ▼                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                 Secret Masker & Structured JSON Logger                                               │  │
│  │   (Automated Redaction of API Keys, Access Tokens, JWTs in Logs, Tracing, & Error Payloads)                         │  │
│  └──────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                 │                                                                                                          │
│                 ▼                                                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                  Dedicated Redis Queue Broker (`phantom:*`)                                          │  │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌─────────────────┐ │  │
│  │  │ Webhook Q    │   │ Clone Q      │   │ Index Q      │   │ Execution Q  │   │ PR Q         │   │ Dead Letter Q   │ │  │
│  │  └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘   └─────────────────┘ │  │
│  └──────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                 │                                                                                                          │
│                 ▼                                                                                                          │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                                   Standalone Worker Pod (`worker_entry.py`)                                          │  │
│  │   (Idempotent Processing, Bounded Exponential Backoff, Retry Classifier, Graceful Termination)                        │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────┬──────────────────────────────────────────┬──────────────────────────────────┘
                                               │                                          │
                                               ▼                                          ▼
                                ┌──────────────────────────────┐           ┌──────────────────────────────┐
                                │ PostgreSQL DB (Alembic 001)  │           │   Isolated Redis Namespaces  │
                                │ (FKs, Indexes, Unique Rules) │           │   (Queues, Locks, RateLimits)│
                                └──────────────────────────────┘           └──────────────────────────────┘
```

---

## 🔥 Key Features

- 🔄 **Closed-Loop Adversarial Engine**: Never marks a task complete based on AI output alone. Evaluated by Nemotron 3 verifiers and an independent GLM 5.2 global reviewer.
- 🔀 **Hybrid GitHub Architecture**: Decouples user identity (GitHub OAuth + PKCE) from repository automation (GitHub App short-lived tokens & webhooks).
- 🧠 **4-Tier Memory System**: Working, Session, Project, and Experience Memory for zero-drift execution.
- 🌳 **Tree-Sitter AST RAG**: Incremental AST re-indexing on git push events using symbol call-graphs.
- 🖥 **Antigravity IDE**: Deep Slate & Neon Amber multi-pane developer UI with live WebSocket state streaming.
- 🛡 **Enterprise Defense**: Nonce-based CSP, secret redactor (`***REDACTED***`), Fernet AES-256 vault, and Redis sliding-window rate limiting.

---

## ⏱ Quick Start (< 5 Minutes)

### 1. Clone & Set Environment
```bash
git clone https://github.com/atharv-tyagi1/Agent_Phantom_Recovery.git
cd Agent_Phantom_Recovery
cp .env.example .env
```

### 2. Start PostgreSQL & Redis Services
```bash
docker-compose up -d db redis
```

### 3. Run FastAPI Backend
```bash
cd services/api
python -m venv venv
venv\Scripts\activate  # On Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### 4. Run Standalone Background Worker
```bash
cd services/api
python worker_entry.py
```

### 5. Start Antigravity IDE Frontend
```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser!

---

## 🧪 Testing & Production Release Gate

Run the complete backend test suite and production release gate:

```bash
# Run 34/34 Backend Pytest Assertions
set PYTHONPATH=services/api
python -m pytest services/api/tests/

# Execute Production Readiness Release Gate
python services/api/scripts/production_readiness_gate.py
```

---

## 📚 Documentation Links

- 📖 [Master Production Readiness Dossier](docs/master_production_readiness_dossier.md)
- 🚀 [Product Context Document](product_context_document.md)
- 🛠 [Developer Onboarding Guide](docs/developer_onboarding.md)
- ☸️ [Kubernetes Deployment Guide](docs/deployment_guide.md)
- 🔒 [Security Policy](SECURITY.md)
- 🤝 [Contributing Guidelines](CONTRIBUTING.md)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
