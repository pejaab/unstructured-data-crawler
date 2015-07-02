from django.core.exceptions import ValidationError
from django.test import TestCase

from interface.models import Template, Crawler

class TemplateModelsTest(TestCase):

    def test_saving_and_retrieving_items(self):
        first_item = Template()
        first_item.url_abbr = 'etoz'
        first_item.url = 'http://www.etoz.ch/model-21245/'
        first_item.desc = 'AALVARO'
        first_item.save()

        saved_item = Template.objects.latest('id')

        self.assertEqual(saved_item, first_item)

    def test_cannot_save_empty_template_item(self):
        item = Template(url_abbr='', url='', desc='')
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_get_absolute_url(self):
        item = Template.objects.create()
        self.assertEqual(item.get_absolute_url(), '/templates/%d/' % (item.id))

class CrawlerModelsTest(TestCase):

    def test_saving_and_retrieving_crawlers(self):
        template = Template.objects.create(url_abbr='etozi', url='http://www.etoz.ch/', desc='Alvar')
        first_crawler = Crawler.objects.create(template=template, url='http://www.etoz.ch/', xpath='path', content='content')
        second_crawler = Crawler.objects.create(template=template, url='http://www.etoz.ch/', xpath='path2', content='content2')

        saved_template = Template.objects.first()
        self.assertEqual(saved_template, template)

        saved_crawlers = Crawler.objects.all()
        self.assertEqual(saved_crawlers.count(), 2)
        
        first_saved = saved_crawlers[0]
        second_saved = saved_crawlers[1]
        self.assertEqual(first_crawler, first_saved)
        self.assertEqual(second_crawler, second_saved)
