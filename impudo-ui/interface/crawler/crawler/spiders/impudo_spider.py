import scrapy
import re 
from scrapy.spiders import CrawlSpider, Rule 
from scrapy.linkextractors import LinkExtractor
from crawler.items import Product
from crawler.analyzer import Analyzer
from crawler.dao import Dao


class ImpudoSpider(CrawlSpider):
	"""docstring for ImpudoSpider"""
	name = "etoz"
	allowed_domains = ["etoz.ch"]
	start_urls = ["http://www.etoz.ch"]

	rules = (

		Rule(LinkExtractor(allow=('/collection/','/tag/')), follow=True),
		Rule(LinkExtractor(allow=('/.+/'), deny=('/tag/', '/designers/')), callback='parse_product'),

		)


	def __init__(self, *a, **kw):
		super(ImpudoSpider, self).__init__(*a, **kw)
		self.dao = Dao()
		result = self.dao.get_path(self.start_urls[0])
		self.xpath = result[0]
		self.templateid = result[1]
	
	#def parse(self, response):
	#	pass

	def parse_product(self, response):
		
		content = Analyzer.search_content(response.url,self.xpath)

		self.dao.insert_record(response.url, content, self.templateid)

		'''
		item = Product()

		text = ""

		item['image_urls'] = []

		item['title'] = ""
		item['desc'] = content  
		'''

