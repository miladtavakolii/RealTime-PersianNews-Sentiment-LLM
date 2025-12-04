from ollama import Client
from sentiment_engine.base import BaseSentimentProvider


class OllamaClient(BaseSentimentProvider):
    """
    Ollama sentiment provider. 
    Uses local LLM models.
    """

    def __init__(self, prompt_template: str, model: str = "gemma3:4b-it-qat"):
        super().__init__(prompt_template=prompt_template)
        self.client = Client()
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            stream=False
        )
        return response["response"]
