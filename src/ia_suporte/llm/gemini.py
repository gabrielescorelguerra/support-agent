import time

from google import genai

from ia_suporte.config import settings


class GeminiLLM:
    def __init__(self, model):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = model
        self.max_retries = 3

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
