from .base_spider import BaseNewsSpider


class MashreghnewsSpider(BaseNewsSpider):
    '''
    Spider for crawling MashreghNews news archive and article pages.

    Inherits:
        BaseNewsSpider — handles listing traversal and date filtering.

    Overrides:
        - Listing XPaths specific to MashreghNews
        - Article detail XPaths

    Attributes:
        name: Spider name used by Scrapy commands.
        allowed_domains: Domain restriction for crawling.
        start_urls: Entry archive page to begin crawling.
    '''
    name = 'mashreghnews'
    allowed_domains = ['www.mashreghnews.ir']
    start_urls = ['https://www.mashreghnews.ir/archive']

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
    TAGS_XPATH = '//section[contains(@class,"tags")][.//header//h2[contains(normalize-space(),"برچسب")]]//ul/li/a/text()'
