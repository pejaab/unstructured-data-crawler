import re

import ast
from django import forms

from interface.models import Template, Crawler, CrawlerImg, CrawlerImgPath
from interface.analyzer.analyzer import Analyzer


EMPTY_URL_ERROR = 'You need to supply a URL'
EMPTY_DESC_ERROR = 'You need to supply a description'

SCRAPE_TEXT = '''ALVAR AALTO
MODEL 2145, 1942/ 1950S
MORE
EMBRU, SWITZERLAND

SOLD
'''

class TemplateForm(forms.models.ModelForm):

    class Meta:
        model = Template
        fields = ('url', 'desc',)
        widgets = {
                'url': forms.fields.URLInput(attrs={
                    'placeholder': 'Enter a url, e.g. http://www.etoz.ch/model-2145/',
                    'class': 'form-control input-lg',
                }),
                'desc': forms.Textarea(attrs={
                    'placeholder': 'Enter text to scrape, e.g.\n' + SCRAPE_TEXT,
                    'class': 'form-control input-lg',
                    }),
            }
        error_messages = {
                'url': {'required': EMPTY_URL_ERROR},
                'desc': {'required': EMPTY_DESC_ERROR},
                }

    def save(self):
        '''
        Saves the missing url_abbr field by pattern matching.
        '''
        #template = super(TemplateForm, self).save(commit=False)
        url = self['url'].value()
        match = re.search(r'^(http://|https://)(www.)?(?P<abbr>.*?)\.', url)
        url_abbr = match.group('abbr') if match else url
        self.instance.url_abbr = url_abbr
        return super(TemplateForm, self).save()

    def analyze(self):
        desc = self['desc'].value().replace('\r', '')
        url = self['url'].value()
        analyzer = Analyzer(url)
        paths = analyzer.analyze(desc)
        img_paths = analyzer.analyze_img()
        for path, content in paths:
            Crawler.objects.create(template= self.instance, xpath= path,
                                   content= content, url= url)

        for path in img_paths:
            crawler = CrawlerImgPath.objects.create(template= self.instance, xpath= path)
            for img in analyzer.search_imgs(path[:]):
                CrawlerImg.objects.create(img_path_id= crawler.pk, path= analyzer.download_img(img))

    def save_active_paths(self, active):
        url = self['url'].value()

        for crawler in active:
            #TODO: delete active xpaths from all_paths
            Crawler.objects.create(template= self.instance, xpath= crawler.xpath,
                                   content= crawler.content, url= url, active= 1)

    def save_active_imgs(self, active):
        url = self['url'].value()
        analyzer = Analyzer(url)
        for img in active:
            crawler = CrawlerImgPath.objects.create(template= self.instance, xpath= img.xpath, active= 1)
            for i in analyzer.search_imgs(ast.literal_eval(img.xpath)[:]):
                CrawlerImg.objects.create(img_path_id= crawler.pk, path= analyzer.download_img(i))

