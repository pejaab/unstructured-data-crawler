# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Product(scrapy.Item):
	template_id = scrapy.Field()
	title = scrapy.Field()
	content = scrapy.Field()
	url = scrapy.Field()
	image_urls = scrapy.Field()
	images = scrapy.Field()
	image_paths = scrapy.Field()
