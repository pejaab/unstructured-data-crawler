import scrapy
import re 
from crawler.items import Product



class EtozSpider(scrapy.Spider):
	"""docstring for EtozSpider"""
	name = "etoz"
	allowed_domains = ["etoz.ch"]
	start_urls = [
		"http://www.etoz.ch/collection/seating/"
		#,"http://www.etoz.ch/collection/tables/"
		#TODO
	]

	def parse(self, response):
		products = response.xpath("//a[@class='thumbnail']/@href")
		for p in products:
			#print p.extract()
			yield scrapy.Request(p.extract(),callback=self.parse_products)


	def parse_products(self, response):
		item = Product()

		text = ''.join(response.xpath("//article[@class='product']/div[@class='row'][1]/div[1]//text()").
		extract()).strip()
		text = re.sub('\s+', ' ', text) #remove whitespaces

		item['image_urls'] = []

		imagesurl = response.xpath("//li[@class='detail-image']/img/@src")

		for url in imagesurl:
			item['image_urls'].append(url.extract())

		item['title'] = ""
		item['desc'] = text  


		yield item

