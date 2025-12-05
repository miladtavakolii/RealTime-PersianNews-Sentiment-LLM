import os
from google import genai
from sentiment_engine.base import BaseSentimentProvider


class GeminiClient(BaseSentimentProvider):
    '''
    LLM sentiment provider using Google Gemini API.

    This class implements the `generate` method from BaseSentimentProvider
    and communicates with the Gemini model using the official Google GenAI SDK.

    Attributes:
        model:
            Name of the Gemini model (e.g., 'gemini-2.5-pro').
        client:
            GenAI client instance used to send generation requests.
    '''

    def __init__(self, prompt_template: str, model: str = 'gemini-1.5-flash'):
        '''
        Initialize the Gemini sentiment provider.

        Args:
            prompt_template: Base LLM prompt template.
            model: Gemini model name.
        '''
        super().__init__(prompt_template=prompt_template)

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY not set in environment variables!')

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        '''
        Send the formatted prompt to Gemini API and return the raw text output.

        Args:
            prompt: Fully constructed prompt string.

        Returns:
            Raw text output from Gemini model.
        '''
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        # Extract plain text result
        return response.text
