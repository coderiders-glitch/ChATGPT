import os
import logging
from typing import Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_ENDPOINT = os.getenv("LLM_API_ENDPOINT", "https://api.openai.com/v1/chat/completions")


class LLMClient:
    """Client for interacting with the external LLM API."""

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {LLM_API_KEY}",
            "Content-Type": "application/json"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate_response(self, prompt: str) -> dict:
        """Send a prompt to the LLM and return the response."""
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(LLM_API_ENDPOINT, json=payload, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return {"response": content, "confidence": 0.95}
            except httpx.HTTPStatusError as e:
                logger.error(f"LLM API error: {e.response.status_code}")
                raise
            except Exception as e:
                logger.error(f"Unexpected LLM error: {str(e)}")
                raise

    async def health_check(self) -> bool:
        """Check if the LLM service is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(LLM_API_ENDPOINT.replace("/completions", ""), headers=self.headers)
                return response.status_code in (200, 403, 404)
        except Exception:
            return False