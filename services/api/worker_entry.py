import asyncio
import logging
import signal
import sys
import time
from typing import Dict, Any
import redis.asyncio as redis
from core.config import settings
from core.workers.queue_broker import QueueBroker, PoisonMessageError
from core.observability.logging_config import configure_structured_logging

configure_structured_logging()
logger = logging.getLogger("phantom.worker")

running = True


def handle_shutdown(sig, frame):
    global running
    logger.info(f"[WorkerProcess] Signal {sig} received. Initiating graceful shutdown...")
    running = False


class NonRetryableJobError(Exception):
    """Exception class for errors that must not be retried (e.g. fatal validation errors)."""
    pass


async def process_job(job_data: Dict[str, Any]):
    job_id = job_data.get("job_id")
    job_type = job_data.get("job_type")
    payload = job_data.get("payload", {})

    logger.info(f"[WorkerProcess] Processing job {job_id} ({job_type}) [Envelope v{job_data.get('version', '1.0')}]")

    # Validate payload for poison message check
    if payload.get("trigger_poison"):
        raise NonRetryableJobError("Fatal poison message payload received")

    await asyncio.sleep(0.1)
    logger.info(f"[WorkerProcess] Job {job_id} completed successfully.")


async def worker_loop():
    global running
    redis_client = redis.from_url(settings.REDIS_URL)
    logger.info("[WorkerProcess] Agent Phantom Dedicated Worker active. Listening on queues...")

    try:
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)
    except (ValueError, AttributeError):
        pass  # Windows thread signal handling fallback

    queues = ["webhook", "clone", "index", "execution", "pr"]

    while running:
        for q in queues:
            if not running:
                break
            try:
                job = await QueueBroker.dequeue(redis_client, q, timeout=1)
                if job:
                    attempts = job.get("attempts", 0) + 1
                    job["attempts"] = attempts
                    try:
                        await process_job(job)
                    except NonRetryableJobError as fatal_err:
                        logger.error(f"[WorkerProcess] Non-retryable error for job {job.get('job_id')}: {fatal_err}")
                        await QueueBroker.route_to_dlq(redis_client, job, str(fatal_err))
                    except Exception as e:
                        logger.error(f"[WorkerProcess] Retryable error processing job {job.get('job_id')}: {e}")
                        if attempts < job.get("max_retries", 3):
                            backoff = min(2 ** attempts, 60)
                            logger.info(f"[WorkerProcess] Retrying job {job.get('job_id')} in {backoff}s...")
                            await asyncio.sleep(backoff)
                            await QueueBroker.enqueue(redis_client, q, job.get("job_type"), job.get("payload"))
                        else:
                            await QueueBroker.route_to_dlq(redis_client, job, str(e))
            except Exception as e:
                logger.error(f"[WorkerProcess] Worker loop exception on queue {q}: {e}")
                await asyncio.sleep(1)

    await redis_client.close()
    logger.info("[WorkerProcess] Worker process cleanly shutdown.")


if __name__ == "__main__":
    asyncio.run(worker_loop())
