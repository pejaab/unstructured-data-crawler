from billiard import Process
#from multiprocessing import Process
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings
from spiders.impudo_spider import ImpudoSpider
from twisted.internet import reactor
from scrapy import signals

class CrawlerScript(Process):
    
    def __init__(self, spider, template_id):
        Process.__init__(self)
        self.crawler = Crawler(ImpudoSpider, get_project_settings())
        self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        #self.spider = spider
        self.template_id = template_id

    def run(self):
        self.crawler.crawl(self.template_id)
        reactor.run()

    #def crawl(self):
    #    self.start()
    #    self.join()

def run_spider(template_id):
    spider = ImpudoSpider(template_id)
    crawler = CrawlerScript(spider, template_id)
    crawler.start()
    crawler.join
    #crawler.crawl()


'''

#based on http://stackoverflow.com/a/22202877
class CrawlerScript(Process):
        def __init__(self, spider):
            Process.__init__(self)
            settings = get_project_settings()
            self.crawler = Crawler(spider, settings)
            self.crawler.configure()
            self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
            self.spider = spider

        def run(self):
            self.crawler.crawl(self.spider)
            self.crawler.start()
            reactor.run()	

def run_spider():
	spider = ImpudoSpider()
	crawler = CrawlerScript(spider)
	crawler.start()
	crawler.join()


'''
'''
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess


class CrawlerScript2():

    def __init__(self):
        self.process = CrawlerProcess(get_project_settings())

    def _crawl(self, spider):
        self.process.crawl(spider)
        self.process.start()
        self.process.stop()

    def crawl(self, args):
        p = Process(target=self._crawl)
        p.start()
        p.join()


def domain_crawl(args):
    crawler.crawl(args)

'''

if __name__ == "__main__":
	print("test")
	#pass
	process = CrawlerProcess(get_project_settings())
	#print('Argument List:', str(sys.argv))
	
	process.crawl(ImpudoSpider, template_id=27)
	process.start()


