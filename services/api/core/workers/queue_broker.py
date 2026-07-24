import json
import logging
import time
import uuid
import asyncio
from typing import Any, Dict, Optional, Tuple
import redis.asyncio as redis
from core.config import settings

logger = logging.getLogger(__name__)


class PoisonMessageError(Exception):
    """Raised when a job payload is malformed, corrupt, or unparseable."""
    pass


class QueueBroker:
    """
    Isolated Redis Queue Broker managing job queues, versioned envelopes,
    idempotency keys, poison-message classification, exponential backoff,
    and Dead Letter Queue (DLQ) routing.
    """

    QUEUES = {
        "webhook": "phantom:queue:webhook",
        "clone": "phantom:queue:clone",
        "index": "phantom:queue:index",
        "execution": "phantom:queue:execution",
        "pr": "phantom:queue:pr",
        "dlq": "phantom:queue:dlq",
    }

    @classmethod
    async def enqueue(
        cls,
        redis_client: Optional[redis.Redis],
        queue_name: str,
        job_type: str,
        payload: Dict[str, Any],
        idempotency_key: Optional[str] = None
    ) -> str:
        job_id = idempotency_key or str(uuid.uuid4())
        queue_key = cls.QUEUES.get(queue_name, f"phantom:queue:{queue_name}")

        # Idempotency check
        if idempotency_key and redis_client:
            idem_key = f"phantom:idempotency:{idempotency_key}"
            exists = await redis_client.get(idem_key)
            if exists:
                logger.info(f"[QueueBroker] Job {idempotency_key} already enqueued/processed. Skipping duplicate.")
                return idempotency_key
            await redis_client.set(idem_key, "enqueued", ex=86400)  # 24h TTL

        # Versioned job envelope (v1.0)
        job_data = {
            "version": "1.0",
            "job_id": job_id,
            "job_type": job_type,
            "payload": payload,
            "attempts": 0,
            "max_retries": 3,
            "created_at": time.time(),
        }

        if redis_client:
            await redis_client.rpush(queue_key, json.dumps(job_data))
            logger.info(f"[QueueBroker] Enqueued job {job_id} (v1.0) on {queue_key}")

        return job_id

    @classmethod
    async def dequeue(cls, redis_client: Optional[redis.Redis], queue_name: str, timeout: int = 2) -> Optional[Dict[str, Any]]:
        if not redis_client:
            return None

        queue_key = cls.QUEUES.get(queue_name, f"phantom:queue:{queue_name}")
        res = await redis_client.blpop(queue_key, timeout=timeout)
        if not res:
            return None

        _, raw_data = res
        try:
            job_data = json.loads(raw_data)
            if not isinstance(job_data, dict) or "payload" not in job_data:
                raise PoisonMessageError("Invalid job payload envelope structure")
            return job_data
        except (json.JSONDecodeError, PoisonMessageError) as e:
            logger.error(f"[QueueBroker] Poison message detected on {queue_key}: {e}")
            corrupt_envelope = {
                "version": "corrupt",
                "raw_payload": str(raw_data),
                "error": str(e),
                "failed_at": time.time(),
            }
            await cls.route_to_dlq(redis_client, corrupt_envelope, error_msg=f"PoisonMessage: {e}")
            return None

    @classmethod
    async def route_to_dlq(cls, redis_client: Optional[redis.Redis], job_data: Dict[str, Any], error_msg: str):
        job_data["failed_at"] = time.time()
        job_data["terminal_error"] = error_msg
        dlq_key = cls.QUEUES["dlq"]
        if redis_client:
            await redis_client.rpush(dlq_key, json.dumps(job_data))
            logger.error(f"[QueueBroker] Job {job_data.get('job_id')} routed to DLQ ({dlq_key}): {error_msg}")
