import re

from django import forms

from interface.models import Template, Crawler
from interface.analyzer.analyzer import Analyzer


EMPTY_URL_ERROR = 'You cannot have an empty URL'
EMPTY_DESC_ERROR = 'You cannot have an empty description'

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
        analyzer = Analyzer()

        def split_on_eof(desc):
            #desc_items = list(filter(None, map(str.lower, desc.split('\n'))))
            desc_items = list(filter(None, desc.split('\n')))
            return desc_items

        def split_on_space(item):
            desc_items = list(filter(None, item.split(' ')))
            return desc_items
        
        #TODO: try and except catch of indexerror in analyzer???
        paths = []
        results = []
        for line in split_on_eof(desc):
            try:
                path = analyzer.search_path(url, line)
                if not path in paths:
                    paths.append(path)
                    results.append(analyzer.search_content(url, path))
            except IndexError as e:
                print('Error: %s' %(e,))
                '''
                for item in split_on_space(line):
                    try:
                        path = analyzer.search_path(url, item)
                        if not path in paths:
                            paths.append(path)
                            results.append(analyzer.search_content(url, path))
                    except IndexError as e:
                        print('Error: %s' %(e,))
                '''
        #print(self.instance.pk)
        #print(paths)
        #print(results)
        crawler, created = Crawler.objects.get_or_create(
                template=self.instance.pk, defaults={'paths':';'.join(paths), 'results':';'.join(results)}
                )
        if not created:
            crawler.paths = ';'.join(paths)
            crawler.results = ';'.join(results)
            crawler.save()
