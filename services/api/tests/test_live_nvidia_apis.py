import asyncio
import os
import base64
import tempfile
from openai import OpenAI
import httpx
import pytest

from core.config import settings
from core.tools.ocr import NemotronOCRTool
from core.llm.reviewer import GlobalReviewer


def test_live_glm_api():
    print("\n--- Testing Live GLM 5.2 NVIDIA API ---")
    reviewer = GlobalReviewer()
    report = reviewer.review_execution(
        task_goal="Fix user authentication session timeout bug",
        execution_steps=[
            {"step": 1, "action": "updated token expiry in auth.py"}
        ],
        modified_files=["services/api/core/auth.py"],
        test_results="pytest test_auth.py passed (3/3 passed)"
    )
    print(f"Status Approved: {report.approved}")
    print(f"Quality Score: {report.quality_score}")
    print(f"Summary: {report.summary}")
    assert report.approved is not None


@pytest.mark.asyncio
async def test_live_ocr_api():
    print("\n--- Testing Live Nemotron-OCR-v2 NVIDIA API ---")
    ocr_tool = NemotronOCRTool()
    
    # Create a 1x1 test PNG image file
    test_png_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(test_png_bytes)
        tmp_path = tmp.name

    try:
        result = await ocr_tool.execute(image_path=tmp_path)
        print(f"OCR Success: {result['success']}")
        assert "success" in result
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    test_live_glm_api()
    asyncio.run(test_live_ocr_api())
