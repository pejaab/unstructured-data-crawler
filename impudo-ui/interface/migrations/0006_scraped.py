# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0005_auto_20150706_1418'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scraped',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=200, default=None)),
                ('url', models.URLField()),
                ('result', models.TextField()),
                ('template', models.ForeignKey(default=None, to='interface.Template')),
            ],
        ),
    ]
