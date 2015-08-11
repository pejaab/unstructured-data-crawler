import scrapy
from scrapy.pipelines.images import ImagesPipeline

class ImpudoImagesPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
    	print "media request " 
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        item['image_paths'] = image_paths
        print "ImpudoPipeline:" + results
        return item