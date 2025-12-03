import scrapy
from utils.date_parser import parse_date


class BaseNewsSpider(scrapy.Spider):
    '''
    Base spider for crawling news websites with archive-style listing pages.

    This class handles:
        - Listing page traversal
        - Extracting title, URL, raw date
        - Date filtering based on start_date and end_date arguments
        - Pagination handling
        - Standard article-page parsing through `parse_article`

    Child classes must override:
        LIST_BLOCK_XPATH, TITLE_XPATH, URL_XPATH, DATE_XPATH, NEXT_PAGE_XPATH  
        CATEGORY_XPATH, SUMMARY_XPATH, BODY_XPATH, TAGS_XPATH

    Args:
        start_date: Minimum timestamp. Articles older than this will stop crawling.
        end_date: Maximum timestamp. Articles newer than this will be skipped.
    '''

    # Listing selectors (override per site)
    LIST_BLOCK_XPATH = None
    TITLE_XPATH = None
    URL_XPATH = None
    DATE_XPATH = None
    NEXT_PAGE_XPATH = None

    # Article selectors (override per site)
    CATEGORY_XPATH = None
    SUMMARY_XPATH = None
    BODY_XPATH = None
    TAGS_XPATH = None

    def __init__(self, start_date=None, end_date=None, *args, **kwargs):
        '''
        Initialize spider with optional date filters.

        Args:
            start_date: Minimum UNIX timestamp to include.
            end_date: Maximum UNIX timestamp to include.
        '''
        super().__init__(*args, **kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def parse(self, response):
        '''
        Parse listing/archive pages.

        Steps:
            1. Extract article blocks using LIST_BLOCK_XPATH
            2. Extract title, URL, and publication date
            3. Convert date to timestamp and apply filtering
            4. Yield article requests to `parse_article`
            5. Follow pagination link if available

        Yields:
            scrapy.Request: Requests for individual article pages.
        '''
        blocks = response.xpath(self.LIST_BLOCK_XPATH)

        for b in blocks:
            title = b.xpath(self.TITLE_XPATH).get()
            href = b.xpath(self.URL_XPATH).get()
            date_str = b.xpath(self.DATE_XPATH).get()

            if not date_str:
                continue

            dt = parse_date(date_str)
            iso = dt.isoformat()
            ts = dt.timestamp()

            # Date filtering base time
            if self.end_date and ts > self.end_date:
                continue
            if self.start_date and ts < self.start_date:
                return

            url = response.urljoin(href.strip()) if href else None

            if url:
                yield scrapy.Request(
                    url,
                    callback=self.parse_article,
                    meta={'title': title, 'date': iso, 'timestamp': ts}
                )

        next_page = response.xpath(self.NEXT_PAGE_XPATH).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        '''
        Generic article page parser.

        Extracts:
            - Category list
            - Summary text
            - Cleaned article body
            - Tags list

        Only XPaths differ between websites; the extraction mechanism is universal.

        Args:
            response: Article page response.

        Yields:
            NewsArticleItem: Fully structured article data.
        '''
        from scrapy_app.items import NewsArticleItem

        meta = response.meta
        item = NewsArticleItem()

        # Simple direct fields
        item['title'] = meta['title']
        item['publication_date'] = meta['date']
        item['publication_timestamp'] = int(meta['timestamp'])
        item['url'] = response.url

        # Extract category
        category = response.xpath(self.CATEGORY_XPATH).getall()
        item['category'] = [c.strip() for c in category if c.strip()]

        # Summary
        item['summary'] = response.xpath(self.SUMMARY_XPATH).get()

        # Body paragraphs
        paragraphs = response.xpath(self.BODY_XPATH).getall()
        body = '\n'.join([p.strip() for p in paragraphs if p.strip()])
        item['content'] = body

        # Tags
        tags = response.xpath(self.TAGS_XPATH).getall()
        item['tags'] = [t.strip() for t in tags if t.strip()]

        yield item
