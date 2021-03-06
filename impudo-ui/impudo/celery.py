from __future__ import absolute_import

import os

from celery import Celery



# set the defualt Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'impudo.settings')

from django.conf import settings


app = Celery('impudo', backend='rpc://', broker='amqp://')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


