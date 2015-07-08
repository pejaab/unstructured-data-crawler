# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0004_auto_20150702_0849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='desc',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='template',
            name='url_abbr',
            field=models.TextField(verbose_name='Name'),
        ),
    ]
