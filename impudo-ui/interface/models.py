from django.core.urlresolvers import reverse
from django.db import models

from interface.analyzer.analyzer import Analyzer

class Template(models.Model):
    url_abbr = models.TextField()
    url = models.URLField()
    desc = models.TextField()
    
    def __str__(self):
        return self.url_abbr
    
    def get_absolute_url(self):
        return reverse('view_template', args=[self.id])


class Crawler(models.Model):
    template = models.IntegerField(primary_key=True)
    paths = models.TextField()
    results = models.TextField()
    url = models.URLField()

    def get_absolute_url(self):
        return reverse('view_template', args=[self.template])
