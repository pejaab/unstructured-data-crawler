from django.core.urlresolvers import reverse
from django.db import models

class Template(models.Model):
    url_abbr = models.TextField(verbose_name='Name')
    url = models.URLField()
    desc = models.TextField(verbose_name='Description')
    img = models.TextField(verbose_name='Image link')
    
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

class Record(models.Model):
    template = models.ForeignKey(Template, default=None)
    title = models.CharField(max_length=200, default=None)
    url = models.URLField()
    result = models.TextField()
    
    def __str__(self):
        return str(self.pk)


class CrawlerImg(models.Model):
    template = models.ForeignKey(Template, default=None)
    xpath = models.TextField()
    url = models.TextField()

'''
class Image(models.Model):
    record = models.ForeignKey(Record, default=None)
    url = models.URLField()
    path = CharField(max_lenth=200, default=None)
'''
