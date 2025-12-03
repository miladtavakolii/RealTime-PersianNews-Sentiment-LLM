# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from typing import List, Optional


class NewsArticleItem(scrapy.Item):
    '''
    Item container for structured news article data extracted by spiders.

    Fields:
        title: Title of the news article.
        publication_date: The publication date in ISO format (YYYY-MM-DD HH:MM:SS).
        publication_timestamp: UNIX timestamp of the publication time.
        content: Full article body after assembling and cleaning text.
        summary: Metadata or short summary of the article if provided by the website.
        category: List of extracted article categories.
        tags: List of article tags.
        url: Absolute URL of the article page.
    '''
    title: str = scrapy.Field()  # type: ignore
    publication_date: str = scrapy.Field()  # type: ignore
    publication_timestamp: int = scrapy.Field()  # type: ignore
    content: str = scrapy.Field()  # type: ignore
    summary: Optional[str] = scrapy.Field()  # type: ignore
    category: List[str] = scrapy.Field()  # type: ignore
    tags: List[str] = scrapy.Field()  # type: ignore
    url: str = scrapy.Field()  # type: ignore
