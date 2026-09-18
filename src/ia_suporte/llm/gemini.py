import time

from google import genai

from ia_suporte.config import settings
from ia_suporte.llm.base import LLM


class GeminiLLM(LLM):
    def __init__(self, model: str, api_key: str | None = None):
        self.client = genai.Client(api_key=api_key or settings.gemini_api_key)
        self.model = model
        self.max_retries = 3

    # gera uma resposta do modelo Gemini para o prompt fornecido, com tentativas de retry em caso de falha
    def generate(self, prompt: str):
        for attempt in range(self.max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )

                return response.text

            except Exception:
                if attempt == self.max_retries - 1:
                    raise

                delay = 2**attempt
                time.sleep(delay)
