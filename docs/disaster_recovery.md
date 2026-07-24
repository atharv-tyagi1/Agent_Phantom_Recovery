# Agent Phantom Recovery — Disaster Recovery & Operations Guide

---

## 1. Database Backup & Restoration

- **Backup Schedule**: Automated PostgreSQL WAL-G / pg_dump snapshots every 6 hours.
- **Restore Command**:
  ```bash
  pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME --clean --if-exists backup_snapshot.dump
  ```
- **Alembic Migration Verification**:
  ```bash
  services/api/venv/Scripts/alembic upgrade head
  ```

---

## 2. Queue & Background Worker Failover

- **Redis Persistence**: AOF (Append-Only File) enabled with `appendfsync everysec`.
- **Dead Letter Queue (DLQ) Recovery**:
  Inspect failing DLQ entries at `phantom:queue:dlq`:
  ```python
  from core.workers.queue_broker import QueueBroker
  # Inspect failed payloads
  ```

---

## 3. Secret Rotation & Zero-Downtime Rollout

- **Fernet Token Encryption Key Rotation**: Maintain primary & secondary key array for token decryption during key rotation window.
- **GitHub App Private Key Rotation**: Register dual active GitHub App keys in GitHub App settings, replace key in K8s secret `phantom-secrets`.
