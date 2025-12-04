from abc import ABC, abstractmethod
from typing import Any


class BaseSentimentProvider(ABC):
    """
    Base class for all LLM providers (Ollama, Gemini, etc).
    Handles:
    - Loading the prompt template from file
    - Building final prompt per article
    - Parsing model JSON output
    """

    def __init__(self, prompt_format: str):
        self.prompt_template = prompt_format

    @abstractmethod
    def generate(self, prompt: str) -> str:
        '''Generate raw model output.'''
        pass

    def build_prompt(self, **kwargs: Any) -> str:
        '''Format prompt with article fields.'''
        return self.prompt_template.format(**kwargs)

    def analyze(self, **fields: Any) -> dict:
        '''
        High-level method:
        1. Build prompt
        2. Call LLM provider
        3. Parse JSON
        '''

        import json

        prompt = self.build_prompt(**fields)
        raw_output = self.generate(prompt)

        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            raise ValueError(
                f'[ERROR] Provider returned invalid JSON:\n{raw_output}')
