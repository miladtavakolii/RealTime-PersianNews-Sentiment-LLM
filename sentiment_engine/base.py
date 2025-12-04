from abc import ABC, abstractmethod
from typing import Any
import json
import re


class BaseSentimentProvider(ABC):
    """
    Base class for all LLM providers (Ollama, Gemini, etc).
    Handles:
    - Loading the prompt template from file
    - Building final prompt per article
    - Parsing model JSON output
    """

    def __init__(self, prompt_template: str):
        self.prompt_template = prompt_template

    @abstractmethod
    def generate(self, prompt: str) -> str:
        '''Generate raw model output.'''
        pass

    def build_prompt(self, **kwargs: Any) -> str:
        '''Format prompt with article fields.'''
        return self.prompt_template.format(**kwargs)

    def extract_json(self, text: str) -> dict:
        """
        Extract valid JSON from any LLM output.
        Removes markdown fences, extra text, and returns parsed dict.
        """
        # Remove markdown code fences
        text = text.strip()
        text = re.sub(r"^```[a-zA-Z]*", "", text)
        text = re.sub(r"```$", "", text)
        text = text.strip()

        # Try parse as JSON directly
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # If JSON is inside text somewhere:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group(0))

        raise ValueError("[ERROR] No valid JSON found in model output")

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
            return self.extract_json(raw_output)
        except json.JSONDecodeError:
            raise ValueError(
                f'[ERROR] Provider returned invalid JSON:\n{raw_output}')
