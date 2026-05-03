import asyncio
import json
import logging

from google import genai
from google.genai import types

from config import settings

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_BASE = 1  # seconds


class GeminiService:
    def __init__(self):
        self._client: genai.Client | None = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    async def generate(self, prompt: str) -> dict | None:
        for attempt in range(MAX_RETRIES):
            try:
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=settings.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        response_mime_type="application/json",
                    ),
                )

                text = response.text.strip()
                if not text:
                    logger.warning("Empty response from Gemini (attempt %d)", attempt + 1)
                    continue

                return json.loads(text)

            except json.JSONDecodeError as e:
                logger.warning("Invalid JSON from Gemini (attempt %d): %s", attempt + 1, e)
                if attempt == MAX_RETRIES - 1:
                    return None
            except Exception as e:
                err_str = str(e).lower()
                is_retryable = any(k in err_str for k in ["rate limit", "429", "503", "unavailable", "overloaded"])
                if is_retryable and attempt < MAX_RETRIES - 1:
                    wait = BACKOFF_BASE * (2 ** attempt)
                    logger.warning("Retryable Gemini error (attempt %d), retrying in %ds: %s", attempt + 1, wait, e)
                    await asyncio.sleep(wait)
                else:
                    logger.error("Gemini call failed (attempt %d): %s", attempt + 1, e)
                    return None
        return None


gemini_service = GeminiService()
