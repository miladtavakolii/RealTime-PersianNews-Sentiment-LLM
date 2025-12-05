from ollama import Client
from sentiment_engine.base import BaseSentimentProvider


class OllamaClient(BaseSentimentProvider):
    '''
    Local LLM sentiment provider using the Ollama engine.

    This class implements the `generate` method from BaseSentimentProvider
    and communicates with the local Ollama server to run the configured model.

    Attributes:
        model:
            Name of the Ollama model to use (e.g., 'gemma3:4b-it-qat').
        client:
            Client instance used to send generation requests.
    '''

    def __init__(self, prompt_template: str, model: str = 'gemma3:4b-it-qat'):
        '''
        Initialize the Ollama sentiment provider.

        Args:
            prompt_template:
                Base LLM prompt template.
            model:
                Name of the Ollama model to use.
                Defaults to 'gemma3:4b-it-qat'.
        '''
        super().__init__(prompt_template=prompt_template)
        self.client = Client()
        self.model = model

    def generate(self, prompt: str) -> str:
        '''
        Send the formatted prompt to the local Ollama server and return
        the raw model response.

        Args:
            prompt: Fully prepared prompt string.

        Returns:
            Raw text output from the Ollama model.
        '''
        response = self.client.generate(
            model=self.model,
            prompt=prompt,
            stream=False
        )
        return response['response']
