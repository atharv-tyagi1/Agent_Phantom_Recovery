import pytest
import asyncio
from core.workers.queue_broker import QueueBroker


@pytest.mark.asyncio
async def test_queue_broker_enqueue_dlq():
    job_id = await QueueBroker.enqueue(
        redis_client=None,
        queue_name="webhook",
        job_type="push_event",
        payload={"repo": "demo"},
        idempotency_key="idempotency-key-001"
    )
    assert job_id == "idempotency-key-001"

    # DLQ routing test data structure
    job_data = {
        "job_id": "test-job-999",
        "job_type": "clone",
        "payload": {},
        "attempts": 3
    }
    await QueueBroker.route_to_dlq(redis_client=None, job_data=job_data, error_msg="Terminal timeout error")
    assert job_data["terminal_error"] == "Terminal timeout error"
