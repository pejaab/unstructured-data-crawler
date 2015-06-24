from django.core.urlresolvers import reverse
from django.db import models

class TemplateItem(models.Model):
    url_abbr = models.TextField()
    url = models.URLField()
    desc = models.TextField()

    def __str__(self):
        return self.url_abbr
    
    def get_absolute_url(self):
        return reverse('view_template', args=[self.id])
