# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from dao import Dao
import re

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

	def extract_price_and_dimensions(self, text):

		#moneyregexold = r"""[+-]?[0-9]{1,3}(?:[0-9]*(?:[.,][0-9]{2})?(?:\.-)?|(?:,[0-9]{3})*(?:\.[0-9]{2})?(?:\.-)?|(?:\.[0-9]{3})*(?:,[0-9]{2})?)?(?:\.-)?"""
		moneyregex = r"""[0-9]+(?:[,.]?[0-9]+)*(?:\.-)?"""
		
		#fullwordonly1= r"""(?:^|\s)"""
		#fullwordonly2= r"""(?:$|\s)"""
		#example usage:
		#moneymatch = "(?:"+fullwordonly1+currenciespattern+moneyregex+fullwordonly2+")|(?:"+fullwordonly1+moneyregex+currenciespattern+fullwordonly2+")"
		
		currenciespattern = r"""(?:€|\$|£|EUR|USD|Euro|Dollar|DKK|GBP|AUD|AU\$|CAD|HKD|MXN|CHF|DKK|NOK|Fr\.|¥|JPY|₽|RUB|CNY)"""
		#moneymatch = "(?:"+currenciespattern+ r"[ \t]?"+moneyregex+ r")|(?:" +moneyregex+ r"[ \t]?" +currenciespattern+ ")"
		moneymatch = "(?:" +currenciespattern+ r"[ \t]?"+moneyregex+ r")|(?:(?:\s)" +moneyregex+ r"[ \t]?" +currenciespattern+ ")"

		#to match dimensions in text
		lnum = r"""(?:[0-9]*\,[0-9]+|[0-9]*\.[0-9]+|[0-9]+)"""
		lwh = r"""(?:d|D|w|W|h|H|T|t|L|B)"""
		lunit = r"""(?:mm|cm|dm|"|’’|'|’|'')"""

		#dimmatch = "("+lnum + r"[ \t]?x[ \t]?"+lnum  + r"(?:[ \t]?x[ \t]?" +lnum+ r")?" +"|"+lnum+ r"[ \t]*"+lwh+r"*[ \t]*"+lunit+"|"+lnum+lwh+"|"+r"\b"+lwh+ r"(\:|\.)?[ \t]*"+lnum+ r"[ \t]?"+lunit+"?" +")" 
		dimmatch = "("+lnum +r"[ \t]?" +lunit+"?" + r"[ \t]?x[ \t]?"+lnum +r"[ \t]?" +lunit+"?" + r"(?:[ \t]?x[ \t]?" +lnum +r"[ \t]?" +lunit+"?" + r")?" +"|"+lnum+ r"[ \t]*"+lwh+r"*[ \t]*"+lunit+"|"+lnum+lwh+"|"+r"\b"+lwh+ r"(\:|\.)?[ \t]*"+lnum+ r"[ \t]?"+lunit+"?" +")" 

		moneymatches = []

		for r in re.findall(moneymatch,text,re.IGNORECASE):
			if r:
				moneymatches.append(r)

		dimensionmatches = []

		for r in re.findall(dimmatch,text,re.IGNORECASE):
			if r[0]:
				dimensionmatches.append(r[0])


		return (moneymatches,dimensionmatches)


	def extract_and_save_details(self, id, title, content):
		#extract from content
		x = self.extract_price_and_dimensions(content)

		foundprices = ""
		for a in x[0]:
			foundprices += "".join(a.split()) + " " 
		foundprices = foundprices.strip()

		founddims = ""
		for a in x[1]:
			founddims += "".join(a.split()) + " " 
		founddims = founddims.strip()

		#extract from title
		x = self.extract_price_and_dimensions(title)
		for a in x[0]:
			foundprices += "".join(a.split()) + " " 
		foundprices = foundprices.strip()
		for a in x[1]:
			founddims += "".join(a.split()) + " " 
		founddims = founddims.strip()
                
                return foundprices, founddims

	def save_item_in_db(self, item):
		#insert record
		record_id = self.d.get_last_insert_id()[0]

		image_urls = item['image_urls']
		image_paths = item['image_paths']
		#insert pictures
		for img in image_paths:
			self.d.insert_image(img, record_id)

		#extract and save details (prices, dimensions, ...)
		foundprices, founddims = self.extract_and_save_details(record_id,item['title'],item['content'])
		
		self.d.insert_record(item['title'], item['url'], item['content'], item['template_id'], foundprices, founddims)
