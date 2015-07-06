from django.core.urlresolvers import reverse
from django.db import models

from interface.analyzer.analyzer import Analyzer

class Template(models.Model):
    url_abbr = models.TextField(verbose_name='Name')
    url = models.URLField()
    desc = models.TextField(verbose_name='Description')
    
    def __str__(self):
        return self.url_abbr
    
    def get_absolute_url(self):
        return reverse('view_template', args=[self.id])


class Crawler(models.Model):
    template = models.ForeignKey(Template, default=None)
    xpath = models.TextField()
    content = models.TextField()
    url = models.URLField()
    active = models.BooleanField(default=False)
    crawled = models.CharField(max_length=20, default='False')

    def __str__(self):
        return str(self.pk)
