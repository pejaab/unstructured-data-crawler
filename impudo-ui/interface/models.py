from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver

from StringIO import StringIO
from PIL import Image as Img
import os

from impudo.settings import BASE_DIR
from impudo.settings import MEDIA_ROOT

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


class CrawlerImgPath(models.Model):
    template = models.ForeignKey(Template, default=None)
    xpath = models.TextField()
    active = models.IntegerField(default=0)

class CrawlerImg(models.Model):
    img_path = models.ForeignKey(CrawlerImgPath, default=None)
    path = models.CharField(max_length=500)

    def img(self):
        return u'<img src="../../../../media/%s" width="100"/>' % (self.path)

class Image(models.Model):
    record = models.ForeignKey(Record, default=None)
    path = models.CharField(max_length=500)

    def img(self):
        return u'<img src="../../../../media/%s" width="100"/>' % (self.path)
    img.short_description = 'Image'
    img.allow_tags = True

    def __str__(self):
        return str(self.pk)

@receiver(models.signals.post_delete, sender=CrawlerImg)
def CrawlerImg_delete(sender, instance, *args, **kwargs):
    try:
        os.remove(os.path.join(MEDIA_ROOT, instance.path))
    except OSError:
        pass

@receiver(models.signals.post_delete, sender=Image)
def Image_delete(sender, instance, *args, **kwargs):
    try:
        os.remove(os.path.join(MEDIA_ROOT, instance.path))
    except OSError:
        pass
