import os 
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import scrapy
import re 
from scrapy.spiders import CrawlSpider, Rule 
from scrapy.linkextractors import LinkExtractor

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from analyzer.analyzer import Analyzer
from dao import Dao
from items import Product

from urlparse import urlparse

class ImpudoSpider(CrawlSpider):
	"""docstring for ImpudoSpider"""
	name = "impudo"
	allowed_domains = ["etoz.ch"]
	start_urls = ["http://www.etoz.ch"]
	

	def __init__(self, template_id):
		self.dao = Dao()

		self.template_id  = template_id

		o = urlparse(dao.get_url(template_id)[0])

		#set domain and start_url 
		self.allowed_domains=[]
		self.allowed_domains.append(o.netloc)
		self.start_urls=[]
		self.start_urls.append(o.scheme+"://"+o.netloc+"/")

		#get xpaths
		result = self.dao.get_path(self.template_id)
		self.xpaths = []
		for (xpath)  in result:
			self.xpaths.append(xpath[0])

		#get and set rules for specific domain if they exist in the db
		textrules = self.dao.get_rules(self.allowed_domains[0])
		
		if textrules:
			follows = tuple(textrules[0].split(','))
			parses = tuple(textrules[1].split(','))
			follow_denies = tuple(textrules[2].split(','))
			parse_denies = tuple(textrules[3].split(','))

			ImpudoSpider.rules = (
				Rule(LinkExtractor(allow=follows, deny=follow_denies), follow=True),
				Rule(LinkExtractor(allow=parses, deny=parse_denies), callback='parse_product'),

			)
		else:
			#follow all links
			ImpudoSpider.rules = (
				Rule(LinkExtractor(allow=('')), callback='parse_product', follow=True),
			)


		super(ImpudoSpider, self).__init__()
	



	def parse_product(self, response):
		a = Analyzer(response.url)	

		for xp in self.xpaths:
			content = a.find_content(xp)

			title = response.xpath("/html/head/title/text()").extract()[0]
			url = response.url

			#ignore if no content is found
			if content:
				print title.encode('utf-8'), response.url, content.encode('utf-8')
				#self.dao.insert_record(title, response.url, content, self.template_id)
			else:
				self.logger.warning('No content found on %s in domain %s', response.url, self.allowed_domains[0])


if __name__ == "__main__":
	#process = CrawlerProcess(get_project_settings())
	print 'Argument List:', str(sys.argv)

	#process.crawl(ImpudoSpider)
	#process.start()
