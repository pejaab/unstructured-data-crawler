import os
import sys
import ast
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

    def __init__(self, template_id):
        self.dao = Dao()

        self.template_id  = template_id

        o = urlparse(self.dao.get_url(template_id)[0])

        #set domain and start_url
        self.allowed_domains=[]
        self.allowed_domains.append(o.netloc)
        self.start_urls=[]
        self.start_urls.append(o.scheme+"://"+o.netloc+"/")

        #get desc xpaths
        result = self.dao.get_desc_xpath(self.template_id, active=1)
        self.desc_xpaths = []
        for xpath  in result:
            self.desc_xpaths.append(ast.literal_eval(xpath[0]))

        #get all other xpaths
        result = self.dao.get_desc_xpath(self.template_id, active=0)
        self.not_desc_xpaths = []
        for xpath in result:
            self.not_desc_xpaths.append(ast.literal_eval(xpath[0]))

        result = self.dao.get_content(self.template_id, active=0)
        self.not_desc_contents = []
        for content in result:
            self.not_desc_contents.append(content[0])

        self.xpath_begin = ast.literal_eval(list(self.dao.get_desc_xpath(self.template_id, active=2))[0][0])
        self.content_begin = list(self.dao.get_content(self.template_id, active=2))[0][0]
        self.xpath_end = ast.literal_eval(list(self.dao.get_desc_xpath(self.template_id, active=3))[0][0])
        self.content_end = list(self.dao.get_content(self.template_id, active=3))[0][0]


        #get img xpath
        self.img_xpath = self.dao.get_img_xpath(self.template_id)[0]

        #get and set rules for specific domain if they exist in the db
        textrules = self.dao.get_rules(self.allowed_domains[0])

        if textrules:
            follows = tuple(textrules[0].split(','))
            parses = tuple(textrules[1].split(','))
            follow_denies = tuple(textrules[2].split(','))
            parse_denies = tuple(textrules[3].split(','))
            xpath_follow_restrict = textrules[4]

            #If xpath_restrictions exist
            if xpath_follow_restrict:
                ImpudoSpider.rules = (
                    Rule(LinkExtractor(allow=follows, deny=follow_denies, restrict_xpaths=(xpath_follow_restrict)), follow=True),
                    Rule(LinkExtractor(allow=parses, deny=parse_denies), callback='parse_product'),
                )
            else:
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

        content = ""

        title = response.xpath("/html/head/title/text()").extract()[0]
        title = re.sub("[ \t]+", " ", title).strip()
        url = response.url

        for path in self.desc_xpaths:
            print(path)
            print(response.url)
            tempcont = a.find_content(path)

            if tempcont:
                content += ' ' + tempcont
                print(content)
        #ignore if no content is found
        if content:
            found_xpaths = a.analyze()
            check = a.eliminate_begin_and_end(found_xpaths, (self.xpath_begin, self.content_begin), (self.xpath_end, self.content_end))
            if not check:
                found_xpaths = self.desc_xpaths
            print(found_xpaths)
            print('#'*20)
            result = ''
            for xp in found_xpaths:
                tempcont = a.find_content(xp)

                if tempcont:
                    result += ' ' + tempcont

            '''
            contains_paths = False
            for path in self.desc_xpaths:
                if path in xpaths_to_use:
                    contains_paths = True

                if contains_paths:
                    break

                if not contains_paths:
                    result = content
            '''
            print title.encode('utf-8'), response.url, result.encode('utf-8')

            # get image urls
            image_urls = []
            for img in a.find_imgs(self.img_xpath):
                print(img)
                image_urls.append(img)

            #convert to utf8
            title = title.encode('utf-8')
            content = result.encode('utf-8')


            p = Product()
            p['template_id'] = self.template_id
            p['title'] = title
            p['content'] = content
            p['url'] = response.url
            p['image_urls'] = image_urls
            yield p
        else:
            self.logger.warning('No content found on %s in domain %s', response.url, self.allowed_domains[0])


if __name__ == "__main__":
	#process = CrawlerProcess(get_project_settings())
	print 'Argument List:', str(sys.argv)

	#process.crawl(ImpudoSpider)
	#process.start()
