import scrapy
from scrapy_app.items import NewsArticleItem
from utils.date_parser import parse_date 


class MehrnewsSpider(scrapy.Spider):
    name = "mehrnews"
    allowed_domains = ["mehrnews.com"]
    start_urls = ["https://mehrnews.com/archive"]

    def __init__(self, start_date=None, end_date=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_date = start_date
        self.end_date = end_date
        
    def parse(self, response):
        '''Parse the archive/listing page to extract article links and metadata.'''
        blocks = response.xpath("//div[@class='desc']")
        for b in blocks:
            title = b.xpath(".//h3/a/text()").get()
            href = b.xpath(".//h3/a/@href").get()
            date = parse_date(b.xpath("normalize-space(.//time//text())").get())
            timestamp = date.timestamp()
            date = date.isoformat()

            if self.end_date and date > self.end_date:
                continue
            if self.start_date and date < self.start_date:
                return
            
            if href:
                url = response.urljoin(href.strip())
            else:
                url = None

            yield scrapy.Request(
                url,
                callback=self.parse_article,
                meta={"title": title, "date": date, "timestamp": timestamp}
            )

        next_page = response.xpath("//a[contains(@class,'next') or contains(text(),'بعدی')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        news_item = NewsArticleItem()
        meta = response.meta
        title = meta.get("title")
        url = response.url
        publish_date = meta.get("date")
        publish_timestamp = meta.get("timestamp")
        category = response.xpath('//ol[@class="breadcrumb"]//li[last()]/a/text()').get()
        summary = response.xpath("//meta[@name='description']/@content").get()
        body_paragraphs = response.xpath('//div[@class="item-body"]//p//text()').getall()
        body = "\n".join([p.strip() for p in body_paragraphs if p.strip()])
        tags = response.xpath('//a[@rel="tag"]/text()').getall()
        tags = [t.strip() for t in tags]

        news_item['title'] = title
        news_item['publication_date'] = publish_date
        news_item['publication_timestamp'] = int(publish_timestamp)
        news_item['content'] = body
        news_item['summary'] = summary
        news_item['category'] = category
        news_item['tags'] = tags
        news_item['url'] = url

        yield news_item
