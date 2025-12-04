from twisted.internet import asyncioreactor
asyncioreactor.install()
import asyncio
from utils.config_manager import ConfigManager
from scheduler.scrapy_scheduler import ScrapyScheduler
from workers.preprocess_worker import PreprocessWorker
import logging


class ServiceRunner:
    def __init__(self, config_path: str = "config/settings.yaml"):
        config = ConfigManager(config_path)
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


    runner = ServiceRunner()
    asyncio.run(runner.run())
