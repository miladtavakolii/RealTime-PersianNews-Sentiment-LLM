import scrapy
from scrapy_app.items import NewsArticleItem
from utils.date_parser import parse_date 


class TarafdariSpider(scrapy.Spider):
    name = "tarafdari"
    allowed_domains = ["www.tarafdari.com"]
    start_urls = ["https://www.tarafdari.com/static/page/archive"]

    def parse(self, response):
        '''Parse the archive/listing page to extract article links and metadata.'''
        blocks = response.xpath('//article[contains(@class, "node-content")]')
        for b in blocks:
            title = b.xpath('.//h2//a/text()').get()
            href = b.xpath('.//h2//a/@href').get()
            date = parse_date(b.xpath('.//abbr[@class="timeago"]/@title').get())

            if href:
                url = response.urljoin(href.strip())
            else:
                url = None

            yield scrapy.Request(
                url,
                callback=self.parse_article,
                meta={"list_title": title, "list_date": date}
            )

        next_page = response.xpath("//a[contains(@class,'next') or contains(text(),'بعدی')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        news_item = NewsArticleItem()
        meta = response.meta
        title = meta.get("list_title")
        url = response.url
        publish_date = meta.get("list_date")
        category = response.xpath('//div[contains(@class,"field-name-field-category")]//div[contains(@class,"field-item")]/a/text()').getall()
        summary = response.xpath('.//div[contains(@class, "field-name-field-teaser")]//p/text()').get()
        body_paragraphs = response.xpath('//div[contains(@class,"field-name-body")]//div[contains(@class,"field-item")]//text()').getall()
        body = "\n".join([p.strip() for p in body_paragraphs if p.strip()])
        tags = response.xpath('//div[contains(@class,"field-name-field-tags")]//div[contains(@class,"field-item")]/a/text()').getall()
        tags = [t.strip() for t in tags]

        news_item['title'] = title
        news_item['publication_date'] = publish_date
        news_item['content'] = body
        news_item['summary'] = summary
        news_item['category'] = category
        news_item['tags'] = tags
        news_item['url'] = url

        yield news_item
