from sentiment_engine.base import BaseSentimentProvider

class SentimentEngine:
    """
    High-level engine for sentiment analysis.
    Accepts any provider implementing BaseSentimentProvider.
    """

    def __init__(self, provider: BaseSentimentProvider):
        self.provider = provider

    def analyze(self, title: str, publication_date: str, summary: str, content: str, categories: list[str], tags: list[str]) -> dict[str, str]:
        return self.provider.analyze(
            title=title,
            publication_date=publication_date,
            summary=summary,
            content=content,
            categories=", ".join(categories),
            tags=", ".join(tags)
        )
