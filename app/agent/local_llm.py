import requests

from app.config.settings import settings
from app.utils.logger import logger


class LocalLLM:
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        timeout: int = 600,
    ) -> None:
        self.model = model or settings.default_llm_model
        self.base_url = base_url or settings.ollama_base_url
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        logger.info("Generating response with model: %s", self.model)

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                },
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()["response"]