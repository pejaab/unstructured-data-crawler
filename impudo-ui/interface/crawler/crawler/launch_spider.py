from spiders.impudo_spider import ImpudoSpider
from scrapy.crawler import CrawlerProcess

from scrapy.utils.project import get_project_settings

import sys

if __name__ == "__main__":
	print "test"
	#pass
	process = CrawlerProcess(get_project_settings())
	print 'Argument List:', str(sys.argv)

	process.crawl(ImpudoSpider)
	process.start()
