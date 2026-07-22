import unittest
import asyncio
import os
import tempfile
from unittest.mock import patch, MagicMock

from core.tools.ocr import NemotronOCRTool
from core.tools.startup import tool_registry


class TestNemotronOCRTool(unittest.TestCase):

    def setUp(self):
        self.ocr_tool = NemotronOCRTool()

    def test_tool_metadata(self):
        self.assertEqual(self.ocr_tool.name, "nemotron_ocr")
        self.assertIn("Nemotron-OCR-v2", self.ocr_tool.description)

        schema = self.ocr_tool.to_schema()
        self.assertEqual(schema["name"], "nemotron_ocr")
        self.assertIn("image_path", schema["parameters"]["properties"])

    def test_tool_registry_registration(self):
        registered = tool_registry.get_tool("nemotron_ocr")
        self.assertIsNotNone(registered)
        self.assertEqual(registered.name, "nemotron_ocr")

    def test_execute_missing_file(self):
        async def run_test():
            result = await self.ocr_tool.execute(image_path="non_existent_image.png")
            self.assertFalse(result["success"])
            self.assertIn("not found", result["error"])

        asyncio.run(run_test())

    def test_execute_mocked_success(self):
        async def run_test():
            # Create temporary image file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
                tmp_path = tmp.name

            try:
                mock_data = {"predictions": [{"text": "Hello World Agent Phantom"}]}
                
                with patch("httpx.AsyncClient.post") as mock_post:
                    mock_resp = MagicMock()
                    mock_resp.status_code = 200
                    mock_resp.raise_for_status.return_value = None
                    mock_resp.json.return_value = mock_data
                    mock_post.return_value = mock_resp

                    result = await self.ocr_tool.execute(
                        image_path=tmp_path,
                        api_key="nvapi-test-key"
                    )

                    self.assertTrue(result["success"])
                    self.assertIn("Hello World Agent Phantom", result["output"])
                    self.assertEqual(result["data"], mock_data)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
