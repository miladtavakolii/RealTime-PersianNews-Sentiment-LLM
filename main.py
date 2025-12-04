import asyncio
from utils.config_manager import ConfigManager
from scheduler.scrapy_scheduler import ScrapyScheduler
from scheduler.write_last_timestamp import write_last_timestamp
from workers.preprocess_worker import PreprocessWorker
import logging
import subprocess


class ServiceRunner:
    def __init__(self, config: ConfigManager):
        self.scheduler = ScrapyScheduler(config.get_spider_configs())
        self.preprocess_worker = PreprocessWorker()

    async def start_Preprocess_worker(self) -> None:
        print("[Main] Starting PreprocessWorker...")
        await asyncio.to_thread(self.preprocess_worker.start)

    async def run(self) -> None:
        # Run both scheduler and worker concurrently
        await asyncio.gather(
            self.start_Preprocess_worker(),
            self.scheduler.start(),
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("pika").setLevel(logging.WARNING)
    logging.getLogger("pika").disabled = True

    config_path: str = "config/settings.yaml"
    config = ConfigManager(config_path)
    website_date_config = config.get_website_date_config()

    for cfg in website_date_config:
        if cfg['end_date']:
            subprocess.run([
                "scrapy",
                "crawl",
                cfg['name'],
                "-a", f"start_date={cfg['start_date']}",
                "-a", f"end_date={cfg['end_date']}",
            ])
        else:
            write_last_timestamp(cfg['name'], timestamp=int(cfg['start_date'].timestamp()))

    runner = ServiceRunner(config)
    asyncio.run(runner.run())
