import re

from django import forms

from interface.models import Template, Crawler
from interface.analyzer.analyzer import Analyzer


EMPTY_URL_ERROR = 'You need to supply a URL'
EMPTY_DESC_ERROR = 'You need to supply a description'

class TemplateForm(forms.models.ModelForm):

    class Meta:
        model = Template
        fields = ('url', 'desc',)
        widgets = {
                'url': forms.fields.URLInput(attrs={
                    'placeholder': 'Enter a url, e.g. http://www.etoz.ch/model-21245/',
                    'class': 'form-control input-lg',
                }),
                'desc': forms.Textarea(attrs={
                    'placeholder': 'Enter text to scrape',
                    'class': 'form-control input-lg',
                    }),
            }
        error_messages = {
                'url': {'required': EMPTY_URL_ERROR},
                'desc': {'required': EMPTY_DESC_ERROR}
                }
     
    def save(self):
        '''
        Saves the missing url_abbr field by pattern matching.
        '''
        url = self['url'].value() 
        match = re.search(r'^(http://www.|http://)(.*)\.', url)
        url_abbr = match.group(2) if match else url
        self.instance.url_abbr = url_abbr
        return super().save() 
    
    def analyze(self): 
        desc = self['desc'].value().replace('\r', '')
        url = self['url'].value()
        analyzer = Analyzer(url)
        paths = analyzer.analyze(desc)

        for path in paths:
            Crawler.objects.create(template= self.instance, xpath= path, content= analyzer.find_content(path), url= url)
