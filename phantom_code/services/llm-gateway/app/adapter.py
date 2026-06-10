import os
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

logger = logging.getLogger(__name__)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class OpenRouterAdapter:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "Agent Phantom Recovery",
            },
            timeout=120.0
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
    )
    async def generate_completion(self, model: str, messages: list):
        try:
            response = await self.client.post("/chat/completions", json={
                "model": model,
                "messages": messages,
                "response_format": {"type": "json_object"}
            })
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {e}")
            raise
