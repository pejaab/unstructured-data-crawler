from django.core.urlresolvers import reverse
from django.db import models

from StringIO import StringIO
from PIL import Image as Img
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
    active = models.IntegerField(default=0)
    crawled = models.CharField(max_length=20, default='False')

    def __str__(self):
        return str(self.pk)

class Record(models.Model):
    template = models.ForeignKey(Template, default=None)
    title = models.CharField(max_length=200, default=None)
    url = models.URLField()
    result = models.TextField()
    price = models.CharField(max_length=100, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.pk)


class CrawlerImg(models.Model):
    template = models.ForeignKey(Template, default=None)
    xpath = models.TextField()
    path = models.CharField(max_length=500)
    active = models.IntegerField(default=0)

    def img(self):
        return u'<img src="../../../../media/{}" width="100"/>'.format(self.path)

class Image(models.Model):
    '''
    # after: https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.FileField.upload%5Fto
    # and: http://stackoverflow.com/questions/1190697/django-filefield-with-upload-to-determined-at-runtime
    def directory_path(self, filename):
        return 'template_{0}/record_{1}/{2}'.format()
    '''
    record = models.ForeignKey(Record, default=None)
    path = models.CharField(max_length=500)

    def img(self):
        return u'<img src="../../../../media/%s" width="100"/>' % (self.path)
    img.short_description = 'Image'
    img.allow_tags = True

    def __str__(self):
        return str(self.pk)

