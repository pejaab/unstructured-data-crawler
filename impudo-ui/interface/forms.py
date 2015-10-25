import re

from django import forms

from interface.models import Template, Crawler, CrawlerImg
from interface.analyzer.analyzer import Analyzer


EMPTY_URL_ERROR = 'You need to supply a URL'
EMPTY_DESC_ERROR = 'You need to supply a description'
EMPTY_IMG_ERROR = 'You need to supply a URL to an image'

SCRAPE_TEXT = '''ALVAR AALTO
MODEL 2145, 1942/ 1950S	
MORE
EMBRU, SWITZERLAND

SOLD
'''

class TemplateForm(forms.models.ModelForm):

    class Meta:
        model = Template
        fields = ('url', 'desc', 'img',)
        widgets = {
                'url': forms.fields.URLInput(attrs={
                    'placeholder': 'Enter a url, e.g. http://www.etoz.ch/model-2145/',
                    'class': 'form-control input-lg',
                }),
                'desc': forms.Textarea(attrs={
                    'placeholder': 'Enter text to scrape, e.g.\n' + SCRAPE_TEXT,
                    'class': 'form-control input-lg',
                    }),
                'img': forms.TextInput(attrs={
                    'placeholder': 'Enter image url, e.g. http://www.etoz.ch/wp-content/uploads/2015/03/AALTOalvar_Sofa2145_001.jpg',
                    'class': 'form-control input-lg',
                    })
            }
        error_messages = {
                'url': {'required': EMPTY_URL_ERROR},
                'desc': {'required': EMPTY_DESC_ERROR},
                'img': {'required': EMPTY_IMG_ERROR},
                }
     
    def save(self):
        '''
        Saves the missing url_abbr field by pattern matching.
        '''
        #template = super(TemplateForm, self).save(commit=False)
        url = self['url'].value()
        match = re.search(r'^(http://www.|http://)(.*)\.', url)
        url_abbr = match.group(2) if match else url
        self.instance.url_abbr = url_abbr
        return super(TemplateForm, self).save()
    
    def analyze(self): 
        desc = self['desc'].value().replace('\r', '')
        url = self['url'].value()
        img_url = self['img'].value()
        analyzer = Analyzer(url)
        paths = analyzer.analyze(desc)
        img_path = analyzer.find_img_xpath(img_url)
        for path, content in paths:
            Crawler.objects.create(template= self.instance, xpath= path, content= content, url= url)

        CrawlerImg.objects.create(template= self.instance, xpath= img_path, url= analyzer.find_img_url(img_path))

    def save_inactive_records(self, active):
        url = self['url'].value()
        analyzer = Analyzer(url)
        all_paths = analyzer.analyze()
        #index_begin = next((idx for idx, tup in enumerate(all_paths) if tup[1] == active[0].content), None)
        #index_end = next((idx for idx, tup in enumerate(all_paths) if tup[1] == active[-1].content), None)
        path_begin = (active[0].xpath, active[0].content)
        path_end = (active[-1].xpath, active[-1].content)
        #path_begin = all_paths[index_begin-1]
        #path_end = all_paths[index_end+1]
        Crawler.objects.create(template= self.instance, xpath= path_begin[0], content = path_begin[1], url= url, active= 2)
        Crawler.objects.create(template= self.instance, xpath= path_end[0], content= path_end[1], url= url, active= 3)
        
        analyzer.eliminate_begin_and_end(all_paths, path_begin, path_end)
        
        actives = []
        import ast
        for crawler in active:
            #TODO: delete active xpaths from all_paths
            Crawler.objects.create(template= self.instance, xpath= crawler.xpath, content= crawler.content, url= url, active= 1)
            actives.append((ast.literal_eval(crawler.xpath), crawler.content))
       
        analyzer.eliminate_actives(all_paths, actives)

        for path, content in all_paths:
            Crawler.objects.create(template= self.instance, xpath= path, content= content, url= url) 
