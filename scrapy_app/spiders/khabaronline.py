from .base_spider import BaseNewsSpider
from typing import List


class KhabaronlineSpider(BaseNewsSpider):
    '''
    Spider for crawling KhabarOnline news archive and article pages.

    Inherits:
        BaseNewsSpider — handles listing traversal and date filtering.

    Overrides:
        - Listing XPaths specific to KhabarOnline
        - Article detail XPaths

    Attributes:
        name: Spider name used by Scrapy commands.
        allowed_domains: Domain restriction for crawling.
        start_urls: Entry archive page to begin crawling.
    '''
    name: str = 'khabaronline'
    allowed_domains: List[str] = ['www.khabaronline.ir']
    start_urls: List[str] = ['https://www.khabaronline.ir/archive']

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
