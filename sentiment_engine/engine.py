from sentiment_engine.base import BaseSentimentProvider

class SentimentEngine:
    '''
    High-level sentiment analysis orchestrator.

    This class serves as a unified interface that delegates the actual
    LLM inference to a provider implementing `BaseSentimentProvider`.
    It is model-agnostic and can work with Ollama, Gemini, OpenAI, etc.

    Attributes:
        provider:
            The backend LLM provider responsible for analyzing text.
    '''

    def __init__(self, provider: BaseSentimentProvider):
        '''
        Initialize the sentiment engine.

        Args:
            provider:
                An instance of a provider capable of generating and parsing
                sentiment results.
        '''
        self.provider = provider

    def analyze(self, title: str, publication_date: str, summary: str, content: str, categories: list[str], tags: list[str]) -> dict[str, str]:
        '''
        Run full sentiment analysis on a news article.

        This method passes normalized article metadata to the underlying
        provider and returns the parsed JSON sentiment result.

        Args:
            title: The article title.
            publication_date: Publication timestamp in string format.
            summary: Short summary of the article.
            content: Main article body.
            categories: Category tags.
            tags: Additional metadata tags.

        Returns:
            Structured sentiment analysis result.
        '''
        return self.provider.analyze(
            title=title,
            publication_date=publication_date,
            summary=summary,
            content=content,
            categories=', '.join(categories),
            tags=', '.join(tags)
        )
