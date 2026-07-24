# Agent Phantom Recovery — Product Context Document
*The Single Source of Truth for Product Architecture, Engineering Capabilities, Marketing Messaging, and UI/UX Design System*

---

## 1. Product Overview

### What is Agent Phantom Recovery?
**Agent Phantom Recovery** is an enterprise-grade, long-horizon autonomous engineering system designed to solve complex software engineering problems, debug multi-service codebases, fix critical vulnerabilities, and execute full codebase recoveries. Unlike conversational AI coding assistants (which function as interactive chatbots), Agent Phantom operates as a fully agentic, goal-driven execution system. Given a high-level goal, bug report, or automated GitHub push/PR event, Agent Phantom autonomously plans, investigates, edits code, executes tests in sandboxed environments, visually verifies UI/browser states, and passes through an independent global audit review before declaring task completion or opening an automated Pull Request.

### Canonical Hybrid GitHub Architecture & Hardened Security
Agent Phantom Recovery strictly decouples user identity from repository automation using a **Hybrid GitHub Architecture**:

1. **Identity Layer (GitHub OAuth)**:
   - User authentication & sign in with GitHub via Next.js Edge (`middleware.ts`) and FastAPI backend.
   - OAuth 2.0 PKCE (`code_verifier` & `code_challenge` SHA-256) and signed HMAC state token validation.
   - Automatic single-use replay protection and Fernet AES-256 token encryption at rest.
   - User identity, profile, email, avatar, and organization discovery.

2. **Automation Layer (GitHub App)**:
   - Repository installation and access management using short-lived installation access tokens (`installation_access_token`).
   - Real-time Webhook Engine listening to `push`, `pull_request`, `check_run`, and `installation` events.
   - HMAC `X-Hub-Signature-256` signature verification and `X-GitHub-Delivery` idempotency checks.
   - Automatic incremental AST re-indexing and monitoring triggers (`auto_investigate`, `auto_fix`, `auto_pr`).

3. **Enterprise Defense & Secret Masking**:
   - Next.js Edge Nonce-based Content Security Policy (`script-src 'self' 'nonce-{nonce}' 'strict-dynamic'`).
   - Automatic secret redaction (`***REDACTED***`) across all structured JSON logs, trace contexts, error messages, and database payloads.
   - Sliding-window Redis rate limiting (`phantom:rate_limit:`) and per-workspace execution quotas.

---

## 2. Core Features

### Feature 1: Closed-Loop Adversarial Execution Engine
- **Purpose**: Ensures that no task is marked complete based solely on AI output confidence; execution must pass empirical testing and independent audit verification.
- **How It Works**: Operates on a strict state machine: `Goal → Plan → Investigate → Execute → Verify → Global Review Audit → [Complete OR Reset to Re-Plan]`. The GLM 5.2 Global Reviewer audits the execution output. If the quality score falls below acceptable thresholds, the reviewer constructs a structured `AuditReport` with `rejection_reason` and `actionable_fix`, forcing the engine back to `RE_PLANNING`.
- **Benefits**: Zero silent failures, zero superficial symptom masking, guaranteed quality compliance.
- **Implementation Status**: **Fully Implemented & Verified** (`services/api/core/engine/controller.py`).

### Feature 2: Multi-Model Intelligence Pipeline
- **Purpose**: Eliminates single-model bias and latency bottlenecks by delegating specialized sub-tasks to optimal LLMs.
- **How It Works**:
  - **Planner & Reasoner**: Kimi K3 (via Zenmux.ai) handles task decomposition, visual UI reasoning, and patch architecture.
  - **Verifier**: Nemotron 3 Ultra Free verifies test assertions and execution logs.
  - **Global Reviewer**: GLM 5.2 (via OpenRouter / BigModel) acts as an unbiased quality auditor evaluating completeness, edge cases, and code standards.
- **Benefits**: High-speed planning, rock-solid verification, and objective evaluation without single-model blind spots.
- **Implementation Status**: **Fully Implemented & Verified** (`services/api/core/llm/reviewer.py`).

### Feature 3: Standalone Worker Topology & Queue Broker
- **Purpose**: Decouples heavy execution workloads from API responsiveness in production environments.
- **How It Works**: Redis Queue Broker with versioned envelopes (`"version": "1.0"`), poison-message classification, idempotency TTL (`phantom:idempotency:*`), exponential backoff retries, and Dead Letter Queue (`phantom:queue:dlq`) routing. Runs in standalone worker containers via `python worker_entry.py` with graceful `SIGTERM` / `SIGINT` shutdown handling.
- **Benefits**: Infinite horizontal scaling, zero job loss, resilient background processing.
- **Implementation Status**: **Fully Implemented & Verified** (`services/api/core/workers/queue_broker.py`, `worker_entry.py`).

### Feature 4: Repository Intelligence & AST RAG
- **Purpose**: Converts massive repositories into high-signal, deterministic evidence instead of flooding LLM context windows with raw code dumps.
- **How It Works**: Tree-Sitter AST parsers extract functions, classes, imports, and symbol definitions. A network call-graph builder maps inter-module dependencies. Vector embeddings enable semantic search over indexed symbols. Incremental AST indexer re-indexes only added, modified, or deleted diff files on git push events.
- **Benefits**: Low token cost, deep context comprehension, zero hallucinated symbol paths.
- **Implementation Status**: **Fully Implemented & Verified** (`services/api/core/repo_intel/`).

### Feature 5: Multi-Tier Memory Store
- **Purpose**: Maintains continuity across long-horizon executions and prevents contextual drift or repeated mistakes.
- **How It Works**: Maintains 4 distinct memory tiers:
  1. *Working Memory*: Live transient state key-value store for current step variables.
  2. *Session Memory*: Ordered, timestamped event log of thoughts, tool inputs, and observations.
  3. *Project Memory*: Persistent project facts, architectural rules, and user preferences.
  4. *Experience Memory*: Vector database of past verified patches and solutions retrieved via semantic similarity.
- **Benefits**: Prevents infinite loops, retains project-specific constraints, leverages past successful solutions.
- **Implementation Status**: **Fully Implemented & Verified** (`services/api/core/memory/manager.py`).

### Feature 6: Antigravity IDE (Multi-Pane Workspace)
- **Purpose**: Gives developers full real-time visibility into the agent's internal reasoning, code edits, terminal stream, and audit reviews.
- **How It Works**: A Next.js 16 full-screen application featuring a Deep Slate & Neon Amber high-density design system. Supports split-pane navigation across 6 dedicated panes: Chat & Reasoning, Monaco Code Editor, Terminal Stream, Browser Preview, Memory Store, and Step Timeline. Pushes live state via WebSockets (`/ws/executions/{id}`).
- **Benefits**: Total transparency, zero "black box" execution anxiety, real-time control.
- **Implementation Status**: **Fully Implemented & Verified** (`apps/web/src/components/ide/`).

---

## 3. Platform Hierarchy & Workspace Model

```
User
 │
 └── Workspace (Members, Invitations, Audit Logs, App Installations, Billing)
      │
      └── Project (Task Groupings & Environment Context)
           │
           └── Repository (Git Storage, Incremental AST Index, Monitoring Settings)
                │
                └── Execution (Closed-Loop Engine: Kimi K3 -> Nemotron -> GLM 5.2)
                     │
                     └── Report & Automated Pull Request
```

---

## 4. Technology Stack & Enterprise Observability

- **Frontend**: Next.js 16 (Turbopack), React 19, Nonce CSP Edge Middleware (`middleware.ts`), TailwindCSS v4, Monaco Editor, xterm.js, WebSockets.
- **Backend Service**: FastAPI (Python 3.11+), SQLAlchemy 2.0 (Hardened Pool), Fernet AES-256 Vault, Redis asyncio.
- **Security**: OAuth 2.0 PKCE, Signed HMAC State Validation, Secret Masker (`***REDACTED***`), Path & Command Sanitizers, Sliding Window Rate Limiter.
- **Observability & Probes**: OpenTelemetry Tracing (`X-Trace-ID`), Structured JSON Logger, `/livez` (liveness), `/readyz` (readiness), `/healthz` (health), `/metrics` (token-authenticated Prometheus exporter).
- **AI Pipeline**: Kimi K3 (Planner/Reasoner), Nemotron 3 Ultra (Verifier), GLM 5.2 (Global Reviewer Auditor), NVIDIA Nemotron-OCR-v2.
- **Infrastructure**: Kubernetes manifests (`k8s/api-deployment.yaml`, `k8s/worker-deployment.yaml`, `k8s/web-deployment.yaml`), Docker Compose, Alembic migration `001_phase11_hardening.py`.

---

## 5. Production Readiness Status

- **Automated Release Gate Score**: **100% (9/9 Pillars Verified)**
- **Pytest Backend Test Suite**: **33 / 33 Passed (100%)**
- **Frontend TypeScript Compiler**: **0 Type Errors**
- **System Readiness**: **EVIDENCE-BACKED PRODUCTION READY**
