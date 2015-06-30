from django.core.exceptions import ValidationError
from django.test import TestCase

from interface.models import Template

class TemplateItemModelsTest(TestCase):

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
