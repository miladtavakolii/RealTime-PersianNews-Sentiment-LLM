# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os
import hashlib

def sanitize_filename(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()

class JsonPerPagePipeline:
    def open_spider(self, spider):
        self.output_dir = "../data/raw"
        os.makedirs(self.output_dir, exist_ok=True)

    def process_item(self, item, spider):
        filename = spider.name + '-' + sanitize_filename(item['url']) + ".json"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dict(item), f, ensure_ascii=False, indent=4)
        return item
