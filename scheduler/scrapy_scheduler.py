import json
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from scheduler.spider_runner import SpiderRunner


class ScrapyScheduler:
    '''
    Main scheduler responsible for running multiple Scrapy spiders independently.

    Features:
    - Each spider has its own independent interval
    - Each spider is executed via the Scrapy API, not subprocess
    - Fully asynchronous (asyncio + APScheduler)
    - Spiders can run in parallel
    '''

    def __init__(self, spider_configs: dict, meta_dir: str = 'meta'):
        '''
        Initialize the scheduler.

        Args:
            spider_configs: List of dictionaries containing:
                {
                    'spider': 'spider_name',
                    'interval': minutes_between_runs
                }
            meta_dir: Directory where timestamp files are stored
        '''
        self.spider_configs = spider_configs
        self.meta_dir = meta_dir
        self.scheduler = AsyncIOScheduler()

    def ts_file(self, spider_name: str) -> str:
        '''Return the path to the timestamp file for the given spider.'''
        return f'{self.meta_dir}/{spider_name}_last.json'

    def load_last_ts(self, spider_name: str) -> int:
        '''
        Load last processed timestamp for the spider.

        NOTE:
        In production, this should ideally be updated by downstream workers,
        not by the scheduler itself.

        Args:
            spider_name: name of spider for find meta file

        Returns:
            dictionary of meta file
        '''
        with open(self.ts_file(spider_name), 'r') as f:
            data = json.load(f)
            return data.get('last_timestamp', 0)

    async def run_single_spider(self, spider_name: str) -> None:
        '''
        Callback function that runs a single spider when triggered by APScheduler.

        Args:
            spider_name: name of spider that want to start
        '''
        runner = SpiderRunner(
            spider_name=spider_name,
            last_ts_provider=self.load_last_ts
        )

        await runner.run()

    def schedule_spider(self, spider_name: str, interval_minutes: int) -> None:
        '''
        Assigns a separate APScheduler job to one spider.

        Args:
            spider_name: Spider to schedule
            interval_minutes: Frequency in minutes
        '''
        print(
            f'[Scheduler] Scheduling spider={spider_name} every {interval_minutes} minutes'
        )

        self.scheduler.add_job(
            self.run_single_spider,
            args=[spider_name],
            trigger='interval',
            minutes=interval_minutes,
            next_run_time=datetime.now()  # first run immediately
        )

    def start(self) -> None:
        '''
        Start the APScheduler and the asyncio event loop.

        Creates independent jobs for each spider and keeps the event loop alive.
        '''
        for cfg in self.spider_configs:
            self.schedule_spider(cfg['spider'], cfg['interval'])

        self.scheduler.start()

        # Keep asyncio alive for good
        try:
            asyncio.get_event_loop().run_forever()
        except KeyboardInterrupt:
            print('[Scheduler] Stopped by user.')
