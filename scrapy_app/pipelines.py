# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import json
from utils.rabbitmq import RabbitMQClient
from utils.sanitize_filename import sanitize_filename


class RawSaveAndPublishPipeline:
    '''
    Scrapy pipeline responsible for:
      1. Saving RAW crawled items to disk
      2. Publishing RAW items to RabbitMQ for preprocessing phase
    '''

    def __init__(self, raw_dir='data/raw', queue_name='raw_news'):
        self.raw_dir = raw_dir
        self.queue_name = queue_name
        self.client = None

        # Ensure directory exists
        os.makedirs(self.raw_dir, exist_ok=True)

    def open_spider(self, spider):
        '''Initialize RabbitMQ connection when spider starts.'''
        self.client = RabbitMQClient()
        self.client.declare_queue(self.queue_name)

    def process_item(self, item, spider):
        '''Save RAW file and publish to RabbitMQ.'''
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

    def close_spider(self, spider):
        '''Close RabbitMQ connection gracefully.'''
        if self.client:
            self.client.close()
