# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0006_scraped'),
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('title', models.CharField(default=None, max_length=200)),
                ('url', models.URLField()),
                ('result', models.TextField()),
                ('template', models.ForeignKey(default=None, to='interface.Template')),
            ],
        ),
        migrations.RemoveField(
            model_name='scraped',
            name='template',
        ),
        migrations.DeleteModel(
            name='Scraped',
        ),
    ]
