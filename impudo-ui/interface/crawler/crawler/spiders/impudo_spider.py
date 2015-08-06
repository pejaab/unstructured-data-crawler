import scrapy
import re 
from scrapy.spiders import CrawlSpider, Rule 
from scrapy.linkextractors import LinkExtractor
from crawler.items import Product
from crawler.analyzer import Analyzer
from crawler.dao import Dao


class ImpudoSpider(CrawlSpider):
	"""docstring for ImpudoSpider"""
	name = "impudo"
	allowed_domains = ["etoz.ch"]
	start_urls = ["http://www.etoz.ch"]

	'''rules = (

		Rule(LinkExtractor(allow=('/collection/','/tag/')), follow=True),
		Rule(LinkExtractor(allow=('/.+/'), deny=('/tag/', '/designers/')), callback='parse_product'),

		)
	'''


	def __init__(self, domain= '', start_url=''):
		self.dao = Dao()

		#get and set rules for specific domain
		textrules = self.dao.get_rules(self.allowed_domains[0])
		
		follows = tuple(textrules[0].split(','))
		parses = tuple(textrules[1].split(','))
		follow_denies = tuple(textrules[2].split(','))
		parse_denies = tuple(textrules[3].split(','))

		ImpudoSpider.rules = (
			Rule(LinkExtractor(allow=follows, deny=follow_denies), follow=True),
			Rule(LinkExtractor(allow=parses, deny=parse_denies), callback='parse_product'),

		)

		super(ImpudoSpider, self).__init__()
		
		#get xpath
		result = self.dao.get_path(self.start_urls[0])
		self.xpath = result[0]
		self.templateid = result[1]


		if start_url and domain:
			start_urls=[]
			start_urls.append(start_url)
			allowed_domains=[]
			allowed_domains.append(domain)

	
	#def parse(self, response):
	#	pass

	def parse_product(self, response):
		
		content = Analyzer.search_content(response.url,self.xpath)

		title = Analyzer.search_content(response.url, "/html/head/title")
		url = response.url


		print title, response.url, content

		#self.dao.insert_record(title, response.url, content, self.templateid)

		'''
		item = Product()

		text = ""

		item['image_urls'] = []

		item['title'] = ""
		item['desc'] = content  
		'''

