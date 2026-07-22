import base64
import os
import logging
from typing import Any, Dict, Optional, Type
import httpx
from pydantic import BaseModel, Field

from core.config import settings
from core.tools.base import BaseTool

logger = logging.getLogger(__name__)

NVIDIA_OCR_INVOKE_URL = "https://ai.api.nvidia.com/v1/cv/nvidia/nemotron-ocr-v2"


class NemotronOCRArgs(BaseModel):
    image_path: str = Field(
        ...,
        description="Path to the image file (PNG, JPG, JPEG) to perform OCR on."
    )
    api_key: Optional[str] = Field(
        None,
        description="Optional NVIDIA API key override. Defaults to system setting."
    )


class NemotronOCRTool(BaseTool):
    """
    NVIDIA Nemotron-OCR-v2 vision/OCR tool for high-precision text and code extraction from images.
    """

    @property
    def name(self) -> str:
        return "nemotron_ocr"

    @property
    def description(self) -> str:
        return (
            "Extract pixel-accurate text, terminal logs, code snippets, or structured data "
            "from an image file using NVIDIA Nemotron-OCR-v2."
        )

    @property
    def args_schema(self) -> Type[BaseModel]:
        return NemotronOCRArgs

    async def execute(self, image_path: str, api_key: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        target_key = api_key or settings.NVIDIA_API_KEY
        if not target_key or target_key == "placeholder-nvidia-key":
            return {
                "success": False,
                "output": None,
                "error": "NVIDIA API Key is missing or unconfigured."
            }

        if not os.path.exists(image_path):
            return {
                "success": False,
                "output": None,
                "error": f"Image file not found at path: {image_path}"
            }

        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            # Basic check for base64 size constraint
            if len(image_b64) > 180_000:
                logger.warning(f"Image {image_path} base64 length ({len(image_b64)}) exceeds 180k limit.")

            headers = {
                "Authorization": f"Bearer {target_key}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            payload = {
                "input": [
                    {
                        "type": "image_url",
                        "url": f"data:image/png;base64,{image_b64}"
                    }
                ]
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(NVIDIA_OCR_INVOKE_URL, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

            return {
                "success": True,
                "output": str(data),
                "data": data,
                "error": None
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"[NemotronOCR] HTTP error {e.response.status_code}: {e.response.text}")
            return {
                "success": False,
                "output": None,
                "error": f"NVIDIA API HTTP Error {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            logger.error(f"[NemotronOCR] Unexpected error: {e}", exc_info=True)
            return {
                "success": False,
                "output": None,
                "error": f"OCR extraction failed: {str(e)}"
            }
