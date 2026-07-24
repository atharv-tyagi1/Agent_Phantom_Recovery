# Agent Phantom Recovery — Hackathon Presentation Guide 🏆

Welcome judges and reviewers! This document highlights why **Agent Phantom Recovery** stands out as a groundbreaking autonomous engineering system.

---

## 🌟 The Core Innovation

Most AI coding tools are **interactive chatbots** — they generate code snippets in a chat window and rely on human engineers to copy-paste, test, debug, and push them.

**Agent Phantom Recovery** is different: it is an **autonomous software recovery workforce**:
- **Autonomous Execution**: Accepts high-level engineering goals ("Fix memory leak in redis queue broker", "Resolve 500 error in auth service") and works independently for up to 100 execution steps.
- **Tree-Sitter AST RAG**: Analyzes multi-service monorepos by indexing code symbols, call graphs, and structural AST nodes rather than naive text chunking.
- **Closed-Loop Verification**: Runs unit test suites locally and submits every generated patch to an independent **GLM 5.2 Global Reviewer** audit before committing.

---

## 🏗 Key Architectural Highlights

1. **Hybrid GitHub Architecture**: Separates OAuth Identity (user login via PKCE) from GitHub App Automation (short-lived installation access tokens).
2. **4-Tier Memory System**: Working, Session, Project, and Experience Memory for zero-drift execution.
3. **Standalone Background Worker Topology**: Production queue broker (`worker_entry.py`) handling 5 Redis queue channels + Dead Letter Queue (`phantom:queue:dlq`).
4. **100% Production Readiness Gate**: Verified by an automated gate runner checking 34 Pytest assertions and 0 TypeScript errors.

---

## 📸 Demo & Quick Trial

Check out the full product demonstration and master technical dossier in [`docs/master_production_readiness_dossier.md`](docs/master_production_readiness_dossier.md).
