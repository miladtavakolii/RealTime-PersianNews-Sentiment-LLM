from .base_spider import BaseNewsSpider
from typing import List


class TarafdariSpider(BaseNewsSpider):
    '''
    Spider for crawling Tarafdari news archive and article pages.

    Inherits:
        BaseNewsSpider — handles listing traversal and date filtering.

    Overrides:
        - Listing XPaths specific to Tarafdari
        - Article detail XPaths

    Attributes:
        name: Spider name used by Scrapy commands.
        allowed_domains: Domain restriction for crawling.
        start_urls: Entry archive page to begin crawling.
    '''
    name: str = 'tarafdari'
    allowed_domains: List[str] = ['www.tarafdari.com']
    start_urls: List[str] = ['https://www.tarafdari.com/static/page/archive']

    # Listing XPaths
    LIST_BLOCK_XPATH = '//article[contains(@class, "node-content")]'
    TITLE_XPATH = './/h2//a/text()'
    URL_XPATH = './/h2//a/@href'
    DATE_XPATH = './/abbr[@class="timeago"]/@title'
    NEXT_PAGE_XPATH = "//a[contains(@class,'next') or contains(text(),'بعدی')]/@href"

    # Article XPaths
    CATEGORY_XPATH = '//div[contains(@class,"field-name-field-category")]//div[contains(@class,"field-item")]/a/text()'
    SUMMARY_XPATH = './/div[contains(@class, "field-name-field-teaser")]//p/text()'
    BODY_XPATH = '//div[contains(@class,"field-name-body")]//div[contains(@class,"field-item")]//text()'
    TAGS_XPATH = '//div[contains(@class,"field-name-field-tags")]//div[contains(@class,"field-item")]/a/text()'
