import asyncio
import json
import logging
from typing import Any, Dict, Optional, Tuple, Type
from google import genai
from google.genai import types
from pydantic import BaseModel
from app.config import settings

logger = logging.getLogger("NetCoop.Gemini")

class GeminiService:
    def __init__(self):
        self.api_key = settings.google_api_key.strip()
        self.model = settings.gemini_model
        self.client: Optional[genai.Client] = None
        self.is_active: bool = False
        self.fallback_reason: Optional[str] = None
        self._initialize_and_probe()

    def _initialize_and_probe(self):
        if not self.api_key or self.api_key.startswith("your_") or len(self.api_key) < 15:
            self.is_active = False
            return

        try:
            self.client = genai.Client(api_key=self.api_key)
            # Lightweight probe verification
            resp = self.client.models.generate_content(
                model=self.model,
                contents="ping",
                config=types.GenerateContentConfig(max_output_tokens=3)
            )
            if resp and resp.text:
                self.is_active = True
                self.fallback_reason = None
                logger.info(f"Gemini API handshake succeeded with {self.model}.")
            else:
                self.fallback_reason = "Model returned empty response on verification ping"
        except Exception as e:
            err_msg = str(e)
            if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
                self.fallback_reason = "Google Gen AI quota limit exceeded (429)"
            elif "API_KEY_INVALID" in err_msg or "400" in err_msg:
                self.fallback_reason = "Invalid Google Gen AI API key provided"
            else:
                self.fallback_reason = f"Handshake failed: {err_msg[:60]}"
            self.is_active = False
            logger.warning(f"Operating in deterministic fallback mode: {self.fallback_reason}")

    async def generate_structured(
        self,
        system_instruction: str,
        user_prompt: str,
        response_schema: Optional[Type[BaseModel]] = None
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        if not self.is_active or self.client is None:
            return None, "deterministic_fallback"

        retries = settings.gemini_max_retries
        delay = 1.0

        for attempt in range(retries + 1):
            try:
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.1,
                    response_mime_type="application/json" if response_schema else None,
                    response_schema=response_schema if response_schema else None,
                )

                loop = asyncio.get_running_loop()
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None,
                        lambda: self.client.models.generate_content(
                            model=self.model,
                            contents=user_prompt,
                            config=config
                        )
                    ),
                    timeout=settings.gemini_timeout_seconds
                )

                if response.text:
                    parsed = json.loads(response.text)
                    return parsed, "gemini_ai"

            except asyncio.TimeoutError:
                logger.warning(f"Gemini API timeout (attempt {attempt + 1})")
            except Exception as e:
                logger.warning(f"Gemini API error (attempt {attempt + 1}): {e}")

            if attempt < retries:
                await asyncio.sleep(delay)
                delay *= 2

        return None, "deterministic_fallback"

gemini_service = GeminiService()