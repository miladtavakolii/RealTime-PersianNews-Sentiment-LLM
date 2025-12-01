from .base_spider import BaseNewsSpider


class IsnaSpider(BaseNewsSpider):
    name = "isna"
    allowed_domains = ["www.isna.ir"]
    start_urls = ["https://www.isna.ir/page/archive.xhtml"]

    # Listing XPaths
    LIST_BLOCK_XPATH = "//div[@class='desc']"
    TITLE_XPATH = ".//h3/a/text()"
    URL_XPATH = ".//h3/a/@href"
    DATE_XPATH = "normalize-space(.//time//text())"
    NEXT_PAGE_XPATH = "//a[contains(@class,'next') or contains(text(),'بعدی')]/@href"

    # Article XPaths
    CATEGORY_XPATH = '//li[.//i[contains(@class, "fa-folder-o")]]//span[@class="text-meta"]/text()'
    SUMMARY_XPATH = "//meta[@name='description']/@content"
    BODY_XPATH = '//div[@itemprop="articleBody"]//text()'
    TAGS_XPATH = '//footer[@class="tags"]//ul//li//a/text()'
