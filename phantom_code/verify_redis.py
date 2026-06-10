import asyncio
import json
from fakeredis import FakeAsyncRedis
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'packages/shared-events'))
from events import TaskCreatedEvent, TaskFailedEvent

async def verify_redis_streams():
    print("=== STARTING REDIS (Emulated via FakeRedis) ===")
    redis = FakeAsyncRedis(decode_responses=True)
    
    stream_name = "execution_stream"
    group_name = "execution_group"
    dlq_name = "execution_dlq"
    results_stream = "task_results_stream"
    consumer_name = "worker-test"

    print("\n[Worker] Creating Consumer Group with MKSTREAM...")
    await redis.xgroup_create(stream_name, group_name, mkstream=True)
    
    print("\n[Publisher] Publishing TaskCreated Event...")
    event = TaskCreatedEvent(payload={"task_id": "test-123", "execution_id": "exec-abc"})
    msg_id = await redis.xadd(stream_name, {"payload": event.model_dump_json()})
    print(f"  -> Published Message ID: {msg_id}")

    print("\n[Worker] Consuming from Stream...")
    messages = await redis.xreadgroup(group_name, consumer_name, {stream_name: ">"}, count=1)
    for stream, msg_list in messages:
        for m_id, m_data in msg_list:
            print(f"  -> Consumed Message ID: {m_id}")
            print(f"  -> Raw Payload: {m_data['payload'][:80]}...")
            
            print("\n[Worker] Simulating Validation Failure...")
            failed_event = TaskFailedEvent(
                payload={"original_event": m_data["payload"]},
                execution_id="exec-abc",
                task_id="test-123",
                failure_reason="Simulated validation failure for verification",
                correlation_id=event.correlation_id,
                trace_id=event.trace_id
            )
            
            print("\n[Worker] Publishing TaskFailedEvent to Results Stream...")
            res_id = await redis.xadd(results_stream, {"payload": failed_event.model_dump_json()})
            print(f"  -> Result Message ID: {res_id}")
            
            print("\n[Worker] ACKing Original Message...")
            await redis.xack(stream_name, group_name, m_id)

    print("\n=== VERIFYING ACTUAL STREAM CONTENTS ===")
    
    # Verify execution_stream is acked
    pending = await redis.xpending(stream_name, group_name)
    print(f"Pending messages in {stream_name}: {pending['pending']}")
    
    # Verify results_stream has the event
    results = await redis.xrange(results_stream, "-", "+")
    print(f"Contents of {results_stream}:")
    for r_id, r_data in results:
        parsed = json.loads(r_data["payload"])
        print(f"  [{r_id}] Event: {parsed.get('event_name')} | Reason: {parsed.get('failure_reason')}")

if __name__ == "__main__":
    asyncio.run(verify_redis_streams())
