import scrapy
import Image
from crawler.items import Product

class ImageSpider(scrapy.Spider):
	name = "imagespider"
	allowed_domains = ["etoz.ch"]
	start_urls = ["http://www.etoz.ch/la-tourette/"]

	imagexpath ="/html/body/section[2]/div/div/article/div[2]/div/ul/li[4]/img/@src"
	imagexpath2 = "/html/body/section[2]/div/div/article/div[2]/div/ul/li[1]/img/@src"

	def parse(self, response):

		product = Product()
		product['template_id'] = 27
		product['title'] = "Test-Title"
		product['content'] = "Test-Content"
		product['url'] = "http://testurl.com/"

		image_urls = []

		extractedurls = response.xpath(self.imagexpath).extract()
		for url in extractedurls:
			image_urls.append(url)
		
		extractedurls = response.xpath(self.imagexpath2).extract()
		for url in extractedurls:
			image_urls.append(url)
		
		product['image_urls'] = image_urls
		#print product['template_id']
		#print product['images']
		return product
		
