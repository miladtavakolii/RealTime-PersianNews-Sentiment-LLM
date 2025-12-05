import scrapy
from scrapy_app.items import NewsArticleItem
from utils.date_parser import parse_date
from typing import Optional, Any, List, Generator
from scrapy.http import Response, Request


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
    LIST_BLOCK_XPATH: str = ''
    TITLE_XPATH: str = ''
    URL_XPATH: str = ''
    DATE_XPATH: str = ''
    NEXT_PAGE_XPATH: str = ''

    # Article selectors (override per site)
    CATEGORY_XPATH: str = ''
    SUMMARY_XPATH: str = ''
    BODY_XPATH: str = ''
    TAGS_XPATH: str = ''

    def __init__(self, start_date: Optional[int] = None, end_date: Optional[int] = None, *args: Any, **kwargs: Any) -> None:
        '''
        Initialize spider with optional date filters.

        Args:
            start_date: Minimum UNIX timestamp to include.
            end_date: Maximum UNIX timestamp to include.
        '''
        super().__init__(*args, **kwargs)
        self.start_date = start_date
        self.end_date = end_date

    def parse(self, response: Response) -> Generator[Request, None, None]:
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
            title: Optional[str] = b.xpath(self.TITLE_XPATH).get()
            href: Optional[str] = b.xpath(self.URL_XPATH).get()
            date_str: Optional[str] = b.xpath(self.DATE_XPATH).get()

            if not date_str:
                continue

            dt = parse_date(date_str)
            iso: str = dt.isoformat()
            ts: int = int(dt.timestamp())

            # Date filtering base time
            if self.end_date and ts > int(self.end_date):
                continue
            if self.start_date and ts < int(self.start_date):
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

    def parse_article(self, response: Response) -> Generator[NewsArticleItem, None, None]:
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
        item['title'] = str(meta['title'])
        item['publication_date'] = str(meta['date'])
        item['publication_timestamp'] = int(meta['timestamp'])
        item['url'] = str(response.url)

        # Extract category
        category_list: List[str] = [
            c.strip() for c in response.xpath(self.CATEGORY_XPATH).getall()
            if c.strip()
        ]
        item['category'] = category_list

        # Summary
        summary: Optional[str] = response.xpath(self.SUMMARY_XPATH).get()
        item['summary'] = summary

        # Body paragraphs
        paragraphs: List[str] = response.xpath(self.BODY_XPATH).getall()
        body: str = '\n'.join([p.strip() for p in paragraphs if p.strip()])
        item['content'] = body

        # Tags
        tags: List[str] = [
            t.strip() for t in response.xpath(self.TAGS_XPATH).getall()
            if t.strip()
        ]
        item['tags'] = tags

        yield item
