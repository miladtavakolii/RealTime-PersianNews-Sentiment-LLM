from .base_spider import BaseNewsSpider


class KhabaronlineSpider(BaseNewsSpider):
    name = "khabaronline"
    allowed_domains = ["www.khabaronline.ir"]
    start_urls = ["https://www.khabaronline.ir/archive"]

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
