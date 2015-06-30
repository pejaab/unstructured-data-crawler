from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase

from interface.forms import EMPTY_URL_ERROR, EMPTY_DESC_ERROR, TemplateForm
from interface.models import Template
from interface.views import home_page

class HomePageTest(TestCase):

    def test_home_page_renders_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_uses_template_item_form(self):
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], TemplateForm)


    def test_saving_and_retrieving_items(self):
        first_item = Template()
        first_item.url_abbr = 'etoz'
        first_item.url = 'http://www.etoz.ch/model-2145/'
        first_item.desc = 'Aalvaro'
        first_item.save()

        saved_item = Template.objects.latest('id')

        self.assertEqual(saved_item, first_item)
 
class NewTemplateTest(TestCase):

    def test_saving_POST_request(self):
        url =  'http://www.etoz.ch/model-2145'
        desc = 'Aalvaro'
        self.client.post('/templates/new',
                data={
                    'url': url,
                    'desc': desc
                    }
                )
        
        self.assertEqual(Template.objects.count(), 1)
        new_item = Template.objects.latest('id')
        self.assertEqual(new_item.url_abbr, 'etoz')
        self.assertEqual(new_item.url,  url)
        self.assertEqual(new_item.desc, desc)

    def test_redirects_after_POST(self):
        url = 'http://www.etoz.ch/model-2145' 
        desc = 'Aalvaro'
        
        response = self.client.post(
                '/templates/new',
                data={
                    'url': url,
                    'desc': desc
                    }
                )
        item = Template.objects.latest('id')
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
        self.assertIsInstance(response.context['form'], TemplateForm)

    def test_invalid_templates_arent_saved(self):
        self.client.post('/templates/new', data={'url': '', 'desc': ''})
        self.assertEqual(Template.objects.count(), 0)

    def test_displays_template_item_form(self):
        item = Template.objects.create()
        response = self.client.get('/templates/%d/' % (item.id))
        self.assertIsInstance(response.context['form'], TemplateForm)
        self.assertContains(response, 'name="url"')
        self.assertContains(response, 'name="desc"')

class TemplateViewTest(TestCase):

    def test_uses_template_template(self):
        item = Template.objects.create()
        response = self.client.get('/templates/%d/' % (item.id,))
        self.assertTemplateUsed(response, 'template.html')
    
    def test_displays_template_content(self):
        item = Template.objects.create(url_abbr='etoz', url='http://www.etoz.ch/model-2145', desc='Aalvaro')

        response = self.client.get('/templates/%d/' % (item.id,))
        self.assertContains(response, 'http://www.etoz.ch/model-2145')
        self.assertContains(response, 'Aalvaro')

    def test_passes_correct_id_to_template(self):
        other_item = Template.objects.create()
        correct_item = Template.objects.create()
        response = self.client.get('/templates/%d/' % (correct_item.id,))
        self.assertEqual(response.context['item'], correct_item)

    def test_saves_POST_request_to_existing_template(self):
        item = Template.objects.create(url_abbr='test', url='http://test.com', desc='test')
        self.client.post(
                '/templates/%d/' % (item.id,),
                data={'url': 'http://www.etoz.ch/model-2145', 'desc': 'Aalvaro'}
                )
        changed_item = Template.objects.get(id=item.id) 
        self.assertEqual(changed_item.url, 'http://www.etoz.ch/model-2145')
        self.assertEqual(changed_item.desc, 'Aalvaro')

    def post_invalid_input(self):
        item = Template.objects.create()
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
        self.assertIsInstance(response.context['form'], TemplateForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, EMPTY_URL_ERROR)
        self.assertContains(response, EMPTY_DESC_ERROR)


