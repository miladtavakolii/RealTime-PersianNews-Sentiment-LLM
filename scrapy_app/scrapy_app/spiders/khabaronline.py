from hmac import new
import scrapy
from scrapy_app.items import NewsArticleItem  


class KhabaronlineSpider(scrapy.Spider):
    name = "khabaronline"
    allowed_domains = ["khabaronline.ir"]
    start_urls = ["https://khabaronline.ir/archive"]

    def parse(self, response):
        '''Parse the archive/listing page to extract article links and metadata.'''
        blocks = response.xpath("//div[@class='desc']")
        for b in blocks:
            title = b.xpath(".//h3/a/text()").get()
            href = b.xpath(".//h3/a/@href").get()
            date = b.xpath("normalize-space(.//time//text())").get()

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
        category = response.xpath('//ol[@class="breadcrumb"]//li[last()]/a/text()').get()
        summary = response.xpath("//meta[@name='description']/@content").get()
        body_paragraphs = response.xpath('//div[@class="item-body"]//p//text()').getall()[:-1]
        body = "\n".join([p.strip() for p in body_paragraphs if p.strip()])
        tags = response.xpath('//a[@rel="tag"]/text()').getall()
        tags = [t.strip() for t in tags]

        news_item['title'] = title
        news_item['publication_date'] = publish_date
        news_item['content'] = body
        news_item['summary'] = summary
        news_item['category'] = category
        news_item['tags'] = tags
        news_item['url'] = url

        yield news_item
