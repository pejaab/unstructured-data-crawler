from django.test import TestCase

from interface.forms import EMPTY_URL_ERROR, EMPTY_DESC_ERROR, TemplateItemForm
from interface.models import TemplateItem

class TemplateItemFormTest(TestCase):

    def test_form_renders_template_item_text_input(self):
        form = TemplateItemForm()
        self.assertIn('placeholder="Enter a url, e.g. http://www.etoz.ch/model-21245/"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())
        self.assertIn('placeholder="Enter text to scrape"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = TemplateItemForm(data={'url': '', 'desc': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
                form.errors['url'],
                [EMPTY_URL_ERROR]
                )
        self.assertEqual(
                form.errors['desc'],
                [EMPTY_DESC_ERROR]
                )

    def test_form_save_handles_saving_to_db(self):
        form = TemplateItemForm(data={'url': 'http://www.etoz.ch/', 'desc': 'AALVARO'})
        new_template = form.save()
        self.assertEqual(new_template, TemplateItem.objects.first())
        self.assertEqual(new_template.url_abbr, 'etoz')
        self.assertEqual(new_template.url, 'http://www.etoz.ch/')
        self.assertEqual(new_template.desc, 'AALVARO')
