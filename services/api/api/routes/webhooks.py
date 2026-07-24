import hmac
import hashlib
import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from core.config import settings
from db.session import get_db
from db.models.webhook_event import WebhookEvent, WebhookStatus
from core.github.webhook_processor import handle_webhook_event

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Webhooks"])


def verify_github_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Validate X-Hub-Signature-256 HMAC signature."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected_sig = signature_header.split("sha256=")[1]
    computed_sig = hmac.new(
        settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_sig, expected_sig)


@router.post("/api/webhooks/github", status_code=status.HTTP_200_OK)
async def receive_github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    x_github_delivery: str = Header(..., alias="X-GitHub-Delivery"),
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256")
):
    """
    Receives incoming GitHub webhooks (`push`, `pull_request`, `installation`).
    Validates HMAC signature, guarantees idempotency, persists event to DB,
    and dispatches to autonomous processor.
    """
    raw_body = await request.body()

    # Signature check (skip if using placeholder secret in dev)
    if settings.GITHUB_WEBHOOK_SECRET != "phantom-webhook-secret-key":
        if not verify_github_signature(raw_body, x_hub_signature_256):
            logger.warning(f"[Webhook] Invalid HMAC signature for delivery {x_github_delivery}")
            raise HTTPException(status_code=400, detail="Invalid signature")

    # Idempotency check via delivery_id
    existing = db.query(WebhookEvent).filter(WebhookEvent.delivery_id == x_github_delivery).first()
    if existing:
        return {"status": "ignored", "reason": "duplicate_delivery"}

    try:
        payload = json.loads(raw_body)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {e}")

    inst_id = payload.get("installation", {}).get("id")

    webhook_event = WebhookEvent(
        delivery_id=x_github_delivery,
        github_event_type=x_github_event,
        installation_id=inst_id,
        payload=payload,
        status=WebhookStatus.PROCESSING
    )
    db.add(webhook_event)
    db.commit()
    db.refresh(webhook_event)

    # Dispatch to Webhook Processor
    try:
        result = await handle_webhook_event(db, webhook_event)
        webhook_event.status = WebhookStatus.COMPLETED
        webhook_event.processed_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "processed", "result": result}
    except Exception as e:
        logger.error(f"[Webhook] Error processing event {x_github_delivery}: {e}")
        webhook_event.status = WebhookStatus.FAILED
        webhook_event.error_message = str(e)
        db.commit()
        return {"status": "failed", "error": str(e)}
