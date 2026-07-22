"""
WebSocket endpoint: streams real-time execution events to the IDE client.
Events are sourced from Redis pub/sub keyed by execution_id.
"""
import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.memory.manager import memory_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/executions/{execution_id}")
async def execution_stream(websocket: WebSocket, execution_id: str):
    """
    Stream all session events for an execution in real-time.
    Client connects and receives a burst of historical events, then live updates
    are pushed every time a new event is appended to the session log.
    """
    await websocket.accept()
    logger.info(f"[WS] Client connected for execution {execution_id}")

    # Track how many events we've already sent
    last_sent_index = 0

    try:
        while True:
            # Fetch current full session log
            events = await memory_manager.get_session(execution_id)

            # Push any new events since last poll
            if len(events) > last_sent_index:
                new_events = events[last_sent_index:]
                for event in new_events:
                    await websocket.send_text(json.dumps(event))
                last_sent_index = len(events)

                # Check if execution has reached a terminal state
                terminal_states = {"COMPLETED", "FAILED", "CANCELLED"}
                latest = new_events[-1]
                if latest.get("type") == "state_change" and latest.get("status") in terminal_states:
                    # Send final close message then break
                    await websocket.send_text(json.dumps({"type": "stream_end", "status": latest.get("status")}))
                    break

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected from execution {execution_id}")
    except Exception as e:
        logger.error(f"[WS] Error in execution stream {execution_id}: {e}")
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass
