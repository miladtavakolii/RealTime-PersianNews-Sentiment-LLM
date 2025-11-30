# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class NewsArticleItem(scrapy.Item):
    '''Item for news article'''
    title = scrapy.Field()
    publication_date = scrapy.Field()
    content = scrapy.Field()
    category = scrapy.Field()
    tags = scrapy.Field()
    url = scrapy.Field()
