# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import json
from utils.rabbitmq import RabbitMQClient
from utils.sanitize_filename import sanitize_filename
from scrapy import Spider
from typing import Dict, Any
import logging


class RawSaveAndPublishPipeline:
    '''
    Pipeline responsible for:

        1. Saving RAW crawled items to disk as JSON files.
        2. Publishing RAW items to a RabbitMQ queue for downstream preprocessing.

    Workflow:
        - On spider open: initializes RabbitMQ client + queue
        - On item process:
              * Saves item to disk under `data/raw/<spider-name>-<filename>.json`
              * Publishes JSON to RabbitMQ
        - On spider close: closes RabbitMQ connection

    Args:
        raw_dir: Directory path to store raw JSON files.
        queue_name: RabbitMQ queue name for sending items.
    '''

    def __init__(self, raw_dir: str = 'data/raw', queue_name: str = 'raw_news'):
        '''
        Initialize pipeline with directories and queue configuration.

        Args:
            raw_dir: Directory where JSON files are saved.
            queue_name: RabbitMQ queue for output publishing.
        '''
        self.raw_dir = raw_dir
        self.queue_name = queue_name

        # Ensure directory exists
        os.makedirs(self.raw_dir, exist_ok=True)
        logging.getLogger("pika").setLevel(logging.ERROR)

    def open_spider(self, spider: Spider) -> None:
        '''
        Called when the spider starts.

        Initializes RabbitMQ connection and declares queue.

        Args:
            spider: The running spider instance.
        '''
        self.client: RabbitMQClient = RabbitMQClient()
        self.client.declare_queue(self.queue_name)

    def process_item(self, item: Dict[str, Any], spider: Spider) -> Dict[str, Any]:
        '''
        Save item to disk and publish to RabbitMQ.

        Args:
            item (dict | Item): Extracted news item.
            spider (scrapy.Spider): Spider instance.

        Returns:
            item: The same item, unchanged.
        '''
        data = dict(item)

        # Save RAW file
        filename = f'{spider.name}-{sanitize_filename(item["url"])}.json'
        filepath = os.path.join(self.raw_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Add raw filename to item for later use
        data['raw_filename'] = filename

        # Publish RAW item to RabbitMQ
        self.client.publish(self.queue_name, data)

        return item

    def close_spider(self, spider: Spider) -> None:
        '''
        Called when the spider finishes.

        Closes the RabbitMQ connection gracefully.

        Args:
            spider (scrapy.Spider): The spider that has finished execution
        '''
        if self.client:
            self.client.close()
