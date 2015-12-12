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


        #get img xpath
        self.img_xpath = []
        result = self.dao.get_img_xpath(self.template_id)
        for xpath in result:
            self.img_xpath.append(ast.literal_eval(xpath[0]))

        #get and set rules for specific domain if they exist in the db
        textrules = self.dao.get_rules(self.allowed_domains[0])

        if textrules:
            frulesactive = False
            prulesactive = False
            fprulesactive = False
            frule = None
            prule = None
            fprule = None

            follows = None
            follow_denies = None
            xpath_follow_restrict = None
            parses = None
            parse_denies = None
            xpath_parse_restrict = None
            follow_and_parse = None
            follow_and_parse_denies = None
            xpath_fp_restrict = None

            if textrules[0] or textrules[1] or textrules[2]:
                frulesactive = True
                follows = tuple(textrules[0].split(','))
                follow_denies = tuple(textrules[1].split(','))
                xpath_follow_restrict = textrules[2]
                if not xpath_follow_restrict:
                    frule = Rule(LinkExtractor(allow=follows, deny=follow_denies,), follow=True)
                else:
                    frule = Rule(LinkExtractor(allow=follows, deny=follow_denies, restrict_xpaths=(xpath_follow_restrict)), follow=True)

            if textrules[3] or textrules[4] or textrules[5]:
                prulesactive = True
                parses = tuple(textrules[3].split(','))
                parse_denies = tuple(textrules[4].split(','))
                xpath_parse_restrict = textrules[5]
                if not xpath_parse_restrict:
                    prule = Rule(LinkExtractor(allow=parses, deny=parse_denies, ), callback='parse_product')
                else:
                    prule = Rule(LinkExtractor(allow=parses, deny=parse_denies, restrict_xpaths=(xpath_parse_restrict)), callback='parse_product')


            if textrules[6] or textrules[7] or textrules[8]:
                fprulesactive = True
                follow_and_parse = tuple(textrules[6].split(','))
                follow_and_parse_denies = tuple(textrules[7].split(','))
                xpath_fp_restrict = textrules[8]
                if not xpath_fp_restrict:
                    fprule = Rule(LinkExtractor(allow=follow_and_parse, deny=follow_and_parse_denies,), callback='parse_product', follow=True)
                else:
                    fprule = Rule(LinkExtractor(allow=follow_and_parse, deny=follow_and_parse_denies, restrict_xpaths=(xpath_fp_restrict)), callback='parse_product', follow=True)

            #given rules were empty, use standard Ruleset
            if not frulesactive and not prulesactive and not fprulesactive:
                ImpudoSpider.rules = (Rule(LinkExtractor(allow=('')), callback='parse_product', follow=True),)
            else:
                ImpudoSpider.rules = ()
                if fprulesactive:
                    ImpudoSpider.rules = ImpudoSpider.rules +  (fprule, )
                if frulesactive:
                    ImpudoSpider.rules = ImpudoSpider.rules + (frule, )
                if prulesactive:
                    ImpudoSpider.rules = ImpudoSpider.rules + (prule, )

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
        counter = 0
        for path in self.desc_xpaths:
            tempcont = a.find_content(path)

            if tempcont:
                content += ' ' + tempcont
            else:
                counter += 1
        #ignore if no content is found
        if counter >= 2:
            content = ''
        if content:
            print title.encode('utf-8'), response.url, content.encode('utf-8')
            # get image urls
            image_urls = []
            for xpath in self.img_xpath:
                img_url = a.search_imgs(xpath[:])
                if img_url is not None:
                    image_urls += img_url
            # clean out duplicates
            result = []
            for img in image_urls:
                if img not in result:
                    result.append(img)
            image_urls = result

            for img in image_urls:
                print(img)

            #convert to utf8
            title = title.encode('utf-8')
            content = content.encode('utf-8')


            p = Product()
            p['template_id'] = self.template_id
            p['title'] = title
            p['content'] = content[1:]
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
