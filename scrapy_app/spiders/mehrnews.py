from .base_spider import BaseNewsSpider
from typing import List


class MehrnewsSpider(BaseNewsSpider):
    '''
    Spider for crawling MehrNews news archive and article pages.

    Inherits:
        BaseNewsSpider — handles listing traversal and date filtering.

    Overrides:
        - Listing XPaths specific to MehrNews
        - Article detail XPaths

    Attributes:
        name: Spider name used by Scrapy commands.
        allowed_domains: Domain restriction for crawling.
        start_urls: Entry archive page to begin crawling.
    '''
    name: str = 'mehrnews'
    allowed_domains: List[str] = ['www.mehrnews.com']
    start_urls: List[str] = ['https://www.mehrnews.com/archive']

    # Listing XPaths
    LIST_BLOCK_XPATH = "//div[@class='desc']"
    TITLE_XPATH = ".//h3/a/text()"
    URL_XPATH = ".//h3/a/@href"
    DATE_XPATH = "normalize-space(.//time//text())"
    NEXT_PAGE_XPATH = "//a[contains(@class,'next') or contains(text(),'بعدی')]/@href"

    # Article XPaths
    CATEGORY_XPATH = '//ol[@class="breadcrumb"]//li[last()]/a/text()'
    SUMMARY_XPATH = "//meta[@name='description']/@content"
    BODY_XPATH = '//div[@class="item-body"]//p//text()'
    TAGS_XPATH = '//a[@rel="tag"]/text()'
