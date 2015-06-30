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
                ('template', models.IntegerField(serialize=False, primary_key=True)),
                ('paths', models.TextField()),
                ('result', models.TextField()),
            ],
        ),
    ]
