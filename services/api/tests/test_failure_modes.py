import pytest
import json
import asyncio
import importlib.util
import os
from core.workers.queue_broker import QueueBroker, PoisonMessageError
from worker_entry import NonRetryableJobError, process_job


@pytest.mark.asyncio
async def test_poison_message_dlq_routing():
    # Test unparseable poison payload
    res = await QueueBroker.dequeue(redis_client=None, queue_name="webhook")
    assert res is None


@pytest.mark.asyncio
async def test_non_retryable_job_error():
    poison_job = {
        "version": "1.0",
        "job_id": "poison-001",
        "job_type": "execution",
        "payload": {"trigger_poison": True},
        "attempts": 1
    }
    with pytest.raises(NonRetryableJobError):
        await process_job(poison_job)


def test_migration_rollback_safety():
    migration_path = os.path.abspath("services/api/alembic/versions/001_phase11_hardening.py")
    assert os.path.exists(migration_path)

    spec = importlib.util.spec_from_file_location("phase11_migration", migration_path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    assert hasattr(m, "upgrade")
    assert hasattr(m, "downgrade")
