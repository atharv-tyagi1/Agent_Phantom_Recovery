import logging
import asyncio
import uuid
import json
import sys
import os

from pydantic import ValidationError
from redis.asyncio import Redis
from redis.exceptions import ResponseError

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../packages/shared-events'))
try:
    from events import TaskCreatedEvent, TaskFailedEvent
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
logger = logging.getLogger(__name__)

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")

class LLMValidationException(Exception):
    pass

async def execution_loop():
    logger.info("Starting execution engine worker...")
    redis = Redis.from_url(redis_url, decode_responses=True)
    
    # Startup Resiliency Ping
    connected = False
    while not connected:
        try:
            await redis.ping()
            connected = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning(f"Redis not ready, retrying in 2 seconds... {e}")
            await asyncio.sleep(2)

    stream_name = "execution_stream"
    dlq_name = "execution_dlq"
    group_name = "execution_group"
    consumer_name = f"worker-{uuid.uuid4().hex}"

    # Create consumer group with MKSTREAM and BUSYGROUP handling
    try:
        await redis.xgroup_create(stream_name, group_name, mkstream=True)
        logger.info(f"Created consumer group {group_name} on {stream_name}")
    except ResponseError as e:
        if "BUSYGROUP" in str(e):
            logger.info(f"Consumer group {group_name} already exists.")
        else:
            raise

    try:
        while True:
            try:
                # Read from stream
                messages = await redis.xreadgroup(
                    group_name,
                    consumer_name,
                    {stream_name: ">"},
                    count=1,
                    block=2000
                )
                
                if not messages:
                    continue

                for stream, msg_list in messages:
                    for message_id, message_data in msg_list:
                        # Handle nested JSON payloads
                        if isinstance(message_data, dict) and "payload" in message_data and isinstance(message_data["payload"], str):
                            try:
                                message_data = json.loads(message_data["payload"])
                            except json.JSONDecodeError:
                                pass

                        event_id = message_data.get("event_id", "unknown")
                        correlation_id = message_data.get("correlation_id", "unknown")
                        trace_id = message_data.get("trace_id", "unknown")

                        logger.info(f"Received message {message_id} [event_id={event_id}, correlation_id={correlation_id}]")

                        try:
                            # Poison pill protection
                            event = TaskCreatedEvent.model_validate(message_data)
                        except ValidationError as e:
                            logger.error(f"Malformed event (Poison Pill): {e} [event_id={event_id}]")
                            # DLQ Routing
                            await redis.xadd(dlq_name, message_data)
                            await redis.xack(stream_name, group_name, message_id)
                            continue

                        # Process Event
                        try:
                            # Placeholder for actual task execution logic
                            pass
                        except LLMValidationException as e:
                            logger.error(f"Validation Fallback triggered: {e} [event_id={event_id}]")
                            
                            execution_id = event.payload.get("execution_id", "unknown")
                            task_id = event.payload.get("task_id", "unknown")
                            
                            failed_event = TaskFailedEvent(
                                payload={"original_event": event.model_dump()},
                                execution_id=execution_id,
                                task_id=task_id,
                                failure_reason=str(e),
                                correlation_id=event.correlation_id,
                                trace_id=getattr(event, 'trace_id', trace_id)
                            )
                            
                            # Publish before ACK
                            await redis.xadd("task_results_stream", {"payload": failed_event.model_dump_json()})
                        except Exception as e:
                            logger.error(f"Unhandled exception processing event: {e} [event_id={event_id}]")
                            await redis.xadd(dlq_name, message_data)
                        
                        # ACK original message
                        await redis.xack(stream_name, group_name, message_id)

            except asyncio.CancelledError:
                logger.info("Worker shutting down gracefully...")
                break
            except Exception as e:
                logger.error(f"Error in Redis consumer loop: {e}")
                await asyncio.sleep(1) # Backoff
    finally:
        await redis.close()

if __name__ == "__main__":
    try:
        asyncio.run(execution_loop())
    except KeyboardInterrupt:
        pass
