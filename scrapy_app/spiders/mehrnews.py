from .base_spider import BaseNewsSpider


class MehrnewsSpider(BaseNewsSpider):
    name = "mehrnews"
    allowed_domains = ["www.mehrnews.com"]
    start_urls = ["https://www.mehrnews.com/archive"]

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
