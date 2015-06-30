import re

from django import forms

from interface.models import TemplateItem

EMPTY_URL_ERROR = 'You cannot have an empty URL'
EMPTY_DESC_ERROR = 'You cannot have an empty description'

class TemplateItemForm(forms.models.ModelForm):

    class Meta:
        model = TemplateItem
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
    
