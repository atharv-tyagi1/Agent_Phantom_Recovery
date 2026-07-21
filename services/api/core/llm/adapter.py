import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from core.llm.config import (
    OPENROUTER_BASE_URL, OPENROUTER_API_KEY,
    ZENMUX_BASE_URL, ZENMUX_API_KEY,
    PRIMARY_MODEL, FALLBACK_MODEL, VERIFIER_MODEL,
    HEADERS
)

logger = logging.getLogger(__name__)

class LLMAdapter:
    def __init__(self):
        self.openrouter_client = httpx.AsyncClient(
            base_url=OPENROUTER_BASE_URL,
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", **HEADERS},
            timeout=120.0
        )
        self.zenmux_client = httpx.AsyncClient(
            base_url=ZENMUX_BASE_URL,
            headers={"Authorization": f"Bearer {ZENMUX_API_KEY}", **HEADERS},
            timeout=120.0
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def _call_openrouter(self, model: str, messages: list):
        response = await self.openrouter_client.post("/chat/completions", json={
            "model": model,
            "messages": messages,
            "response_format": {"type": "json_object"}
        })
        response.raise_for_status()
        return response.json()

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def _call_zenmux(self, model: str, messages: list):
        response = await self.zenmux_client.post("/chat/completions", json={
            "model": model,
            "messages": messages,
            "response_format": {"type": "json_object"}
        })
        response.raise_for_status()
        return response.json()

    async def generate_completion(self, model: str, messages: list):
        if model == PRIMARY_MODEL:
            try:
                # Try Zenmux (Kimi K3)
                logger.info(f"Attempting Zenmux for model {model}")
                return await self._call_zenmux(model, messages)
            except Exception as e:
                logger.warning(f"Zenmux API failed for model {model}: {e}. Falling back to OpenRouter ({FALLBACK_MODEL}).")
                # Fallback to OpenRouter (Tencent Hy3)
                return await self._call_openrouter(FALLBACK_MODEL, messages)
        elif model == VERIFIER_MODEL or model == FALLBACK_MODEL:
            # Send directly to OpenRouter
            logger.info(f"Attempting OpenRouter for model {model}")
            return await self._call_openrouter(model, messages)
        else:
            raise ValueError(f"Unknown model requested: {model}")
