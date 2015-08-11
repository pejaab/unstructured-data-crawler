# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from dao import Dao

class ImpudoImagesPipeline(ImagesPipeline):

	d = Dao()

	def get_media_requests(self, item, info):
		for image_url in item['image_urls']:
			yield scrapy.Request(image_url)

	def item_completed(self, results, item, info):
		image_paths = [x['path'] for ok, x in results if ok]
		item['image_paths'] = image_paths
		print "ImpudoPipeline:"  
		print results
		print "Image_paths"
		print image_paths

		print item['title']

		return item

	def save_item_in_db(self, item):
		
		self.d.insert_record(item['title'], item['url'], item['url'], item['template_id'])
		recordid = self.d.get_last_insert_id()[0]
		pass