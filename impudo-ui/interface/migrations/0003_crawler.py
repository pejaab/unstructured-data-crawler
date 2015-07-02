# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0002_auto_20150630_1231'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crawler',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('template', models.IntegerField()),
                ('xpath', models.TextField()),
                ('content', models.TextField()),
                ('url', models.URLField()),
                ('active', models.BooleanField(default=False)),
                ('crawled', models.CharField(max_length=20, default='False')),
            ],
        ),
    ]
