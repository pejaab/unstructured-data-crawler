import os 
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import scrapy
import re 
from scrapy.spiders import CrawlSpider, Rule 
from scrapy.linkextractors import LinkExtractor

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from analyzer.analyzer import Analyzer
from crawler.dao import Dao

import sys


class ImpudoSpider(CrawlSpider):
	"""docstring for ImpudoSpider"""
	name = "impudo"
	allowed_domains = ["etoz.ch"]
	start_urls = ["http://www.etoz.ch"]

	#follow all links
	rules = (
		Rule(LinkExtractor(allow=('')), callback='parse_product', follow=True),
		)
	


	def __init__(self, domain= '', start_url=''):
		#set domain and start_url 
		#usage: scrapy crawl impudo -a domain=example.com -a start_url=http://example.com/
		if start_url and domain:
			self.start_urls=[]
			self.start_urls.append(start_url)
			self.allowed_domains=[]
			self.allowed_domains.append(domain)

		self.dao = Dao()

		#get and set rules for specific domain
		'''textrules = self.dao.get_rules(self.allowed_domains[0])
		
		follows = tuple(textrules[0].split(','))
		parses = tuple(textrules[1].split(','))
		follow_denies = tuple(textrules[2].split(','))
		parse_denies = tuple(textrules[3].split(','))

		ImpudoSpider.rules = (
			Rule(LinkExtractor(allow=follows, deny=follow_denies), follow=True),
			Rule(LinkExtractor(allow=parses, deny=parse_denies), callback='parse_product'),

		) '''

		super(ImpudoSpider, self).__init__()
		
		#get xpath
		result = self.dao.get_path(self.start_urls[0])
		self.xpath = result[0]
		self.templateid = result[1]


	def parse_product(self, response):
		a = Analyzer(response.url)	
		content = a.find_content(self.xpath)

		title = response.xpath("/html/head/title/text()").extract()[0]
		url = response.url

		#ignore if no content is found
		if content:
			print title.encode('utf-8'), response.url, content.encode('utf-8')
			#self.dao.insert_record(title, response.url, content, self.templateid)
		else:
			self.logger.warning('No content found on %s in domain %s', response.url, self.allowed_domains[0])

if __name__ == "__main__":
	
	#process = CrawlerProcess(get_project_settings())
	#print 'Argument List:', str(sys.argv)

	#process.crawl(ImpudoSpider)
	#process.start()
