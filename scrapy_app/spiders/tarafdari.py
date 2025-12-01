from .base_spider import BaseNewsSpider


class TarafdariSpider(BaseNewsSpider):
    name = "tarafdari"
    allowed_domains = ["www.tarafdari.com"]
    start_urls = ["https://www.tarafdari.com/static/page/archive"]

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
