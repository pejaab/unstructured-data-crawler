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

        #Name download version
        def file_path(self, request, response=None, info=None):
            template_id = request.meta['template_id']
            image_guid = request.url.split('/')[-1]
            return 'full/template_{0}/{1}'.format(template_id, image_guid)
            #return 'full/%s' % (image_guid)

	def get_media_requests(self, item, info):
		for image_url in item['image_urls']:
                    yield scrapy.Request(image_url, meta={'template_id': item['template_id']})

	def item_completed(self, results, item, info):
		image_paths = [x['path'] for ok, x in results if ok]
		item['image_paths'] = image_paths

		self.save_item_in_db(item)
		
		return item

	def save_item_in_db(self, item):
		#insert record
		self.d.insert_record(item['title'], item['url'], item['content'], item['template_id'])
		record_id = self.d.get_last_insert_id()[0]

		image_urls = item['image_urls']
		image_paths = item['image_paths']
		#insert pictures
		for img in image_paths:
			self.d.insert_image(img, record_id)
		
