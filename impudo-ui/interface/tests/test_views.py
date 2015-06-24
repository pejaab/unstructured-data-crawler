from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase

from interface.forms import EMPTY_URL_ERROR, EMPTY_DESC_ERROR, TemplateItemForm
from interface.models import TemplateItem
from interface.views import home_page

class HomePageTest(TestCase):

    def test_home_page_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_template_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], TemplateItemForm)


    def test_saving_and_retrieving_items(self):
        first_item = TemplateItem()
        first_item.url_abbr = 'etoz'
        first_item.url = 'http://www.etoz.ch/model-21245/'
        first_item.desc = 'AALVARO'
        first_item.save()

        saved_item = TemplateItem.objects.latest('id')

        self.assertEqual(saved_item, first_item)
 
class NewTemplateTest(TestCase):

    def test_saving_POST_request(self):
        url =  'http://www.etoz.ch'
        desc = 'AALVARO'
        self.client.post('/templates/new',
                data={
                    'url': url,
                    'desc': desc
                    }
                )
        
        self.assertEqual(TemplateItem.objects.count(), 1)
        new_item = TemplateItem.objects.latest('id')
        self.assertEqual(new_item.url_abbr, 'etoz')
        self.assertEqual(new_item.url,  url)
        self.assertEqual(new_item.desc, desc)

    def test_redirects_after_POST(self):
        url = 'http://www.d-68.com' 
        desc = 'AALVARO'
        
        response = self.client.post(
                '/templates/new',
                data={
                    'url': url,
                    'desc': desc
                    }
                )
        item = TemplateItem.objects.latest('id')
        self.assertRedirects(response, '/templates/%d/' % (item.id))

    def test_for_invalid_input_renders_home_template(self):
        response = self.client.post('/templates/new', data={'url': '', 'desc': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_validation_errors_are_shown_on_home_page(self):
        response = self.client.post('/templates/new', data={'url': '', 'desc': ''})
        self.assertContains(response, EMPTY_URL_ERROR)
        self.assertContains(response, EMPTY_DESC_ERROR)

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.client.post('/templates/new', data={'url': '', 'desc': ''})
        self.assertIsInstance(response.context['form'], TemplateItemForm)

    def test_invalid_templates_arent_saved(self):
        self.client.post('/templates/new', data={'url': '', 'desc': ''})
        self.assertEqual(TemplateItem.objects.count(), 0)

    def test_displays_template_item_form(self):
        item = TemplateItem.objects.create()
        response = self.client.get('/templates/%d/' % (item.id))
        self.assertIsInstance(response.context['form'], TemplateItemForm)
        self.assertContains(response, 'name="url"')
        self.assertContains(response, 'name="desc"')

class TemplateViewTest(TestCase):

    def test_uses_template_template(self):
        item = TemplateItem.objects.create()
        response = self.client.get('/templates/%d/' % (item.id,))
        self.assertTemplateUsed(response, 'template.html')
    
    def test_displays_template_content(self):
        item = TemplateItem.objects.create(url_abbr='etoz', url='http://www.etoz.ch/', desc='AALVARO')

        response = self.client.get('/templates/%d/' % (item.id,))
        self.assertContains(response, 'http://www.etoz.ch/')
        self.assertContains(response, 'AALVARO')

    def test_passes_correct_id_to_template(self):
        other_item = TemplateItem.objects.create()
        correct_item = TemplateItem.objects.create()
        response = self.client.get('/templates/%d/' % (correct_item.id,))
        self.assertEqual(response.context['item'], correct_item)

    def test_saves_POST_request_to_existing_template(self):
        item = TemplateItem.objects.create(url_abbr='test', url='http://test.com', desc='test')
        self.client.post(
                '/templates/%d/' % (item.id,),
                data={'url': 'http://changed.com', 'desc': 'changes desc'}
                )
        changed_item = TemplateItem.objects.get(id=item.id) 
        self.assertEqual(changed_item.url, 'http://changed.com')
        self.assertEqual(changed_item.desc, 'changes desc')

    def post_invalid_input(self):
        item = TemplateItem.objects.create()
        return self.client.post(
                '/templates/%d/' % (item.id),
                data={'url': '', 'desc': ''}
                )

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'template.html')

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context['form'], TemplateItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, EMPTY_URL_ERROR)
        self.assertContains(response, EMPTY_DESC_ERROR)


