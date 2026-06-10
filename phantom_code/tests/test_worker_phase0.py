import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import json
import sys
import os

# Add paths to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../services/execution-engine/app'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../packages/shared-events'))

from worker import execution_loop, LLMValidationException
from events import TaskCreatedEvent, TaskFailedEvent

@pytest.fixture
def mock_redis():
    with patch('worker.Redis.from_url') as mock_redis_cls:
        mock_instance = AsyncMock()
        mock_redis_cls.return_value = mock_instance
        # Mock ping to succeed
        mock_instance.ping.return_value = True
        
        # Prevent tight loop starvation when xreadgroup returns empty
        async def mock_xreadgroup(*args, **kwargs):
            await asyncio.sleep(0.05)
            return []
        mock_instance.xreadgroup.side_effect = mock_xreadgroup
        
        yield mock_instance

@pytest.mark.asyncio
async def test_redis_startup_delay(mock_redis):
    # Simulate first ping failing, second succeeding
    mock_redis.ping.side_effect = [Exception("Connection refused"), True]
    
    # We run the loop but cancel it almost immediately to avoid infinite loop
    task = asyncio.create_task(execution_loop())
    await asyncio.sleep(0.1)
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
        
    assert mock_redis.ping.call_count > 0

@pytest.mark.asyncio
async def test_mkstream_and_busygroup(mock_redis):
    # Simulate BUSYGROUP error
    from redis.exceptions import ResponseError
    mock_redis.xgroup_create.side_effect = ResponseError("BUSYGROUP Consumer Group name already exists")
    
    task = asyncio.create_task(execution_loop())
    await asyncio.sleep(0.1)
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
        
    mock_redis.xgroup_create.assert_called_with("execution_stream", "execution_group", mkstream=True)

@pytest.mark.asyncio
async def test_poison_pill_routing(mock_redis):
    # Malformed data
    malformed_msg = {"event_id": "123", "payload": "not_valid_schema"}
    
    call_count = {"count": 0}
    async def mock_xreadgroup(*args, **kwargs):
        if call_count["count"] == 0:
            call_count["count"] += 1
            return [("execution_stream", [("12345-0", malformed_msg)])]
        else:
            await asyncio.sleep(0.1)
            return []
            
    mock_redis.xreadgroup.side_effect = mock_xreadgroup
    
    task = asyncio.create_task(execution_loop())
    await asyncio.sleep(0.1)
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
        
    # Should be routed to DLQ
    mock_redis.xadd.assert_any_call("execution_dlq", malformed_msg)
    # Should be acked
    mock_redis.xack.assert_any_call("execution_stream", "execution_group", "12345-0")
