from google import genai
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ia_suporte.config import settings
from ia_suporte.llm.base import LLM


class GeminiLLM(LLM):
    def __init__(self, model: str, api_key: str | None = None):
        self.client = genai.Client(api_key=api_key or settings.gemini_api_key)
        self.model = model

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=2),
        reraise=True,
    )
    def generate(self, prompt: str):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        return response.text
