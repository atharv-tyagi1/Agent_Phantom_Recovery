import json
import logging
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class LLMValidationException(Exception):
    pass

class LLMValidator:
    def __init__(self, adapter):
        self.adapter = adapter

    async def generate_and_validate(self, model: str, messages: list, schema: type[BaseModel], max_repairs=2):
        attempts = 0
        while attempts <= max_repairs:
            response = await self.adapter.generate_completion(model, messages)
            try:
                content = response["choices"][0]["message"]["content"]
                parsed_json = json.loads(content)
                validated_data = schema(**parsed_json)
                return validated_data
            except (json.JSONDecodeError, ValidationError) as e:
                attempts += 1
                logger.warning(f"Validation failed on attempt {attempts}: {e}")
                if attempts > max_repairs:
                    raise LLMValidationException(f"Max repair attempts exceeded. Last error: {e}")
                
                # Repair prompt
                repair_prompt = f"Your previous output failed schema validation:\n{e}\nPlease provide the correct JSON."
                messages.append({"role": "assistant", "content": content})
                messages.append({"role": "user", "content": repair_prompt})
