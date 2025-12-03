import asyncio
from typing import Callable
from scrapy.crawler import CrawlerRunner
from twisted.internet.defer import Deferred
from datetime import datetime

class SpiderRunner:
    '''
    Runner responsible for executing a single Scrapy spider using the Scrapy API.

    This class encapsulates:
    - Fetching the last processed timestamp
    - Running the spider with arguments
    - Converting Twisted Deferred to asyncio Future
    '''

    def __init__(self, spider_name: str, last_ts_provider: Callable):
        '''
        Initialize the runner.

        Args:
            spider_name: Name of the Scrapy spider to run
            last_ts_provider: Callable that returns the last processed timestamp for the spider
        '''
        self.spider_name: str = spider_name
        self.last_ts_provider: Callable = last_ts_provider
        self.runner: CrawlerRunner = CrawlerRunner()

    async def run(self) -> None:
        '''
        Execute the spider using the Scrapy API.

        Converts the Twisted Deferred returned by `runner.crawl` into an asyncio Future
        so that we can await the crawl operation inside an asyncio-based scheduler.
        '''
        last_ts: int = self.last_ts_provider(self.spider_name)
        last_time = datetime.fromtimestamp(last_ts)
        print(
            f'[Runner] Starting spider={self.spider_name}, last_ts={last_ts}, last_time{last_time}')

        deferred: Deferred = self.runner.crawl(
            self.spider_name,
            start_date=last_ts
        )

        # Convert Twisted Deferred to asyncio Future
        await asyncio.wrap_future(asyncio.ensure_future(deferred))

        print(f'[Runner] Finished spider={self.spider_name}')
