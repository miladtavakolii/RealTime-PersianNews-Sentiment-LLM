import json
import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime

class ScrapyScheduler:
    '''
    Main scheduler responsible for running multiple Scrapy spiders independently.

    Features:
    - Each spider has its own independent interval
    - Each spider is executed via subprocess
    - Fully asynchronous (asyncio + APScheduler)
    - Spiders can run in parallel
    '''

    def __init__(self, spider_configs: list[dict], meta_dir: str = 'meta'):
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
        self.scheduler = BlockingScheduler()

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

    def run_single_spider(self, spider_name: str) -> None:
        '''
        Callback function that runs a single spider when triggered by APScheduler.

        Args:
            spider_name: name of spider that want to start
        '''
        subprocess.run([
            'scrapy',
            'crawl',
            spider_name,
            '-a', f'start_date={self.load_last_ts(spider_name)}',
        ])

    async def start(self) -> None:
        '''
        Start the APScheduler and the asyncio event loop.

        Creates independent jobs for each spider and keeps the event loop alive.
        '''
        for cfg in self.spider_configs:
            self.scheduler.add_job(
                self.run_single_spider,
                'interval',
                minutes=cfg['interval'],
                next_run_time=datetime.datetime.now(),
                args=[cfg['spider']],
                max_instances=1,
                coalesce=True
            )
        print('[Scheduler] Scheduler is running...')
        self.scheduler.start()
